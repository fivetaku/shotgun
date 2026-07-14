# Changelog

## v0.3.1 (2026-07-14)

Wake injection hardening, field-tested against VS Code:

- Synthetic cmd+V paste is ignored by Electron terminals — wake is back to
  character keystrokes (the channel verified to land), with a sacrificial
  char + delete against first-character drops and a 1.2s pause so the slash
  menu settles on the exact /bang match before Enter fires.
- Typing-collision guard: wake now waits for a pause in the user's own typing
  (HID idle ≥ 1.2s, up to 15s) and cancels itself if a hook consumed the flag
  meanwhile.
- Caveat: in a session opened BEFORE the plugin was installed, /bang doesn't
  exist and Enter can select the top fuzzy menu entry instead — restart open
  windows after installing.

## v0.3.0 (2026-07-14)

- **Wake now types `/bang`** — a real slash command instead of a prompt blob.
  The plugin's own `/bang` instruction file drives the fixed workflow:
  apology FIRST, then consume detection state (intensity/combo), then the
  structured asked-vs-did re-review, then the redo. Works identically when a
  human types /bang.
- **Clipboard-paste injection** replaces System Events keystrokes — fixes the
  dropped first character ("BANG" arriving as "ANG") and handles any language.
  Original clipboard contents are restored afterwards.
- **Windows auto-port (experimental, untested on real hardware)**: the same
  code now detects the OS — ffmpeg dshow capture, winsound chime, PowerShell
  balloon notification, clipboard+SendKeys wake, tasklist-based pid check
  (os.kill(pid,0) kills processes on Windows — never used there), and the
  hook script resolves python3/python for Git Bash. macOS behavior unchanged.

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
