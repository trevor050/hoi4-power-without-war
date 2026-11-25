#!/usr/bin/env python3
"""Run every scenario test in its own game session and print a pass/fail table.

Scenario tests are not composable in one session (one test's setup changes the
world another test reads), so each folder gets a fresh `tools/run_hoi4.py` run.
Two-session tests (save and reload) run both sessions in order.

    python tools/run_all_tests.py                  # default suite, vanilla
    python tools/run_all_tests.py --r56            # default suite with Road to 56
    python tools/run_all_tests.py --both           # vanilla then Road to 56
    python tools/run_all_tests.py --only wolfram   # names containing "wolfram"
    python tools/run_all_tests.py --engine         # add the Phase 0 engine tests
    python tools/run_all_tests.py --soak           # add the 2-year soak run
    python tools/run_all_tests.py --list

A test passes when every session exits 0 (no FAIL line, no pww error.log line,
completion marker seen). Output folders: .hoi4-userdir/runs/all_<stamp>/<test>.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HARNESS = REPO / "tools" / "run_hoi4.py"
EXIT_NAMES = {0: "pass", 1: "FAIL", 2: "TIMEOUT", 3: "REFUSED", 4: "CRASH"}


@dataclass
class Test:
    name: str
    sessions: list[list[str]]          # harness args per session (the test dir is added)
    path: str
    group: str = "default"             # default | engine | soak | manual
    r56: bool = True                   # also meaningful under --r56
    notes: str = ""


def T(path: str, *sessions: list[str], group: str = "default", r56: bool = True, notes: str = "",
      label: str = "") -> Test:
    return Test(label or Path(path).name, [list(s) for s in sessions] or [[]], path, group, r56, notes)


TESTS: list[Test] = [
    T("tests/smoke/pww_smoke", []),
    T("tests/ledger/ledger_t1", []),
    T("tests/coercion/coer_t1", ["--tag", "GER"]),
    T("tests/diplomacy/diplo_ai_propose", ["--tag", "SWI"]),
    T("tests/diplomacy/diplo_auction", ["--tag", "SWI"]),
    T("tests/diplomacy/diplo_haggle", ["--tag", "GER"]),
    T("tests/diplomacy/diplo_seed_reload",
      ["--autosave", "MONTHLY", "--clear-saves"], ["--continue-last-save"]),
    T("tests/situations/sit_wolfram_ai", ["--tag", "HAI"]),
    T("tests/situations/sit_human_holder", []),
    T("tests/situations/sit_noise_cap", []),
    T("tests/situations/sit_reload",
      ["--tag", "HAI", "--autosave", "MONTHLY", "--clear-saves", "--until", "sit_reload.session1_done"],
      ["--continue-last-save"]),
    T("tests/integration/wolfram_full", ["--tag", "HAI", "--timeout", "1500"]),
    T("tests/integration/wolfram_full", ["--tag", "POR", "--timeout", "1500"], label="wolfram_full_human"),
    T("tests/integration/soak", ["--tag", "HAI", "--days", "730", "--timeout", "3600"], group="soak"),
    T("tests/diplomacy/diplo_gui_look", ["--leave-running", "--screenshot"], group="manual",
      notes="manual GUI look; never run by this script"),
]
for _d in sorted((REPO / "tests" / "engine").glob("t*")):
    if _d.is_dir():
        TESTS.append(T(str(_d.relative_to(REPO)).replace("\\", "/"), ["--no-pww"], group="engine",
                       r56=_d.name == "t9_discovery"))


@dataclass
class Result:
    test: str
    variant: str
    code: int
    seconds: float
    passes: int = 0
    fails: int = 0
    errors: int = 0
    out: str = ""
    sessions: list[int] = field(default_factory=list)


def game_running() -> bool:
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq hoi4.exe", "/NH"], capture_output=True, text=True).stdout
    return "hoi4.exe" in out.lower()


def wait_idle(limit_s: int = 3600) -> None:
    """Wait while any game runs: another agent's --leave-running session holds no lock
    but shares the isolated user dir and its logs."""
    t0 = time.time()
    said = False
    while game_running() and time.time() - t0 < limit_s:
        if not said:
            print("    a game is running (another session); waiting", flush=True)
            said = True
        time.sleep(3)  # other agents relaunch quickly: poll often to catch the gap


def run_session(test: Test, args: list[str], r56: bool, out: Path, timeout_pad: int) -> tuple[int, dict]:
    cmd = [sys.executable, str(HARNESS), "--test", str(REPO / test.path), "--out", str(out), "--name", test.name]
    if r56:
        cmd.append("--r56")
    cmd += args
    print(f"\n>>> {test.name} [{'r56' if r56 else 'vanilla'}] {' '.join(args)}", flush=True)
    rc = 3
    for attempt in range(40):  # another agent's run may hold the harness lock
        if attempt:
            print(f"    harness busy (refused); retry {attempt} in 30s", flush=True)
            time.sleep(30)
        wait_idle()
        try:
            rc = subprocess.run(cmd, cwd=str(REPO), timeout=timeout_pad).returncode
        except subprocess.TimeoutExpired:
            rc = 2
        if rc != 3 or (out / "summary.json").exists():
            break
    summary = {}
    sj = out / "summary.json"
    if sj.exists():
        try:
            summary = json.loads(sj.read_text(encoding="utf-8"))
        except ValueError:
            pass
    return rc, summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--r56", action="store_true", help="run under Road to 56 only")
    ap.add_argument("--both", action="store_true", help="run vanilla, then Road to 56")
    ap.add_argument("--engine", action="store_true", help="include the Phase 0 engine tests (without the mod)")
    ap.add_argument("--soak", action="store_true", help="include the long soak run")
    ap.add_argument("--only", action="append", default=[], metavar="TEXT", help="tests whose name contains TEXT")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    groups = {"default"} | ({"engine"} if a.engine else set()) | ({"soak"} if a.soak else set())
    tests = [t for t in TESTS if t.group in groups]
    if a.only:
        tests = [t for t in TESTS if t.group != "manual" and any(o in t.name for o in a.only)]
    if a.list:
        for t in TESTS:
            print(f"{t.group:8} {t.name:22} sessions={len(t.sessions)} {t.notes}")
        return 0
    variants = [False, True] if a.both else [a.r56]

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    root = REPO / ".hoi4-userdir" / "runs" / f"all_{stamp}"
    results: list[Result] = []
    for r56 in variants:
        for t in tests:
            if r56 and not t.r56:
                continue
            variant = "r56" if r56 else "vanilla"
            t0 = time.time()
            res = Result(t.name, variant, 0, 0)
            for i, sargs in enumerate(t.sessions):
                out = root / f"{t.name}_{variant}" / f"s{i + 1}"
                timeout = 900
                if "--timeout" in sargs:
                    timeout = int(sargs[sargs.index("--timeout") + 1])
                rc, summ = run_session(t, sargs, r56, out, timeout + 180)
                res.sessions.append(rc)
                res.passes += summ.get("passes", 0)
                res.fails += summ.get("fails", 0)
                res.errors += summ.get("pww_error_lines", 0)
                res.out = str(out.parent)
                if rc != 0:
                    res.code = rc
                    break
            res.seconds = time.time() - t0
            results.append(res)

    print("\n" + "=" * 96)
    print(f"{'test':24} {'variant':8} {'result':8} {'pass':>5} {'fail':>5} {'pww_err':>8} {'time':>7}  logs")
    print("-" * 96)
    for r in results:
        print(f"{r.test:24} {r.variant:8} {EXIT_NAMES.get(r.code, str(r.code)):8} {r.passes:5} {r.fails:5} "
              f"{r.errors:8} {r.seconds:6.0f}s  {Path(r.out).relative_to(REPO) if r.out else '-'}")
    print("-" * 96)
    bad = [r for r in results if r.code != 0]
    print(f"{len(results) - len(bad)}/{len(results)} passed")
    (root).mkdir(parents=True, exist_ok=True)
    (root / "results.json").write_text(json.dumps([r.__dict__ for r in results], indent=1), encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
