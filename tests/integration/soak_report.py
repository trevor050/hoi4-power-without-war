#!/usr/bin/env python3
"""Summarize soak runs: game days per real second and the monthly counters.

    python tests/integration/soak_report.py <run_dir_with_mod> [<baseline_run_dir>]

Reads game.log from each harness output folder. Speed comes from the wall-clock
prefix of the "soak.month" lines (first to last), so loading time is excluded.
"""
import re
import sys
from datetime import datetime
from pathlib import Path

LINE = re.compile(r"^\[(\d\d:\d\d:\d\d)\].*PWW_RESULT soak\.month INFO .*? day=(\d+)(.*)$")


def speed(run: Path):
    pts = []
    for line in (run / "game.log").read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.match(line)
        if m:
            pts.append((datetime.strptime(m.group(1), "%H:%M:%S"), int(m.group(2)), m.group(3).strip()))
    if len(pts) < 2:
        return None, pts
    secs = 0.0
    for (a, _, _), (b, _, _) in zip(pts, pts[1:]):
        d = (b - a).total_seconds()
        secs += d if d >= 0 else d + 86400
    return (pts[-1][1] - pts[0][1]) / secs if secs else None, pts


def main() -> int:
    runs = [Path(p) for p in sys.argv[1:]]
    rates = []
    for r in runs:
        rate, pts = speed(r)
        rates.append(rate)
        print(f"== {r.name}: {len(pts)} monthly lines, " + (f"{rate:.2f} game days per real second" if rate else "no rate"))
        for t, day, rest in pts:
            print(f"  day {day:4}  {rest}")
    if len(rates) == 2 and all(rates):
        print(f"\nmod vs baseline: {rates[0]:.2f} vs {rates[1]:.2f} days/s ({(rates[0] / rates[1] - 1) * 100:+.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
