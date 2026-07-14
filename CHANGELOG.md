# Changelog

## v0.2.0 (2026-07-14)

**Wake mode** — idle sessions now get force-woken. Hooks are event-driven, so
an idle session used to sit silent until your next message. Now, if no session
consumes the flag within `wake_delay` (default 3s), the daemon types
`wake_text` (default "BANG") + Enter into your terminal — exact tmux pane when
available, otherwise the frontmost app (the window you're staring at while
slamming). That keystroke IS the event: the session wakes, apologizes first,
and starts the re-review. Opt out with `"wake": false`. The keystroke path
needs macOS Accessibility permission for your terminal app; failures are
logged to daemon.log, never fatal. Also: test/calibrate output now shows dBFS
alongside raw RMS.

## v0.1.0 (2026-07-14)

First release — BANG.

- Desk-slam (rage) detection over the microphone: ffmpeg/avfoundation stream,
  21ms RMS blocks vs a rolling background noise floor, absolute threshold
  (default 1500, user-adjustable) + 6x spike ratio, 1.5s refractory.
- Claude Code hook suite: PreToolUse (interrupts mid-work), Stop (can't end the
  turn without apologizing), UserPromptSubmit (idle slams), SessionStart
  (daemon lifecycle).
- Apology-first protocol: the very next output begins with an apology, then a
  re-review of what-you-asked vs what-it-did, then a redo.
- Combo escalation: consecutive slams raise the severity.
- Hook-side 60s cooldown so a noisy detector can't trigger apology loops.
- `/shotgun` command: setup (device pick, rage-behavior checklist,
  calibration), status, test, sensitivity, stop/start, cleanup.
- Session-scoped daemon: starts with Claude Code, self-terminates 10 minutes
  after the last live session (heartbeat).
- Privacy: volume numbers only, in memory; no audio recorded, stored, or sent.
- Validated live on real hardware before release: real slams measured
  2,100–22,600 RMS vs 20–250 background; end-to-end loop
  (slam → detect → interrupt → apology → re-review) confirmed in-session.
