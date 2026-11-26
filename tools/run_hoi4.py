#!/usr/bin/env python3
"""Headless-ish test harness for Hearts of Iron IV mods.

Runs the real game against one or more mods inside an isolated user directory,
waits for completion markers in game.log, then shuts the game down and reports.

Isolation: hoi4.exe ignores -userdir= (launcher-settings.json gameDataPath wins). The
game resolves %USER_DOCUMENTS% from the process USERPROFILE, so the harness launches it
with USERPROFILE=<repo>/.hoi4-userdir/home. The game user dir is then
<repo>/.hoi4-userdir/home/Documents/Paradox Interactive/Hearts of Iron IV. As a second
guard, guarded files in the real user dir are backed up before each run and restored
(sha256-verified) afterwards, and the run aborts if the real logs change.

Log protocol (emit from mod script with the `log = "..."` effect):
    PWW_RESULT <test>.<check> PASS|FAIL|INFO <free text>
    PWW_DONE <test>

See tools/README.md for usage.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# error.log lines that are known engine false positives (see AGENTS.md).
# context_type = diplomatic_action is required for diplomatic-action send GUIs
# and works at runtime, but the parser still warns (Millennium Dawn documents
# the same warning).
KNOWN_FALSE_POSITIVES = (
    '"Unexpected token: context_type',
)

try:
    import psutil  # type: ignore
except ImportError:  # pragma: no cover
    psutil = None

REPO = Path(__file__).resolve().parent.parent
GAME_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")
GAME_EXE = GAME_DIR / "hoi4.exe"
REAL_USERDIR = Path(os.path.expanduser("~")) / "Documents" / "Paradox Interactive" / "Hearts of Iron IV"
R56_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\820260968")
DEFAULT_USERDIR = REPO / ".hoi4-userdir"
DEFAULT_OUT = REPO / ".hoi4-userdir" / "runs"  # game user dir: .hoi4-userdir/home/Documents/...

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_TIMEOUT = 2
EXIT_REFUSED = 3
EXIT_CRASH = 4

RESULT_RE = re.compile(r"PWW_RESULT\s+(\S+)\s+(PASS|FAIL|INFO)\b\s*(.*)")
DONE_RE = re.compile(r"PWW_DONE\s+(\S+)")
SENTINEL_STARTED = "PWW_HARNESS_STARTED"
SENTINEL_DAYS = "PWW_HARNESS_DAYS_DONE"

SENTINEL_NAME = "pww_harness_sentinel"


# --------------------------------------------------------------------------- utils

def log(msg: str) -> None:
    print(f"[harness] {msg}", flush=True)


def norm(p: Path) -> str:
    return str(p.resolve()).replace("\\", "/")


def list_hoi4_processes() -> list[dict]:
    procs: list[dict] = []
    if psutil is not None:
        for p in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
            try:
                if (p.info["name"] or "").lower() == "hoi4.exe":
                    procs.append({
                        "pid": p.info["pid"],
                        "cmdline": " ".join(p.info["cmdline"] or []),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return procs
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process -Filter \"Name='hoi4.exe'\" | "
         "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],
        capture_output=True, text=True,
    ).stdout.strip()
    if not out:
        return procs
    data = json.loads(out)
    if isinstance(data, dict):
        data = [data]
    for d in data:
        procs.append({"pid": d["ProcessId"], "cmdline": d.get("CommandLine") or ""})
    return procs


def pid_alive(pid: int) -> bool:
    if psutil is not None:
        return psutil.pid_exists(pid)
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
    return str(pid) in out


def real_mtime_changed(path: Path, before: float | None) -> bool:
    try:
        now = path.stat().st_mtime if path.exists() else None
    except OSError:
        return False
    return now is not None and now != before


def game_window_rect(pid: int):
    """Screen rect of the largest visible top-level window of `pid` (game window only)."""
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    try:
        user32.SetProcessDPIAware()
    except Exception:  # noqa: BLE001
        pass
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        wpid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value == pid and user32.IsWindowVisible(hwnd):
            r = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            found.append((r.right - r.left) * (r.bottom - r.top) and (r.left, r.top, r.right, r.bottom))
        return True

    user32.EnumWindows(cb, 0)
    found = [f for f in found if f]
    return max(found, key=lambda r: (r[2] - r[0]) * (r[3] - r[1])) if found else None


def kill_tree(pid: int) -> None:
    subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)


# --------------------------------------------------------------------------- lock

class Lock:
    def __init__(self, path: Path):
        self.path = path
        self.held = False

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, json.dumps({"harness_pid": os.getpid(), "game_pid": None,
                                         "started": _dt.datetime.now().isoformat()}).encode())
                os.close(fd)
                self.held = True
                return
            except FileExistsError:
                try:
                    info = json.loads(self.path.read_text() or "{}")
                except (OSError, ValueError):
                    info = {}
                hp = info.get("harness_pid")
                if hp and pid_alive(int(hp)) and int(hp) != os.getpid():
                    raise SystemExit(self._refuse(f"another harness run (pid {hp}) holds {self.path}"))
                gp = info.get("game_pid")
                if gp and pid_alive(int(gp)):
                    log(f"stale lock: killing orphaned harness game pid {gp}")
                    kill_tree(int(gp))
                log("removing stale lock")
                self.path.unlink(missing_ok=True)
        raise SystemExit(self._refuse(f"could not acquire {self.path}"))

    def set_game_pid(self, pid: int) -> None:
        data = json.loads(self.path.read_text())
        data["game_pid"] = pid
        self.path.write_text(json.dumps(data))

    def release(self) -> None:
        if self.held:
            self.path.unlink(missing_ok=True)
            self.held = False

    @staticmethod
    def _refuse(msg: str) -> int:
        print(f"[harness] REFUSED: {msg}", file=sys.stderr)
        return EXIT_REFUSED


# --------------------------------------------------------------------------- userdir setup

def mod_descriptor(name: str, path: Path, extra: str = "") -> str:
    return (f'name="{name}"\n'
            f'path="{norm(path)}"\n'
            f'supported_version="1.20.*"\n'
            f'version="0.0.1"\n{extra}')


def sentinel_files(days: int) -> dict[str, str]:
    """A tiny always-on mod that reports startup and an optional day count."""
    days_block = ""
    if days > 0:
        days_block = f"""
	on_daily = {{
		effect = {{
			if = {{
				limit = {{ tag = GER NOT = {{ has_global_flag = pww_harness_days_done }} }}
				add_to_variable = {{ global.pww_harness_days = 1 }}
				if = {{
					limit = {{ check_variable = {{ global.pww_harness_days > {days - 1} }} }}
					set_global_flag = pww_harness_days_done
					log = "{SENTINEL_DAYS} [GetDateText]"
				}}
			}}
		}}
	}}"""
    on_actions = f"""on_actions = {{
	on_startup = {{
		effect = {{
			log = "{SENTINEL_STARTED} [GetDateText]"
		}}
	}}{days_block}
}}
"""
    return {"common/on_actions/zz_pww_harness_sentinel.txt": on_actions}


def write_sentinel(userdir: Path, days: int) -> Path:
    root = userdir.parent.parent.parent.parent / "harness_mods" / SENTINEL_NAME
    if root.exists():
        shutil.rmtree(root)
    for rel, text in sentinel_files(days).items():
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    return root


def write_settings(userdir: Path, width: int, height: int, autosave: str = "NEVER") -> None:
    """Windowed, silent settings. Seeds from the real settings (read-only) when present."""
    settings = userdir / "settings.txt"
    src = REAL_USERDIR / "settings.txt"
    text = src.read_text(encoding="utf-8", errors="replace") if src.exists() else 'language="l_english"\n'
    text = re.sub(r"size=\{\s*x=\d+\s*y=\d+\s*\}", f"size={{ x={width} y={height} }}", text)
    text = re.sub(r"fullScreen=\w+", "fullScreen=no", text)
    text = re.sub(r"borderless=\w+", "borderless=no", text)
    # The real cursor may sit outside the test window: without this the camera
    # edge-scrolls on its own and posted map clicks (tests/ui) miss.
    text = re.sub(r"corner_scrolling=\w+", "corner_scrolling=no", text)
    for key in ("master_volume", "music_volume", "sound_fx_volume", "ambient_volume", "voice_volume"):
        text = re.sub(rf"{key}=[\d.]+", f"{key}=0.000000", text)
    text = re.sub(r'(?m)^autosave="\w+"\s*$', "", text)
    text = re.sub(r"(?m)^save_as_binary=\w+\s*$", "", text)
    text = re.sub(r"(?m)^lastplayer=.*$", "", text)
    text += f'\nautosave="{autosave}"\nsave_as_binary=no\n'
    settings.write_text(text, encoding="utf-8")
    pdx = userdir / "pdx_settings.txt"
    pdx.write_text(
        '"Graphics"={\n'
        '\t"display_mode"={ value="windowed" version=0 }\n'
        f'\t"windowed_resolution"={{ value="{width}x{height}" version=0 }}\n'
        '\t"vsync"={ enabled=no version=0 }\n'
        '}\n'
        '"System"={ "language"={ value="l_english" version=0 } }\n',
        encoding="utf-8",
    )


def prepare_userdir(userdir: Path, mods: list[tuple[str, Path]], r56: bool, days: int,
                    sentinel: bool, width: int, height: int, fresh_logs: bool = True,
                    autosave: str = "NEVER") -> list[str]:
    userdir.mkdir(parents=True, exist_ok=True)
    moddir = userdir / "mod"
    if moddir.exists():
        shutil.rmtree(moddir)
    moddir.mkdir()
    enabled: list[str] = []
    if r56:
        if not R56_DIR.exists():
            raise SystemExit(f"Road to 56 not found at {R56_DIR}")
        desc = (R56_DIR / "descriptor.mod").read_text(encoding="utf-8", errors="replace")
        desc = re.sub(r'^path=.*$', "", desc, flags=re.M) + f'\npath="{norm(R56_DIR)}"\n'
        (moddir / "ugc_820260968.mod").write_text(desc, encoding="utf-8")
        enabled.append("mod/ugc_820260968.mod")
    if sentinel:
        mods = mods + [(SENTINEL_NAME, write_sentinel(userdir, days))]
    for name, path in mods:
        fname = f"{name}.mod"
        (moddir / fname).write_text(mod_descriptor(name, path), encoding="utf-8")
        enabled.append(f"mod/{fname}")
    (userdir / "dlc_load.json").write_text(
        json.dumps({"enabled_mods": enabled, "disabled_dlcs": []}, indent=2), encoding="utf-8")
    write_settings(userdir, width, height, autosave)
    if fresh_logs:
        logs = userdir / "logs"
        if logs.exists():
            for f in logs.glob("*.log"):
                try:
                    f.unlink()
                except OSError:
                    pass
    return enabled


# --------------------------------------------------------------------------- real user dir guard

# Files in the real user dir that a launch may rewrite. Backed up before every launch and
# restored byte for byte afterwards (also on timeout, crash or kill). Never touched:
# launcher-v2*.sqlite, save games, mod descriptors the harness did not create.
GUARDED_FILES = ["dlc_load.json", "settings.txt", "pdx_settings.txt", "gameplaysettings.txt",
                 "continue_game.json"]
BACKUP_ROOT = DEFAULT_USERDIR / "backups"


def _sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def backup_user_files() -> Path:
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    dst = BACKUP_ROOT / stamp
    dst.mkdir(parents=True, exist_ok=True)
    manifest: dict = {"files": {}, "mods": []}
    for name in GUARDED_FILES:
        src = REAL_USERDIR / name
        if src.exists():
            shutil.copy2(src, dst / name)
            manifest["files"][name] = _sha(src)
        else:
            manifest["files"][name] = None
    moddir = REAL_USERDIR / "mod"
    if moddir.exists():
        manifest["mods"] = sorted(p.name for p in moddir.iterdir())
    (dst / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    old = sorted(d for d in BACKUP_ROOT.iterdir() if d.is_dir())[:-30]  # keep the newest 30
    for d in old:
        shutil.rmtree(d, ignore_errors=True)
    return dst


def restore_user_files(backup: Path, created_mods: list[str] | None = None) -> list[str]:
    """Restore guarded files from `backup`. Returns a list of actions taken."""
    manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    actions: list[str] = []
    for name, digest in manifest["files"].items():
        live = REAL_USERDIR / name
        if digest is None:
            if live.exists():
                live.unlink()
                actions.append(f"removed {name} (did not exist before)")
            continue
        if not live.exists() or _sha(live) != digest:
            shutil.copy2(backup / name, live)
            actions.append(f"restored {name}")
    moddir = REAL_USERDIR / "mod"
    before = set(manifest.get("mods", []))
    for name in created_mods or []:
        p = moddir / name
        if name not in before and p.exists():
            p.unlink()
            actions.append(f"removed mod/{name}")
    return actions


def latest_backup() -> Path | None:
    if not BACKUP_ROOT.exists():
        return None
    cands = sorted(d for d in BACKUP_ROOT.iterdir() if (d / "manifest.json").exists())
    return cands[-1] if cands else None


# --------------------------------------------------------------------------- isolation

def data_dir(root: Path) -> Path:
    """The game's user dir under the redirected profile.

    hoi4.exe ignores -userdir= (launcher-settings.json gameDataPath, which points at
    %USER_DOCUMENTS%, wins). It resolves %USER_DOCUMENTS% from the USERPROFILE of the
    process, so the harness launches the game with USERPROFILE=<root>/home and the game
    uses <root>/home/Documents/Paradox Interactive/Hearts of Iron IV.
    """
    return root / "home" / "Documents" / "Paradox Interactive" / "Hearts of Iron IV"


def game_env(root: Path) -> dict:
    env = dict(os.environ)
    home = (root / "home").resolve()
    env["USERPROFILE"] = str(home)
    env["HOMEDRIVE"] = str(home)[:2]
    env["HOMEPATH"] = str(home)[2:]
    return env


# --------------------------------------------------------------------------- run

class LogTail:
    def __init__(self, path: Path):
        self.path = path
        self.pos = 0

    def read_new(self) -> list[str]:
        if not self.path.exists():
            return []
        try:
            size = self.path.stat().st_size
            if size < self.pos:
                self.pos = 0
            with self.path.open("r", encoding="utf-8", errors="replace") as f:
                f.seek(self.pos)
                data = f.read()
                self.pos = f.tell()
        except OSError:
            return []
        return data.splitlines()


STAMP_RE = re.compile(r"^\[(\d\d):(\d\d):(\d\d)\]")


def stale_line(line: str, launch: _dt.datetime) -> bool:
    """True for a game.log line stamped before this launch (wall clock, 2 s slack)."""
    m = STAMP_RE.match(line)
    if not m:
        return False
    h, mi, se = (int(x) for x in m.groups())
    line_s = h * 3600 + mi * 60 + se
    launch_s = launch.hour * 3600 + launch.minute * 60 + launch.second - 2
    return (line_s - launch_s) % 86400 > 43200  # more than 12 h "after" means before


def build_args(a: argparse.Namespace, root: Path) -> list[str]:
    # -userdir= is ignored by the game but kept: it tags harness-launched processes.
    args = [str(GAME_EXE), f"-userdir={norm(root)}", "-gdpr-compliant"]
    if a.tag and not a.continue_last_save:  # -start_tag overrides -continuelastsave
        args.append(f"-start_tag={a.tag}")
    if a.speed is not None:
        args.append(f"-start_speed={a.speed}")
    if a.hands_off:
        args.append("-hands_off")
    if a.continue_last_save:
        args.append("-continuelastsave")
    for flag in a.flags:
        args.append(flag if flag.startswith("-") else f"-{flag}")
    return args


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod", action="append", default=[], metavar="DIR",
                    help="mod root to load (repeatable). Default: <repo>/mod unless --no-pww")
    ap.add_argument("--test", action="append", default=[], metavar="DIR",
                    help="test mod root (repeatable); the run waits for 'PWW_DONE <dirname>' from each")
    ap.add_argument("--no-pww", action="store_true", help="do not load <repo>/mod automatically")
    ap.add_argument("--r56", action="store_true", help="also enable The Road to 56 (load order: first)")
    ap.add_argument("--tag", default="POR", help="start tag (-start_tag=). Default POR")
    ap.add_argument("--speed", type=int, default=4,
                    help="start speed, 0-indexed 0..4 (-start_speed=). 4 = fastest (default); 5 falls back to slowest")
    ap.add_argument("--hands-off", action="store_true", help="pass -hands_off (observer-style AI run)")
    ap.add_argument("--days", type=int, default=0,
                    help="stop after N in-game days (sentinel). 0 = rely on PWW_DONE markers")
    ap.add_argument("--timeout", type=int, default=900, help="wall-clock seconds before killing the game")
    ap.add_argument("--until", metavar="REGEX", help="also stop when a game.log line matches REGEX")
    ap.add_argument("--flags", nargs="*", default=["nosound", "nofilewatcher", "disableoutdatedmodwarning"],
                    help="extra game flags (without leading dash ok)")
    ap.add_argument("--continue-last-save", action="store_true",
                    help="pass -continuelastsave (reload the newest save in the isolated userdir)")
    ap.add_argument("--autosave", default="NEVER", choices=["NEVER", "MONTHLY", "HALFYEAR", "YEARLY"],
                    help="autosave setting for the isolated userdir (saves are written as text)")
    ap.add_argument("--clear-saves", action="store_true", help="delete saves in the isolated userdir first")
    ap.add_argument("--screenshot", action="store_true", help="capture the desktop to <out>/screen.png at completion")
    ap.add_argument("--keep-logs", action="store_true", help="do not clear userdir logs before the run")
    ap.add_argument("--userdir", type=Path, default=DEFAULT_USERDIR)
    ap.add_argument("--out", type=Path, default=None, help="output folder (default .hoi4-userdir/runs/<stamp>)")
    ap.add_argument("--name", default="run", help="label for the output folder")
    ap.add_argument("--size", default="1280x720", help="window size WxH")
    ap.add_argument("--grace", type=int, default=3, help="seconds to keep running after completion (log flush)")
    ap.add_argument("--leave-running", action="store_true", help="do not kill the game at the end (manual poking)")
    ap.add_argument("--dry-run", action="store_true", help="prepare the userdir and print the command only")
    ap.add_argument("--restore-user-files", nargs="?", const="latest", metavar="BACKUP_DIR",
                    help="restore guarded real-user-dir files from a backup (default: latest) and exit")
    a = ap.parse_args(argv)

    if a.restore_user_files:
        b = latest_backup() if a.restore_user_files == "latest" else Path(a.restore_user_files)
        if not b or not (b / "manifest.json").exists():
            log("no backup found")
            return EXIT_REFUSED
        acts = restore_user_files(b)
        log(f"restore from {b}: " + ("; ".join(acts) or "all files already identical"))
        return EXIT_PASS

    root: Path = a.userdir.resolve()
    userdir: Path = data_dir(root)
    if REAL_USERDIR.exists() and REAL_USERDIR.resolve() in (root, userdir):
        log("REFUSED: --userdir points at the real user directory")
        return EXIT_REFUSED
    if not GAME_EXE.exists():
        log(f"game not found at {GAME_EXE}")
        return EXIT_REFUSED

    mods: list[tuple[str, Path]] = []
    if not a.no_pww:
        mods.append(("pww_mod", (REPO / "mod").resolve()))
    for m in a.mod:
        p = Path(m).resolve()
        mods.append((f"pww_test_{p.name}", p))  # name depends only on the folder: saves record it
    tests = [Path(t).resolve() for t in a.test]
    for t in tests:
        mods.append((f"pww_test_{t.name}", t))
    for _, p in mods:
        if not p.is_dir():
            log(f"mod dir does not exist: {p}")
            return EXIT_REFUSED

    expected_done = {t.name for t in tests}
    if not expected_done and a.days <= 0 and not a.until:
        a.days = 3  # pure load test: run a few days and stop
    w, h = (int(x) for x in a.size.lower().split("x"))

    # Foreign game guard: never touch a game the harness did not start.
    udn = norm(root).lower()
    foreign = [p for p in list_hoi4_processes() if udn not in p["cmdline"].replace("\\", "/").lower()]
    real_logs = REAL_USERDIR / "logs" / "system.log"
    real_mtime = real_logs.stat().st_mtime if real_logs.exists() else None
    if foreign and not a.dry_run:
        log("REFUSED: a Hearts of Iron IV instance not started by this harness is running "
            f"(pid {', '.join(str(p['pid']) for p in foreign)}). Close it and retry; the harness never kills it.")
        return EXIT_REFUSED

    lock = Lock(root / "harness.lock")
    lock.acquire()
    proc = None
    backup = None
    try:
        if not a.dry_run:
            backup = backup_user_files()
            log(f"real user files backed up to {backup}")
        if a.clear_saves:
            shutil.rmtree(userdir / "save games", ignore_errors=True)
            (userdir / "continue_game.json").unlink(missing_ok=True)
        enabled = prepare_userdir(userdir, mods, a.r56, a.days, True, w, h, fresh_logs=not a.keep_logs,
                                  autosave=a.autosave)
        args = build_args(a, root)
        log("mods: " + ", ".join(enabled))
        log("cmd: " + " ".join(args))
        if a.dry_run:
            return EXIT_PASS

        stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        out = (a.out or (DEFAULT_OUT / f"{stamp}_{a.name}")).resolve()
        out.mkdir(parents=True, exist_ok=True)

        game_log = userdir / "logs" / "game.log"
        # A previous run's game.log (a killed run, or another agent's game that
        # still holds it) must not leak its PWW_DONE into this run: remove or
        # rotate it, and accept only lines stamped at or after launch.
        skip = 0
        if game_log.exists():
            try:
                game_log.unlink()
            except OSError:
                try:
                    game_log.replace(game_log.with_name("game.prev.log"))
                except OSError:
                    skip = game_log.stat().st_size
                    log("warning: could not rotate game.log (in use); ignoring its existing lines")
        tail = LogTail(game_log)
        tail.pos = skip
        launch_clock = _dt.datetime.now()
        t0 = time.time()
        proc = subprocess.Popen(args, cwd=str(GAME_DIR), env=game_env(root))
        lock.set_game_pid(proc.pid)
        log(f"game pid {proc.pid}; timeout {a.timeout}s; waiting for: "
            + (", ".join(sorted(expected_done)) or "-")
            + (f"; {a.days} days" if a.days > 0 else "")
            + (f"; /{a.until}/" if a.until else ""))

        results: list[tuple[str, str, str]] = []
        done: set[str] = set()
        started_at = None
        status = None
        until_re = re.compile(a.until) if a.until else None
        days_done = False
        while True:
            for line in tail.read_new():
                if stale_line(line, launch_clock):
                    continue
                if (SENTINEL_STARTED in line or "Launching SINGLEPLAYER-game" in line) and started_at is None:
                    # on_startup does not fire when a save is loaded; the engine line covers that case.
                    started_at = time.time()
                    log(f"game started after {started_at - t0:.0f}s: {line.strip()}")
                if SENTINEL_DAYS in line:
                    days_done = True
                    log(line.strip())
                m = RESULT_RE.search(line)
                if m:
                    results.append((m.group(1), m.group(2), m.group(3).strip()))
                    print(f"  {m.group(2):4} {m.group(1)}  {m.group(3).strip()}", flush=True)
                m = DONE_RE.search(line)
                if m:
                    done.add(m.group(1))
                    log(f"done: {m.group(1)}")
                if until_re and until_re.search(line):
                    log(f"until matched: {line.strip()}")
                    status = "until"
            if expected_done and expected_done <= done and (a.days <= 0 or days_done):
                status = status or "done"
            elif not expected_done and a.days > 0 and days_done:
                status = status or "done"
            if status:
                break
            if real_mtime_changed(real_logs, real_mtime):
                log("ABORT: the real user dir logs changed; the game is not using the isolated userdir. Killing it.")
                status = "isolation_failed"
                break
            if proc.poll() is not None:
                status = "exited"
                break
            if time.time() - t0 > a.timeout:
                status = "timeout"
                break
            time.sleep(1.0)

        if status in ("done", "until") and a.grace > 0 and proc.poll() is None:
            time.sleep(a.grace)
            for line in tail.read_new():
                m = RESULT_RE.search(line)
                if m:
                    results.append((m.group(1), m.group(2), m.group(3).strip()))
                    print(f"  {m.group(2):4} {m.group(1)}  {m.group(3).strip()}", flush=True)
        if a.screenshot and proc.poll() is None:
            try:
                from PIL import ImageGrab
                rect = game_window_rect(proc.pid)
                if rect is None:
                    raise RuntimeError("game window not found")
                ImageGrab.grab(bbox=rect, all_screens=True).save(out / "screen.png")
                log(f"screenshot: {out / 'screen.png'}")
            except Exception as e:  # noqa: BLE001
                log(f"screenshot failed: {e}")
        rc_game = proc.poll()
        if not a.leave_running and proc.poll() is None:
            kill_tree(proc.pid)
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                pass
        elapsed = time.time() - t0
        if real_mtime is not None and real_logs.exists() and real_logs.stat().st_mtime != real_mtime:
            log("WARNING: the real user dir logs changed during this run; isolation failed. Stop and investigate.")

        # Collect logs.
        for name in ("error.log", "game.log", "system.log", "setup.log", "text.log"):
            src = userdir / "logs" / name
            if src.exists():
                shutil.copy2(src, out / name)
        tests_dir = userdir / "logs" / "tests"
        if tests_dir.exists():
            shutil.copytree(tests_dir, out / "tests", dirs_exist_ok=True)

        err_lines: list[str] = []
        err_path = userdir / "logs" / "error.log"
        if err_path.exists():
            for line in err_path.read_text(encoding="utf-8", errors="replace").splitlines():
                if "pww" in line.lower() and not any(p in line for p in KNOWN_FALSE_POSITIVES):
                    err_lines.append(line)
        if err_lines:
            log(f"{len(err_lines)} pww-related error.log lines:")
            for line in err_lines[:200]:
                print("  " + line)
            if len(err_lines) > 200:
                print(f"  ... {len(err_lines) - 200} more in {out / 'error.log'}")

        fails = [r for r in results if r[1] == "FAIL"]
        passes = [r for r in results if r[1] == "PASS"]
        missing = sorted(expected_done - done)
        summary = {
            "status": status, "elapsed_s": round(elapsed), "game_exit_code": rc_game,
            "started": started_at is not None, "passes": len(passes), "fails": len(fails),
            "missing_done": missing, "pww_error_lines": len(err_lines), "out": str(out),
            "results": results,
        }
        (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        log(f"status={status} elapsed={elapsed:.0f}s pass={len(passes)} fail={len(fails)} "
            f"pww_errors={len(err_lines)} missing_done={missing or '-'}")
        log(f"logs: {out}")

        if status == "isolation_failed":
            return EXIT_REFUSED
        if status == "exited":
            log("game exited before completion (crash or manual close). See crashes/ in the userdir.")
            return EXIT_CRASH
        if status == "timeout":
            if started_at is None:
                log("game never reached on_startup: likely stuck in a menu. See tools/README.md (start flow).")
            return EXIT_TIMEOUT
        if fails or err_lines:
            return EXIT_FAIL
        return EXIT_PASS
    finally:
        if proc is not None and proc.poll() is None and not a.leave_running:
            kill_tree(proc.pid)
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                pass
        if backup is not None and not (a.leave_running and proc is not None and proc.poll() is None):
            acts = restore_user_files(backup)
            log("real user files: " + ("; ".join(acts) if acts else "unchanged (verified by sha256)"))
        lock.release()


if __name__ == "__main__":
    sys.exit(main())
