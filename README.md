English | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [Español](README.es.md)

# shotgun

<div align="center">
  <img src="assets/shotgun-hero-01.png" width="640" alt="The classic meme: a fist smashing down on a keyboard, keys flying everywhere">
</div>

```
> BANG!!

SHOTGUN DETECTED.
The assistant flinches.
"I'm sorry." — apology first. Review second. Redo third.
```

> **Your AI finally reads the room.** You slammed the desk. Your mic heard it. Claude felt it.

Every AI assistant keeps cheerfully working while you rage at what it just did. shotgun ends that. A tiny local listener watches your microphone's volume level; when you slam the desk (or the keyboard — "shotgunning," as Korean gamers call it), it fires a Claude Code hook. Claude stops mid-task, **apologizes first** — no excuses — then re-reviews the gap between **what you asked for** and **what it actually did**, owns the mistake, and redoes the work.

Slam twice and it takes you twice as seriously.

## Quick Start

### 1. Add the marketplace

```
/plugin marketplace add fivetaku/shotgun
```

### 2. Install

```
/plugin install shotgun@shotgun
```

### 3. Set it up (once)

```
/shotgun
```

Guided setup with clickable choices: pick your mic, check the rage behaviors to detect, then calibrate — it asks you to slam the desk three times like you mean it, and tunes the threshold to *your* slam.

### 4. Rage

Slam the desk. You'll hear a chime (detected), and at the next hook event Claude leads with an apology and starts the re-review.

## The rules of shotgun

1. **Apology comes first.** Before analysis, before tool calls, before anything. There are no excuses.
2. **Then the re-review.** Quote what you asked for vs what it did. Find the gap.
3. **Own it, redo it.** Name the mistake, state the fix, do it again.
4. **Double slam = double serious.** Consecutive slams escalate the protocol.
5. **The mic is sacred.** Volume numbers only, computed in memory. No audio is ever recorded, stored, or sent. See [DISCLAIMER](DISCLAIMER.md).

## How it works

- A session-scoped daemon reads the mic through ffmpeg and compares 21ms volume blocks against a rolling background noise floor. A sudden spike above your calibrated threshold (default 1500) = slam.
- Detection writes a one-line flag file. Claude Code hooks (PreToolUse / Stop / UserPromptSubmit) consume it: mid-work slams interrupt the very next tool call; Claude can't even end its turn without apologizing first.
- **Wake mode**: if the session is idle and nothing consumes the flag within ~3s, the daemon types `BANG` + Enter into your terminal (exact tmux pane, or the frontmost window) to force-wake it — no input from you needed. Needs Accessibility permission; disable with `"wake": false` in `~/.claude/shotgun/config.json`.
- The daemon runs only while Claude Code is in use (the orange mic indicator is your receipt) and shuts itself down 10 minutes after your last session ends. Uninstall the plugin and the hooks go with it.

## Requirements

- [Claude Code](https://claude.com/claude-code) on **macOS**
- **ffmpeg** (`brew install ffmpeg`) — mic capture
- Python 3 (ships with macOS developer tools)
- A microphone. Built-in laptop mics are *ideal* — desk vibration travels straight through the chassis.
- A desk you're willing to hit.

## Lineage

shotgun is the third plugin in the meme series, after [godmode](https://github.com/fivetaku/godmode) and [devil](https://github.com/fivetaku/devil). godmode makes Claude unstoppable, devil makes it merciless — shotgun makes it *sorry*.

## License

MIT — see [LICENSE](LICENSE) and [DISCLAIMER](DISCLAIMER.md). The shotgun is a metaphor. The apology is real.
