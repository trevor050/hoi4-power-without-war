"""UI lane generator: python tools/pww_ui_gen.py

Writes the UI lane's generated files (all prefixed pww_ui_):
  mod/interface/pww_ui.gui                          Trade Desk, Dossier, alert strip
  mod/interface/pww_ui_sprites.gfx                  sprites (vanilla textures only)
  mod/common/scripted_guis/pww_ui_guis.txt          scripted GUI blocks
  mod/common/scripted_localisation/pww_ui_scripted_loc.txt
  mod/common/scripted_effects/pww_ui_slots.txt      per-slot store/clear/copy helpers
  mod/localisation/english/pww_ui_l_english.yml     UTF-8 with BOM

The data the GUIs read is built by mod/common/scripted_effects/pww_ui_effects.txt
(hand written). HoI4 GUI has no layout engine, so every position is computed
here from a few grid constants. Rerun after editing; the outputs are plain files.
"""
import os

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mod")
P_GUI = os.path.join(ROOT, "interface", "pww_ui.gui")
P_GFX = os.path.join(ROOT, "interface", "pww_ui_sprites.gfx")
P_SG = os.path.join(ROOT, "common", "scripted_guis", "pww_ui_guis.txt")
P_SL = os.path.join(ROOT, "common", "scripted_localisation", "pww_ui_scripted_loc.txt")
P_FX = os.path.join(ROOT, "common", "scripted_effects", "pww_ui_slots.txt")
P_LOC = os.path.join(ROOT, "localisation", "english", "pww_ui_l_english.yml")

RES = ["oil", "aluminium", "rubber", "tungsten", "steel", "chromium", "coal"]
RES_NAME = ["Oil", "Aluminium", "Rubber", "Tungsten", "Steel", "Chromium", "Coal"]
NSIT = 4          # situation slots (noise cap)
NAG = 6           # ledger rows per page
NK = 3            # dossier agreement rows
F16, F18, F24 = "hoi_16mbs", "hoi_18mbs", "hoi_24header"

loc = {}          # key -> text
sl = []           # scripted loc blocks


def L(key, text):
    assert key not in loc, key
    assert "—" not in text, key
    loc[key] = text


# --------------------------------------------------------------------------- gui helpers
def tb(name, x, y, text, w, h=18, font=F16, fmt="left", tip=None, transparent=True):
    s = (f'\t\tinstantTextBoxType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
         f'\t\t\tfont = "{font}"\n\t\t\ttext = "{text}"\n\t\t\tmaxWidth = {w}\n\t\t\tmaxHeight = {h}\n'
         f'\t\t\tformat = {fmt}\n\t\t\tfixedsize = yes\n')
    if tip:
        s += f'\t\t\tpdx_tooltip = "{tip}"\n'
    elif transparent:
        s += "\t\t\talwaystransparent = yes\n"
    return s + "\t\t}\n"


def btn(name, x, y, sprite, text=None, font=F16, size=None, tip=None, transparent=False, click=None, scale=None):
    s = f'\t\tbuttonType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
    if size:
        s += f"\t\t\tsize = {{ x = {size[0]} y = {size[1]} }}\n"
    s += f'\t\t\tquadTextureSprite = "{sprite}"\n'
    if text is not None:
        s += f'\t\t\tbuttonText = "{text}"\n\t\t\tbuttonFont = "{font}"\n'
    if tip:
        s += f'\t\t\tpdx_tooltip = "{tip}"\n'
    if transparent:
        s += "\t\t\talwaystransparent = yes\n"
    if scale:
        s += f"\t\t\tscale = {scale}\n"
    if click:
        s += f"\t\t\tclicksound = {click}\n"
    return s + "\t\t}\n"


def icon(name, x, y, sprite, frame=None, scale=None):
    s = f'\t\ticonType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tspriteType = "{sprite}"\n'
    if frame:
        s += f"\t\t\tframe = {frame}\n"
    if scale:
        s += f"\t\t\tscale = {scale}\n"
    return s + "\t\t\talwaystransparent = yes\n\t\t}\n"


def window(name, x, y, w, h, body, bg=None, orientation=None):
    s = (f'\tcontainerWindowType = {{\n\t\tname = "{name}"\n\t\tposition = {{ x = {x} y = {y} }}\n'
         f'\t\tsize = {{ width = {w} height = {h} }}\n\t\tclipping = no\n')
    if orientation:
        s += f'\t\torientation = {orientation}\n'
    if bg:
        s += f'\t\tbackground = {{\n\t\t\tname = "background"\n\t\t\tquadTextureSprite = "{bg}"\n\t\t}}\n'
    return s + "\n" + body + "\t}\n\n"


def dt(name, cases, default=None):
    """defined_text: cases = [(trigger, key)]."""
    s = f"defined_text = {{\n\tname = {name}\n"
    for trig, key in cases:
        s += f"\ttext = {{ trigger = {{ {trig} }} localization_key = {key} }}\n"
    if default:
        s += f"\ttext = {{ localization_key = {default} }}\n"
    sl.append(s + "}\n")


def cv(var, op, val):
    return f"check_variable = {{ {var} {op} {val} }}"


# --------------------------------------------------------------------------- shared loc
L("pww_ui_blank", "")
for i, n in enumerate(RES_NAME):
    L(f"pww_mkt_res_{RES[i]}", n)
L("pww_seat_lc_0", "claimant")
L("pww_seat_lc_1", "holder")
L("pww_seat_lc_2", "patron")
STATE_KEYS = ["pww_state_defiant", "pww_state_strained", "pww_state_wavering", "pww_state_cornered",
              "pww_state_ready_to_fold"]


def res_dt(name, var):
    dt(name, [(cv(var, "=", i), f"pww_mkt_res_{r}") for i, r in enumerate(RES)], "pww_ui_blank")


def state_dt(name, var):
    dt(name, [(cv(var, "=", i), k) for i, k in enumerate(STATE_KEYS)], "pww_ui_blank")


# --------------------------------------------------------------------------- Trade Desk
DW, DH = 500, 586
X0 = 20                       # left content edge
XR = DW - 20                  # right content edge
CW = XR - X0                  # content width
SIT_Y, SIT_ROW = 72, 40
LED_HDR = SIT_Y + NSIT * SIT_ROW + 14
LED_Y, LED_ROW = LED_HDR + 26, 22
LED_CP, LED_ST = 168, 70      # counterparty and status columns
MKT_HDR = LED_Y + NAG * LED_ROW + 14
MKT_Y, MKT_ROW = MKT_HDR + 26, 18
assert MKT_Y + 7 * MKT_ROW + 12 <= DH, MKT_Y + 7 * MKT_ROW

L("pww_desk_title", "Trade Desk")
L("pww_desk_sec_situations", "Active Situations")
L("pww_desk_empty_situations", "§gNo contested Situations in your seats. Watch the market report for emerging shortages.§!")
L("pww_desk_sec_ledger", "Agreements Ledger")
L("pww_desk_empty_ledger", "§gNo active agreements. Open talks through any country's diplomacy panel.§!")
L("pww_desk_sec_market", "Monthly Market Report")
L("pww_desk_empty_market", "§gFirst monthly report posts at the turn of the month.§!")
L("pww_ui_desk_btn", "Trade Desk")
L("pww_ui_desk_btn_tt", "Open the Trade Desk: live Situations in your seats, your agreements ledger and the monthly market report.")
L("pww_ui_desk_close_tt", "Close the Trade Desk.")
L("pww_ui_mkt_dated", "§g[?global.pww_ui_mkt_date.GetDateStringNoHourLong]§!")
L("pww_ui_page", "[?pww_ui_page_n]/[?pww_ui_npages]")
L("pww_ui_page_prev_tt", "Previous page")
L("pww_ui_page_next_tt", "Next page")


def desk_body():
    b = tb("pww_ui_desk_title", X0, 10, "pww_desk_title", 300, h=28, font=F24)
    b += btn("pww_ui_desk_close", DW - 37, 9, "GFX_closebutton", tip="pww_ui_desk_close_tt", click="click_close")
    # situations
    b += tb("pww_ui_desk_sit_hdr", X0, 48, "pww_desk_sec_situations", CW, h=20, font=F18)
    b += tb("pww_ui_desk_sit_empty", X0, SIT_Y + 2, "pww_desk_empty_situations", CW, h=36)
    for k in range(NSIT):
        y = SIT_Y + k * SIT_ROW
        b += btn(f"pww_ui_ds{k}_hl", X0 - 19, y + 2, "GFX_production_line_arrow_right", transparent=True, scale="0.55")
        b += tb(f"pww_ui_ds{k}_l1", X0, y + 1, f"[pww_ui_sl_s{k}_head]", CW - 150, tip=f"pww_ui_s{k}_tt")
        b += tb(f"pww_ui_ds{k}_date", XR - 150, y + 1, f"pww_ui_s{k}_date", 150, fmt="right", tip="pww_ui_date_tt")
        b += tb(f"pww_ui_ds{k}_l2", X0, y + 19, f"pww_ui_s{k}_line2", CW, tip=f"pww_ui_s{k}_tt")
    # ledger
    b += icon("pww_ui_desk_div1", X0 - 6, LED_HDR - 10, "GFX_pww_ui_divider", scale=f"{(CW + 12) / 514:.3f}")
    b += tb("pww_ui_desk_led_hdr", X0, LED_HDR, "pww_desk_sec_ledger", 300, h=20, font=F18)
    b += btn("pww_ui_desk_pg_prev", XR - 74, LED_HDR + 2, "GFX_pww_diplo_prev", tip="pww_ui_page_prev_tt")
    b += tb("pww_ui_desk_pg", XR - 56, LED_HDR + 1, "pww_ui_page", 38, fmt="centre")
    b += btn("pww_ui_desk_pg_next", XR - 16, LED_HDR + 2, "GFX_pww_diplo_next", tip="pww_ui_page_next_tt")
    b += tb("pww_ui_desk_led_empty", X0, LED_Y + 2, "pww_desk_empty_ledger", CW, h=36)
    for k in range(NAG):
        y = LED_Y + k * LED_ROW
        b += tb(f"pww_ui_dl{k}_cp", X0, y, f"pww_ui_l{k}_cp", LED_CP, tip=f"pww_ui_l{k}_tt")
        b += tb(f"pww_ui_dl{k}_terms", X0 + LED_CP + 6, y, f"[pww_ui_sl_l{k}_terms]", CW - LED_CP - 6 - LED_ST - 4,
                tip=f"pww_ui_l{k}_tt")
        b += tb(f"pww_ui_dl{k}_st", XR - LED_ST, y, f"[pww_ui_sl_l{k}_status]", LED_ST, fmt="right", tip=f"pww_ui_l{k}_tt")
    # market report
    b += icon("pww_ui_desk_div2", X0 - 6, MKT_HDR - 10, "GFX_pww_ui_divider", scale=f"{(CW + 12) / 514:.3f}")
    b += tb("pww_ui_desk_mkt_hdr", X0, MKT_HDR, "pww_desk_sec_market", 300, h=20, font=F18)
    b += tb("pww_ui_desk_mkt_date", XR - 170, MKT_HDR + 2, "pww_ui_mkt_dated", 170, fmt="right")
    b += tb("pww_ui_desk_mkt_empty", X0, MKT_Y + 2, "pww_desk_empty_market", CW, h=36)
    for i, r in enumerate(RES):
        y = MKT_Y + i * MKT_ROW
        b += icon(f"pww_ui_dm_{r}_icon", X0, y - 1, "GFX_resources_strip", frame=i + 1, scale="0.6")
        b += tb(f"pww_ui_dm_{r}", X0 + 22, y, f"[pww_ui_sl_mkt_{r}]", CW - 22)
    return b


# situation slot loc
L("pww_ui_date_tt", "Decision date. Each seat must make its move before then.")
for k in range(NSIT):
    v = f"pww_ui_s{k}"
    dt(f"pww_ui_sl_s{k}_title", [(f"{cv(v + '_tmpl', '>', 0)}", "pww_sit_wolfram_title")],
       f"pww_ui_s{k}_title_generic")
    L(f"pww_ui_s{k}_title_generic", f"[pww_ui_sl_s{k}_res] dispute")
    res_dt(f"pww_ui_sl_s{k}_res", f"{v}_res")
    dt(f"pww_ui_sl_s{k}_seat", [(cv(f"{v}_seat", "=", i), f"pww_seat_{n}") for i, n in
                               enumerate(["claimant", "holder", "patron"])], "pww_ui_blank")
    state_dt(f"pww_ui_sl_s{k}_tstate", f"{v}_tstate")
    dt(f"pww_ui_sl_s{k}_dev", [(cv(f"{v}_dev", "=", d), f"pww_sit_dev_{d}") for d in range(1, 16)], "pww_ui_blank")
    # head: title and our seat; the focus slot is highlighted by the row frame
    dt(f"pww_ui_sl_s{k}_head", [], f"pww_ui_s{k}_head")
    L(f"pww_ui_s{k}_head", f"§H[pww_ui_sl_s{k}_title]§!  [?{v}_ho.GetAdjective] [pww_ui_sl_s{k}_res_lc]")
    L(f"pww_ui_s{k}_date", f"[?{v}_date.GetDateStringNoHourLong]")
    # line 2: stake and the holder's standing, then the latest development
    L(f"pww_ui_s{k}_line2", f"§g[pww_ui_sl_s{k}_seat]:§! [pww_ui_sl_s{k}_tstate_short] §g[pww_ui_sl_s{k}_dev]§!")
    dt(f"pww_ui_sl_s{k}_res_lc", [(cv(f"{v}_res", "=", i), f"pww_ui_res_lc_{r}") for i, r in enumerate(RES)], "pww_ui_blank")
    dt(f"pww_ui_sl_s{k}_tstate_short", [(f"{cv(v + '_tstate', '=', i)}", f"pww_ui_s{k}_ts_{i}") for i in range(5)],
       "pww_ui_blank")
    for i, key in enumerate(STATE_KEYS):
        L(f"pww_ui_s{k}_ts_{i}", f"[?{v}_ho.GetName] is ${key}$.")
    L(f"pww_ui_s{k}_tt", f"§H[pww_ui_sl_s{k}_title]§!\\nOur seat: [pww_ui_sl_s{k}_seat]\\n"
                         f"Claimant: [?{v}_cl.GetNameWithFlag]\\nHolder: [?{v}_ho.GetNameWithFlag]\\n"
                         f"[pww_ui_sl_s{k}_patron]\\nDecision date: [?{v}_date.GetDateStringNoHourLong]")
    dt(f"pww_ui_sl_s{k}_patron", [(cv(f"{v}_hasp", "=", 1), f"pww_ui_s{k}_patron")], "pww_ui_no_patron")
    L(f"pww_ui_s{k}_patron", f"Patron: [?{v}_pa.GetNameWithFlag]")
L("pww_ui_no_patron", "Patron: none")
for i, r in enumerate(RES):
    L(f"pww_ui_res_lc_{r}", RES_NAME[i].lower())

# ledger slot loc
STATUS = {1: "pww_ag_status_active", 2: "pww_ag_status_suspended", 7: "pww_ag_status_reserved"}
L("pww_ag_status_draft", "Draft")
L("pww_ag_status_active", "§GActive§!")
L("pww_ag_status_suspended", "§YSuspended§!")
L("pww_ag_status_completed", "Completed")
L("pww_ag_status_terminated", "Terminated")
L("pww_ag_status_defaulted", "§RDefaulted§!")
L("pww_ag_status_nationalized", "§RNationalized§!")
L("pww_ag_status_reserved", "§HReserved§!")
L("pww_ag_vehicle_supply", "Supply Agreement")
L("pww_ag_vehicle_lease", "Named-State Lease")
L("pww_ag_type_noncommittal", "Non-committal")
L("pww_ag_type_committal", "Committal")
L("pww_ui_ag_tt_status_1", "Deliveries and payments are flowing on schedule.")
L("pww_ui_ag_tt_status_2", "Flows are paused by interdiction, quarantine, or a provisional truce. Resolve it before the window closes.")
L("pww_ui_ag_tt_status_7", "Conditional pledge. Activates automatically if its trigger fires.")
for k in range(NAG):
    v = f"pww_ui_l{k}"
    L(f"pww_ui_l{k}_cp", f"[?{v}_cp.GetNameWithFlag]")
    res_dt(f"pww_ui_sl_l{k}_res", f"{v}_res")
    dt(f"pww_ui_sl_l{k}_res_lc", [(cv(f"{v}_res", "=", i), f"pww_ui_res_lc_{r}") for i, r in enumerate(RES)],
       f"pww_ui_l{k}_allres")
    L(f"pww_ui_l{k}_allres", "all output")
    dt(f"pww_ui_sl_l{k}_status", [(cv(f"{v}_st", "=", s), key) for s, key in STATUS.items()], "pww_ui_blank")
    # terms: lease (kind 1/2) by side, else supply by side; then payment
    dt(f"pww_ui_sl_l{k}_terms", [
        (f"{cv(v + '_kind', '>', 0)} {cv(v + '_side', '=', 1)}", f"pww_ui_l{k}_t_lease_in"),
        (f"{cv(v + '_kind', '>', 0)}", f"pww_ui_l{k}_t_lease_out"),
        (cv(v + "_side", "=", 1), f"pww_ui_l{k}_t_buy"),
    ], f"pww_ui_l{k}_t_sell")
    L(f"pww_ui_l{k}_t_lease_in", f"We lease [?{v}_state.GetName][pww_ui_sl_l{k}_pay]")
    L(f"pww_ui_l{k}_t_lease_out", f"They lease [?{v}_state.GetName][pww_ui_sl_l{k}_pay]")
    L(f"pww_ui_l{k}_t_buy", f"We buy [?{v}_amt|0] [pww_ui_sl_l{k}_res_lc][pww_ui_sl_l{k}_pay]")
    L(f"pww_ui_l{k}_t_sell", f"We sell [?{v}_amt|0] [pww_ui_sl_l{k}_res_lc][pww_ui_sl_l{k}_pay]")
    # Usual direction: whoever receives the goods (or the lease) pays, so the
    # line reads "We buy 8 steel for 2 factories". The reverse reads as a rider.
    usual = (f"OR = {{ AND = {{ {cv(v + '_side', '=', 1)} {cv(v + '_wepay', '=', 1)} }} "
             f"AND = {{ {cv(v + '_side', '=', 0)} {cv(v + '_wepay', '=', 0)} }} }}")
    dt(f"pww_ui_sl_l{k}_pay", [
        (f"{cv(v + '_pay', '=', 1)} {usual}", f"pww_ui_l{k}_pay_civ"),
        (f"{cv(v + '_pay', '=', 1)} {cv(v + '_wepay', '=', 1)}", f"pww_ui_l{k}_pay_civ_we"),
        (cv(v + "_pay", "=", 1), f"pww_ui_l{k}_pay_civ_they"),
        (f"{cv(v + '_pay', '=', 2)} {usual}", "pww_ui_pay_pp"),
        (f"{cv(v + '_pay', '=', 2)} {cv(v + '_wepay', '=', 1)}", "pww_ui_pay_pp_we"),
        (cv(v + "_pay", "=", 2), "pww_ui_pay_pp_they"),
    ], "pww_ui_blank")
    L(f"pww_ui_l{k}_pay_civ", f" for [?{v}_civ|0] [pww_ui_sl_l{k}_fac]")
    L(f"pww_ui_l{k}_pay_civ_we", f", and we pay [?{v}_civ|0] [pww_ui_sl_l{k}_fac]")
    L(f"pww_ui_l{k}_pay_civ_they", f", and they pay [?{v}_civ|0] [pww_ui_sl_l{k}_fac]")
    dt(f"pww_ui_sl_l{k}_fac", [(cv(v + "_civ", "=", 1), "pww_ui_factory")], "pww_ui_factories")
    dt(f"pww_ui_sl_l{k}_end", [(cv(v + "_open", "=", 1), "pww_ui_open_ended")], f"pww_ui_l{k}_until")
    L(f"pww_ui_l{k}_until", f"Runs until [?{v}_end.GetDateStringNoHourLong].")
    dt(f"pww_ui_sl_l{k}_vehicle", [(cv(v + "_kind", ">", 0), "pww_ag_vehicle_lease")], "pww_ag_vehicle_supply")
    dt(f"pww_ui_sl_l{k}_type", [(cv(v + "_com", "=", 1), "pww_ag_type_committal")], "pww_ag_type_noncommittal")
    dt(f"pww_ui_sl_l{k}_sttt", [(cv(v + "_st", "=", s), f"pww_ui_ag_tt_status_{s}") for s in STATUS], "pww_ui_blank")
    L(f"pww_ui_l{k}_tt", f"§H[pww_ui_sl_l{k}_vehicle]§!, [pww_ui_sl_l{k}_type] with [?{v}_cp.GetName]\\n"
                         f"[pww_ui_sl_l{k}_terms].\\n[pww_ui_sl_l{k}_end]\\n\\n[pww_ui_sl_l{k}_status]: [pww_ui_sl_l{k}_sttt]")
L("pww_ui_factory", "factory")
L("pww_ui_factories", "factories")
L("pww_ui_pay_pp", " for political power")
L("pww_ui_pay_pp_we", ", and we pay political power")
L("pww_ui_pay_pp_they", ", and they pay political power")
L("pww_ui_open_ended", "Open-ended; either side may end it.")

# market report
BANDS = ["glut", "slack", "steady", "firm", "tight", "scarce", "frantic"]
BAND_TXT = ["glut", "slack", "steady", "firm", "§Ytight§!", "§Oscarce§!", "§Rfrantic§!"]
for i, b_ in enumerate(BANDS):
    L(f"pww_mkt_band_{b_}", BAND_TXT[i])
L("pww_mkt_cause_quiet_season", "quiet trading")
for i, r in enumerate(RES):
    g = f"global.pww_ui_mkt"
    dt(f"pww_ui_sl_mkt_band_{r}", [(cv(f"{g}_band_{r}", "=", j), f"pww_mkt_band_{b_}") for j, b_ in enumerate(BANDS)],
       "pww_ui_blank")
    dt(f"pww_ui_sl_mkt_c1_{r}", [(cv(f"{g}_c1_{r}", "=", 1), f"pww_ui_mkt_buyer_{r}"),
                                 (cv(f"{g}_c1_{r}", "=", 2), f"pww_ui_mkt_rivals_{r}"),
                                 (cv(f"{g}_c1_{r}", "=", 3), "pww_mkt_cause_quiet_season")], "pww_ui_blank")
    L(f"pww_ui_mkt_buyer_{r}", f"[?{g}_b1_{r}.GetAdjective] buying")
    L(f"pww_ui_mkt_rivals_{r}", f"[?{g}_b1_{r}.GetAdjective] and [?{g}_b2_{r}.GetAdjective] bidding")
    L(f"pww_ui_mkt_contested_{r}", f"[?{g}_ho_{r}.GetAdjective] output contested")
    dt(f"pww_ui_sl_mkt_{r}", [
        (f"{cv(g + '_c1_' + r, '>', 0)} {cv(g + '_c2_' + r, '=', 1)}", f"pww_ui_mkt_line2_{r}"),
        (cv(f"{g}_c1_{r}", ">", 0), f"pww_ui_mkt_line1_{r}"),
        (cv(f"{g}_c2_{r}", "=", 1), f"pww_ui_mkt_linec_{r}"),
    ], f"pww_ui_mkt_line0_{r}")
    L(f"pww_ui_mkt_line0_{r}", f"{RES_NAME[i]}: [pww_ui_sl_mkt_band_{r}].")
    L(f"pww_ui_mkt_line1_{r}", f"{RES_NAME[i]}: [pww_ui_sl_mkt_band_{r}], [pww_ui_sl_mkt_c1_{r}].")
    L(f"pww_ui_mkt_linec_{r}", f"{RES_NAME[i]}: [pww_ui_sl_mkt_band_{r}], $pww_ui_mkt_contested_{r}$.")
    L(f"pww_ui_mkt_line2_{r}", f"{RES_NAME[i]}: [pww_ui_sl_mkt_band_{r}], [pww_ui_sl_mkt_c1_{r}]; $pww_ui_mkt_contested_{r}$.")


# --------------------------------------------------------------------------- trade tab button
def desk_button_body():
    return btn("pww_ui_desk_open", 0, 0, "GFX_button_148x34", text="pww_ui_desk_btn", tip="pww_ui_desk_btn_tt",
               click="click_default")


# --------------------------------------------------------------------------- alert strip
AW, AROW = 400, 26
ALERT_KINDS = {
    0: "[pww_ui_sl_s{k}_title]: [?pww_ui_s{k}_ho.GetName] is [pww_ui_sl_s{k}_tstate]",
    1: "§R[pww_ui_sl_s{k}_title]: [?pww_ui_s{k}_ho.GetName] is Cornered§!",
    2: "§G[pww_ui_sl_s{k}_title]: [?pww_ui_s{k}_ho.GetName] ready to fold§!",
    3: "§Y[pww_ui_sl_s{k}_title]: [?pww_ui_s{k}_cl.GetName] demands an answer§!",
    4: "§H[pww_ui_sl_s{k}_title]: write lots for bidding§!",
    5: "[pww_ui_sl_s{k}_title]: [?pww_ui_s{k}_ho.GetName] under pressure",
    6: "§H[pww_ui_sl_s{k}_title]: underwriting [?pww_ui_s{k}_ho.GetName]§!",
    7: "§Y[pww_ui_sl_s{k}_title]: lease renewal due§!",
}
for k in range(NSIT):
    for kind, txt in ALERT_KINDS.items():
        L(f"pww_ui_al{k}_k{kind}", txt.replace("{k}", str(k)))
    dt(f"pww_ui_sl_al{k}", [(cv(f"pww_ui_s{k}_kind", "=", kind), f"pww_ui_al{k}_k{kind}") for kind in ALERT_KINDS],
       "pww_ui_blank")
    L(f"pww_ui_al{k}_tt", f"§H[pww_ui_sl_s{k}_title]§!, our seat: [pww_ui_sl_s{k}_seat]\\n[pww_ui_s{k}_line2]\\n"
                          f"Decision date: [?pww_ui_s{k}_date.GetDateStringNoHourLong]\\n\\n"
                          f"Click to open the Trade Desk on this Situation.")


def alert_body():
    b = ""
    for k in range(NSIT):
        y = k * AROW
        b += btn(f"pww_ui_al{k}_btn", 0, y, "GFX_pww_ui_alert_row", size=(AW, AROW - 2), tip=f"pww_ui_al{k}_tt",
                 click="click_default")
        b += tb(f"pww_ui_al{k}_txt", 10, y + 4, f"[pww_ui_sl_al{k}]", AW - 128)
        b += tb(f"pww_ui_al{k}_date", AW - 116, y + 4, f"pww_ui_s{k}_date", 106, fmt="right")
    return b


# --------------------------------------------------------------------------- dossier
OW, OH = 514, 240
OX, OY = 8, 110                      # in the diplomacy tab's coordinates
TOGGLE = (OX + OW - 106, OY + 6)     # dossier toggle: party box corner, dossier header when open
L("pww_ui_dos_btn", "[pww_ui_sl_dos_btn]")
L("pww_ui_dos_btn_plain", "Dossier")
L("pww_ui_dos_btn_hot", "§YDossier§!")
L("pww_ui_dos_btn_close", "Close")
L("pww_ui_dos_btn_tt", "Commercial dossier on [FROM.GetName]: shortages, import reliance, known agreements and leases, and the state of any demand or Situation between us.")
L("pww_dossier_title", "Commercial Dossier")
L("pww_dossier_sec_shortages", "Shortages")
L("pww_ui_dos_imports", "Import reliance: [pww_ui_sl_dos_imp]")
L("pww_ui_dos_nag", "[pww_ui_sl_dos_nag]")
L("pww_ui_dos_nag_0", "§gNo mod-tracked agreements on file.§!")
L("pww_ui_dos_nag_n", "Agreements and leases on file: [?pww_ui_nk_all|0]")
IMP = ["Self-sufficient", "Light", "Moderate", "§YHeavy§!", "§ODependent§!"]
for i, t in enumerate(IMP):
    L(f"pww_ui_imp_{i}", t)
L("pww_ui_imp_tt", "Share of their resource consumption met by imports and mod supply agreements, last month.")
SHORT = ["§gample§!", "tight", "§Yshort§!", "§Osevere§!", "§Rdesperate§!"]
for i, t in enumerate(SHORT):
    L(f"pww_ui_short_{i}", t)
L("pww_ui_short_tt", "How hard [FROM.GetName] is pressed for each resource, judged from deficits, fuel runway and idle mills. Bands only; the ministries guard the figures.")
dt("pww_ui_sl_dos_btn", [("ROOT = { has_country_flag = pww_ui_dos_open }", "pww_ui_dos_btn_close"),
                         (f"OR = {{ check_variable = {{ pww_ui_rd_viewer = ROOT }} check_variable = {{ pww_ui_pr_viewer = ROOT }} check_variable = {{ pww_ui_st_viewer = ROOT }} }}",
                          "pww_ui_dos_btn_hot")], "pww_ui_dos_btn_plain")
dt("pww_ui_sl_dos_imp", [(cv("pww_ui_imp_band", "=", i), f"pww_ui_imp_{i}") for i in range(5)], "pww_ui_imp_0")
dt("pww_ui_sl_dos_nag", [(cv("pww_ui_nk_all", ">", 0), "pww_ui_dos_nag_n")], "pww_ui_dos_nag_0")
for i, r in enumerate(RES):
    dt(f"pww_ui_sl_short_{r}", [(cv(f"pww_desp_{r}", ">", t), f"pww_ui_short_{j}") for j, t in
                                [(4, 79), (3, 59), (2, 39), (1, 19)]], "pww_ui_short_0")
# known agreement rows (target perspective: "they")
for k in range(NK):
    v = f"pww_ui_k{k}"
    dt(f"pww_ui_sl_k{k}_res_lc", [(cv(f"{v}_res", "=", i), f"pww_ui_res_lc_{r}") for i, r in enumerate(RES)],
       "pww_ui_blank")
    dt(f"pww_ui_sl_k{k}", [
        (f"{cv(v + '_kind', '>', 0)} {cv(v + '_side', '=', 1)}", f"pww_ui_k{k}_lease_in"),
        (cv(v + "_kind", ">", 0), f"pww_ui_k{k}_lease_out"),
        (cv(v + "_side", "=", 1), f"pww_ui_k{k}_buy"),
    ], f"pww_ui_k{k}_sell")
    L(f"pww_ui_k{k}_lease_in", f"Leases [?{v}_state.GetName] from [?{v}_cp.GetNameWithFlag]")
    L(f"pww_ui_k{k}_lease_out", f"[?{v}_state.GetName] leased to [?{v}_cp.GetNameWithFlag]")
    L(f"pww_ui_k{k}_buy", f"Buys [pww_ui_sl_k{k}_res_lc] from [?{v}_cp.GetNameWithFlag]")
    L(f"pww_ui_k{k}_sell", f"Sells [pww_ui_sl_k{k}_res_lc] to [?{v}_cp.GetNameWithFlag]")
    dt(f"pww_ui_sl_k{k}_st", [(cv(f"{v}_st", "=", s), key) for s, key in STATUS.items()], "pww_ui_blank")
# demand / pressure / situation lines
DTYPE = ["an output share", "a named-state lease", "a cutoff of a third party"]
for i, t in enumerate(DTYPE):
    L(f"pww_ui_dtype_{i}", t)
dt("pww_ui_sl_rd_type", [(cv("pww_ui_rd_dtype", "=", i), f"pww_ui_dtype_{i}") for i in range(3)], "pww_ui_blank")
dt("pww_ui_sl_pr_type", [(cv("pww_ui_pr_dtype", "=", i), f"pww_ui_dtype_{i}") for i in range(3)], "pww_ui_blank")
L("pww_ui_rd_head", "Our demand: [FROM.GetName] is [pww_coer_loc_state]. Decision [?pww_ui_rd_date.GetDateStringNoHourLong].")
L("pww_ui_rd_head_tt", "We demand [pww_ui_sl_rd_type] of [FROM.GetName].\\n\\n[pww_coer_loc_state_desc]")
L("pww_ui_rd_for", "§GFor us:§! [pww_coer_loc_for_0]")
L("pww_ui_rd_hold", "§RHolding out:§! [pww_coer_loc_hold_0]")
L("pww_ui_rd_for_tt", "§HWorking for you§!\\n[pww_coer_loc_for_0]\\n[pww_coer_loc_for_1]\\n[pww_coer_loc_for_2]\\n[pww_coer_loc_for_3]")
L("pww_ui_rd_hold_tt", "§HWhy they are holding out§!\\n[pww_coer_loc_hold_0]\\n[pww_coer_loc_hold_1]\\n[pww_coer_loc_hold_2]\\n[pww_coer_loc_hold_3]")
L("pww_ui_rd_more", "[pww_ui_sl_rd_more]")
dt("pww_ui_sl_rd_more", [(cv("pww_coer_rd_intel", ">", 0), "pww_ui_rd_intel"),
                         (cv("pww_coer_rd_warn", ">", 0), "pww_ui_rd_warn"),
                         (cv("pww_coer_rd_reveal", "<", 2), "pww_ui_rd_locked")], "pww_ui_blank")
L("pww_ui_rd_intel", "[pww_coer_loc_intel]")
L("pww_ui_rd_warn", "[pww_coer_loc_cornered]")
L("pww_ui_rd_locked", "§gFurther factors obscured. Raise civilian intel on [FROM.GetName] to see more.§!")
L("pww_ui_pr_head", "[FROM.GetName] demands [pww_ui_sl_pr_type] from us. We are [pww_ui_sl_pr_state]. Decision [?pww_ui_pr_date.GetDateStringNoHourLong].")
state_dt("pww_ui_sl_pr_state", "pww_ui_pr_tstate")
SEATN = ["claimant", "holder", "patron"]
ENTRY = {
    (0, 1): "Propose Trade Deal, Lease Mines or a Demand will move them.",
    (0, 2): "They are bidding against us for the same output.",
    (1, 0): "Their offers and demands reach us here; we answer in the reply window.",
    (1, 2): "Their pledge would let us hold out; their offer competes with the claimant's.",
    (2, 1): "Pledge Support or Propose Trade Deal keeps them out of the claimant's hands.",
    (2, 0): "Join Our Embargo and a pledge to the holder raise their price.",
}
cases = []
for (me, them), txt in ENTRY.items():
    key = f"pww_ui_st_{me}_{them}"
    L(key, f"[pww_ui_sl_st_title]: they are the {SEATN[them]}. {txt}")
    cases.append((f"{cv('pww_ui_st_myseat', '=', me)} {cv('pww_ui_st_seat', '=', them)}", key))
dt("pww_ui_sl_st_line", cases, "pww_ui_blank")
dt("pww_ui_sl_st_title", [(cv("pww_ui_st_tmpl", ">", 0), "pww_sit_wolfram_title")], "pww_ui_st_title_generic")
L("pww_ui_st_title_generic", "[pww_ui_sl_st_res] dispute")
res_dt("pww_ui_sl_st_res", "pww_ui_st_res")
L("pww_ui_dos_quiet", "§gNo demand or Situation stands between us.§!")
L("pww_ui_dos_st", "[pww_ui_sl_st_line]")


def dossier_body():
    b = tb("pww_ui_dos_title", 12, 8, "pww_dossier_title", 300, h=20, font=F18)
    # shortages: seven equal cells, icon centred over a band word (tooltip explains)
    cw = (OW - 24) // 7
    for i, r in enumerate(RES):
        cx = 12 + i * cw
        b += icon(f"pww_ui_dos_{r}_icon", cx + (cw - 27) // 2, 32, "GFX_resources_strip", frame=i + 1)
        b += tb(f"pww_ui_dos_{r}_band", cx, 60, f"[pww_ui_sl_short_{r}]", cw, fmt="centre", tip="pww_ui_short_tt")
    y = 82
    b += tb("pww_ui_dos_imp", 12, y, "pww_ui_dos_imports", 240, tip="pww_ui_imp_tt")
    b += tb("pww_ui_dos_nag", 256, y, "pww_ui_dos_nag", OW - 268, fmt="right")
    for k in range(NK):
        yy = y + 18 + k * 17
        b += tb(f"pww_ui_dos_k{k}", 12, yy, f"[pww_ui_sl_k{k}]", OW - 120)
        b += tb(f"pww_ui_dos_k{k}_st", OW - 102, yy, f"[pww_ui_sl_k{k}_st]", 90, fmt="right")
    y = y + 18 + NK * 17 + 3
    b += icon("pww_ui_dos_div", 4, y, "GFX_pww_ui_divider", scale=f"{(OW - 8) / 514:.3f}")
    y += 8
    # our demand (readout), their demand on us, a shared Situation
    b += tb("pww_ui_dos_rd_head", 12, y, "pww_ui_rd_head", OW - 24, tip="pww_ui_rd_head_tt")
    b += tb("pww_ui_dos_rd_for", 12, y + 18, "pww_ui_rd_for", OW - 24, tip="pww_ui_rd_for_tt")
    b += tb("pww_ui_dos_rd_hold", 12, y + 36, "pww_ui_rd_hold", OW - 24, tip="pww_ui_rd_hold_tt")
    b += tb("pww_ui_dos_rd_more", 12, y + 54, "pww_ui_rd_more", OW - 24)
    b += tb("pww_ui_dos_pr_head", 12, y, "pww_ui_pr_head", OW - 24, h=34)
    b += tb("pww_ui_dos_st", 12, y + 36, "pww_ui_dos_st", OW - 24, h=34)
    b += tb("pww_ui_dos_quiet", 12, y, "pww_ui_dos_quiet", OW - 24)
    assert y + 72 <= OH - 6, y
    return b


def dossier_toggle_body():
    return btn("pww_ui_dos_toggle", 0, 0, "GFX_button_94x31", text="pww_ui_dos_btn", tip="pww_ui_dos_btn_tt",
               click="click_default")


# --------------------------------------------------------------------------- GUI file
gui = ["# Power Without War: UI lane layout (generated by tools/pww_ui_gen.py).\n",
       "# Trade Desk (two windows with identical bodies: one rides on the trade view,\n",
       "# one floats when opened from the alert strip), the trade view button, the\n",
       "# alert strip on the top bar, and the Dossier inside the diplomacy tab.\n",
       "guiTypes = {\n"]
gui.append(window("pww_ui_desk_trade", 696, 0, DW, DH, desk_body(), bg="GFX_tiled_window_1b_border"))
gui.append(window("pww_ui_desk_float", 683, 78, DW, DH, desk_body(), bg="GFX_tiled_window_1b_border"))
gui.append(window("pww_ui_desk_button", 496, 6, 148, 34, desk_button_body()))
gui.append(window("pww_ui_alerts", -710, 90, AW, NSIT * AROW, alert_body(), orientation="UPPER_RIGHT"))
gui.append(window("pww_ui_dossier", OX, OY, OW, OH, dossier_body(), bg="GFX_tiled_window_1b_border"))
gui.append(window("pww_ui_dossier_toggle", TOGGLE[0], TOGGLE[1], 94, 31, dossier_toggle_body()))
gui.append("}\n")

gfx = """# Power Without War: UI lane sprites (vanilla textures only).
spriteTypes = {
	corneredTileSpriteType = {
		name = "GFX_pww_ui_alert_row"
		size = { x = 32 y = 32 }
		textureFile = "gfx/interface/tiles/tiled_mini_dialog.dds"
		borderSize = { x = 12 y = 12 }
		effectFile = "gfx/FX/buttonstate.lua"
	}
	spriteType = {
		name = "GFX_pww_ui_divider"
		texturefile = "gfx/interface/divider.dds"
	}
}
"""

# --------------------------------------------------------------------------- scripted GUIs
def desk_triggers():
    t = ["\t\t\tpww_ui_desk_sit_empty_visible = { check_variable = { pww_ui_ns = 0 } }\n",
         "\t\t\tpww_ui_desk_led_empty_visible = { check_variable = { pww_ui_nag = 0 } }\n",
         "\t\t\tpww_ui_desk_mkt_empty_visible = { NOT = { has_global_flag = pww_ui_mkt_ready } }\n",
         "\t\t\tpww_ui_desk_mkt_date_visible = { has_global_flag = pww_ui_mkt_ready }\n"]
    for n in ("pww_ui_desk_pg_prev", "pww_ui_desk_pg", "pww_ui_desk_pg_next"):
        t.append(f"\t\t\t{n}_visible = {{ check_variable = {{ pww_ui_npages > 1 }} }}\n")
    for k in range(NSIT):
        on = f"check_variable = {{ pww_ui_ns > {k} }}"
        for e in ("l1", "date", "l2"):
            t.append(f"\t\t\tpww_ui_ds{k}_{e}_visible = {{ {on} }}\n")
        t.append(f"\t\t\tpww_ui_ds{k}_hl_visible = {{ {on} check_variable = {{ pww_ui_focus = {k} }} }}\n")
    for k in range(NAG):
        for e in ("cp", "terms", "st"):
            t.append(f"\t\t\tpww_ui_dl{k}_{e}_visible = {{ check_variable = {{ pww_ui_l{k}_on = 1 }} }}\n")
    for r in RES:
        for e in (f"pww_ui_dm_{r}", f"pww_ui_dm_{r}_icon"):
            t.append(f"\t\t\t{e}_visible = {{ has_global_flag = pww_ui_mkt_ready }}\n")
    return "".join(t)


def desk_effects():
    close = ("\t\t\t\tclr_country_flag = pww_ui_desk_open\n\t\t\t\tclr_country_flag = pww_ui_desk_float\n"
             "\t\t\t\tset_variable = { pww_ui_focus = -1 }\n\t\t\t\tadd_to_variable = { pww_ui_dirty = 1 }\n")
    e = f"\t\t\tpww_ui_desk_close_click = {{\n{close}\t\t\t}}\n"
    e += ("\t\t\tpww_ui_desk_pg_next_click = {\n\t\t\t\tadd_to_variable = { pww_ui_page = 1 }\n"
          "\t\t\t\tif = { limit = { NOT = { check_variable = { pww_ui_page < pww_ui_npages } } } set_variable = { pww_ui_page = 0 } }\n"
          "\t\t\t\tpww_ui_refresh = yes\n\t\t\t}\n")
    e += ("\t\t\tpww_ui_desk_pg_prev_click = {\n\t\t\t\tsubtract_from_variable = { pww_ui_page = 1 }\n"
          "\t\t\t\tif = { limit = { check_variable = { pww_ui_page < 0 } } set_variable = { pww_ui_page = pww_ui_npages } subtract_from_variable = { pww_ui_page = 1 } }\n"
          "\t\t\t\tpww_ui_refresh = yes\n\t\t\t}\n")
    return e


sg = ["# Power Without War: UI lane scripted GUIs (generated by tools/pww_ui_gen.py).\n",
      "# Data: mod/common/scripted_effects/pww_ui_effects.txt (pww_ui_refresh runs daily\n",
      "# for human players and on every click). No randomness anywhere here.\n",
      "scripted_gui = {\n"]
for gname, wname, parent, vis in [
    ("pww_ui_desk_trade_gui", "pww_ui_desk_trade", "trade_tab",
     "has_country_flag = pww_ui_desk_open NOT = { has_country_flag = pww_ui_desk_float }"),
    ("pww_ui_desk_float_gui", "pww_ui_desk_float", None, "has_country_flag = pww_ui_desk_float"),
]:
    sg.append(f"\t{gname} = {{\n\t\tcontext_type = player_context\n\t\twindow_name = \"{wname}\"\n")
    if parent:
        sg.append(f"\t\tparent_window_token = {parent}\n")
    sg.append(f"\t\tvisible = {{ {vis} }}\n\t\tdirty = pww_ui_dirty\n")
    sg.append("\t\teffects = {\n" + desk_effects() + "\t\t}\n")
    sg.append("\t\ttriggers = {\n" + desk_triggers() + "\t\t}\n")
    sg.append("\t\tai_enabled = { always = no }\n\t}\n")
sg.append("""	pww_ui_desk_button_gui = {
		context_type = player_context
		window_name = "pww_ui_desk_button"
		parent_window_token = trade_tab
		visible = { always = yes }
		dirty = pww_ui_dirty
		effects = {
			pww_ui_desk_open_click = {
				if = {
					limit = { OR = { has_country_flag = pww_ui_desk_open has_country_flag = pww_ui_desk_float } }
					clr_country_flag = pww_ui_desk_open
					clr_country_flag = pww_ui_desk_float
				}
				else = {
					set_country_flag = pww_ui_desk_open
					pww_ui_refresh = yes
				}
				add_to_variable = { pww_ui_dirty = 1 }
			}
		}
		ai_enabled = { always = no }
	}
""")
al_fx = "".join(
    f"\t\t\tpww_ui_al{k}_btn_click = {{\n\t\t\t\tclr_country_flag = pww_ui_desk_open\n"
    f"\t\t\t\tset_country_flag = pww_ui_desk_float\n\t\t\t\tset_variable = {{ pww_ui_focus = {k} }}\n"
    f"\t\t\t\tpww_ui_refresh = yes\n\t\t\t}}\n" for k in range(NSIT))
al_tr = "".join(
    f"\t\t\tpww_ui_al{k}_{e}_visible = {{ check_variable = {{ pww_ui_ns > {k} }} }}\n"
    for k in range(NSIT) for e in ("btn", "txt", "date"))
sg.append(f"""	pww_ui_alerts_gui = {{
		context_type = player_context
		window_name = "pww_ui_alerts"
		parent_window_token = top_bar
		visible = {{ check_variable = {{ pww_ui_ns > 0 }} }}
		dirty = pww_ui_dirty
		effects = {{
{al_fx}		}}
		triggers = {{
{al_tr}		}}
		ai_enabled = {{ always = no }}
	}}
""")
foreign = "NOT = { tag = ROOT } ROOT = { is_ai = no }"
dos_tr = [f"\t\t\tpww_ui_dos_k{k}_visible = {{ check_variable = {{ pww_ui_nk > {k} }} }}\n" for k in range(NK)]
dos_tr += [f"\t\t\tpww_ui_dos_k{k}_st_visible = {{ check_variable = {{ pww_ui_nk > {k} }} }}\n" for k in range(NK)]
rd = "check_variable = { pww_ui_rd_viewer = ROOT }"
pr = "check_variable = { pww_ui_pr_viewer = ROOT }"
st = "check_variable = { pww_ui_st_viewer = ROOT }"
for e in ("head", "for", "hold", "more"):
    dos_tr.append(f"\t\t\tpww_ui_dos_rd_{e}_visible = {{ {rd} }}\n")
dos_tr.append(f"\t\t\tpww_ui_dos_pr_head_visible = {{ {pr} NOT = {{ {rd} }} }}\n")
dos_tr.append(f"\t\t\tpww_ui_dos_st_visible = {{ {st} NOT = {{ {rd} }} }}\n")
dos_tr.append(f"\t\t\tpww_ui_dos_quiet_visible = {{ NOT = {{ {rd} }} NOT = {{ {pr} }} NOT = {{ {st} }} }}\n")
sg.append(f"""	pww_ui_dossier_gui = {{
		context_type = diplomacy_target_context
		window_name = "pww_ui_dossier"
		parent_window_token = selected_country_view_diplomacy
		visible = {{ {foreign} ROOT = {{ has_country_flag = pww_ui_dos_open }} }}
		dirty = pww_ui_dirty
		triggers = {{
{''.join(dos_tr)}		}}
		ai_enabled = {{ always = no }}
	}}
	pww_ui_dossier_toggle_gui = {{
		context_type = diplomacy_target_context
		window_name = "pww_ui_dossier_toggle"
		parent_window_token = selected_country_view_diplomacy
		visible = {{ {foreign} }}
		dirty = pww_ui_dirty
		effects = {{
			pww_ui_dos_toggle_click = {{
				ROOT = {{
					if = {{
						limit = {{ has_country_flag = pww_ui_dos_open }}
						clr_country_flag = pww_ui_dos_open
					}}
					else = {{
						set_country_flag = pww_ui_dos_open
						pww_ui_refresh = yes
					}}
					add_to_variable = {{ pww_ui_dirty = 1 }}
				}}
			}}
		}}
		ai_enabled = {{ always = no }}
	}}
}}
""")

# --------------------------------------------------------------------------- generated effects
fx = ["###############################################################################\n",
      "# Power Without War: UI lane slot helpers (generated by tools/pww_ui_gen.py).\n",
      "# Called only from pww_ui_effects.txt. Inputs are the pww_ui_t_* temps that\n",
      "# pww_ui_load_sit / pww_ui_load_ag fill; the slot index comes from\n",
      "# pww_ui_ns (situations), pww_ui_lslot (ledger) or pww_ui_nk (dossier).\n",
      "###############################################################################\n\n"]
SIT_F = ["id", "seat", "tmpl", "res", "days", "phase", "tstate", "pledge", "dev", "hasp", "cl", "ho", "pa", "date",
         "kind"]
AG_F = ["id", "st", "kind", "res", "amt", "side", "cp", "state", "civ", "pay", "wepay", "end", "open", "com"]


def store(name, prefix, n, slotvar, fields, extra=""):
    s = f"{name} = {{\n"
    for k in range(n):
        kw = "if" if k == 0 else "else_if"
        s += f"\t{kw} = {{\n\t\tlimit = {{ check_variable = {{ {slotvar} = {k} }} }}\n"
        for f_ in fields:
            s += f"\t\tset_variable = {{ {prefix}{k}_{f_} = pww_ui_t_{f_} }}\n"
        s += extra.replace("{k}", str(k))
        s += "\t}\n"
    return s + "}\n\n"


fx.append(store("pww_ui_store_sit_slot", "pww_ui_s", NSIT, "pww_ui_ns", SIT_F))
fx.append(store("pww_ui_store_ag_slot", "pww_ui_l", NAG, "pww_ui_lslot", AG_F, "\t\tset_variable = { pww_ui_l{k}_on = 1 }\n"))
fx.append(store("pww_ui_store_k_slot", "pww_ui_k", NK, "pww_ui_nk", AG_F))
fx.append("pww_ui_clear_ag_slots = {\n" + "".join(f"\tset_variable = {{ pww_ui_l{k}_on = 0 }}\n" for k in range(NAG)) + "}\n\n")
RD = ["dem", "state", "prev", "cause", "cause_side", "for0", "for1", "for2", "for3", "hold0", "hold1", "hold2",
      "hold3", "nfor", "nhold", "reveal", "warn", "intel", "cred_band", "alarm_band"]
fx.append("# Viewer scope: copy the loaded coercion readout into temps.\npww_ui_readout_to_temps = {\n"
          + "".join(f"\tset_temp_variable = {{ pww_ui_c_{f_} = pww_coer_rd_{f_} }}\n" for f_ in RD)
          + "\tset_temp_variable = { pww_ui_c_patron = pww_patron }\n\tset_temp_variable = { pww_ui_c_rival = pww_rival }\n}\n\n")
fx.append("# Target scope: write the temps where the coercion scripted loc reads them\n"
          "# (unprefixed, on THIS = the dossier target; the loc lines use FROM = target).\n"
          "pww_ui_readout_from_temps = {\n"
          + "".join(f"\tset_variable = {{ pww_coer_rd_{f_} = pww_ui_c_{f_} }}\n" for f_ in RD)
          + "\tif = { limit = { check_variable = { pww_ui_c_patron > 0 } } set_variable = { pww_patron = pww_ui_c_patron } }\n"
          + "\tif = { limit = { check_variable = { pww_ui_c_rival > 0 } } set_variable = { pww_rival = pww_ui_c_rival } }\n}\n\n")
# market report, one block per resource
mk = ["# Global market report (any scope). Bands from the two most desperate buyers\n",
      "# of each resource (core desperation); causes from those buyers and from live\n",
      "# Situations over the resource.\npww_ui_market_report = {\n",
      "\tset_variable = { global.pww_ui_mkt_date = global.date }\n",
      "\tset_variable = { global.pww_ui_mkt_day = global.num_days }\n",
      "\tset_global_flag = pww_ui_mkt_ready\n"]
for i, r in enumerate(RES):
    g = "global.pww_ui_mkt"
    mk.append(f"""	# {r}
	set_temp_variable = {{ pww_ui_m1 = 0 }}
	set_temp_variable = {{ pww_ui_m2 = 0 }}
	set_variable = {{ {g}_b1_{r} = 0 }}
	set_variable = {{ {g}_b2_{r} = 0 }}
	every_country = {{
		limit = {{ exists = yes has_variable = pww_desp_{r} }}
		if = {{
			limit = {{ check_variable = {{ pww_desp_{r} > pww_ui_m1 }} }}
			set_temp_variable = {{ pww_ui_m2 = pww_ui_m1 }}
			set_variable = {{ {g}_b2_{r} = {g}_b1_{r} }}
			set_temp_variable = {{ pww_ui_m1 = pww_desp_{r} }}
			set_variable = {{ {g}_b1_{r} = THIS }}
		}}
		else_if = {{
			limit = {{ check_variable = {{ pww_desp_{r} > pww_ui_m2 }} }}
			set_temp_variable = {{ pww_ui_m2 = pww_desp_{r} }}
			set_variable = {{ {g}_b2_{r} = THIS }}
		}}
	}}
	set_temp_variable = {{ pww_ui_ms = pww_ui_m1 }}
	multiply_temp_variable = {{ pww_ui_ms = 0.6 }}
	set_temp_variable = {{ pww_ui_m2s = pww_ui_m2 }}
	multiply_temp_variable = {{ pww_ui_m2s = 0.4 }}
	add_to_temp_variable = {{ pww_ui_ms = pww_ui_m2s }}
	pww_ui_band_from_score = yes
	set_variable = {{ {g}_band_{r} = pww_ui_mb }}
	set_variable = {{ {g}_c1_{r} = 0 }}
	if = {{
		limit = {{ check_variable = {{ pww_ui_m2 > 39 }} }}
		set_variable = {{ {g}_c1_{r} = 2 }}
	}}
	else_if = {{
		limit = {{ check_variable = {{ pww_ui_m1 > 39 }} }}
		set_variable = {{ {g}_c1_{r} = 1 }}
	}}
	else_if = {{
		limit = {{ check_variable = {{ pww_ui_mb < 2 }} }}
		set_variable = {{ {g}_c1_{r} = 3 }}
	}}
	set_variable = {{ {g}_c2_{r} = 0 }}
	if = {{
		limit = {{ has_global_flag = pww_sit_loaded }}
		for_each_loop = {{
			array = global.pww_sit_live
			value = pww_ui_sv
			if = {{
				limit = {{ check_variable = {{ global.pww_sit_res^pww_ui_sv = {i} }} }}
				set_variable = {{ {g}_c2_{r} = 1 }}
				set_variable = {{ {g}_ho_{r} = global.pww_sit_holder^pww_ui_sv }}
			}}
		}}
	}}
""")
mk.append("}\n\n")
fx.extend(mk)
fx.append("# Country scope: temps pww_ui_imp (units imported) and pww_ui_con (units\n"
          "# consumed) summed over the seven resources.\npww_ui_import_sums = {\n"
          "\tset_temp_variable = { pww_ui_imp = 0 }\n\tset_temp_variable = { pww_ui_con = 0 }\n"
          + "".join(f"\tadd_to_temp_variable = {{ pww_ui_imp = resource_imported@{r} }}\n"
                    f"\tadd_to_temp_variable = {{ pww_ui_con = resource_consumed@{r} }}\n" for r in RES)
          + "}\n")

# --------------------------------------------------------------------------- write
def write(path, text, bom=False):
    with open(path, "w", encoding="utf-8-sig" if bom else "utf-8", newline="\n") as f:
        f.write(text)


write(P_GUI, "".join(gui))
write(P_GFX, gfx)
write(P_SG, "".join(sg))
write(P_SL, "# Power Without War: UI lane scripted localisation (generated by tools/pww_ui_gen.py).\n" + "".join(sl))
write(P_FX, "".join(fx))
lines = ["l_english:\n"] + [f' {k}:0 "{v}"\n' for k, v in loc.items()]
write(P_LOC, "".join(lines), bom=True)
print(f"ok: {len(loc)} loc keys, {len(sl)} defined_texts")
