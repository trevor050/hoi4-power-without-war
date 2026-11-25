#!/usr/bin/env python3
"""Generate the coercion lane's data files.

Outputs (all overwritten):
  mod/common/scripted_effects/pww_coer_map_data.txt
      Per-state sea approaches, land region and nearby air regions for vanilla
      and Road to 56, computed offline with tools/map_tables.py (script has no
      trigger for "sea regions adjacent to a state"). The mod picks a variant at
      runtime by state count (see pww_coer_map_init in pww_coer_core.txt).
  mod/common/scripted_localisation/pww_coer_scripted_loc.txt
      defined_text entries that turn the reason, state and warning ids loaded
      by pww_coer_load_readout into loc keys.
  mod/localisation/english/pww_coer_readouts_l_english.yml
  mod/localisation/english/pww_coer_reputation_l_english.yml
      Converted from docs/content/readouts.md and reputation_voices.md (keys
      kept). UTF-8 with BOM.

The reason id tables below are the single source of truth for the ids stored in
the demand records; the header of pww_coer_core.txt mirrors them.

Usage:
    python tools/pww_coer_gen.py            # needs the game install (and R56)
    python tools/pww_coer_gen.py --no-r56   # vanilla table only (R56 skipped)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

# ---------------------------------------------------------------------------
# Reason ids. Index in the list = id (0 is "none").
FOR_REASONS = [
    None,
    "fleet_station", "fleet_ramping", "air_based", "air_access", "border_mass",
    "border_ramping", "dep_buyer", "dep_supplier", "clearing_debt", "cutoff_oil",
    "cutoff_coal", "cutoff_metal", "cutoff_rubber", "energy_shortage",
    "subsidy_pulled", "market_closed", "envoy_leverage", "embargo", "join_embargo",
    "quarantine", "strangulation", "convoy_pinch", "patron_backed_down",
    "patron_blocked", "no_patron", "rival_outbid", "fig_leaf", "timed_clause",
    "quiet_channel", "credibility_high", "target_at_war", "low_stability",
    "idle_mills", "clock_short",
]
HOLD_REASONS = [
    None,
    "patron_pledge", "guarantee", "faction", "alt_buyers", "rival_bid", "land_route",
    "rally_effect", "no_pretext", "dictator_pride", "demand_size", "humiliation",
    "recent_humiliation", "high_stability", "high_war_support", "hardened",
    "force_cap", "force_ramping", "fleet_contested", "air_range", "border_thin",
    "quiet_ceiling", "quarantine_lapsed", "embargo_ignored", "credibility_low",
    "reliability_low", "regional_alarm", "coercer_distracted", "held_stock",
    "coal_ok", "stalling", "provisional", "small_lot", "own_fig_leaf",
    "patron_called",
]
# Cornered warning ids (pww_cd_warn).
CORNERED = [
    None,
    "calc_plan", "calc_patron", "calc_frontier", "calc_mobilizing", "calc_pride",
    "calc_alliance", "desp_fuel", "desp_embargo", "desp_quarantine", "desp_runway",
    "desp_coal", "desp_isolation", "choice_fig_leaf", "choice_temporary",
    "choice_smaller_lot", "choice_push", "choice_patron_watch", "choice_cabinet_split",
]
# Intel line ids (pww_cd_intel).
INTEL = [
    None,
    "cornered_3w", "cornered_2w", "cornered_1w", "war_plan", "runway_short",
    "patron_talks", "patron_wavering", "leak_imminent", "fig_leaf_ready",
    "stall_detected", "split_lot_prep", "nationalize_risk", "cabinet_softening",
    "third_party_cheat",
]
STATES = ["defiant", "strained", "wavering", "cornered", "ready_to_fold"]
SLOTS = 4


def gen_map_table(r56: bool) -> tuple[int, list[str]]:
    import map_tables as mt  # noqa: E402  (tools/map_tables.py)

    L = mt.Layers(r56)
    color_to_id, ptype = mt.load_definitions(L)
    adj = mt.province_adjacency(L, color_to_id)
    prov_region, _names = mt.load_regions(L)
    states = mt.load_states(L)
    land_regions = {prov_region[p] for p, t in ptype.items() if t == "land" and p in prov_region}
    region_adj: dict[int, set[int]] = {}
    neighbors: dict[int, set[int]] = {}
    for a, b in adj:
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
        ra, rb = prov_region.get(a), prov_region.get(b)
        if ra is None or rb is None or ra == rb:
            continue
        if ptype.get(a) == "land" and ptype.get(b) == "land":
            region_adj.setdefault(ra, set()).add(rb)
            region_adj.setdefault(rb, set()).add(ra)
    lines: list[str] = []
    for sid in sorted(states):
        s = states[sid]
        regs = [prov_region[p] for p in s["provinces"] if p in prov_region]
        if not regs:
            continue
        # Land region: the region holding most of the state's provinces.
        lreg = max(set(regs), key=regs.count)
        seas: set[int] = set()
        for p in s["provinces"]:
            for n in neighbors.get(p, ()):
                if ptype.get(n) == "sea" and n in prov_region:
                    seas.add(prov_region[n])
        air = [lreg] + sorted(r for r in region_adj.get(lreg, ()) if r in land_regions and r != lreg)
        parts = [f"set_variable = {{ pww_coer_lreg = {lreg} }}"]
        parts += [f"add_to_array = {{ pww_coer_seas = {r} }}" for r in sorted(seas)[:6]]
        parts += [f"add_to_array = {{ pww_coer_airs = {r} }}" for r in air[:8]]
        lines.append(f"\t{sid} = {{ {' '.join(parts)} }}")
    return len(states), lines


def write_map_data(do_r56: bool) -> None:
    out = ROOT / "mod/common/scripted_effects/pww_coer_map_data.txt"
    hdr = [
        "###############################################################################",
        "# Power Without War: coercion map tables (GENERATED by tools/pww_coer_gen.py)",
        "#",
        "# Do not edit by hand. Regenerate after a game or Road to 56 map update:",
        "#     python tools/pww_coer_gen.py",
        "# Per state (state scope variables, set once by pww_coer_map_init):",
        "#   pww_coer_lreg   land strategic region holding most of the state",
        "#   pww_coer_seas   array: sea strategic regions adjacent to the state",
        "#   pww_coer_airs   array: the state's region plus adjacent land regions",
        "#                   (where planes based nearby count for an air demonstration)",
        "###############################################################################",
        "",
    ]
    body: list[str] = []
    n, lines = gen_map_table(False)
    body += [f"# vanilla: {n} states", "pww_coer_map_load_vanilla = {"] + lines + ["}", ""]
    vcount = n
    rcount = 0
    if do_r56:
        n, lines = gen_map_table(True)
        rcount = n
        body += [f"# Road to 56: {n} states", "pww_coer_map_load_r56 = {"] + lines + ["}", ""]
    else:
        body += ["pww_coer_map_load_r56 = {", "\tset_variable = { global.pww_coer_map_variant = 0 }", "}", ""]
    body += [
        "# Fingerprints (state counts) the tables were generated for.",
        "pww_coer_map_fingerprints = {",
        f"\tset_variable = {{ global.pww_coer_map_fp_vanilla = {vcount} }}",
        f"\tset_variable = {{ global.pww_coer_map_fp_r56 = {rcount} }}",
        "}",
        "",
    ]
    out.write_text("\n".join(hdr + body), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} (vanilla {vcount}, r56 {rcount})")


def defined_text(name: str, entries: list[tuple[str, str]], default: str | None) -> list[str]:
    out = ["defined_text = {", f"\tname = {name}"]
    for trig, key in entries:
        out.append(f"\ttext = {{ trigger = {{ {trig} }} localization_key = {key} }}")
    if default:
        out.append(f"\ttext = {{ localization_key = {default} }}")
    out.append("}")
    out.append("")
    return out


def write_scripted_loc() -> None:
    out = ROOT / "mod/common/scripted_localisation/pww_coer_scripted_loc.txt"
    L = [
        "###############################################################################",
        "# Power Without War: coercion readout scripted localisation",
        "# (GENERATED by tools/pww_coer_gen.py; do not edit by hand)",
        "#",
        "# Reads the readout loaded on the viewing country by pww_coer_load_readout",
        "# (country variables pww_coer_rd_*). Use from loc as [pww_coer_loc_for_0],",
        "# [pww_coer_loc_state], ... in a context whose scope is the viewer. The",
        "# texts use [FROM...] for the target and [pww_patron...] / [pww_rival...]",
        "# (variables the loader sets on the viewer).",
        "###############################################################################",
        "",
    ]
    st = [(f"check_variable = {{ pww_coer_rd_state = {i} }}", f"pww_state_{s}") for i, s in enumerate(STATES)]
    L += defined_text("pww_coer_loc_state", st, None)
    L += defined_text("pww_coer_loc_state_desc", [(t, k + "_desc") for t, k in st], None)
    L += defined_text("pww_curr_state", st, None)
    L += defined_text("pww_prev_state",
                      [(f"check_variable = {{ pww_coer_rd_prev = {i} }}", f"pww_state_{s}") for i, s in enumerate(STATES)], None)
    cause = [(f"check_variable = {{ pww_coer_rd_cause_side = 0 }} check_variable = {{ pww_coer_rd_cause = {i} }}",
              f"pww_cause_for_{r}") for i, r in enumerate(FOR_REASONS) if r]
    cause += [(f"check_variable = {{ pww_coer_rd_cause_side = 1 }} check_variable = {{ pww_coer_rd_cause = {i} }}",
               f"pww_cause_against_{r}") for i, r in enumerate(HOLD_REASONS) if r]
    L += defined_text("pww_shift_cause", cause, "pww_coer_blank")
    L += defined_text("pww_coer_loc_shift",
                      [("check_variable = { pww_coer_rd_prev < pww_coer_rd_state }", "pww_readout_shift_up"),
                       ("check_variable = { pww_coer_rd_prev > pww_coer_rd_state }", "pww_readout_shift_down")],
                      "pww_coer_blank")
    for side, reasons, prefix, empty in (("for", FOR_REASONS, "pww_cause_for_", "pww_readout_empty_for"),
                                          ("hold", HOLD_REASONS, "pww_cause_against_", "pww_readout_empty_against")):
        for k in range(SLOTS):
            ent: list[tuple[str, str]] = []
            if k == 0:
                ent.append((f"check_variable = {{ pww_coer_rd_n{side} = 0 }}", empty))
            else:
                # Hidden by intel: the first hidden slot says so, later ones are blank.
                ent.append((f"check_variable = {{ pww_coer_rd_reveal = {k} }} check_variable = {{ pww_coer_rd_n{side} > {k} }}",
                            "pww_readout_intel_locked"))
                ent.append((f"check_variable = {{ pww_coer_rd_reveal < {k} }}", "pww_coer_blank"))
            ent += [(f"check_variable = {{ pww_coer_rd_{side}{k} = {i} }}", prefix + r)
                    for i, r in enumerate(reasons) if r]
            L += defined_text(f"pww_coer_loc_{side}_{k}", ent, "pww_coer_blank")
    L += defined_text("pww_coer_loc_cornered",
                      [(f"check_variable = {{ pww_coer_rd_warn = {i} }}", f"pww_cornered_{w}")
                       for i, w in enumerate(CORNERED) if w], "pww_coer_blank")
    L += defined_text("pww_coer_loc_intel",
                      [(f"check_variable = {{ pww_coer_rd_intel = {i} }}", f"pww_intel_{w}")
                       for i, w in enumerate(INTEL) if w], "pww_coer_blank")
    L += defined_text("pww_coer_loc_cred_band",
                      [(f"check_variable = {{ pww_coer_rd_cred_band = {i} }}", f"pww_rep_cred_band_{i}") for i in range(5)], None)
    L += defined_text("pww_coer_loc_alarm_band",
                      [(f"check_variable = {{ pww_coer_rd_alarm_band = {i} }}", f"pww_rep_alarm_band_{i}") for i in range(5)], None)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


ROW = re.compile(r"^\|(.*)\|\s*$")


def md_loc(md: Path) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in md.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line.strip())
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        ticks = [c[1:-1] for c in cells if len(c) >= 2 and c.startswith("`") and c.endswith("`")]
        keys = [t for t in ticks if re.fullmatch(r"pww_\w+", t)]
        if not keys or len(ticks) < 2:
            continue
        key, text = keys[0], ticks[-1]
        if text == key:
            continue
        pairs.append((key, text))
    return pairs


def write_yml(name: str, pairs: list[tuple[str, str]], extra: list[tuple[str, str]] = ()) -> None:
    out = ROOT / "mod/localisation/english" / name
    lines = ["l_english:"]
    seen = set()
    for k, v in list(pairs) + list(extra):
        if k in seen:
            continue
        seen.add(k)
        if "—" in v:
            raise SystemExit(f"em dash in {k}")
        # The content bible's GetCapitalName is not a loc function (renders
        # empty): vanilla uses Capital.GetCapitalVictoryPointName.
        v = v.replace(".GetCapitalName]", ".Capital.GetCapitalVictoryPointName]")
        v = v.replace('"', '\\"')
        lines.append(f' {k}:0 "{v}"')
    out.write_text("﻿" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(seen)} keys)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-r56", action="store_true")
    ap.add_argument("--skip-map", action="store_true", help="only regenerate loc and scripted loc")
    a = ap.parse_args()
    if not a.skip_map:
        write_map_data(not a.no_r56)
    write_scripted_loc()
    write_yml("pww_coer_readouts_l_english.yml", md_loc(ROOT / "docs/content/readouts.md"),
              [("pww_coer_blank", "")])
    write_yml("pww_coer_reputation_l_english.yml", md_loc(ROOT / "docs/content/reputation_voices.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
