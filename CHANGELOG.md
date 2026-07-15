# Changelog

## v0.4.0 (2026-07-15)

**Self-watching sessions — the idle wake no longer depends on typing.**
SessionStart now arms an in-session background watch (Monitor / background
loop) on the flag file. When you slam, the session wakes ITSELF on the event
and apologizes — no keystroke injection, so focus, window position, IME,
Secure Keyboard Entry, and app quirks stop mattering. Works in every
terminal and IDE identically. The typed /shotgun:bang wake remains as a
fallback and cancels itself automatically when a session's watch consumes
the flag first (which it normally does, within ~0.5s). Sessions arm on
their first turn; restart old windows to get the watch.

## v0.3.10 (2026-07-15)

Default threshold 1500 → 5000. A day of live measurements: deliberate slams
land at 5,100–22,600 RMS while everyday noise (cups, doors, hard typing,
light taps) stays under ~4,500. Only real rage triggers now; calibration
still tunes per setup.

## v0.3.9 (2026-07-14)

Wake follows you across workspaces. Every hook event now records its
session's GUI host app pid to `last-host`, and wake activates the most
recently active session's host — not the app that happened to spawn the
daemon first. Multi-workspace / multi-terminal setups get the command in the
window they last touched.

## v0.3.8 (2026-07-14)

Daemon liveness is now "any Claude Code process running" (pgrep), not
hook-event heartbeats — an open-but-idle window keeps the mic on instead of
the daemon dying every 10 quiet minutes. All windows closed → daemon exits
within ~2 minutes. Heartbeat file remains as a fallback signal.

## v0.3.7 (2026-07-14)

- **Daemon revives on any hook event** — after the 10-minute idle
  self-shutdown, the next activity in an existing session restarts the mic
  (previously only a brand-new session did, leaving the mic off).
- **Host app resolved in the hook, handed to the daemon via env** — a
  hook-spawned daemon is reparented to launchd before it can walk its own
  ancestry, so the hook (whose parent chain is alive) resolves the GUI host
  pid and passes SHOTGUN_HOST_PID down. Verified: hook-spawned daemon
  correctly targets the hosting IDE.

## v0.3.6 (2026-07-14)

No more hardcoded app names. The daemon walks its own process ancestry at
startup to the topmost *.app/Contents/MacOS ancestor — the actual GUI app
hosting Claude Code (Terminal, iTerm, VS Code, Antigravity, any fork) — and
wake activates that app by pid. TERM_PROGRAM=vscode had been wrongly mapped
to Microsoft VS Code, which broke wake entirely for VS Code forks
(field-observed on Antigravity IDE). `wake_bundle` still overrides.

## v0.3.5 (2026-07-14)

Wake now finds your session instead of trusting the frontmost window
(field-observed: /shotgun:bang typed into a browser):

- Activates the app hosting Claude Code first (auto-detected from
  TERM_PROGRAM: VS Code / Terminal / iTerm2; override with `wake_bundle`).
- Inside VS Code, reads the focused element via Accessibility — if it isn't a
  terminal panel (e.g. the editor), clicks View > Terminal (en/ko menus) to
  move focus before typing, so the command can't land in a source file.

## v0.3.4 (2026-07-14)

Faster trigger-to-command: default wake_delay 2s → 0.6s, pre-Enter menu
settle 0.6s → 0.35s, halved remaining injection gaps (backspace burst 25).
BANG-to-Enter is now roughly 1.5s end to end.

## v0.3.3 (2026-07-14)

- **Apology outruns everything**: /bang now emits the apology as the very
  first output, BEFORE any tool call — state consumption happens after. Field
  test showed the state-read running first and delaying the apology.
- Flag consumption switched to `mv` (no file deletion command) — user safety
  hooks that block deletion commands caused a 40s+ retry loop mid-apology.
  Also collapsed to one fast command.
- Wake injection clears leftover input first (ESC + backspace burst) so a
  previous wake's remnant text can't trap the new command in the slash menu
  filter.

## v0.3.2 (2026-07-14)

- **Wake types the fully-qualified `/shotgun:bang`** — plugin commands
  register namespaced, so bare `/bang` had no exact match in the slash menu
  and Enter could fire whatever fuzzy entry was on top (field-observed:
  /coupang-search). An exact match reliably tops the menu.
- Snappier injection: settle 0.25s, sacrificial-char gaps 0.1s, menu-settle
  0.6s, HID-idle threshold 0.8s; default wake_delay 3s → 2s.

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
