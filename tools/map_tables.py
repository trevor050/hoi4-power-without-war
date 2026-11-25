#!/usr/bin/env python3
"""Offline map tables for HoI4 (vanilla or with The Road to 56 layered on top).

HoI4 script has no trigger for "sea strategic regions adjacent to a state", so
sea approaches must be computed from the map files. This tool reads
definition.csv, provinces.bmp, map/strategicregions and history/states and emits
per-state: owner, resources, land strategic region, coastal flag and the
adjacent sea strategic regions.

Usage:
    python tools/map_tables.py                       # vanilla, summary for POR
    python tools/map_tables.py --r56                 # with Road to 56
    python tools/map_tables.py --json out.json       # full table
    python tools/map_tables.py --tag POR --resource tungsten
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

GAME_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV")
R56_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\820260968")
# Road to 56 declares replace_path for these folders.
R56_REPLACE = {"history/states", "map/strategicregions"}

Image.MAX_IMAGE_PIXELS = None


class Layers:
    def __init__(self, r56: bool):
        self.roots = [R56_DIR, GAME_DIR] if r56 else [GAME_DIR]
        self.r56 = r56

    def file(self, rel: str) -> Path:
        for root in self.roots:
            p = root / rel
            if p.exists():
                return p
        raise FileNotFoundError(rel)

    def folder(self, rel: str) -> list[Path]:
        files: dict[str, Path] = {}
        for root in reversed(self.roots):  # later roots override
            if self.r56 and rel in R56_REPLACE and root != R56_DIR:
                continue
            d = root / rel
            if d.is_dir():
                for f in d.glob("*.txt"):
                    files[f.name] = f
        return [files[k] for k in sorted(files)]


def strip_comments(text: str) -> str:
    return re.sub(r"#[^\n]*", "", text)


def block(text: str, key: str) -> str | None:
    m = re.search(rf"\b{key}\s*=\s*\{{", text)
    if not m:
        return None
    i, depth = m.end(), 1
    while depth and i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return text[m.end(): i - 1]


def load_definitions(L: Layers):
    color_to_id: dict[int, int] = {}
    ptype: dict[int, str] = {}
    with L.file("map/definition.csv").open(encoding="latin-1") as f:
        for row in csv.reader(f, delimiter=";"):
            if len(row) < 5 or not row[0].strip().isdigit():
                continue
            pid = int(row[0])
            if pid == 0:
                continue
            r, g, b = int(row[1]), int(row[2]), int(row[3])
            color_to_id[(r << 16) | (g << 8) | b] = pid
            ptype[pid] = row[4].strip()
    return color_to_id, ptype


def province_adjacency(L: Layers, color_to_id: dict[int, int]) -> set[tuple[int, int]]:
    img = np.asarray(Image.open(L.file("map/provinces.bmp")).convert("RGB"), dtype=np.uint32)
    packed = (img[:, :, 0] << 16) | (img[:, :, 1] << 8) | img[:, :, 2]
    keys = np.array(sorted(color_to_id), dtype=np.uint32)
    vals = np.array([color_to_id[k] for k in keys], dtype=np.int32)
    idx = np.searchsorted(keys, packed)
    idx[idx >= len(keys)] = 0
    ids = np.where(keys[idx] == packed, vals[idx], 0)
    pairs: set[tuple[int, int]] = set()
    for a, b in ((ids[:, :-1], ids[:, 1:]), (ids[:-1, :], ids[1:, :]),
                 (ids[:, -1:], ids[:, :1])):  # horizontal wrap
        m = (a != b) & (a > 0) & (b > 0)
        stacked = np.unique(np.stack([np.minimum(a[m], b[m]), np.maximum(a[m], b[m])], axis=1), axis=0)
        pairs.update(map(tuple, stacked.tolist()))
    return pairs


def load_regions(L: Layers) -> tuple[dict[int, int], dict[int, str]]:
    prov_region: dict[int, int] = {}
    names: dict[int, str] = {}
    for f in L.folder("map/strategicregions"):
        t = strip_comments(f.read_text(encoding="utf-8-sig", errors="replace"))
        rid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        names[rid] = f.stem
        provs = block(t, "provinces") or ""
        for p in provs.split():
            if p.isdigit():
                prov_region[int(p)] = rid
    return prov_region, names


def load_states(L: Layers) -> dict[int, dict]:
    states: dict[int, dict] = {}
    for f in L.folder("history/states"):
        t = strip_comments(f.read_text(encoding="utf-8-sig", errors="replace"))
        sid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        provs = [int(p) for p in (block(t, "provinces") or "").split() if p.isdigit()]
        res: dict[str, float] = {}
        rb = block(t, "resources")
        if rb:
            for k, v in re.findall(r"(\w+)\s*=\s*([\d.]+)", rb):
                res[k] = float(v)
        hist = block(t, "history") or ""
        m = re.search(r"\bowner\s*=\s*(\w+)", hist)
        name = re.search(r'\bname\s*=\s*"?([\w.]+)"?', t)
        states[sid] = {"id": sid, "file": f.name, "name": name.group(1) if name else "",
                       "owner": m.group(1) if m else None, "provinces": provs, "resources": res}
    return states


def build(r56: bool) -> dict:
    L = Layers(r56)
    color_to_id, ptype = load_definitions(L)
    adj = province_adjacency(L, color_to_id)
    prov_region, region_names = load_regions(L)
    states = load_states(L)
    neighbors: dict[int, set[int]] = {}
    for a, b in adj:
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
    for s in states.values():
        land_regions = sorted({prov_region[p] for p in s["provinces"] if p in prov_region})
        seas: set[int] = set()
        for p in s["provinces"]:
            for n in neighbors.get(p, ()):
                if ptype.get(n) == "sea" and n in prov_region:
                    seas.add(prov_region[n])
        s["land_regions"] = land_regions
        s["sea_regions"] = sorted(seas)
        s["coastal"] = bool(seas)
    return {"variant": "r56" if r56 else "vanilla", "state_count": len(states),
            "region_count": len(region_names), "region_names": region_names, "states": states}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--r56", action="store_true")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--tag", default="POR")
    ap.add_argument("--resource", default="tungsten")
    a = ap.parse_args()
    data = build(a.r56)
    if a.json:
        out = dict(data)
        out["states"] = {k: {kk: vv for kk, vv in v.items() if kk != "provinces"} for k, v in data["states"].items()}
        a.json.write_text(json.dumps(out, indent=1), encoding="utf-8")
    rn = data["region_names"]
    print(f"variant={data['variant']} states={data['state_count']} regions={data['region_count']}")
    for s in sorted(data["states"].values(), key=lambda s: s["id"]):
        if s["owner"] != a.tag:
            continue
        mark = f" {a.resource}={s['resources'][a.resource]:g}" if a.resource in s["resources"] else ""
        print(f"  state {s['id']:>4} {s['file']:<32} land={','.join(rn.get(r, str(r)) for r in s['land_regions'])}"
              f" coastal={s['coastal']}{mark}")
        if s["sea_regions"]:
            print("        seas: " + "; ".join(rn.get(r, str(r)) for r in s["sea_regions"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
