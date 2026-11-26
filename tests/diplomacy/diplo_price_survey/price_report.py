"""Summarize signed trade deal prices from a diplo_price_survey game.log.

    python tests/diplomacy/diplo_price_survey/price_report.py <game.log>

Reads "PWW_DIPLO sign bundle" lines (ok=1): price factor pf = payment market
value / goods market value (1 = at market), the seller's walk-away, storage
fill and spare. Prints the distribution overall, by kind (AI sale draft vs
buyer's proposal) and by resource, and the cheapest deals.
"""
import re
import statistics
import sys

RES = ["oil", "aluminium", "rubber", "tungsten", "steel", "chromium", "coal"]
LINE = re.compile(r"\[([\d.]+)\]: .*PWW_DIPLO sign bundle (\w+)->(\w+) (.*)$")


def q(xs, p):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = (len(xs) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def row(name, xs):
    if not xs:
        return f"{name:<22} n=0"
    return (f"{name:<22} n={len(xs):<4} min={min(xs):.2f} p10={q(xs, .1):.2f} median={statistics.median(xs):.2f} "
            f"p90={q(xs, .9):.2f} max={max(xs):.2f} under0.5={sum(x < 0.5 for x in xs)} under0.25={sum(x < 0.25 for x in xs)}")


def main(path):
    deals = []
    for line in open(path, encoding="utf-8", errors="replace"):
        m = LINE.search(line)
        if not m:
            continue
        kv = dict(re.findall(r"(\w+)=([-\w.]+)", m.group(4)))
        if kv.get("ok") != "1" or "pf" not in kv:
            continue
        deals.append(dict(date=m.group(1), a=m.group(2), b=m.group(3), **kv))
    pf = [float(d["pf"]) for d in deals]
    print(row("all signed", pf))
    for s, name in (("1", "AI sale drafts"), ("0", "buyer proposals")):
        print(row(name, [float(d["pf"]) for d in deals if d.get("sale") == s]))
    for i, r in enumerate(RES):
        xs = [float(d["pf"]) for d in deals if d.get("res") == str(i)]
        if xs:
            print(row("  " + r, xs))
    print("cheapest:")
    for d in sorted(deals, key=lambda d: float(d["pf"]))[:12]:
        print(f"  {d['date']} {d['a']}->{d['b']} seller={d.get('seller')} res={RES[int(d.get('res', 0))]} sale={d.get('sale')} "
              f"pf={d['pf']} m0={d.get('m0')} m1={d.get('m1')} walk={d.get('walk')} stocked={d.get('stocked')} "
              f"fill={d.get('fill')} spare={d.get('spare')} prod={d.get('prod')}")


if __name__ == "__main__":
    main(sys.argv[1])
