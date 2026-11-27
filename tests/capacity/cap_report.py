"""Summarize a capacity measurement run (tests/capacity/cap_measure together
with tests/market/mkt_baseline):

    python tests/capacity/cap_report.py <game.log> [<baseline game.log>]

Prints, by year:
  1. world unsold share of output per resource (mkt.q lines: unsold / prod,
     mean of the year's quarters), against the baseline log when given;
  2. capacity state per resource (countries idling / expanding, mean factor);
  3. signed contract price factors (PWW_DIPLO sign bundle, ok=1) by year and
     by rival-seller count, with the share of deals under 0.7;
  4. exporters' income: factories earned from resource sales (factories not
     owned: vanilla trade plus offsite contract factories, + 9 x contract PP),
     mean over the run, per country, against the baseline when given.
"""
import re
import statistics
import sys
from collections import defaultdict

RES = ["oil", "aluminium", "rubber", "tungsten", "steel", "chromium", "coal"]
MKT = re.compile(r"PWW_RESULT mkt\.q INFO (.*?) res=(\w+) (.*)$")
CAP = re.compile(r"PWW_RESULT cap_measure\.cap INFO (.*?) res=(\w+) (.*)$")
INC = re.compile(r"PWW_RESULT cap_measure\.inc INFO (.*?) tag=(\w+) (.*)$")
SIGN = re.compile(r"\[(\d{4})[\d.]*\]: .*PWW_DIPLO sign bundle (\w+)->(\w+) (.*)$")
YEAR = re.compile(r"(\d{4})")


def kv(s):
    return {k: float(v) for k, v in re.findall(r"(\w+)=([-\d.]+)", s)}


def read(path):
    mkt = defaultdict(lambda: defaultdict(list))
    cap = defaultdict(lambda: defaultdict(list))
    inc = defaultdict(list)
    deals = []
    for line in open(path, encoding="utf-8", errors="replace"):
        m = MKT.search(line)
        if m:
            y = YEAR.search(m.group(1))
            v = kv(m.group(3))
            if y and v.get("prod", 0) > 0:
                mkt[m.group(2)][int(y.group(1))].append(v)
            continue
        m = CAP.search(line)
        if m:
            y = YEAR.search(m.group(1))
            if y:
                cap[m.group(2)][int(y.group(1))].append(kv(m.group(3)))
            continue
        m = INC.search(line)
        if m:
            v = kv(m.group(3))
            # fx = factories not owned (vanilla trade income plus offsite
            # contract factories); PP payments count at 9 factories per PP a
            # day (the cartel lane's equivalence). "van" is the pool on offer,
            # not sales, so it is not income.
            inc[m.group(2)].append(v.get("fx", 0) + 9 * v.get("pp", 0))
            continue
        m = SIGN.search(line)
        if m:
            d = dict(re.findall(r"(\w+)=([-\w.]+)", m.group(4)))
            if d.get("ok") == "1" and "pf" in d:
                d["year"] = int(m.group(1))
                deals.append(d)
    return mkt, cap, inc, deals


def share(rows):
    xs = [r["unsold"] / r["prod"] for r in rows if r.get("prod", 0) > 0]
    return statistics.mean(xs) if xs else float("nan")


def main(path, base=None):
    mkt, cap, inc, deals = read(path)
    bm = binc = None
    if base:
        bm, _, binc, _ = read(base)
    years = sorted({y for r in mkt.values() for y in r})
    print("== world unsold share of output (mean of quarters; baseline in brackets)")
    print(f"{'res':<10}" + "".join(f"{y:>14}" for y in years))
    for r in RES:
        if r not in mkt:
            continue
        cells = []
        for y in years:
            s = share(mkt[r].get(y, []))
            b = share(bm[r].get(y, [])) if bm and r in bm else None
            cells.append(f"{s:6.0%}" + (f" [{b:4.0%}]" if b is not None and b == b else "       "))
        print(f"{r:<10}" + "".join(f"{c:>14}" for c in cells))

    if bm:
        # A pure exporter's unsold share is (1 - export share) at any output,
        # so the share hides idling: show volumes against the baseline.
        print("\n== world unsold units a day and output, this run / baseline (mean of quarters)")
        print(f"{'res':<10}" + "".join(f"{y:>18}" for y in years))
        for r in RES:
            if r not in mkt or r not in bm:
                continue
            cells = []
            for y in years:
                a, b = mkt[r].get(y, []), bm[r].get(y, [])
                if a and b:
                    ua = statistics.mean(x["unsold"] for x in a)
                    ub = statistics.mean(x["unsold"] for x in b)
                    pa = statistics.mean(x["prod"] for x in a)
                    pb = statistics.mean(x["prod"] for x in b)
                    cells.append(f"u x{ua / ub:.2f} p x{pa / pb:.2f}")
                else:
                    cells.append("-")
            print(f"{r:<10}" + "".join(f"{c:>18}" for c in cells))

    if cap:
        print("\n== capacity (last quarter of each year): idling / expanding countries, mean factor, units idled / added")
        for r in RES:
            if r not in cap:
                continue
            cells = []
            for y in years:
                q = cap[r].get(y)
                if q:
                    v = q[-1]
                    cells.append(f"{v['idle']:.0f}/{v['exp']:.0f} {v['mean']:.2f} -{v['lost']:.0f}+{v['gained']:.0f}")
                else:
                    cells.append("-")
            print(f"{r:<10}" + "".join(f"{c:>24}" for c in cells))

    if deals:
        print("\n== signed contract price factors")
        for y in sorted({d['year'] for d in deals}):
            xs = [float(d["pf"]) for d in deals if d["year"] == y]
            print(f"{y}: n={len(xs):<4} median={statistics.median(xs):.2f} p10={sorted(xs)[len(xs) // 10]:.2f} "
                  f"under0.7={sum(x < 0.7 for x in xs)} over1.2={sum(x > 1.2 for x in xs)}")
        print("by rival sellers at signing (all years | peace 1936-1938 | 1939-1940):")
        for lo, hi, name in ((0, 0, "no rival"), (1, 2, "1-2 rivals"), (3, 5, "3-5 rivals"), (6, 999, "6+ rivals")):
            parts = []
            for ys in (None, (1936, 1937, 1938), (1939, 1940)):
                xs = [float(d["pf"]) for d in deals if "comp" in d and lo <= int(d["comp"]) <= hi
                      and (ys is None or d["year"] in ys)]
                parts.append(f"n={len(xs):<3} med={statistics.median(xs):.2f} min={min(xs):.2f}" if xs else "n=0")
            print(f"  {name:<11} " + " | ".join(parts))
        print("by resource (median, n):", ", ".join(
            f"{r} {statistics.median(xs):.2f}/{len(xs)}" for i, r in enumerate(RES)
            for xs in [[float(d['pf']) for d in deals if d.get('res') == str(i)]] if xs))

    if inc:
        print("\n== exporters' income, factories a day (mean over the run; baseline and ratio when given)")
        rows = sorted(inc.items(), key=lambda kv_: -statistics.mean(kv_[1]))
        for tag, xs in rows[:30]:
            m = statistics.mean(xs)
            if binc and tag in binc:
                b = statistics.mean(binc[tag])
                flag = "" if b < 0.25 or abs(m / b - 1) <= 0.2 else "  <- outside 20%"
                print(f"  {tag} {m:6.2f}  base {b:6.2f}  x{m / b if b else float('nan'):.2f}{flag}")
            else:
                print(f"  {tag} {m:6.2f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
