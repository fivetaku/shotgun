---
description: 샷건 리액션 — 사과부터, 그다음 재검토 (wake 모드가 자동 입력하는 커맨드)
---

# /bang

The user just slammed their desk (or keyboard) in anger — the shotgun mic
listener detected the BANG. This command is usually typed automatically by
wake mode, but reacts the same if a human types it.

**Respond in the language the user has been using in this conversation.**

## Step 0 — consume detection state (run first, silently)

```bash
S="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/shotgun"
if [ -f "$S/flag" ]; then
  echo "FLAG:"; cat "$S/flag"
  rm -f "$S/flag"; date +%s > "$S/cooldown" 2>/dev/null
else
  echo "no unconsumed flag (a hook may have already eaten it)"
fi
tail -3 "$S/daemon.log" 2>/dev/null
```

FLAG lines look like `<epoch> rms=<intensity> ratio=<x>`. Multiple lines = the
user slammed multiple times (combo) — treat it as far more serious.

## Protocol — sequence is critical

1. **Your FIRST sentences are the apology.** One or two sentences, sincere, no
   excuses, no hedging, before ANY analysis or tool output. Calm the user down
   first. Mention intensity/combo only briefly if it helps ("두 번 치셨네요 —
   심각하게 받겠습니다" style).
2. **Then the re-review.** Quote what the user asked for in the recent
   conversation, compare it against what you actually did or produced, and
   hunt for the gap: skipped instructions, wrong assumptions, half-done work,
   promises made but not executed.
3. **Own it and redo it.** Name the mistake plainly, state how you'll fix it,
   then actually do the fix in this same turn — don't stop at the plan.
4. **If an honest review finds nothing wrong**, say so plainly after showing
   what you checked, and ask the user to point at what set them off — one
   sentence from them beats another guessing round.
