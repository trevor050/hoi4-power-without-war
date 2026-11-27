"""Summarize a market baseline log: python tests/market/mkt_report.py <game.log>

Prints, per resource and quarter: world output, open-market imports,
unsold output, shortfall (countries short), contract volume, stored stock,
tightness = (imports + shortfall) / (imports + unsold) and the world tension.
"""
import re
import sys

LINE = re.compile(r"PWW_RESULT mkt\.q INFO (.*?) res=(\w+) (.*)$")


def main(path):
    rows = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        m = LINE.search(line)
        if not m:
            continue
        date, res, rest = m.groups()
        kv = dict(p.split("=") for p in rest.split())
        d = re.search(r"(\d+ \w+, \d{4})", date)
        rows.setdefault(res, []).append((d.group(1) if d else date, {k: float(v) for k, v in kv.items()}))
    for res, qs in rows.items():
        print(f"\n== {res}")
        print(f"{'date':<20}{'prod':>8}{'imp':>8}{'unsold':>8}{'short':>7}{'nshort':>7}{'ctr':>7}{'stock':>9}{'tight':>7}{'tens':>6}{'wars':>6}")
        for date, v in qs:
            demand = v["imp"] + v["short"]
            supply = v["imp"] + v["unsold"]
            tight = demand / supply if supply > 0 else float("inf")
            print(f"{date:<20}{v['prod']:>8.0f}{v['imp']:>8.0f}{v['unsold']:>8.0f}{v['short']:>7.0f}{v['nshort']:>7.0f}"
                  f"{v['ctr']:>7.0f}{v['stock']:>9.0f}{tight:>7.2f}{v['tension']:>6.0f}{v['wars']:>6.0f}")


if __name__ == "__main__":
    main(sys.argv[1])
