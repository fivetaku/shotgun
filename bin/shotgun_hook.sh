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

if [ "$EVENT" = "session-start" ]; then
  if [ -f "$STATE/config.json" ] && [ -n "$PY" ]; then
    nohup "$PY" "$HERE/shotgun_listener.py" >/dev/null 2>&1 &
    disown 2>/dev/null || true
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
    "down first. Do not finish your current thought first.\n"
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
