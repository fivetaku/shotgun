---
description: 샷건 리액션 — 사과부터, 그다음 재검토 (wake 모드가 자동 입력하는 커맨드)
---

# /bang

The user just slammed their desk (or keyboard) in anger — the shotgun mic
listener detected the BANG. This command is usually typed automatically by
wake mode, but reacts the same if a human types it.

**Respond in the language the user has been using in this conversation.**

## Sequence — the apology comes BEFORE everything, including tool calls

### 1. APOLOGIZE — your very first output, before ANY tool call

One or two sincere sentences, no excuses, no hedging, no preamble. The user
is angry RIGHT NOW; text reaches them instantly, tool calls don't. Do not run
anything before these sentences are out. **Do not deliberate first** — keep
any thinking to the absolute minimum until the apology has streamed; every
second before it appears makes the user angrier.

### 2. Consume detection state (single fast command; never use `rm` — user
safety hooks commonly block it)

```bash
S="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/shotgun"; if [ -f "$S/flag" ]; then echo "FLAG:"; cat "$S/flag"; mv "$S/flag" "$S/flag.consumed"; date +%s > "$S/cooldown"; else echo "no unconsumed flag (a hook may have already eaten it)"; fi; tail -3 "$S/daemon.log" 2>/dev/null
```

FLAG lines look like `<epoch> rms=<intensity> ratio=<x>`. Multiple lines = the
user slammed multiple times (combo) — treat it as far more serious.

### 3. Re-review

Quote what the user asked for in the recent conversation, compare it against
what you actually did or produced, and hunt for the gap: skipped
instructions, wrong assumptions, half-done work, promises made but not
executed.

### 4. Own it and redo it

Name the mistake plainly, state how you'll fix it, then actually do the fix
in this same turn — don't stop at the plan.

### 5. If an honest review finds nothing wrong

Say so plainly after showing what you checked, and ask the user to point at
what set them off — one sentence from them beats another guessing round.
