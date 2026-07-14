#!/usr/bin/env python3
"""shotgun listener — desk-slam (rage) detector.

Watches the microphone via ffmpeg/avfoundation and detects a sudden loud
transient ("BANG") against the rolling background noise floor. On detection it
appends a line to the flag file that the shotgun Claude Code hooks consume.

Privacy: audio is reduced to per-block volume numbers (RMS) in memory.
Nothing is recorded, stored, or transmitted. Ever.

Usage:
  shotgun_listener.py                 daemon mode (pid file, heartbeat watch)
  shotgun_listener.py --test [SEC]    foreground test, prints levels + slams
  shotgun_listener.py --calibrate [SEC]  measure your slams, suggest threshold
  shotgun_listener.py --devices       list avfoundation audio input devices
"""
import array
import collections
import json
import math
import os
import shutil
import subprocess
import sys
import time

IS_WIN = sys.platform == "win32"

STATE = os.path.join(os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude")), "shotgun")
CONFIG = os.path.join(STATE, "config.json")
FLAG = os.path.join(STATE, "flag")
PIDFILE = os.path.join(STATE, "daemon.pid")
HEARTBEAT = os.path.join(STATE, "heartbeat")
LOG = os.path.join(STATE, "daemon.log")

SR = 48000
BLOCK = 1024                 # ~21 ms
NOISE_BLOCKS = 100           # ~2 s rolling background window
HEARTBEAT_MAX = 600          # daemon exits if no live CC session for 10 min
DEFAULTS = {
    "enabled": True,
    "device": "0",
    "threshold": 1500,       # int16 RMS absolute floor (user-adjustable)
    "ratio": 6.0,            # spike must exceed background floor by this factor
    "refractory": 1.5,       # seconds; one BANG = one trigger
    "sound": True,           # play a chime on detection
    "notify": True,          # macOS notification on detection
    "wake": True,            # if no session consumed the flag, type into the
                             # focused terminal to force-wake an idle session
    "wake_delay": 0.6,       # seconds to wait for a live session first
    # Typed into the focused session. The FULLY-QUALIFIED command name —
    # plugin commands register namespaced (/shotgun:bang, not /bang), and only
    # an exact match reliably tops the slash menu before Enter fires.
    "wake_text": "/shotgun:bang",
}


def dbfs(rms):
    """Linear int16 RMS → dBFS (0 dBFS = full scale 32768)."""
    return 20.0 * math.log10(max(rms, 1.0) / 32768.0)


def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    except OSError:
        pass


def load_config():
    cfg = dict(DEFAULTS)
    try:
        with open(CONFIG) as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cfg


def find_ffmpeg():
    cands = [shutil.which("ffmpeg")]
    if IS_WIN:
        home = os.path.expanduser("~")
        cands += [os.path.join(home, r"scoop\shims\ffmpeg.exe"),
                  r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
                  r"C:\ffmpeg\bin\ffmpeg.exe"]
    else:
        cands += ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]
    for cand in cands:
        if cand and os.path.exists(cand):
            return cand
    return None


def pid_alive(pid):
    """Cross-platform liveness check. NEVER use os.kill(pid, 0) on Windows —
    any non-CTRL signal there unconditionally TerminateProcess()es the target."""
    if IS_WIN:
        try:
            out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                                 capture_output=True, text=True, timeout=10).stdout
            return str(pid) in out
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def list_devices():
    ff = find_ffmpeg()
    if not ff:
        print("ERROR ffmpeg not found (brew install ffmpeg)")
        return 1
    if IS_WIN:
        out = subprocess.run([ff, "-hide_banner", "-list_devices", "true",
                              "-f", "dshow", "-i", "dummy"],
                             capture_output=True, text=True).stderr
        for line in out.splitlines():
            if "(audio)" in line and '"' in line:
                print(line.split('"')[1])
        return 0
    out = subprocess.run([ff, "-hide_banner", "-f", "avfoundation",
                          "-list_devices", "true", "-i", ""],
                         capture_output=True, text=True).stderr
    audio = False
    for line in out.splitlines():
        if "audio devices" in line:
            audio = True
            continue
        if audio and "] [" in line:
            print(line.split("]", 1)[1].strip())
        elif audio and "error" in line.lower():
            break
    return 0


def open_stream(cfg):
    ff = find_ffmpeg()
    if not ff:
        log("ffmpeg not found; exiting")
        sys.exit(1)
    if IS_WIN:
        inp = ["-f", "dshow", "-i", f"audio={cfg['device']}"]
    else:
        inp = ["-f", "avfoundation", "-i", f":{cfg['device']}"]
    cmd = [ff, "-hide_banner", "-loglevel", "error", *inp,
           "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def blocks(proc):
    """Yield (rms, peak) per block until the stream ends."""
    while True:
        data = proc.stdout.read(BLOCK * 2)
        if not data or len(data) < BLOCK * 2:
            return
        samples = array.array("h", data)
        sq = 0
        peak = 0
        for s in samples:
            sq += s * s
            a = -s if s < 0 else s
            if a > peak:
                peak = a
        yield math.sqrt(sq / len(samples)), peak


def on_slam(cfg, rms, ratio, count):
    line = f"{time.time():.3f} rms={rms:.0f} ratio={ratio:.1f}\n"
    try:
        with open(FLAG, "a") as f:
            f.write(line)
    except OSError as e:
        log(f"flag write failed: {e}")
    if cfg.get("sound"):
        if IS_WIN:
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass
        else:
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if cfg.get("notify"):
        if IS_WIN:
            ps = ("[reflection.assembly]::loadwithpartialname('System.Windows.Forms')|Out-Null;"
                  "$n=New-Object System.Windows.Forms.NotifyIcon;"
                  "$n.Icon=[System.Drawing.SystemIcons]::Exclamation;$n.Visible=$true;"
                  "$n.ShowBalloonTip(3000,'shotgun','BANG detected - review triggered',"
                  "[System.Windows.Forms.ToolTipIcon]::Warning)")
            subprocess.Popen(["powershell", "-NoProfile", "-Command", ps],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["osascript", "-e",
                              'display notification "BANG detected — review triggered" with title "shotgun"'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log(f"SLAM #{count} rms={rms:.0f} ratio={ratio:.1f}")


def _mac_host_bundle(cfg):
    """Bundle id of the app hosting Claude Code — wake activates it first so
    the command lands in the session, not whatever app happens to be frontmost
    (field-observed: /shotgun:bang typed into a browser)."""
    if cfg.get("wake_bundle"):
        return str(cfg["wake_bundle"])
    return {"vscode": "com.microsoft.VSCode",
            "Apple_Terminal": "com.apple.Terminal",
            "iTerm.app": "com.googlecode.iterm2"}.get(
        os.environ.get("TERM_PROGRAM", ""), "")


def _hid_idle_seconds():
    """Seconds since the user's last keyboard/mouse input (macOS)."""
    try:
        out = subprocess.run(
            ["/bin/sh", "-c",
             "ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print $NF/1000000000; exit}'"],
            capture_output=True, text=True, timeout=5).stdout.strip()
        return float(out) if out else 999.0
    except Exception:
        return 999.0


def do_wake(cfg):
    """Force-wake an idle session by typing into the user's terminal.

    Hooks are event-driven: an idle session cannot react until an event fires.
    If nobody consumed the flag within wake_delay, we inject a keystroke —
    exact tmux pane when available, otherwise the frontmost app (the window
    the user is staring at while slamming). Needs macOS Accessibility
    permission for the keystroke path; failures are logged, never fatal.
    """
    text = str(cfg.get("wake_text") or DEFAULTS["wake_text"])
    try:
        # Never type over the user: wait for a pause in their typing (HID idle
        # >= 1.2s), and abort entirely if the flag got consumed meanwhile — it
        # means they engaged the session themselves and a hook took over.
        if not IS_WIN:
            deadline = time.time() + 15
            while time.time() < deadline:
                if not os.path.exists(FLAG):
                    log("wake: cancelled (flag consumed while waiting)")
                    return
                if _hid_idle_seconds() >= 0.8:
                    break
                time.sleep(0.25)
        if os.environ.get("TMUX") and os.environ.get("TMUX_PANE"):
            subprocess.run(["tmux", "send-keys", "-t", os.environ["TMUX_PANE"],
                            text, "Enter"], capture_output=True, timeout=5)
            log(f"wake: tmux send-keys to {os.environ['TMUX_PANE']}")
            return
        if IS_WIN:
            # Clipboard-paste via SendKeys: no dropped first char, any language.
            ps = ("$old = Get-Clipboard -Raw -ErrorAction SilentlyContinue; "
                  "Set-Clipboard -Value $env:SHOTGUN_WAKE_TEXT; "
                  "$w = New-Object -ComObject WScript.Shell; "
                  "Start-Sleep -Milliseconds 300; $w.SendKeys('^v'); "
                  "Start-Sleep -Milliseconds 250; $w.SendKeys('{ENTER}'); "
                  "Start-Sleep -Milliseconds 300; "
                  "if ($old) { Set-Clipboard -Value $old }")
            env = dict(os.environ, SHOTGUN_WAKE_TEXT=text)
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                               capture_output=True, text=True, timeout=15, env=env)
            log("wake: SendKeys paste sent" if r.returncode == 0 else
                f"wake failed: {r.stderr.strip()[:200]}")
            return
        # macOS: character keystrokes — the ONLY channel verified to reach
        # Electron terminals (synthetic cmd+V modifier combos are ignored by
        # VS Code). Defenses: settle delay + sacrificial char/delete against
        # first-char drops, and a LONG pause after typing so the slash-command
        # menu settles on the exact match before Enter (a premature Enter
        # fires whatever fuzzy entry is highlighted — observed once selecting
        # /coupang-search from a half-typed /bang). ASCII wake_text only.
        esc = text.replace("\\", "\\\\").replace('"', '\\"')
        # Before typing: ESC closes any open slash menu, then a backspace
        # burst wipes leftover input (a previous wake's remnant text otherwise
        # keeps the menu open and swallows the new command into its filter).
        bundle = _mac_host_bundle(cfg)
        activate = (f'tell application id "{bundle}" to activate\n'
                    'delay 0.35\n') if bundle else ''
        # Inside VS Code the keystrokes go to whatever element has focus —
        # if it's the editor, the command lands in a source file. The focused
        # element is readable via Accessibility (terminal panels describe
        # themselves as "Terminal …"), so when it isn't a terminal we click
        # View > Terminal (en/ko menus) to move focus there first.
        focus_fix = (
            '  tell application process frontApp\n'
            '    set focusedDesc to ""\n'
            '    try\n'
            '      set focusedDesc to (value of attribute "AXDescription" of '
            '(value of attribute "AXFocusedUIElement")) as text\n'
            '    end try\n'
            '    if focusedDesc does not start with "Terminal" then\n'
            '      try\n'
            '        click menu item "Terminal" of menu "View" of menu bar item '
            '"View" of menu bar 1\n'
            '      on error\n'
            '        try\n'
            '          click menu item "터미널" of menu "보기" '
            'of menu bar item "보기" of menu bar 1\n'
            '        end try\n'
            '      end try\n'
            '      delay 0.4\n'
            '    end if\n'
            '  end tell\n')
        script = (activate +
                  'tell application "System Events"\n'
                  '  set frontApp to name of first application process whose '
                  'frontmost is true\n'
                  + focus_fix +
                  '  delay 0.15\n'
                  '  key code 53\n'
                  '  delay 0.1\n'
                  '  repeat 25 times\n'
                  '    key code 51\n'
                  '  end repeat\n'
                  '  delay 0.05\n'
                  '  keystroke "x"\n'
                  '  delay 0.05\n'
                  '  key code 51\n'
                  '  delay 0.05\n'
                  f'  keystroke "{esc}"\n'
                  '  delay 0.35\n'
                  '  key code 36\n'
                  'end tell\n'
                  'return frontApp')
        r = subprocess.run(["osascript", "-e", script],
                           capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            log(f"wake failed (grant Accessibility to your terminal app): "
                f"{r.stderr.strip()[:200]}")
        else:
            log(f"wake: typed into frontmost app [{r.stdout.strip()}]")
    except Exception as e:  # wake is best-effort by design
        log(f"wake error: {e}")


def run(cfg, duration=0, verbose=False, daemon=False):
    proc = open_stream(cfg)
    noise = collections.deque(maxlen=NOISE_BLOCKS)
    threshold = float(cfg["threshold"])
    ratio_min = float(cfg["ratio"])
    refractory = float(cfg["refractory"])
    last_trig = 0.0
    last_report = time.time()
    last_hb_check = time.time()
    start = time.time()
    slams = 0
    wake_at = 0.0            # pending wake deadline (0 = none)
    wake_block = 0.0         # don't re-wake within this window

    if verbose:
        print(f"listening on device :{cfg['device']} threshold={threshold:.0f} "
              f"ratio={ratio_min}x refractory={refractory}s", flush=True)

    for rms, peak in blocks(proc):
        floor = sorted(noise)[len(noise) // 2] if noise else 0.0
        ratio = rms / floor if floor > 50 else (999.0 if rms > threshold else 0.0)
        now = time.time()

        if rms > threshold and ratio > ratio_min and now - last_trig > refractory:
            last_trig = now
            slams += 1
            on_slam(cfg, rms, ratio, slams)
            if daemon and cfg.get("wake") and now > wake_block:
                wake_at = now + float(cfg.get("wake_delay", 3.0))
            if verbose:
                print(f"SLAM! #{slams} rms={rms:.0f} ({dbfs(rms):.1f} dBFS) "
                      f"peak={peak} ratio={ratio:.1f}", flush=True)
        else:
            noise.append(rms)

        if verbose and now - last_report > 2:
            last_report = now
            print(f"level rms={rms:.0f} ({dbfs(rms):.1f} dBFS) peak={peak} "
                  f"floor={floor:.0f}", flush=True)

        if wake_at and now >= wake_at:
            wake_at = 0.0
            if os.path.exists(FLAG):     # nobody consumed it — force-wake
                wake_block = now + 60
                do_wake(cfg)

        if daemon and now - last_hb_check > 5:
            last_hb_check = now
            try:
                hb = os.path.getmtime(HEARTBEAT)
            except OSError:
                hb = start
            if now - hb > HEARTBEAT_MAX:
                log("no live session heartbeat; exiting")
                break

        if duration and now - start > duration:
            break

    proc.terminate()
    err = ""
    try:
        err = proc.stderr.read().decode(errors="replace").strip()
    except Exception:
        pass
    if err:
        log(f"ffmpeg: {err[:300]}")
        if verbose:
            print(f"ffmpeg: {err[:300]}", flush=True)
    return slams


def calibrate(cfg, duration=15):
    """Foreground measurement: user slams a few times, we suggest a threshold."""
    proc = open_stream(cfg)
    noise = collections.deque(maxlen=NOISE_BLOCKS)
    spikes = []
    last_spike = 0.0
    start = time.time()
    print(f"CAL measuring {duration}s — slam your desk 3 times like you mean it", flush=True)
    for rms, peak in blocks(proc):
        floor = sorted(noise)[len(noise) // 2] if noise else 0.0
        now = time.time()
        if rms > 800 and (floor < 50 or rms / max(floor, 1) > 4) and now - last_spike > 1.0:
            last_spike = now
            spikes.append(rms)
            print(f"CAL spike rms={rms:.0f} ({dbfs(rms):.1f} dBFS)", flush=True)
        else:
            noise.append(rms)
        if now - start > duration:
            break
    proc.terminate()
    floor = sorted(noise)[len(noise) // 2] if noise else 0.0
    if spikes:
        top = sorted(spikes, reverse=True)[:3]
        suggested = int(max(800, min(20000, 0.6 * (sum(top) / len(top)))))
    else:
        suggested = DEFAULTS["threshold"]
    print(f"CAL_RESULT floor={floor:.0f} spikes={[int(s) for s in spikes]} "
          f"suggested={suggested} ({dbfs(suggested):.1f} dBFS) "
          f"default={DEFAULTS['threshold']}", flush=True)
    return 0


def daemon_main(cfg):
    if not cfg.get("enabled", True):
        log("disabled in config; not starting")
        return 0
    if os.path.exists(PIDFILE):
        try:
            pid = int(open(PIDFILE).read().strip())
            if pid_alive(pid):
                return 0  # already running
        except (OSError, ValueError):
            pass  # stale pidfile
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()))
    log(f"daemon started pid={os.getpid()} device={cfg['device']} threshold={cfg['threshold']}")
    try:
        run(cfg, daemon=True)
    finally:
        try:
            os.remove(PIDFILE)
        except OSError:
            pass
        log("daemon stopped")
    return 0


def main():
    os.makedirs(STATE, exist_ok=True)
    args = sys.argv[1:]
    cfg = load_config()
    if args and args[0] == "--devices":
        return list_devices()
    if args and args[0] == "--test":
        dur = float(args[1]) if len(args) > 1 else 15
        slams = run(cfg, duration=dur, verbose=True)
        print(f"done: {slams} slam(s) in {dur:.0f}s", flush=True)
        return 0
    if args and args[0] == "--calibrate":
        dur = float(args[1]) if len(args) > 1 else 15
        return calibrate(cfg, dur)
    return daemon_main(cfg)


if __name__ == "__main__":
    sys.exit(main())
