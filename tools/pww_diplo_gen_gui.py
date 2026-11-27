"""Diplomacy lane generator: python tools/pww_diplo_gen_gui.py
Generate the diplomacy lane's GUI layout, scripted GUI blocks and scripted
localisation. Output files carry a header saying they are generated; they are
also fine to edit by hand afterwards."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pww_diplo_gen_talks as talks

# --layout-only: write the .gui, .gfx and scripted GUI files only; the scripted
# localisation file is left as it is on disk (another lane may own edits).
LAYOUT_ONLY = "--layout-only" in sys.argv

REPO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mod")
GUI_OUT = os.path.join(REPO, "interface", "pww_diplo.gui")
GFX_OUT = os.path.join(REPO, "interface", "pww_diplo_sprites.gfx")
SG_OUT = os.path.join(REPO, "common", "scripted_guis", "pww_diplo_guis.txt")
SL_OUT = os.path.join(REPO, "common", "scripted_localisation", "pww_diplo_scripted_loc.txt")
FX_OUT = os.path.join(REPO, "common", "scripted_effects", "pww_diplo_bundle_gen.txt")

# Layout grid (UI lane, 2026-11-25). The vanilla frame these windows sit in
# (popupwindow.gui: send_/diplomacy_scripted_popup_window) is 584 wide with
# Cancel at x 77..200 and Send at 386..509. Content uses the same verticals:
# left edge GL = Cancel's left edge, the label/value split at Cancel's right
# edge, right edge GR = Send's right edge. Paragraphs span GL..GR centred, so
# they centre under the frame's centred title; values centre in their column.
W = 584
GL, GR = 77, 509
CW = GR - GL
ROW_H = 26
LX = GL
LW = 118                      # label column (GL..195)
PX, NX = 204, GR - 16         # prev / next arrows (16 px)
VX = PX + 20                  # value column between the arrows
VW = NX - 4 - VX
FONT = "hoi_16mbs"
PAD_BOTTOM = 8

gui = []      # guiTypes body
effects = {}  # gui name -> list of effect blocks
triggers = {} # gui name -> list of trigger blocks


def tb(name, x, y, text, w=CW, h=22, font=FONT, fmt="centre", tooltip=None):
    t = f'\t\tinstantTextBoxType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tfont = "{font}"\n\t\t\ttext = "{text}"\n\t\t\tmaxWidth = {w}\n\t\t\tmaxHeight = {h}\n\t\t\tformat = {fmt}\n\t\t\tfixedsize = yes\n'
    if tooltip:
        t += f'\t\t\tpdx_tooltip = "{tooltip}"\n'
    return t + "\t\t}\n"


def btn(name, x, y, sprite, tooltip=None):
    t = f'\t\tbuttonType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tquadTextureSprite = "{sprite}"\n'
    if tooltip:
        t += f'\t\t\tpdx_tooltip = "{tooltip}"\n'
    return t + "\t\t}\n"


def icon(name, x, y, sprite, scale=None):
    t = f'\t\ticonType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tspriteType = "{sprite}"\n'
    if scale:
        t += f"\t\t\tscale = {scale}\n"
    return t + "\t\t}\n"


def window(name, h, body):
    h += PAD_BOTTOM
    return (f'\tcontainerWindowType = {{\n\t\tname = "{name}"\n\t\tposition = {{ x = 0 y = 0 }}\n'
            f'\t\tsize = {{ width = {W} height = {h} }}\n\t\tmoveable = no\n\t\torientation = center\n\t\tclipping = no\n\n'
            + body + "\t}\n\n")


def cycle_row(g, pre, key, y, label, value, nxt, prv, arrows_vis=None, tooltip=None):
    """A term card: label, prev arrow, value, next arrow."""
    body = tb(f"{pre}_{key}_label", LX, y + 3, label, w=LW, fmt="left")
    body += btn(f"{pre}_{key}_prev", PX, y + 4, "GFX_pww_diplo_prev")
    body += tb(f"{pre}_{key}_value", VX, y + 3, value, w=VW, fmt="centre", tooltip=tooltip)
    body += btn(f"{pre}_{key}_next", NX, y + 4, "GFX_pww_diplo_next")
    effects.setdefault(g, []).append(f"\t\t\t{pre}_{key}_next_click = {{\n{nxt}\t\t\t}}\n")
    effects[g].append(f"\t\t\t{pre}_{key}_prev_click = {{\n{prv}\t\t\t}}\n")
    if arrows_vis:
        for b in ("prev", "next"):
            triggers.setdefault(g, []).append(f"\t\t\t{pre}_{key}_{b}_visible = {{\n{arrows_vis}\t\t\t}}\n")
    return body


def ro_row(pre, key, y, label, value):
    body = tb(f"{pre}_{key}_label", LX, y + 3, label, w=LW, fmt="left")
    body += tb(f"{pre}_{key}_value", VX, y + 3, value, w=GR - VX, fmt="centre")
    return body


def wrap(var, lo, hi, step, root=True, after="pww_diplo_offer_changed = yes"):
    """Effect body cycling ROOT.var by step within lo..hi."""
    if step > 0:
        cmp_ = f"check_variable = {{ {var} > {hi} }}"
        reset = f"set_variable = {{ {var} = {lo} }}"
        op = f"add_to_variable = {{ {var} = 1 }}"
    else:
        cmp_ = f"check_variable = {{ {var} < {lo} }}"
        reset = f"set_variable = {{ {var} = {hi} }}"
        op = f"subtract_from_variable = {{ {var} = 1 }}"
    inner = (f"\t\t\t\t\t{op}\n\t\t\t\t\tif = {{ limit = {{ {cmp_} }} {reset} }}\n"
             f"\t\t\t\t\t{after}\n")
    return f"\t\t\t\tROOT = {{\n{inner}\t\t\t\t}}\n" if root else inner


def checkbox(g, pre, key, y, label, var, val, tooltip=None, scope_this=True):
    """A radio/checkbox row on the receiver: off and on buttons + label."""
    body = btn(f"{pre}_{key}_off", LX, y + 4, "GFX_pww_diplo_box_off", tooltip)
    body += btn(f"{pre}_{key}_on", LX, y + 4, "GFX_pww_diplo_box_on", tooltip)
    body += tb(f"{pre}_{key}_label", LX + 24, y + 3, label, w=CW - 24, fmt="left", tooltip=tooltip)
    set_ = (f"\t\t\t\tif = {{\n\t\t\t\t\tlimit = {{ check_variable = {{ {var} = {val} }} }}\n"
            f"\t\t\t\t\tset_variable = {{ {var} = 0 }}\n\t\t\t\t}}\n"
            f"\t\t\t\telse = {{ set_variable = {{ {var} = {val} }} }}\n"
            f"\t\t\t\tadd_to_variable = {{ pww_diplo_dirty = 1 }}\n")
    if var in ("pww_dr_move", "pww_dr_settle"):
        set_ = (f"\t\t\t\tset_variable = {{ {var} = {val} }}\n"
                f"\t\t\t\tadd_to_variable = {{ pww_diplo_dirty = 1 }}\n")
    for b in ("off", "on"):
        effects.setdefault(g, []).append(f"\t\t\t{pre}_{key}_{b}_click = {{\n{set_}\t\t\t}}\n")
    triggers.setdefault(g, []).append(
        f"\t\t\t{pre}_{key}_on_visible = {{ check_variable = {{ {var} = {val} }} }}\n")
    triggers[g].append(
        f"\t\t\t{pre}_{key}_off_visible = {{ NOT = {{ check_variable = {{ {var} = {val} }} }} }}\n")
    return body


def divider(name, y):
    return icon(name, LX, y, "GFX_divider", scale=f"{CW / 514:.3f}")


# ------------------------------------------------- send offer (trade talks)
gui.append(talks.build_send(effects, triggers))

# --------------------------------------------------------------- send demand
G = "pww_diplo_send_demand_gui"
P = "pww_sd"
locked = "\t\t\t\tROOT = { check_variable = { pww_dm_live < 0 } }\n"
dch = "pww_diplo_demand_changed = yes"
b = tb(f"{P}_title", LX, 8, "[pww_diplo_sl_dm_title]", font="hoi_18mbs")
y0 = 40
rows = [
    ("type", "pww_diplo_lbl_demand", "[pww_diplo_sl_dm_type]",
     wrap("pww_dm_type", 0, 1, 1, after=dch), wrap("pww_dm_type", 0, 1, -1, after=dch), locked),
    ("res", "pww_diplo_lbl_res", "[pww_diplo_sl_dm_res]",
     wrap("pww_dm_res", 0, 6, 1, after=dch), wrap("pww_dm_res", 0, 6, -1, after=dch), locked),
    ("qty", "[pww_diplo_sl_dm_l3]", "[pww_diplo_sl_dm_v3]",
     "\t\t\t\tROOT = {\n\t\t\t\t\tif = {\n\t\t\t\t\t\tlimit = { check_variable = { pww_dm_type = 1 } }\n"
     "\t\t\t\t\t\tadd_to_variable = { pww_dm_slot = 1 }\n\t\t\t\t\t}\n\t\t\t\t\telse = {\n"
     "\t\t\t\t\t\tadd_to_variable = { pww_dm_amt = 1 }\n"
     "\t\t\t\t\t\tif = { limit = { check_variable = { pww_dm_amt > 2 } } set_variable = { pww_dm_amt = 0 } }\n"
     "\t\t\t\t\t}\n\t\t\t\t\tpww_diplo_demand_changed = yes\n\t\t\t\t}\n",
     "\t\t\t\tROOT = {\n\t\t\t\t\tif = {\n\t\t\t\t\t\tlimit = { check_variable = { pww_dm_type = 1 } }\n"
     "\t\t\t\t\t\tadd_to_variable = { pww_dm_slot = 1 }\n\t\t\t\t\t}\n\t\t\t\t\telse = {\n"
     "\t\t\t\t\t\tsubtract_from_variable = { pww_dm_amt = 1 }\n"
     "\t\t\t\t\t\tif = { limit = { check_variable = { pww_dm_amt < 0 } } set_variable = { pww_dm_amt = 2 } }\n"
     "\t\t\t\t\t}\n\t\t\t\t\tpww_diplo_demand_changed = yes\n\t\t\t\t}\n", locked),
    ("dur", "pww_diplo_lbl_dur", "[pww_diplo_sl_dm_dur]",
     wrap("pww_dm_dur", 1, 3, 1, after=dch), wrap("pww_dm_dur", 1, 3, -1, after=dch), locked),
    ("fig", "pww_diplo_lbl_fig", "[pww_diplo_sl_dm_fig]",
     wrap("pww_dm_fig", 0, 4, 1, after=dch), wrap("pww_dm_fig", 0, 4, -1, after=dch), None),
]
for i, (k, lab, val, nx, pv, vis) in enumerate(rows):
    b += cycle_row(G, P, k, y0 + i * ROW_H, lab, val, nx, pv, vis,
                   tooltip="pww_diplo_tt_fig_demand" if k == "fig" else None)
y = y0 + len(rows) * ROW_H
# take less (press only)
b += btn(f"{P}_less_off", LX, y + 4, "GFX_pww_diplo_box_off", "pww_diplo_tt_less")
b += btn(f"{P}_less_on", LX, y + 4, "GFX_pww_diplo_box_on", "pww_diplo_tt_less")
b += tb(f"{P}_less_label", LX + 24, y + 3, "pww_diplo_lbl_less", w=CW - 24, fmt="left")
for s_ in ("off", "on"):
    effects[G].append(
        f"\t\t\t{P}_less_{s_}_click = {{\n\t\t\t\tROOT = {{\n"
        f"\t\t\t\t\tif = {{ limit = {{ check_variable = {{ pww_dm_less = 1 }} }} set_variable = {{ pww_dm_less = 0 }} }}\n"
        f"\t\t\t\t\telse = {{ set_variable = {{ pww_dm_less = 1 }} }}\n\t\t\t\t\tpww_diplo_demand_changed = yes\n\t\t\t\t}}\n\t\t\t}}\n")
triggers[G].append(f"\t\t\t{P}_less_on_visible = {{ ROOT = {{ check_variable = {{ pww_dm_live > -1 }} check_variable = {{ pww_dm_less = 1 }} }} }}\n")
triggers[G].append(f"\t\t\t{P}_less_off_visible = {{ ROOT = {{ check_variable = {{ pww_dm_live > -1 }} check_variable = {{ pww_dm_less = 0 }} }} }}\n")
triggers[G].append(f"\t\t\t{P}_less_label_visible = {{ ROOT = {{ check_variable = {{ pww_dm_live > -1 }} }} }}\n")
y += ROW_H + 4
b += divider(f"{P}_div", y)
y += 12
b += tb(f"{P}_status", LX, y, "[pww_diplo_sl_dm_status]", h=36)
y += 38
b += tb(f"{P}_invalid", LX, y, "[pww_diplo_sl_dm_invalid]")
y += 24
b += tb(f"{P}_desc", LX, y, "[pww_diplo_sl_dm_desc]", h=76)
y += 80
gui.append(window("pww_diplo_send_demand", y, b))

# --------------------------------------------------------------- send pledge
G = "pww_diplo_send_pledge_gui"
P = "pww_sp"
pch = "pww_diplo_pledge_changed = yes"
b = tb(f"{P}_title", LX, 8, "pww_diplo_gui_pledge_title", font="hoi_18mbs")
y0 = 40
vs_next = ("\t\t\t\tset_temp_variable = { pww_gn = pww_dd_pressers^num }\n"
           "\t\t\t\tROOT = {\n\t\t\t\t\tadd_to_variable = { pww_dp_ci = 1 }\n"
           "\t\t\t\t\tif = { limit = { check_variable = { pww_dp_ci > pww_gn } } set_variable = { pww_dp_ci = -1 } }\n"
           "\t\t\t\t\tif = { limit = { check_variable = { pww_dp_ci = pww_gn } } set_variable = { pww_dp_ci = -1 } }\n"
           "\t\t\t\t\tpww_diplo_pledge_changed = yes\n\t\t\t\t}\n")
vs_prev = ("\t\t\t\tset_temp_variable = { pww_gn = pww_dd_pressers^num }\n"
           "\t\t\t\tsubtract_from_temp_variable = { pww_gn = 1 }\n"
           "\t\t\t\tROOT = {\n\t\t\t\t\tsubtract_from_variable = { pww_dp_ci = 1 }\n"
           "\t\t\t\t\tif = { limit = { check_variable = { pww_dp_ci < -1 } } set_variable = { pww_dp_ci = pww_gn } }\n"
           "\t\t\t\t\tpww_diplo_pledge_changed = yes\n\t\t\t\t}\n")
rows = [
    ("vs", "pww_diplo_lbl_against", "[pww_diplo_sl_dp_vs]", vs_next, vs_prev, None),
    ("res", "pww_diplo_lbl_res", "[pww_diplo_sl_dp_res]",
     wrap("pww_dp_res", 0, 6, 1, after=pch), wrap("pww_dp_res", 0, 6, -1, after=pch), None),
    ("qty", "pww_diplo_lbl_qty", "[pww_diplo_sl_dp_amt]",
     wrap("pww_dp_amt", 0, 3, 1, after=pch), wrap("pww_dp_amt", 0, 3, -1, after=pch), None),
    ("pay", "pww_diplo_lbl_pay", "[pww_diplo_sl_dp_pay]",
     "\t\t\t\tROOT = {\n\t\t\t\t\tif = { limit = { check_variable = { pww_dp_pay = 0 } } set_variable = { pww_dp_pay = 3 } }\n"
     "\t\t\t\t\telse = { set_variable = { pww_dp_pay = 0 } }\n\t\t\t\t\tpww_diplo_pledge_changed = yes\n\t\t\t\t}\n",
     "\t\t\t\tROOT = {\n\t\t\t\t\tif = { limit = { check_variable = { pww_dp_pay = 0 } } set_variable = { pww_dp_pay = 3 } }\n"
     "\t\t\t\t\telse = { set_variable = { pww_dp_pay = 0 } }\n\t\t\t\t\tpww_diplo_pledge_changed = yes\n\t\t\t\t}\n", None),
    ("dur", "pww_diplo_lbl_dur", "[pww_diplo_sl_dp_dur]",
     wrap("pww_dp_dur", 1, 4, 1, after=pch), wrap("pww_dp_dur", 1, 4, -1, after=pch), None),
]
for i, (k, lab, val, nx, pv, vis) in enumerate(rows):
    b += cycle_row(G, P, k, y0 + i * ROW_H, lab, val, nx, pv, vis)
y = y0 + len(rows) * ROW_H + 4
b += divider(f"{P}_div", y)
y += 12
b += tb(f"{P}_band", LX, y, "pww_diplo_gui_pledge_exposure")
y += 22
b += tb(f"{P}_invalid", LX, y, "[pww_diplo_sl_dp_invalid]")
y += 24
b += tb(f"{P}_desc", LX, y, "pww_act_pledge_support_desc", h=76)
y += 80
gui.append(window("pww_diplo_send_pledge", y, b))

# -------------------------------------------------------------- send embargo
G = "pww_diplo_send_embargo_gui"
P = "pww_se"
ech = "pww_diplo_embargo_changed = yes"
b = tb(f"{P}_title", LX, 8, "pww_diplo_gui_embargo_title", font="hoi_18mbs")
b += cycle_row(G, P, "tgt", 40, "pww_diplo_lbl_embargo_on", "[pww_diplo_sl_de_target]",
               wrap("pww_de_i", 0, 99, 1, after=ech),
               "\t\t\t\tROOT = {\n\t\t\t\t\tsubtract_from_variable = { pww_de_i = 1 }\n"
               "\t\t\t\t\tif = {\n\t\t\t\t\t\tlimit = { check_variable = { pww_de_i < 0 } }\n"
               "\t\t\t\t\t\tset_variable = { pww_de_i = pww_de_list^num }\n"
               "\t\t\t\t\t\tsubtract_from_variable = { pww_de_i = 1 }\n\t\t\t\t\t}\n"
               "\t\t\t\t\tpww_diplo_embargo_changed = yes\n\t\t\t\t}\n")
y = 40 + ROW_H + 4
b += divider(f"{P}_div", y)
y += 12
b += tb(f"{P}_invalid", LX, y, "[pww_diplo_sl_de_invalid]")
y += 24
b += tb(f"{P}_desc", LX, y, "pww_act_join_embargo_desc", h=58)
y += 62
gui.append(window("pww_diplo_send_embargo", y, b))

# ------------------------------------------------------------------ send bid
G = "pww_diplo_send_bid_gui"
P = "pww_sb"
bch = "pww_diplo_bid_changed = yes"
b = tb(f"{P}_title", LX, 8, "pww_diplo_gui_bid_title", font="hoi_18mbs")
y0 = 40
rows = [
    ("lot", "pww_diplo_lbl_lot", "[pww_diplo_sl_db_lot]",
     wrap("pww_db_i", 0, 99, 1, after=bch),
     "\t\t\t\tROOT = {\n\t\t\t\t\tsubtract_from_variable = { pww_db_i = 1 }\n"
     "\t\t\t\t\tif = {\n\t\t\t\t\t\tlimit = { check_variable = { pww_db_i < 0 } }\n"
     "\t\t\t\t\t\tset_variable = { pww_db_i = pww_db_lots^num }\n"
     "\t\t\t\t\t\tsubtract_from_variable = { pww_db_i = 1 }\n\t\t\t\t\t}\n"
     "\t\t\t\t\tpww_diplo_bid_changed = yes\n\t\t\t\t}\n", None),
    ("pay", "pww_diplo_lbl_pay", "[pww_diplo_sl_db_pay]",
     wrap("pww_db_pay", 0, 4, 1, after=bch), wrap("pww_db_pay", 0, 4, -1, after=bch), None),
    ("price", "pww_diplo_lbl_price", "[pww_diplo_sl_db_price]",
     wrap("pww_db_price", 0, 2, 1, after=bch), wrap("pww_db_price", 0, 2, -1, after=bch), None),
    ("sweet", "pww_diplo_lbl_sweet", "[pww_diplo_sl_db_sweet]",
     wrap("pww_db_sweet", 0, 3, 1, after=bch), wrap("pww_db_sweet", 0, 3, -1, after=bch), None),
    ("fig", "pww_diplo_lbl_fig", "[pww_diplo_sl_db_fig]",
     wrap("pww_db_fig", 0, 6, 1, after=bch), wrap("pww_db_fig", 0, 6, -1, after=bch), None),
]
for i, (k, lab, val, nx, pv, vis) in enumerate(rows):
    b += cycle_row(G, P, k, y0 + i * ROW_H, lab, val, nx, pv, vis)
y = y0 + len(rows) * ROW_H + 4
b += divider(f"{P}_div", y)
y += 12
b += tb(f"{P}_lotdesc", LX, y, "[pww_diplo_sl_db_lotdesc]", h=36)
y += 38
b += tb(f"{P}_bands", LX, y, "[pww_diplo_sl_o_bands]")
y += 22
b += tb(f"{P}_invalid", LX, y, "[pww_diplo_sl_db_invalid]")
y += 24
b += tb(f"{P}_desc", LX, y, "pww_auction_bid_once", h=40)
y += 44
gui.append(window("pww_diplo_send_bid", y, b))

# ---------------------------------------------- receive offer (trade talks)
gui.append(talks.build_recv(effects, triggers))

# ------------------------------------------------------------ receive demand
G = "pww_diplo_recv_demand_gui"
P = "pww_rd"
b = tb(f"{P}_title", LX, 8, "[pww_diplo_sl_rd_title]", font="hoi_18mbs")
b += tb(f"{P}_terms", LX, 38, "[pww_diplo_sl_rd_terms]", h=40)
y = 82
b += divider(f"{P}_div", y)
y += 12
moves = [(1, "pww_rcv_move_small_lot"), (2, "pww_rcv_move_provisional"), (3, "pww_rcv_move_fig_leaf"),
         (4, "pww_rcv_move_call_patron"), (5, "pww_rcv_move_harden"), (6, "pww_rcv_move_refuse"),
         (7, "pww_rcv_move_stall")]
for m, key in moves:
    b += checkbox(G, P, f"m{m}", y, key, "pww_dr_move", m, tooltip=f"{key}_desc")
    y += 24
triggers[G].append(f"\t\t\t{P}_m7_off_visible = {{ check_variable = {{ pww_dr_channel = 0 }} NOT = {{ check_variable = {{ pww_dr_move = 7 }} }} }}\n")
triggers[G].append(f"\t\t\t{P}_m7_label_visible = {{ check_variable = {{ pww_dr_channel = 0 }} }}\n")
y += 4
b += tb(f"{P}_hint", LX, y, "pww_diplo_gui_move_hint", h=36)
y += 40
gui.append(window("pww_diplo_recv_demand", y, b))

# ------------------------------------------------------------ receive settle
G = "pww_diplo_recv_settle_gui"
P = "pww_rs"
b = tb(f"{P}_title", LX, 8, "pww_rcv_settlement_title", font="hoi_18mbs")
b += tb(f"{P}_desc", LX, 36, "pww_diplo_gui_settle_desc", h=40)
y = 80
for v, key in [(0, "pww_rcv_settle_cic"), (1, "pww_rcv_settle_kind"), (2, "pww_rcv_settle_reverse")]:
    b += checkbox(G, P, f"o{v}", y, key, "pww_dr_settle", v, tooltip=f"{key}_desc")
    y += 24
y += 6
b += tb(f"{P}_hint", LX, y, "pww_diplo_gui_settle_hint", h=36)
y += 40
gui.append(window("pww_diplo_recv_settle", y, b))

# Fix the m7 duplicate triggers produced by checkbox(): drop the generic ones.
triggers["pww_diplo_recv_demand_gui"] = [
    t for t in triggers["pww_diplo_recv_demand_gui"]
    if not (t.strip().startswith("pww_rd_m7_off_visible = { NOT"))
]

HEADER = ("# Power Without War: diplomacy lane GUI layout (generated by the diplomacy\n"
          "# lane's layout script; safe to edit by hand). One window per send or\n"
          "# receive scripted GUI; term cards are label + arrows + value rows.\n")
with open(GUI_OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(HEADER + "guiTypes = {\n" + "".join(gui) + "}\n")

with open(GFX_OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("""# Power Without War: diplomacy lane sprites (vanilla textures).
spriteTypes = {
	spriteType = {
		name = "GFX_pww_diplo_prev"
		texturefile = "gfx/interface/scrollbar_leftbutton_type_2.dds"
		effectFile = "gfx/FX/buttonstate.lua"
	}
	spriteType = {
		name = "GFX_pww_diplo_next"
		texturefile = "gfx/interface/scrollbar_rightbutton_type_2.dds"
		effectFile = "gfx/FX/buttonstate.lua"
	}
	spriteType = {
		name = "GFX_pww_diplo_box_off"
		texturefile = "gfx/interface/checkbox_small_unticked.dds"
		effectFile = "gfx/FX/buttonstate.lua"
	}
	spriteType = {
		name = "GFX_pww_diplo_box_on"
		texturefile = "gfx/interface/checkbox_small_ticked.dds"
		effectFile = "gfx/FX/buttonstate.lua"
	}
""" + talks.SPRITES + "}\n")

with open(FX_OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(talks.mirror_effects())

windows = {
    "pww_diplo_send_offer_gui": "pww_diplo_send_offer",
    "pww_diplo_send_demand_gui": "pww_diplo_send_demand",
    "pww_diplo_send_pledge_gui": "pww_diplo_send_pledge",
    "pww_diplo_send_embargo_gui": "pww_diplo_send_embargo",
    "pww_diplo_send_bid_gui": "pww_diplo_send_bid",
    "pww_diplo_recv_offer_gui": "pww_diplo_recv_offer",
    "pww_diplo_recv_demand_gui": "pww_diplo_recv_demand",
    "pww_diplo_recv_settle_gui": "pww_diplo_recv_settle",
}
out = ["# Power Without War: diplomacy lane scripted GUIs (generated layout script;\n"
       "# safe to edit by hand). context_type diplomatic_action: ROOT is the sender,\n"
       "# THIS the receiver. Send GUIs edit the draft on ROOT; receive GUIs write\n"
       "# the receiver's choice (pww_dr_counter, pww_dr_move, pww_dr_settle) on THIS.\n"
       "# No randomness here; all values are computed in effects.\n"
       "#\n"
       "# KNOWN FALSE POSITIVE: the v1.20 parser logs 'Unexpected token: context_type'\n"
       "# once per block for context_type = diplomatic_action. The value is still the\n"
       "# entry point send_scripted_gui / receive_scripted_gui need: maintained 1.20\n"
       "# mods (Millennium Dawn's peace deal builder, workshop 2777392649) document\n"
       "# the same line and warn that player_context breaks the action. Like them,\n"
       "# these blocks carry no top-level 'visible'.\n",
       "scripted_gui = {\n"]
for g, w in windows.items():
    out.append(f"\t{g} = {{\n\t\tcontext_type = diplomatic_action\n\t\twindow_name = \"{w}\"\n"
               f"\t\tdirty = pww_diplo_dirty\n")
    if effects.get(g):
        out.append("\t\teffects = {\n" + "".join(effects[g]) + "\t\t}\n")
    if triggers.get(g):
        out.append("\t\ttriggers = {\n" + "".join(triggers[g]) + "\t\t}\n")
    if talks.PROPS.get(g):
        out.append("\t\tproperties = {\n" + "".join(talks.PROPS[g]) + "\t\t}\n")
    out.append("\t\tai_enabled = { always = no }\n\t}\n")
out.append("}\n")
with open(SG_OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("".join(out))

# ----------------------------------------------------------- scripted loc
sl = ["# Power Without War: diplomacy lane scripted localisation (generated).\n"
      "# Send GUIs read the draft on ROOT (the sender). Receive GUIs read the\n"
      "# pww_dr_* mirror, which is written on both the sender and the receiver\n"
      "# so either scope resolves it.\n"]


def dt(name, cases, default=None):
    s_ = f"defined_text = {{\n\tname = {name}\n"
    for trig, key in cases:
        s_ += f"\ttext = {{\n\t\ttrigger = {{ {trig} }}\n\t\tlocalization_key = {key}\n\t}}\n"
    if default:
        s_ += f"\ttext = {{\n\t\tlocalization_key = {default}\n\t}}\n"
    sl.append(s_ + "}\n")


def enum(name, var, keys, default=None):
    dt(name, [(f"check_variable = {{ {var} = {i} }}", k) for i, k in enumerate(keys)], default)


RES = [f"pww_diplo_v_res_{i}" for i in range(7)]
AMT = [f"pww_diplo_v_amt_{i}" for i in range(4)]
DUR = [f"pww_diplo_v_dur_{i}" for i in range(5)]
PAY = [f"pww_diplo_v_pay_{i}" for i in range(5)]
PRICE = [f"pww_diplo_v_price_{i}" for i in range(3)]
SWEET = [f"pww_diplo_v_sweet_{i}" for i in range(4)]
FIG = ["pww_diplo_v_none", "pww_figleaf_token_purchase", "pww_figleaf_joint_commission",
       "pww_figleaf_sovereignty_note", "pww_figleaf_timed_reversion", "pww_figleaf_clearing_cover",
       "pww_figleaf_neutral_transit"]
BAND = [f"pww_core_band_{i}" for i in range(5)]

# send offer (ROOT)
dt("pww_diplo_sl_o_title", [("ROOT = { check_variable = { pww_do_act = 1 } }", "pww_diplo_gui_lease_title")],
   "pww_diplo_gui_offer_title")
dt("pww_diplo_sl_o_round", [("ROOT = { check_variable = { pww_dd_closed = 1 } }", "pww_diplo_v_round_closed")]
   + [(f"ROOT = {{ check_variable = {{ pww_dd_round = {i} }} }}", f"pww_diplo_v_round_{i}") for i in range(4)],
   "pww_diplo_v_round_3")
dt("pww_diplo_sl_o_deal", [("ROOT = { check_variable = { pww_do_act = 1 } }", "pww_diplo_v_lease"),
                           ("ROOT = { check_variable = { pww_do_dir = 1 } }", "pww_diplo_v_dir_1")], "pww_diplo_v_dir_0")
enum("pww_diplo_sl_o_res", "ROOT.pww_do_res", RES)
dt("pww_diplo_sl_o_l3", [("ROOT = { check_variable = { pww_do_act = 1 } }", "pww_diplo_lbl_district")], "pww_diplo_lbl_qty")
dt("pww_diplo_sl_o_v3", [("ROOT = { check_variable = { pww_do_act = 1 } has_variable = pww_do_state_s }", "pww_diplo_v_state"),
                         ("ROOT = { check_variable = { pww_do_act = 1 } }", "pww_diplo_v_none")]
   + [(f"ROOT = {{ check_variable = {{ pww_do_amt = {i} }} }}", AMT[i]) for i in range(4)])
enum("pww_diplo_sl_o_dur", "ROOT.pww_do_dur", DUR)
enum("pww_diplo_sl_o_pay", "ROOT.pww_do_pay", PAY)
enum("pww_diplo_sl_o_price", "ROOT.pww_do_price", PRICE)
enum("pww_diplo_sl_o_sweet", "ROOT.pww_do_sweet", SWEET)
enum("pww_diplo_sl_o_fig", "ROOT.pww_do_fig", FIG)
dt("pww_diplo_sl_o_bands", [], "pww_diplo_gui_bands")
enum("pww_diplo_sl_o_give", "ROOT.pww_do_band_give", BAND)
enum("pww_diplo_sl_o_get", "ROOT.pww_do_band_get", BAND)
dt("pww_diplo_sl_o_invalid", [(f"ROOT = {{ check_variable = {{ pww_do_valid = {i} }} }}", f"pww_diplo_invalid_{i}")
                              for i in range(1, 7)], "pww_diplo_v_empty")
dt("pww_diplo_sl_o_rl", [(f"ROOT = {{ check_variable = {{ pww_dd_rl = {i} }} }}", k) for i, k in enumerate(
    ["pww_redline_no_lease", "pww_redline_no_permanent", "pww_redline_no_exclusive", "pww_redline_no_political",
     "pww_redline_no_public", "pww_redline_no_full_output", "pww_redline_no_alliance_breach",
     "pww_redline_no_credit_only"])], "pww_diplo_v_empty")
dt("pww_diplo_sl_o_want", [(f"ROOT = {{ check_variable = {{ pww_dd_want = {i} }} }}", k) for i, k in enumerate(
    ["pww_want_clearing_arms", "pww_want_cic_flow", "pww_want_coal_supply", "pww_want_equipment_tranche",
     "pww_want_tech_license", "pww_want_timed_reversion", "pww_want_fig_leaf", "pww_want_split_award",
     "pww_want_patron_cover"])], "pww_diplo_v_empty")
LINES = {}
for i in range(1, 8):
    LINES[10 + i] = f"pww_envoy_patience_low_{i}"
for i in range(1, 6):
    LINES[20 + i] = f"pww_envoy_patience_high_{i}"
for i in range(1, 8):
    LINES[30 + i] = f"pww_envoy_redline_{i}"
# Trade talks wants (pww_diplo_bundle.txt): 0 arms, 1 civilian factories,
# 2 coal, 3 transport, 4 licence, 5 six-month trial, 6 a resource they lack,
# 7 modest share, 8 political power.
for i, k in enumerate(["pww_envoy_want_arms", "pww_envoy_want_cic", "pww_envoy_want_coal", "pww_envoy_want_transport",
                       "pww_envoy_want_tech", "pww_envoy_want_trial", "pww_envoy_want_lack", "pww_envoy_want_modest",
                       "pww_envoy_want_goodwill"]):
    LINES[40 + i] = k
for i in range(1, 7):
    LINES[100 + i] = f"pww_envoy_price_low_{i}"
for i in range(1, 7):
    LINES[50 + i] = f"pww_envoy_rel_doubt_{i}"
for i in range(1, 6):
    LINES[60 + i] = f"pww_envoy_cred_doubt_{i}"
for i in range(1, 7):
    LINES[70 + i] = f"pww_envoy_rival_{i}"
for i in range(1, 7):
    LINES[80 + i] = f"pww_envoy_stall_{i}"
for i in range(1, 4):
    LINES[110 + i] = f"pww_envoy_trust_lock_{i}"
LINES[121] = "pww_diplo_line_cartel_price"
LINES[122] = "pww_diplo_line_cartel_quota"
LINES.update({90: "pww_diplo_line_signed", 91: "pww_diplo_line_failed", 92: "pww_diplo_line_closed",
              93: "pww_diplo_line_auction", 94: "pww_diplo_line_opening", 95: "pww_diplo_line_expired"})
dt("pww_diplo_sl_o_line", [(f"ROOT = {{ check_variable = {{ pww_dd_line = {c} }} }}", k) for c, k in sorted(LINES.items())],
   "pww_diplo_v_empty")

# send demand (ROOT)
dt("pww_diplo_sl_dm_title", [("ROOT = { check_variable = { pww_dm_channel = 1 } }", "pww_diplo_gui_demand_public_title")],
   "pww_diplo_gui_demand_quiet_title")
enum("pww_diplo_sl_dm_type", "ROOT.pww_dm_type", ["pww_diplo_v_dtype_0", "pww_diplo_v_dtype_1"])
enum("pww_diplo_sl_dm_res", "ROOT.pww_dm_res", RES)
dt("pww_diplo_sl_dm_l3", [("ROOT = { check_variable = { pww_dm_type = 1 } }", "pww_diplo_lbl_district")], "pww_diplo_lbl_qty")
dt("pww_diplo_sl_dm_v3", [("ROOT = { check_variable = { pww_dm_type = 1 } has_variable = pww_dm_state_s }", "pww_diplo_v_dm_state"),
                          ("ROOT = { check_variable = { pww_dm_type = 1 } }", "pww_diplo_v_none")]
   + [(f"ROOT = {{ check_variable = {{ pww_dm_amt = {i} }} }}", AMT[i]) for i in range(3)])
dt("pww_diplo_sl_dm_dur", [(f"ROOT = {{ check_variable = {{ pww_dm_dur = {i} }} }}", DUR[i]) for i in range(1, 4)])
enum("pww_diplo_sl_dm_fig", "ROOT.pww_dm_fig", FIG[:5])
dt("pww_diplo_sl_dm_status", [(f"ROOT = {{ check_variable = {{ pww_dm_live > -1 }} check_variable = {{ pww_dm_tstate = {i} }} }}",
                               f"pww_diplo_v_standing_{i}") for i in range(5)], "pww_diplo_v_no_standing")
dt("pww_diplo_sl_dm_invalid", [(f"ROOT = {{ check_variable = {{ pww_dm_valid = {i} }} }}", f"pww_diplo_invalid_{i}")
                               for i in (21, 22, 23)], "pww_diplo_v_empty")
dt("pww_diplo_sl_dm_desc", [("ROOT = { check_variable = { pww_dm_channel = 1 } }", "pww_act_demand_public_desc")],
   "pww_act_demand_quiet_desc")

# send pledge (ROOT)
dt("pww_diplo_sl_dp_vs", [("ROOT = { check_variable = { pww_dp_claimant > 0 } }", "pww_diplo_v_vs_named")],
   "pww_diplo_v_vs_any")
enum("pww_diplo_sl_dp_res", "ROOT.pww_dp_res", RES)
enum("pww_diplo_sl_dp_amt", "ROOT.pww_dp_amt", AMT)
dt("pww_diplo_sl_dp_pay", [("ROOT = { check_variable = { pww_dp_pay = 3 } }", "pww_diplo_v_pay_3")], "pww_diplo_v_pay_0")
dt("pww_diplo_sl_dp_dur", [(f"ROOT = {{ check_variable = {{ pww_dp_dur = {i} }} }}", DUR[i]) for i in range(1, 5)])
enum("pww_diplo_sl_dp_band", "ROOT.pww_dp_band", BAND)
dt("pww_diplo_sl_dp_invalid", [(f"ROOT = {{ check_variable = {{ pww_dp_valid = {i} }} }}", f"pww_diplo_invalid_{i}")
                               for i in (11, 12, 13)], "pww_diplo_v_empty")

# send embargo (ROOT)
dt("pww_diplo_sl_de_target", [("ROOT = { has_variable = pww_de_target }", "pww_diplo_v_de_target")], "pww_diplo_v_none")
dt("pww_diplo_sl_de_invalid", [(f"ROOT = {{ check_variable = {{ pww_de_valid = {i} }} }}", f"pww_diplo_invalid_{i}")
                               for i in (31, 32)], "pww_diplo_v_empty")

# send bid (ROOT)
dt("pww_diplo_sl_db_lot", [("ROOT = { check_variable = { pww_db_lot < 0 } }", "pww_diplo_v_none")]
   + [(f"ROOT = {{ check_variable = {{ pww_db_kind = {i} }} }}", f"pww_diplo_lot_kind_{i}") for i in range(4)])
dt("pww_diplo_sl_db_lotdesc", [("ROOT = { check_variable = { pww_db_lot < 0 } }", "pww_diplo_v_empty")]
   + [(f"ROOT = {{ check_variable = {{ pww_db_kind = {i} }} }}", f"pww_diplo_lot_desc_{i}") for i in range(4)])
enum("pww_diplo_sl_db_pay", "ROOT.pww_db_pay", PAY)
enum("pww_diplo_sl_db_price", "ROOT.pww_db_price", PRICE)
enum("pww_diplo_sl_db_sweet", "ROOT.pww_db_sweet", SWEET)
enum("pww_diplo_sl_db_fig", "ROOT.pww_db_fig", FIG)
dt("pww_diplo_sl_db_invalid", [(f"ROOT = {{ check_variable = {{ pww_db_valid = {i} }} }}", f"pww_diplo_invalid_{i}")
                               for i in (1, 3, 4, 6, 41)], "pww_diplo_v_empty")
enum("pww_diplo_sl_db_res", "ROOT.pww_db_res", RES)
dt("pww_diplo_sl_db_term", [("ROOT = { check_variable = { pww_db_term < 200 } }", "pww_diplo_v_dur_1"),
                            ("ROOT = { check_variable = { pww_db_term < 400 } }", "pww_diplo_v_dur_2")], "pww_diplo_v_dur_3")

# receive offer (pww_dr_* mirror, unprefixed)
dt("pww_diplo_sl_r_title", [("check_variable = { pww_dr_act = 1 }", "pww_rcv_lease_title")], "pww_rcv_proposal_title")
dt("pww_diplo_sl_r_deal", [("check_variable = { pww_dr_act = 1 }", "pww_diplo_v_lease_rcv"),
                           ("check_variable = { pww_dr_dir = 1 }", "pww_diplo_v_rdir_1")], "pww_diplo_v_rdir_0")
enum("pww_diplo_sl_r_res", "pww_dr_res", RES)
dt("pww_diplo_sl_r_l3", [("check_variable = { pww_dr_act = 1 }", "pww_diplo_lbl_district")], "pww_diplo_lbl_qty")
dt("pww_diplo_sl_r_v3", [("check_variable = { pww_dr_act = 1 }", "pww_diplo_v_rstate")]
   + [(f"check_variable = {{ pww_dr_amt = {i} }}", AMT[i]) for i in range(4)])
enum("pww_diplo_sl_r_dur", "pww_dr_dur", DUR)
enum("pww_diplo_sl_r_pay", "pww_dr_pay", PAY)
enum("pww_diplo_sl_r_price", "pww_dr_price", PRICE)
enum("pww_diplo_sl_r_sweet", "pww_dr_sweet", SWEET)
enum("pww_diplo_sl_r_fig", "pww_dr_fig", FIG)
dt("pww_diplo_sl_r_bands", [], "pww_diplo_gui_rbands")
enum("pww_diplo_sl_r_give", "pww_dr_give", BAND)
enum("pww_diplo_sl_r_get", "pww_dr_get", BAND)
dt("pww_diplo_sl_r_line", [("check_variable = { pww_dr_round = 0 }", "pww_diplo_v_empty")]
   + [(f"check_variable = {{ pww_dr_line = {c} }}", k) for c, k in sorted(LINES.items()) if c in (21, 22, 23, 24, 25, 86)],
   "pww_diplo_v_empty")

# receive demand
dt("pww_diplo_sl_rd_title", [("check_variable = { pww_dr_channel = 1 }", "pww_rcv_demand_public_title")],
   "pww_rcv_demand_quiet_title")
dt("pww_diplo_sl_rd_terms", [("check_variable = { pww_dr_dtype = 1 }", "pww_diplo_rcv_terms_lease")],
   "pww_diplo_rcv_terms_share")
enum("pww_diplo_sl_rd_res", "pww_dr_res", RES)
enum("pww_diplo_sl_rd_amt", "pww_dr_amt", AMT)
dt("pww_diplo_sl_rd_dur", [(f"check_variable = {{ pww_dr_dur = {i} }}", DUR[i]) for i in range(1, 4)])
dt("pww_diplo_sl_rd_fig", [("check_variable = { pww_dr_fig > 0 }", "pww_diplo_rcv_with_fig")], "pww_diplo_v_empty")
enum("pww_diplo_sl_rd_figname", "pww_dr_fig", FIG[:5])

if LAYOUT_ONLY:
    print("layout only: scripted localisation not written")
    sys.exit(0)
with open(SL_OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("".join(sl) + "# Trade talks (tools/pww_diplo_gen_talks.py)\n" + "".join(talks.SL))
print("ok", len(gui), "windows")
