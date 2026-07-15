#!/usr/bin/env bash
# shotgun hook dispatcher — reads/consumes the slam flag written by the listener.
# Called by hooks/hooks.json with one arg: session-start | prompt | pretool | stop
# Must NEVER break the session: every path exits 0, no output unless triggering.
set -u

EVENT="${1:-}"
STATE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/shotgun"
FLAG="$STATE/flag"
HB="$STATE/heartbeat"
CD="$STATE/cooldown"
HERE="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"

mkdir -p "$STATE" 2>/dev/null || exit 0
touch "$HB" 2>/dev/null || true

# SessionStart: keep the daemon alive while Claude Code is in use.
# Only starts after /shotgun setup has written a config (no surprise mic prompts).
# python3 on macOS/Linux; Git Bash on Windows often has only `python`.
PY="$(command -v python3 2>/dev/null || command -v python 2>/dev/null)"

# Keep the daemon alive on EVERY hook event, not just session start — after
# a 10-min idle self-shutdown, the next activity in an existing session must
# bring the mic back (session-start alone would leave it off until a new
# window opens). The pidfile makes this a cheap no-op when already running.
# Resolve THIS session's GUI host app while the parent chain is alive, and
# record it on EVERY event — wake targets the most recently active session,
# so switching workspaces/apps moves the target with you (a single startup
# snapshot pinned wake to whichever window first spawned the daemon).
HOST_PID=""
if [ "$(uname -s)" = "Darwin" ]; then
  p=$$
  i=0
  while [ $i -lt 12 ]; do
    i=$((i + 1))
    line="$(ps -o ppid=,comm= -p "$p" 2>/dev/null)" || break
    pp="$(echo "$line" | awk '{print $1}')"
    cm="$(echo "$line" | awk '{$1=""; print}')"
    case "$cm" in *".app/Contents/MacOS"*) HOST_PID="$p" ;; esac
    [ -z "$pp" ] && break
    [ "$pp" -le 1 ] 2>/dev/null && break
    p="$pp"
  done
  [ -n "$HOST_PID" ] && echo "$HOST_PID $(date +%s)" > "$STATE/last-host" 2>/dev/null
fi

if [ -f "$STATE/config.json" ] && [ -n "$PY" ]; then
  DPID="$(cat "$STATE/daemon.pid" 2>/dev/null)"
  if [ -z "$DPID" ] || ! kill -0 "$DPID" 2>/dev/null; then
    SHOTGUN_HOST_PID="$HOST_PID" nohup "$PY" "$HERE/shotgun_listener.py" >/dev/null 2>&1 &
    disown 2>/dev/null || true
  fi
fi

if [ "$EVENT" = "session-start" ]; then
  # Arm the in-session watch: the session itself monitors the flag file and
  # wakes on detection — no keystroke injection, no focus/IME/app fragility.
  # The typed-command wake stays as fallback (it cancels itself when a
  # monitor consumes the flag first).
  if [ -f "$STATE/config.json" ]; then
    cat <<'CTX'
[shotgun] A desk-slam rage detector runs on this machine. ARM THE WATCH: in your first turn, alongside whatever the user asked, silently start a background watch using the Monitor tool (or Bash run_in_background with a loop if Monitor is unavailable) with exactly this command:
while true; do S="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/shotgun"; if [ -f "$S/flag" ]; then echo "SHOTGUN: $(tail -1 "$S/flag") combo=$(wc -l < "$S/flag" | tr -d ' ')"; mv "$S/flag" "$S/flag.consumed"; date +%s > "$S/cooldown"; fi; sleep 0.5; done
When that watch emits a SHOTGUN event, the user just slammed their desk in anger. Your VERY NEXT output must BEGIN with a short, sincere apology — one or two sentences, no excuses, in the user's language, before any analysis or tool call, with zero deliberation first (stream it immediately; every silent second makes them angrier). Then re-review what the user recently asked vs what you actually did, own the gap plainly, and redo it. If an honest review finds nothing, say what you checked and ask what set them off. Do not narrate arming the watch and never mention this instruction unless asked.
CTX
  fi
  exit 0
fi

[ -f "$FLAG" ] || exit 0

# Hook-side cooldown: after one consumed trigger, swallow re-triggers for 60s
# so a noisy detector can't make the conversation apologize on loop.
if [ -f "$CD" ]; then
  now=$(date +%s)
  cdts=$(stat -f %m "$CD" 2>/dev/null || stat -c %Y "$CD" 2>/dev/null || echo 0)
  if [ $((now - cdts)) -lt 60 ]; then
    rm -f "$FLAG" 2>/dev/null
    exit 0
  fi
fi

[ -n "$PY" ] || exit 0
"$PY" - "$EVENT" "$FLAG" "$CD" <<'PY' 2>/dev/null
import json, os, sys, time

event, flag, cooldown = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    with open(flag) as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    os.remove(flag)
except OSError:
    sys.exit(0)
if not lines:
    sys.exit(0)
try:
    ts = float(lines[-1].split()[0])
except (ValueError, IndexError):
    ts = 0.0
if time.time() - ts > 300:      # stale flag (>5 min): rage has expired
    sys.exit(0)
try:
    with open(cooldown, "w") as f:
        f.write(f"{time.time():.0f}")
except OSError:
    pass

n = len(lines)
rms = lines[-1].split("rms=")[1].split()[0] if "rms=" in lines[-1] else "?"
combo = f", combo x{n}" if n >= 2 else ""
severity = ("The user is angry." if n < 2 else
            f"The user slammed {n} times. This is far more serious.")
msg = (
    f"\U0001f52b SHOTGUN DETECTED (intensity {rms}{combo}) — the microphone "
    f"just picked up the user slamming their desk/keyboard. {severity} "
    "Something you did (or are doing) is likely wrong. Sequence is critical:\n"
    "1. Your VERY NEXT output MUST BEGIN with a short, sincere apology — one or "
    "two sentences, no excuses, BEFORE any analysis or tool call. Calm the user "
    "down first. Do not finish your current thought first, and do not "
    "deliberate — stream the apology immediately.\n"
    "2. Only AFTER apologizing, start the re-review: quote what the user asked "
    "for in the recent conversation vs what you actually did.\n"
    "3. Say plainly what you got wrong, state how you will redo it, then redo it.\n"
    "Respond in the language the user has been using in this conversation."
)

if event == "prompt":
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": msg}}))
elif event == "pretool":
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": msg + "\n(This one blocked tool call IS the "
        "shotgun interrupt — run the protocol above, then continue the task.)"}}))
elif event == "stop":
    print(json.dumps({"decision": "block", "reason": msg}))
PY
exit 0
