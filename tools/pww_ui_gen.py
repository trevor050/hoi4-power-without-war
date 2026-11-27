"""UI lane generator: python tools/pww_ui_gen.py

Writes the UI lane's generated files (all prefixed pww_ui_):
  mod/interface/pww_ui.gui                          Trade Desk, Dossier, alert strip
  mod/interface/pww_ui_sprites.gfx                  sprites (vanilla textures only)
  mod/common/scripted_guis/pww_ui_guis.txt          scripted GUI blocks
  mod/common/scripted_localisation/pww_ui_scripted_loc.txt
  mod/common/scripted_effects/pww_ui_slots.txt      per-slot store/clear helpers, layout,
                                                    per-resource readers, market report
  mod/localisation/english/pww_ui_l_english.yml     UTF-8 with BOM

Every line of those six files comes from here: edit this script, never the outputs.
The data the GUIs read is built by mod/common/scripted_effects/pww_ui_effects.txt
(hand written). HoI4 GUI has no layout engine, so every position is computed
here from a few grid constants.

Engine facts the layout relies on (verified in game, tests/ui/ui_probe2):
  - a scripted GUI `properties = { elem = { y = ROOT.var } }` moves text boxes,
    icons and buttons, but NOT a child containerWindowType. Sections that
    flow (Overview tab, reserves footer) therefore get one y variable per
    element (pww_uy_<element suffix>), written by the generated pww_ui_layout.
  - `x` on an icon inside a `clipping = yes` container works: fill bars are a
    full-width fill sprite shifted left by (100 - fill)% inside a clip box.
  - `check_variable = { var@ROOT > n }` works in diplomacy_target_context
    triggers (THIS = target, ROOT = viewer): per-viewer dossier values are
    stored on the target as var@<viewer>.
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
SRES = list(range(1, 7))  # stored / cartel resources (no oil)
NSIT = 4          # situation slots (noise cap)
NAG = 10          # Deals tab rows per page
NK = 3            # dossier agreement rows
NC = 3            # cartel rows (one live cartel per resource; AI keeps <= 2 live)
NM = 6            # member flags shown per cartel row
NRS = 6           # reserve rows (one per stored resource)
NRV = 3           # dossier reserve words
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


def btn(name, x, y, sprite, text=None, font=F16, size=None, tip=None, transparent=False, click=None, scale=None,
        frame=None):
    s = f'\t\tbuttonType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
    if size:
        s += f"\t\t\tsize = {{ x = {size[0]} y = {size[1]} }}\n"
    s += f'\t\t\tquadTextureSprite = "{sprite}"\n'
    if frame:
        s += f"\t\t\tframe = {frame}\n"
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


def icon(name, x, y, sprite, frame=None, scale=None, tip=None, solid=False):
    """solid: takes the mouse (a panel background over vanilla buttons)."""
    s = f'\t\ticonType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tspriteType = "{sprite}"\n'
    if frame:
        s += f"\t\t\tframe = {frame}\n"
    if scale:
        s += f"\t\t\tscale = {scale}\n"
    if tip:
        s += f'\t\t\tpdx_tooltip = "{tip}"\n'
        return s + "\t\t}\n"
    if solid:
        return s + "\t\t}\n"
    return s + "\t\t\talwaystransparent = yes\n\t\t}\n"


def window(name, x, y, w, h, body, bg=None, orientation=None, clip=False):
    s = (f'\tcontainerWindowType = {{\n\t\tname = "{name}"\n\t\tposition = {{ x = {x} y = {y} }}\n'
         f'\t\tsize = {{ width = {w} height = {h} }}\n\t\tclipping = {"yes" if clip else "no"}\n')
    if orientation:
        s += f'\t\torientation = {orientation}\n'
    if bg:
        s += f'\t\tbackground = {{\n\t\t\tname = "background"\n\t\t\tquadTextureSprite = "{bg}"\n\t\t}}\n'
    return s + "\n" + body + "\t}\n\n"


def indent(text):
    return "".join("\t" + ln if ln.strip() else ln for ln in text.splitlines(True))


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
for i, r in enumerate(RES):
    L(f"pww_ui_res_lc_{r}", RES_NAME[i])     # capitalised like vanilla; lowercase "steel" is a loc key in Road to 56
REL_BANDS = 5
SEP = "  ·  "


def res_dt(name, var):
    dt(name, [(cv(var, "=", i), f"pww_mkt_res_{r}") for i, r in enumerate(RES)], "pww_ui_blank")


def res_lc_dt(name, var, default="pww_ui_blank"):
    dt(name, [(cv(var, "=", i), f"pww_ui_res_lc_{r}") for i, r in enumerate(RES)], default)


def state_dt(name, var):
    dt(name, [(cv(var, "=", i), k) for i, k in enumerate(STATE_KEYS)], "pww_ui_blank")


def bond_dt(name, var):
    dt(name, [(cv(var, "=", i), f"pww_rel_band_{i}") for i in range(REL_BANDS)], "pww_ui_blank")


# =========================================================================== Trade Desk
# Element registry: every desk element has a visibility condition (its tab
# plus its own) and optionally a flow slot (section, offset): its y is then
# ROOT.pww_uy_<suffix>, written by the generated pww_ui_layout effect.
DW, DH = 500, 880             # DH: tallest step; the background follows the content
X0 = 20                       # left content edge
XR = DW - 20                  # right content edge
CW = XR - X0                  # content width
CY = 84                       # content top (below the tabs)
TAB_Y, TAB_W = 42, 116        # GFX_tab_small_116 (116 x 36, frame 2 = raised, selected)
TABS = ["pww_ui_tab_overview", "pww_ui_tab_deals", "pww_ui_tab_reserves"]
SIT_ROW, CART_ROW, MKT_ROW, GAP = 38, 38, 18, 12
OPP_ROW, NO = 38, 4          # Opportunities rows
NEWS_ROW, NN = 18, 4         # Recent (news) rows on the Overview
NNA = 2                      # news rows on the top-bar alert strip
HDR = 24                      # section header height before the first row
LED_Y, LED_ROW = CY + 26, 38
LED_CP, LED_ST = 168, 70      # counterparty and status columns
RSV_Y, RSV_ROW = CY + 26, 22
BAR_W, BAR_H = 100, 6

VIS = {}                      # element -> condition (without the tab)
TABOF = {}                    # element -> tab (-1 = always)
FLOW = {}                     # element -> (section, offset)
DESK = []                     # element strings in draw order
CLIPS = []                    # (container name, body) for fill bars


def uy(name):
    return "pww_uy_" + name[len("pww_ui_"):]


def D(tab, name, s, cond=None, flow=None):
    VIS[name] = cond
    TABOF[name] = tab
    if flow:
        FLOW[name] = flow
    DESK.append(s)


def fy(sec, off):
    """Static y for a flowing element (its default before the first layout)."""
    return CY + off


L("pww_desk_title", "Trade Desk")
L("pww_ui_tab_overview", "Overview")
L("pww_ui_tab_deals", "Deals")
L("pww_ui_tab_reserves", "Reserves")
L("pww_ui_tab_overview_tt", "Situations in our seats, cartels that set our prices, and the monthly market report.")
L("pww_ui_tab_deals_tt", "Every trade agreement we are party to: terms, how long it is locked, our bond with the other side and the delivery route.")
L("pww_ui_tab_reserves_tt", "Our strategic reserves: days of use in store, how full each one is, and whether it is filling or being drawn.")
L("pww_desk_sec_situations", "Active Situations")
L("pww_desk_sec_cartels", "Cartels")
L("pww_desk_sec_ledger", "Our Agreements")
L("pww_desk_empty_ledger", "§gNo active agreements. Open talks through any country's diplomacy panel.§!")
L("pww_desk_sec_market", "Monthly Market Report")
L("pww_desk_empty_market", "§gFirst monthly report posts at the turn of the month.§!")
L("pww_desk_sec_reserves", "Strategic Reserves")
L("pww_ui_desk_btn", "Trade Desk")
L("pww_ui_desk_btn_tt", "Open the Trade Desk: Situations in our seats, cartels, the market report, our agreements and our strategic reserves.")
L("pww_ui_desk_close_tt", "Close the Trade Desk.")
L("pww_ui_mkt_dated", "§g[?global.pww_ui_mkt_date.GetDateStringNoHourLong]§!")
L("pww_ui_page", "[?pww_ui_page_n]/[?pww_ui_npages]")
L("pww_ui_page_prev_tt", "Previous page")
L("pww_ui_page_next_tt", "Next page")

ON_TAB = "check_variable = {{ pww_ui_tab = {t} }}"
# The desk's height follows its content (pww_ui_layout picks pww_ui_desk_h):
# one background per height step, so no tab shows a half-empty window.
DESK_HS = list(range(240, DH, 40)) + [DH]


def desk_body():
    DESK.clear()
    CLIPS.clear()
    for h in DESK_HS:
        D(-1, f"pww_ui_desk_bg_{h}", icon(f"pww_ui_desk_bg_{h}", 0, 0, f"GFX_pww_ui_desk_bg_{h}", solid=True),
          cv("pww_ui_desk_h", "=", h) if h != DH else
          f"OR = {{ {cv('pww_ui_desk_h', '=', h)} NOT = {{ has_variable = pww_ui_desk_h }} }}")
    D(-1, "pww_ui_desk_title", tb("pww_ui_desk_title", X0, 10, "pww_desk_title", 300, h=28, font=F24))
    D(-1, "pww_ui_desk_close", btn("pww_ui_desk_close", DW - 37, 9, "GFX_closebutton", tip="pww_ui_desk_close_tt",
                                   click="click_close"))
    for t, key in enumerate(TABS):
        D(-1, f"pww_ui_tab{t}", btn(f"pww_ui_tab{t}", X0 + t * (TAB_W + 4), TAB_Y, "GFX_tab_small_116", text=key,
                                    tip=f"{key}_tt", click="click_default", frame=1))
    # ----------------------------------------------------------- Overview (tab 0), flowing
    D(0, "pww_ui_desk_sit_hdr", tb("pww_ui_desk_sit_hdr", X0, fy("sit", 0), "pww_desk_sec_situations", CW, h=20,
                                   font=F18), "check_variable = { pww_ui_ns > 0 }", ("sit", 0))
    for k in range(NSIT):
        o = HDR + k * SIT_ROW
        on = f"check_variable = {{ pww_ui_ns > {k} }}"
        D(0, f"pww_ui_ds{k}_hl", btn(f"pww_ui_ds{k}_hl", X0 - 19, fy("sit", o + 2), "GFX_production_line_arrow_right",
                                     transparent=True, scale="0.55"), f"{on} check_variable = {{ pww_ui_focus = {k} }}",
          ("sit", o + 2))
        D(0, f"pww_ui_ds{k}_l1", tb(f"pww_ui_ds{k}_l1", X0, fy("sit", o + 1), f"[pww_ui_sl_s{k}_head]", CW - 150,
                                    tip=f"pww_ui_s{k}_tt"), on, ("sit", o + 1))
        D(0, f"pww_ui_ds{k}_date", tb(f"pww_ui_ds{k}_date", XR - 150, fy("sit", o + 1), f"pww_ui_s{k}_date", 150,
                                      fmt="right", tip="pww_ui_date_tt"), on, ("sit", o + 1))
        D(0, f"pww_ui_ds{k}_l2", tb(f"pww_ui_ds{k}_l2", X0, fy("sit", o + 19), f"pww_ui_s{k}_line2", CW,
                                    tip=f"pww_ui_s{k}_tt"), on, ("sit", o + 19))
    # recent: what happened to our agreements (pww_ui_news_poll)
    D(0, "pww_ui_desk_div_news", icon("pww_ui_desk_div_news", X0 - 6, fy("news", -10), "GFX_pww_ui_divider",
                                      scale=f"{(CW + 12) / 514:.3f}"),
      "check_variable = { pww_ui_nn > 0 } check_variable = { pww_ui_ns > 0 }", ("news", -10))
    D(0, "pww_ui_desk_news_hdr", tb("pww_ui_desk_news_hdr", X0, fy("news", 0), "pww_desk_sec_news", CW, h=20,
                                    font=F18), "check_variable = { pww_ui_nn > 0 }", ("news", 0))
    for j in range(NN):
        o = HDR + j * NEWS_ROW
        D(0, f"pww_ui_dn{j}", tb(f"pww_ui_dn{j}", X0, fy("news", o), f"[pww_ui_sl_n{j}]", CW, tip=f"pww_ui_n{j}_tt"),
          f"check_variable = {{ pww_ui_nn > {j} }}", ("news", o))
    # opportunities: what we lack and who sells it, what we cannot sell and who lacks it
    D(0, "pww_ui_desk_div_opp", icon("pww_ui_desk_div_opp", X0 - 6, fy("opp", -10), "GFX_pww_ui_divider",
                                     scale=f"{(CW + 12) / 514:.3f}"),
      "check_variable = { pww_ui_no > 0 } OR = { check_variable = { pww_ui_ns > 0 } check_variable = { pww_ui_nn > 0 } }",
      ("opp", -10))
    D(0, "pww_ui_desk_opp_hdr", tb("pww_ui_desk_opp_hdr", X0, fy("opp", 0), "pww_desk_sec_opps", CW, h=20, font=F18,
                                   tip="pww_desk_sec_opps_tt"), "check_variable = { pww_ui_no > 0 }", ("opp", 0))
    for k in range(NO):
        o = HDR + k * OPP_ROW
        on = f"check_variable = {{ pww_ui_no > {k} }}"
        D(0, f"pww_ui_do{k}_icon", icon(f"pww_ui_do{k}_icon", X0, fy("opp", o), "GFX_resources_strip", frame=1,
                                        scale="0.6"), on, ("opp", o))
        D(0, f"pww_ui_do{k}_l1", tb(f"pww_ui_do{k}_l1", X0 + 22, fy("opp", o + 1), f"[pww_ui_sl_o{k}_l1]", CW - 22,
                                    tip=f"pww_ui_o{k}_tt"), on, ("opp", o + 1))
        D(0, f"pww_ui_do{k}_l2", tb(f"pww_ui_do{k}_l2", X0 + 22, fy("opp", o + 19), f"[pww_ui_sl_o{k}_l2]", CW - 22,
                                    tip=f"pww_ui_o{k}_tt"), on, ("opp", o + 19))
    # cartels
    D(0, "pww_ui_desk_div_cart", icon("pww_ui_desk_div_cart", X0 - 6, fy("cart", -10), "GFX_pww_ui_divider",
                                      scale=f"{(CW + 12) / 514:.3f}"),
      "check_variable = { pww_ui_nc > 0 } OR = { check_variable = { pww_ui_ns > 0 } check_variable = { pww_ui_no > 0 } }",
      ("cart", -10))
    D(0, "pww_ui_desk_cart_hdr", tb("pww_ui_desk_cart_hdr", X0, fy("cart", 0), "pww_desk_sec_cartels", CW, h=20,
                                    font=F18), "check_variable = { pww_ui_nc > 0 }", ("cart", 0))
    for k in range(NC):
        o = HDR + k * CART_ROW
        on = f"check_variable = {{ pww_ui_nc > {k} }}"
        D(0, f"pww_ui_dc{k}_icon", icon(f"pww_ui_dc{k}_icon", X0, fy("cart", o), "GFX_resources_strip", frame=1,
                                        scale="0.6"), on, ("cart", o))
        D(0, f"pww_ui_dc{k}_l1", tb(f"pww_ui_dc{k}_l1", X0 + 22, fy("cart", o + 1), f"pww_ui_c{k}_l1", CW - 22 - 150,
                                    tip=f"pww_ui_c{k}_tt"), on, ("cart", o + 1))
        D(0, f"pww_ui_dc{k}_price", tb(f"pww_ui_dc{k}_price", XR - 150, fy("cart", o + 1), f"[pww_ui_sl_c{k}_price]",
                                       150, fmt="right", tip=f"pww_ui_c{k}_tt"), on, ("cart", o + 1))
        D(0, f"pww_ui_dc{k}_l2", tb(f"pww_ui_dc{k}_l2", X0 + 22, fy("cart", o + 19), f"[pww_ui_sl_c{k}_l2]", CW - 22,
                                    tip=f"pww_ui_c{k}_tt"), on, ("cart", o + 19))
    # market report
    D(0, "pww_ui_desk_div_mkt", icon("pww_ui_desk_div_mkt", X0 - 6, fy("mkt", -10), "GFX_pww_ui_divider",
                                     scale=f"{(CW + 12) / 514:.3f}"),
      "OR = { check_variable = { pww_ui_ns > 0 } check_variable = { pww_ui_nc > 0 } check_variable = { pww_ui_no > 0 } }",
      ("mkt", -10))
    D(0, "pww_ui_desk_mkt_hdr", tb("pww_ui_desk_mkt_hdr", X0, fy("mkt", 0), "pww_desk_sec_market", 300, h=20,
                                   font=F18), None, ("mkt", 0))
    D(0, "pww_ui_desk_mkt_date", tb("pww_ui_desk_mkt_date", XR - 170, fy("mkt", 2), "pww_ui_mkt_dated", 170,
                                    fmt="right"), "has_global_flag = pww_ui_mkt_ready", ("mkt", 2))
    D(0, "pww_ui_desk_mkt_empty", tb("pww_ui_desk_mkt_empty", X0, fy("mkt", 28), "pww_desk_empty_market", CW, h=36),
      "NOT = { has_global_flag = pww_ui_mkt_ready }", ("mkt", 28))
    for i, r in enumerate(RES):
        o = 26 + i * MKT_ROW
        D(0, f"pww_ui_dm_{r}_icon", icon(f"pww_ui_dm_{r}_icon", X0, fy("mkt", o - 1), "GFX_resources_strip",
                                         frame=i + 1, scale="0.6"), "has_global_flag = pww_ui_mkt_ready", ("mkt", o - 1))
        D(0, f"pww_ui_dm_{r}", tb(f"pww_ui_dm_{r}", X0 + 22, fy("mkt", o), f"pww_ui_mkt_line_{r}", CW - 22),
          "has_global_flag = pww_ui_mkt_ready", ("mkt", o))
    # ----------------------------------------------------------- Deals (tab 1)
    D(1, "pww_ui_desk_led_hdr", tb("pww_ui_desk_led_hdr", X0, CY, "pww_desk_sec_ledger", 300, h=20, font=F18))
    pg = "check_variable = { pww_ui_npages > 1 }"
    D(1, "pww_ui_desk_pg_prev", btn("pww_ui_desk_pg_prev", XR - 74, CY + 2, "GFX_pww_diplo_prev",
                                    tip="pww_ui_page_prev_tt"), pg)
    D(1, "pww_ui_desk_pg", tb("pww_ui_desk_pg", XR - 56, CY + 1, "pww_ui_page", 38, fmt="centre"), pg)
    D(1, "pww_ui_desk_pg_next", btn("pww_ui_desk_pg_next", XR - 16, CY + 2, "GFX_pww_diplo_next",
                                    tip="pww_ui_page_next_tt"), pg)
    D(1, "pww_ui_desk_led_empty", tb("pww_ui_desk_led_empty", X0, LED_Y + 2, "pww_desk_empty_ledger", CW, h=36),
      "check_variable = { pww_ui_nag = 0 }")
    for k in range(NAG):
        y = LED_Y + k * LED_ROW
        on = f"check_variable = {{ pww_ui_l{k}_on = 1 }}"
        D(1, f"pww_ui_dl{k}_cp", tb(f"pww_ui_dl{k}_cp", X0, y, f"pww_ui_l{k}_cp", LED_CP, tip=f"pww_ui_l{k}_tt"), on)
        D(1, f"pww_ui_dl{k}_terms", tb(f"pww_ui_dl{k}_terms", X0 + LED_CP + 6, y, f"[pww_ui_sl_l{k}_terms]",
                                       CW - LED_CP - 6 - LED_ST - 4, tip=f"pww_ui_l{k}_tt"), on)
        D(1, f"pww_ui_dl{k}_st", tb(f"pww_ui_dl{k}_st", XR - LED_ST, y, f"[pww_ui_sl_l{k}_status]", LED_ST, fmt="right",
                                    tip=f"pww_ui_l{k}_tt"), on)
        D(1, f"pww_ui_dl{k}_l2", tb(f"pww_ui_dl{k}_l2", X0 + 22, y + 17, f"pww_ui_l{k}_line2", CW - 22 - 76,
                                    tip=f"pww_ui_l{k}_tt"), on)
        # End: first click arms (label turns to Confirm), second click ends it
        D(1, f"pww_ui_dl{k}_end", btn(f"pww_ui_dl{k}_end", XR - 70, y + 15, "GFX_pww_ui_alert_row",
                                      text=f"[pww_ui_sl_l{k}_endb]", size=(70, 20), tip=f"pww_ui_l{k}_end_tt",
                                      click="click_default"),
          f"{on} OR = {{ {cv(f'pww_ui_l{k}_st', '=', 1)} {cv(f'pww_ui_l{k}_st', '=', 2)} }}")
    assert LED_Y + NAG * LED_ROW <= DH - 10
    # ----------------------------------------------------------- Reserves (tab 2)
    D(2, "pww_ui_desk_rsv_hdr", tb("pww_ui_desk_rsv_hdr", X0, CY, "pww_desk_sec_reserves", 300, h=20, font=F18))
    D(2, "pww_ui_desk_rsv_empty", tb("pww_ui_desk_rsv_empty", X0, RSV_Y + 2, "[pww_ui_sl_rsv_empty]", CW, h=36),
      "check_variable = { pww_ui_nr = 0 }")
    for k in range(NRS):
        y = RSV_Y + k * RSV_ROW
        on = f"check_variable = {{ pww_ui_nr > {k} }}"
        tip = f"pww_ui_r{k}_tt"
        D(2, f"pww_ui_dr{k}_icon", icon(f"pww_ui_dr{k}_icon", X0, y - 1, "GFX_resources_strip", frame=2, scale="0.6"),
          on)
        D(2, f"pww_ui_dr{k}_name", tb(f"pww_ui_dr{k}_name", X0 + 22, y, f"[pww_ui_sl_r{k}_name]", 78, tip=tip), on)
        D(2, f"pww_ui_dr{k}_days", tb(f"pww_ui_dr{k}_days", X0 + 100, y, f"[pww_ui_sl_r{k}_days]", 84, fmt="right",
                                      tip=tip), on)
        D(2, f"pww_ui_dr{k}_barbg", icon(f"pww_ui_dr{k}_barbg", X0 + 196, y + 6, "GFX_pww_ui_bar_bg"), on)
        clip = f"pww_ui_dr{k}_clip"
        D(2, clip, None, on)
        CLIPS.append((clip, X0 + 196, y + 6,
                      icon(f"pww_ui_dr{k}_fill", 0, 0, "GFX_pww_ui_bar_fill")))
        VIS[f"pww_ui_dr{k}_fill"] = on
        TABOF[f"pww_ui_dr{k}_fill"] = 2
        D(2, f"pww_ui_dr{k}_trend", tb(f"pww_ui_dr{k}_trend", X0 + 308, y, f"[pww_ui_sl_r{k}_trend]", CW - 308,
                                       tip=tip), on)
    D(2, "pww_ui_desk_rsv_foot", tb("pww_ui_desk_rsv_foot", X0, fy("rsv", 0), "[pww_ui_sl_rsv_foot]", CW, h=36,
                                    tip="pww_ui_rsv_foot_tt"), None, ("rsv", 0))
    b = "".join(s for s in DESK if s)
    for name, x, y, body in CLIPS:
        b += indent(window(name, x, y, BAR_W, BAR_H, body, clip=True))
    return b


# ---------------------------------------------------------------- situation slot loc
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
    # head: title and our seat; the focus slot is highlighted by the row arrow
    dt(f"pww_ui_sl_s{k}_head", [], f"pww_ui_s{k}_head")
    L(f"pww_ui_s{k}_head", f"§H[pww_ui_sl_s{k}_title]§!  [?{v}_ho.GetAdjective] [pww_ui_sl_s{k}_res_lc]")
    L(f"pww_ui_s{k}_date", f"[?{v}_date.GetDateStringNoHourLong]")
    # line 2: our seat as a sentence and the holder's standing (the latest
    # development is the tooltip's first line: both do not fit one row)
    L(f"pww_ui_s{k}_line2", f"§g[pww_ui_sl_s{k}_seatline]§! [pww_ui_sl_s{k}_tstate_short]")
    res_lc_dt(f"pww_ui_sl_s{k}_res_lc", f"{v}_res")
    dt(f"pww_ui_sl_s{k}_tstate_short", [(f"{cv(v + '_tstate', '=', i)}", f"pww_ui_s{k}_ts_{i}") for i in range(5)],
       "pww_ui_blank")
    for i, key in enumerate(STATE_KEYS):
        L(f"pww_ui_s{k}_ts_{i}", f"[?{v}_ho.GetName] is ${key}$.")
    L(f"pww_ui_s{k}_tt", f"§H[pww_ui_sl_s{k}_title]§!\\n[pww_ui_sl_s{k}_dev]\\n\\nOur seat: [pww_ui_sl_s{k}_seat]\\n"
                         f"Claimant: [?{v}_cl.GetFlag] [?{v}_cl.GetName]\\nHolder: [?{v}_ho.GetFlag] [?{v}_ho.GetName]\\n"
                         f"[pww_ui_sl_s{k}_patron]\\nDecision date: [?{v}_date.GetDateStringNoHourLong]")
    dt(f"pww_ui_sl_s{k}_patron", [(cv(f"{v}_hasp", "=", 1), f"pww_ui_s{k}_patron")], "pww_ui_no_patron")
    L(f"pww_ui_s{k}_patron", f"Patron: [?{v}_pa.GetFlag] [?{v}_pa.GetName]")
    # seat as a sentence ("You are the claimant."; keys from the situations lane)
    dt(f"pww_ui_sl_s{k}_seatline", [(cv(f"{v}_seat", "=", i), f"pww_seat_line_{n}")
                                    for i, n in enumerate(["claimant", "holder", "patron"])], "pww_ui_blank")
L("pww_ui_no_patron", "Patron: none")


# ---------------------------------------------------------------- news slot loc
# Slots pww_ui_n<j>_* (newest first, pww_ui_nn rows): nk (1 signed, 2 pledge
# signed, 3 expired, 4 ended, 5 broken, 6 nationalized, 7 suspended, 9 renewal
# due), the agreement fields of pww_ui_load_ag (res amt cp side civ pay wepay
# kind state end com) and date / day of the event. Built by pww_ui_news_poll.
NEWS_KINDS = {1: "§GSigned§!", 2: "§HPledge signed§!", 3: "Expired", 4: "§YEnded§!", 5: "§RContract broken§!",
              6: "§RNationalized§!", 7: "§YSuspended§!", 9: "§HRenewal due§!"}
NEWS_TT = {1: "The agreement is in force.", 2: "It takes force only if its condition fires.",
           3: "It ran its full term.", 4: "One side ended it, or events (war, a lost state) did.",
           5: "A party broke a locked contract early: trust between the two suffers.",
           6: "The host government seized the concession.",
           7: "Deliveries are paused by a quarantine, an interdiction or a truce.",
           9: "It ends soon. Renew it through new talks before it lapses."}
L("pww_desk_sec_news", "Recent")
for j in range(NN):
    v = f"pww_ui_n{j}"
    res_dt(f"pww_ui_sl_n{j}_res", f"{v}_res")
    dt(f"pww_ui_sl_n{j}_head", [(cv(v + "_nk", "=", n), f"pww_ui_news_k{n}") for n in NEWS_KINDS], "pww_ui_blank")
    dt(f"pww_ui_sl_n{j}_deal", [
        (f"{cv(v + '_kind', '>', 0)} {cv(v + '_side', '=', 1)}", f"pww_ui_n{j}_lease_in"),
        (cv(v + "_kind", ">", 0), f"pww_ui_n{j}_lease_out"),
        (cv(v + "_side", "=", 1), f"pww_ui_n{j}_buy"),
    ], f"pww_ui_n{j}_sell")
    cp = f"[?{v}_cp.GetFlag] [?{v}_cp.GetName]"
    L(f"pww_ui_n{j}_lease_in", f"our lease of [?{v}_state.GetName] from {cp}")
    L(f"pww_ui_n{j}_lease_out", f"{cp}'s lease of [?{v}_state.GetName]")
    L(f"pww_ui_n{j}_buy", f"we buy [?{v}_amt|0] [pww_ui_sl_n{j}_res] from {cp}")
    L(f"pww_ui_n{j}_sell", f"we sell [?{v}_amt|0] [pww_ui_sl_n{j}_res] to {cp}")
    dt(f"pww_ui_sl_n{j}", [(cv(v + "_nk", ">", 0), f"pww_ui_n{j}_line")], "pww_ui_blank")
    L(f"pww_ui_n{j}_line", f"[pww_ui_sl_n{j}_head]: [pww_ui_sl_n{j}_deal]")
    dt(f"pww_ui_sl_n{j}_why", [(cv(v + "_nk", "=", n), f"pww_ui_news_tt{n}") for n in NEWS_TT], "pww_ui_blank")
    L(f"pww_ui_n{j}_tt", f"§H[?{v}_date.GetDateStringNoHourLong]§!\\n[pww_ui_sl_n{j}_head]: [pww_ui_sl_n{j}_deal].\\n"
                         f"[pww_ui_sl_n{j}_why]\\n\\nThe Deals tab lists everything in force.")
for n, t in NEWS_KINDS.items():
    L(f"pww_ui_news_k{n}", t)
for n, t in NEWS_TT.items():
    L(f"pww_ui_news_tt{n}", t)
L("pww_ui_news_alert_tt", "Click to open the Trade Desk. Alerts clear when you open it, or after ten days.")

# ---------------------------------------------------------------- opportunity slot loc
# Slots pww_ui_o<k>_*: res kind (0 we are short, 1 our output finds no buyer)
# amt (a day) c1 a1 c2 a2 (the two countries with the most unsold / the
# largest shortfall, a day) n (0..2 named) frame. Built by pww_ui_load_opps.
L("pww_desk_sec_opps", "Opportunities")
L("pww_desk_sec_opps_tt", "Where to buy what we lack, and who lacks what we cannot sell. To trade, open the country's diplomacy panel (click its territory) and choose Propose Trade Deal.")
for k in range(NO):
    v = f"pww_ui_o{k}"
    res_dt(f"pww_ui_sl_o{k}_res", f"{v}_res")
    dt(f"pww_ui_sl_o{k}_l1", [(cv(v + "_kind", "=", 0), f"pww_ui_o{k}_short")], f"pww_ui_o{k}_spare")
    L(f"pww_ui_o{k}_short", f"§H[pww_ui_sl_o{k}_res]§!: we are short §R[?{v}_amt|0]§! a day.")
    L(f"pww_ui_o{k}_spare", f"§H[pww_ui_sl_o{k}_res]§!: §G[?{v}_amt|0]§! a day of ours finds no buyer.")
    c1 = f"[?{v}_c1.GetFlag] [?{v}_c1.GetName] [?{v}_a1|0]"
    c2 = f"[?{v}_c2.GetFlag] [?{v}_c2.GetName] [?{v}_a2|0]"
    dt(f"pww_ui_sl_o{k}_l2", [
        (f"{cv(v + '_kind', '=', 0)} {cv(v + '_n', '>', 1)}", f"pww_ui_o{k}_sell2"),
        (f"{cv(v + '_kind', '=', 0)} {cv(v + '_n', '>', 0)}", f"pww_ui_o{k}_sell1"),
        (cv(v + "_kind", "=", 0), "pww_ui_opp_nosell"),
        (cv(v + "_n", ">", 1), f"pww_ui_o{k}_buy2"),
        (cv(v + "_n", ">", 0), f"pww_ui_o{k}_buy1"),
    ], "pww_ui_opp_nobuy")
    L(f"pww_ui_o{k}_sell2", f"§gUnsold:§! {c1}{SEP}{c2}")
    L(f"pww_ui_o{k}_sell1", f"§gUnsold:§! {c1}")
    L(f"pww_ui_o{k}_buy2", f"§gBuyers:§! {c1}{SEP}{c2}")
    L(f"pww_ui_o{k}_buy1", f"§gBuyers:§! {c1}")
    dt(f"pww_ui_sl_o{k}_tt", [(cv(v + "_kind", "=", 0), "pww_ui_opp_tt_short")], "pww_ui_opp_tt_spare")
    # our own mines for this resource (capacity lane)
    capc = []
    for i_, r_ in enumerate(RES):
        cap = f"pww_cap_{r_}"
        capc.append((f"{cv(v + '_res', '=', i_)} has_variable = {cap} {cv(cap, '<', 0.995)}", f"pww_ui_o_cap_{r_}"))
    dt(f"pww_ui_sl_o{k}_cap", capc, "pww_ui_blank")
    L(f"pww_ui_o{k}_tt", f"[pww_ui_sl_o{k}_l1]\\n[pww_ui_sl_o{k}_l2][pww_ui_sl_o{k}_cap]\\n\\n[pww_ui_sl_o{k}_tt]")
L("pww_ui_opp_nosell", "§gNo country has any to spare.§!")
for r_ in RES:
    L(f"pww_ui_o_cap_{r_}", f"\\n§YOur mines are idling:§! working at [?pww_cap_{r_}|%0] of capacity. "
                            "Output nobody buys slowly goes idle, and takes months to restart.")
L("pww_ui_opp_nobuy", "§gNobody imports it. Our surplus goes to storage.§!")
L("pww_ui_opp_tt_short", "Figures are a day of output nobody buys. A seller sitting on unsold output usually takes less than the market rate. Open its diplomacy panel and choose Propose Trade Deal.")
L("pww_ui_opp_tt_spare", "Output nobody buys slowly goes idle: mines close and output falls until buyers return. Figures are what each country imports a day, plus anything it still lacks. They buy on the open market today; a better offer can win them over, and a buyer that is badly short pays above the market rate. Open its diplomacy panel and choose Propose Trade Deal.")

# ---------------------------------------------------------------- cartel slot loc
# Slots pww_ui_c<k>_*: id res status anchor pct (price over market, %), cb
# (cohesion band 0..4), n (members), nm (flags shown), m0..m5 (members, chair
# first), leader, me (1 member, 2 invited, 0 outsider), quota, sold, room,
# over, sb (our suspicion band), conf (conference decision date value).
L("pww_ui_cart_name_anchor", "Rubber Regulation")
for k in range(NC):
    v = f"pww_ui_c{k}"
    res_dt(f"pww_ui_sl_c{k}_res", f"{v}_res")
    res_lc_dt(f"pww_ui_sl_c{k}_res_lc", f"{v}_res")
    dt(f"pww_ui_sl_c{k}_name", [(cv(f"{v}_anchor", "=", 1), "pww_ui_cart_name_anchor")], f"pww_ui_c{k}_name")
    L(f"pww_ui_c{k}_name", f"[pww_ui_sl_c{k}_res] cartel")
    for j in range(NM):
        dt(f"pww_ui_sl_c{k}_m{j}", [(cv(f"{v}_nm", ">", j), f"pww_ui_c{k}_m{j}")], "pww_ui_blank")
        L(f"pww_ui_c{k}_m{j}", f"[?{v}_m{j}.GetFlag]")
    flags = "".join(f"[pww_ui_sl_c{k}_m{j}]" for j in range(NM))
    L(f"pww_ui_c{k}_l1", f"§H[pww_ui_sl_c{k}_name]§!  {flags}")
    dt(f"pww_ui_sl_c{k}_price", [(cv(f"{v}_status", "=", 0), "pww_ui_cart_conf"),
                                 (cv(f"{v}_pct", "<", 1), "pww_ui_cart_at_market")], f"pww_ui_c{k}_over")
    L(f"pww_ui_c{k}_over", f"§Y+[?{v}_pct|0]%§! over market")
    dt(f"pww_ui_sl_c{k}_coh", [(cv(f"{v}_cb", "=", i), f"pww_cartel_cohesion_band_{i}") for i in range(5)],
       "pww_ui_blank")
    dt(f"pww_ui_sl_c{k}_susp", [(cv(f"{v}_sb", "=", i), f"pww_cartel_susp_band_{i}") for i in range(5)],
       "pww_ui_blank")
    dt(f"pww_ui_sl_c{k}_l2", [
        (f"{cv(v + '_me', '=', 2)}", f"pww_ui_c{k}_l2_invited"),
        (f"{cv(v + '_me', '=', 1)} {cv(v + '_quota', '<', 0)}", f"pww_ui_c{k}_l2_joined"),
        (f"{cv(v + '_me', '=', 1)} {cv(v + '_room', '<', 0)}", f"pww_ui_c{k}_l2_over"),
        (cv(v + "_me", "=", 1), f"pww_ui_c{k}_l2_member"),
        (cv(v + "_status", "=", 0), f"pww_ui_c{k}_l2_conf"),
        (cv(v + "_short", "=", 0), f"pww_ui_c{k}_l2_prod"),
    ], f"pww_ui_c{k}_l2_short")
    coh = f"Cohesion [pww_ui_sl_c{k}_coh]"
    L(f"pww_ui_c{k}_l2_member", f"§g{coh}{SEP}our quota [?{v}_quota|0]/day, [?{v}_room|0] to spare{SEP}"
                                f"suspicion: [pww_ui_sl_c{k}_susp]§!")
    L(f"pww_ui_c{k}_l2_over", f"§g{coh}{SEP}§!§Rwe sell [?{v}_over|0]/day over quota§!§g{SEP}"
                              f"suspicion: [pww_ui_sl_c{k}_susp]§!")
    L(f"pww_ui_c{k}_l2_joined", f"§g{coh}{SEP}we have joined; quotas start when it takes force§!")
    L(f"pww_ui_c{k}_l2_invited", f"§YWe are invited.§! §gAnswer under $pww_cartel_category$ in Decisions.§!")
    L(f"pww_ui_c{k}_l2_conf", f"§gConference decides on [?{v}_conf.GetDateStringNoHourLong]{SEP}"
                              f"[?{v}_n|0] signed so far§!")
    L(f"pww_ui_c{k}_l2_short", f"§g{coh}{SEP}we are short of [pww_ui_sl_c{k}_res_lc] and pay their price§!")
    L(f"pww_ui_c{k}_l2_prod", f"§g{coh}{SEP}we produce [pww_ui_sl_c{k}_res_lc] but are not a member§!")
    dt(f"pww_ui_sl_c{k}_status", [(cv(f"{v}_status", "=", s), f"pww_cartel_status_{s}") for s in range(4)],
       "pww_ui_blank")
    dt(f"pww_ui_sl_c{k}_mine", [
        (cv(v + "_me", "=", 1), f"pww_ui_c{k}_tt_member"),
        (cv(v + "_me", "=", 2), "pww_ui_cart_tt_invited"),
        (cv(v + "_short", "=", 0), "pww_ui_cart_tt_producer"),
    ], "pww_ui_cart_tt_outsider")
    L(f"pww_ui_c{k}_tt_member", f"We are a member. Quota: [?{v}_quota|0] a day through trade agreements; we sell "
                                f"[?{v}_sold|0]. Suspicion of cheating: [pww_ui_sl_c{k}_susp].")
    L(f"pww_ui_c{k}_tt", f"§H[pww_ui_sl_c{k}_name]§!: [pww_ui_sl_c{k}_status]\\n"
                         f"Chair: [?{v}_leader.GetFlag] [?{v}_leader.GetName]\\nMembers: [?{v}_n|0]\\n"
                         f"Cartel price: [pww_ui_sl_c{k}_price]\\nCohesion: [pww_ui_sl_c{k}_coh]\\n\\n"
                         f"[pww_ui_sl_c{k}_mine]")
L("pww_ui_cart_conf", "§gin conference§!")
L("pww_ui_cart_at_market", "at market")
L("pww_ui_cart_tt_invited", "We are invited to join. Members sell less and hold the price; join or refuse through the decisions.")
L("pww_ui_cart_tt_producer", "We produce what it sells but are not a member. We can sell below its price and take its customers, or join it under Producers' Agreements in Decisions.")
L("pww_ui_cart_tt_outsider", "We are not a member. We are short of what it sells, so its price is ours to pay, or to break by courting a member.")

# ---------------------------------------------------------------- ledger slot loc
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
L("pww_ui_route_0", "overland")
L("pww_ui_route_2", "no safe route")
L("pww_ui_term_reserved", "Pledge, activates if its condition fires")
L("pww_ui_term_open", "Open-ended")
L("pww_ui_bond_tt_line", "Bond between the two sides: ")
for k in range(NAG):
    v = f"pww_ui_l{k}"
    L(f"pww_ui_l{k}_cp", f"[?{v}_cp.GetFlag] [?{v}_cp.GetName]")  # GetNameWithFlag ignores cosmetic names
    res_dt(f"pww_ui_sl_l{k}_res", f"{v}_res")
    res_lc_dt(f"pww_ui_sl_l{k}_res_lc", f"{v}_res", f"pww_ui_l{k}_allres")
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
    # line 2: term (locked or not), bond, delivery route
    dt(f"pww_ui_sl_l{k}_term", [(cv(v + "_st", "=", 7), "pww_ui_term_reserved"),
                                (cv(v + "_open", "=", 1), "pww_ui_term_open"),
                                (cv(v + "_com", "=", 1), f"pww_ui_l{k}_locked")], f"pww_ui_l{k}_runs")
    L(f"pww_ui_l{k}_locked", f"Locked to [?{v}_end.GetDateStringNoHourLong]")
    L(f"pww_ui_l{k}_runs", f"Until [?{v}_end.GetDateStringNoHourLong]")
    bond_dt(f"pww_ui_sl_l{k}_bondw", f"{v}_bond")
    dt(f"pww_ui_sl_l{k}_bond", [(cv(v + "_bond", ">", -1), f"pww_ui_l{k}_bond")], "pww_ui_blank")
    L(f"pww_ui_l{k}_bond", f"{SEP}[pww_ui_sl_l{k}_bondw]")
    dt(f"pww_ui_sl_l{k}_route", [
        (f"{cv(v + '_kind', '>', 0)}", "pww_ui_blank"),
        (cv(v + "_route", "=", 0), f"pww_ui_l{k}_route_0"),
        (cv(v + "_route", "=", 1), f"pww_ui_l{k}_route_1"),
        (cv(v + "_route", "=", 2), f"pww_ui_l{k}_route_2"),
    ], "pww_ui_blank")
    L(f"pww_ui_l{k}_route_0", f"{SEP}$pww_ui_route_0$")
    L(f"pww_ui_l{k}_route_1", f"{SEP}sea, +[?{v}_dsh|0]%")
    L(f"pww_ui_l{k}_route_2", f"{SEP}§R$pww_ui_route_2$§!")
    L(f"pww_ui_l{k}_line2", f"§g[pww_ui_sl_l{k}_term][pww_ui_sl_l{k}_bond][pww_ui_sl_l{k}_route]§!")
    dt(f"pww_ui_sl_l{k}_bondtt", [(cv(v + "_bond", ">", -1), f"pww_ui_l{k}_bondtt")], "pww_ui_blank")
    L(f"pww_ui_l{k}_bondtt", f"\\nBond: [pww_ui_sl_l{k}_bondw]. [pww_ui_sl_l{k}_bonddesc]")
    dt(f"pww_ui_sl_l{k}_bonddesc", [(cv(v + "_bond", "=", i), f"pww_rel_band_{i}_desc") for i in range(REL_BANDS)],
       "pww_ui_blank")
    L(f"pww_ui_l{k}_tt", f"§H[pww_ui_sl_l{k}_vehicle]§!, [pww_ui_sl_l{k}_type] with [?{v}_cp.GetName]\\n"
                         f"[pww_ui_sl_l{k}_terms].\\n[pww_ui_sl_l{k}_end][pww_ui_sl_l{k}_bondtt]\\n\\n"
                         f"[pww_ui_sl_l{k}_status]: [pww_ui_sl_l{k}_sttt]")
    # End button: label and consequences (pww_ledger_withdraw: open deals end
    # cleanly, a small bond loss; locked ones are a breach: default, bond cut,
    # our contract reputation falls)
    armed = f"has_variable = pww_ui_end_arm {cv('pww_ui_end_arm', '=', v + '_id')}"
    dt(f"pww_ui_sl_l{k}_endb", [(armed, "pww_ui_end_confirm"), (cv(v + "_com", "=", 1), "pww_ui_end_break")],
       "pww_ui_end")
    dt(f"pww_ui_sl_l{k}_endtt", [(armed, "pww_ui_end_tt_armed"),
                                 (cv(v + "_com", "=", 1), f"pww_ui_l{k}_end_tt_locked")], f"pww_ui_l{k}_end_tt_open")
    L(f"pww_ui_l{k}_end_tt", f"[pww_ui_sl_l{k}_endtt]")
    L(f"pww_ui_l{k}_end_tt_open", f"§HEnd this agreement§!\\nDeliveries and payments stop at once. It is open-ended, "
                                  f"so ending it breaks no promise, though [?{v}_cp.GetName] will trust us a little "
                                  f"less as a partner.\\n\\nClick, then click again to confirm.")
    L(f"pww_ui_l{k}_end_tt_locked", f"§HBreak this contract§!\\nIt is locked until "
                                    f"[?{v}_end.GetDateStringNoHourLong]. Ending it now is a §Rbreach§!: deliveries "
                                    f"and payments stop, our trade bond with [?{v}_cp.GetName] is cut by half or more, "
                                    f"and every country will trust our contracts less in future talks.\\n\\n"
                                    f"Click, then click again to confirm.")
L("pww_ui_factory", "factory")
L("pww_ui_factories", "factories")
L("pww_ui_pay_pp", " for political power")
L("pww_ui_pay_pp_we", ", and we pay political power")
L("pww_ui_pay_pp_they", ", and they pay political power")
L("pww_ui_open_ended", "Open-ended; either side may end it.")
L("pww_ui_end", "End")
L("pww_ui_end_break", "Break")
L("pww_ui_end_confirm", "§RConfirm§!")
L("pww_ui_end_tt_armed", "§RClick again to end this agreement.§! Switching tabs or pages cancels.")

# ---------------------------------------------------------------- reserve slot loc
# Slots pww_ui_r<k>_*: res stock cap fill days in out fx (fill bar x offset).
L("pww_ui_rsv_year", "over a year")
L("pww_ui_rsv_full", "full")
L("pww_ui_rsv_hold", "§gholding§!")
L("pww_ui_rsv_empty_off", "§gReserves are not tracked in this game.§!")
L("pww_ui_rsv_empty", "§gNothing in store yet. Output nobody buys goes into storage every ten days.§!")
dt("pww_ui_sl_rsv_empty", [("NOT = { has_global_flag = pww_stock_loaded }", "pww_ui_rsv_empty_off")],
   "pww_ui_rsv_empty")
for k in range(NRS):
    v = f"pww_ui_r{k}"
    res_dt(f"pww_ui_sl_r{k}_name", f"{v}_res")
    dt(f"pww_ui_sl_r{k}_days", [(cv(f"{v}_days", ">", 365), "pww_ui_rsv_year")], f"pww_ui_r{k}_days")
    L(f"pww_ui_r{k}_days", f"[?{v}_days|0] days")
    dt(f"pww_ui_sl_r{k}_trend", [(cv(f"{v}_out", ">", 0.05), f"pww_ui_r{k}_draw"),
                                 (cv(f"{v}_in", ">", 0.05), f"pww_ui_r{k}_fill"),
                                 (cv(f"{v}_fill", ">", 94.999), "pww_ui_rsv_full")], "pww_ui_rsv_hold")
    L(f"pww_ui_r{k}_draw", f"§Odrawing [?{v}_out|1]/day§!")
    L(f"pww_ui_r{k}_fill", f"§Gfilling +[?{v}_in|1]/day§!")
    dt(f"pww_ui_sl_r{k}_trend_tt", [(cv(f"{v}_out", ">", 0.05), f"pww_ui_r{k}_draw_tt"),
                                    (cv(f"{v}_in", ">", 0.05), f"pww_ui_r{k}_fill_tt"),
                                    (cv(f"{v}_fill", ">", 94.999), "pww_ui_rsv_full_tt")], "pww_ui_rsv_hold_tt")
    L(f"pww_ui_r{k}_draw_tt", f"Drawing [?{v}_out|1] a day to cover a shortfall.")
    L(f"pww_ui_r{k}_fill_tt", f"Filling [?{v}_in|1] a day from output nobody buys.")
    L(f"pww_ui_r{k}_tt", f"§H[pww_ui_sl_r{k}_name] reserve§!\\nIn store: [?{v}_stock|0] of [?{v}_cap|0] unit-days "
                         f"([?{v}_fill|0]% full).\\nCovers [pww_ui_sl_r{k}_days] of our own use.\\n"
                         f"[pww_ui_sl_r{k}_trend_tt]")
L("pww_ui_rsv_full_tt", "Full: further surplus goes to market.")
L("pww_ui_rsv_hold_tt", "Holding: nothing to store and no shortfall to cover.")
dt("pww_ui_sl_rsv_foot", [
    ("NOT = { has_global_flag = pww_stock_loaded }", "pww_ui_blank"),
    ("has_country_flag = pww_stock_depot_building", "pww_ui_rsv_foot_building"),
    ("check_variable = { pww_stock_depots > 3 }", "pww_ui_rsv_foot_max"),
], "pww_ui_rsv_foot")
L("pww_ui_rsv_foot", "§gDepots: [?pww_stock_depots|0] of 4. More room:§! §H$pww_stock_build_depot$§! "
                     "§gunder $pww_stock_category$ in Decisions.§!")
L("pww_ui_rsv_foot_building", "§gDepots: [?pww_stock_depots|0] of 4. Another is under construction.§!")
L("pww_ui_rsv_foot_max", "§gDepots: 4 of 4, the most we can build.§!")
L("pww_ui_rsv_foot_tt", "Each depot raises the capacity of every reserve and lets it release stock faster in a shortage. Stored stock slowly shrinks, about 2% a month.")

# ---------------------------------------------------------------- market report
BANDS = ["glut", "slack", "steady", "firm", "tight", "scarce", "frantic"]
BAND_TXT = ["glut", "slack", "steady", "firm", "§Ytight§!", "§Oscarce§!", "§Rfrantic§!"]
for i, b_ in enumerate(BANDS):
    L(f"pww_mkt_band_{b_}", BAND_TXT[i])
L("pww_mkt_cause_quiet_season", "quiet trading")
L("pww_ui_mkt_cart_1", "; cartel forming")
L("pww_ui_mkt_cart_2", "; cartel holds price up")
L("pww_ui_mkt_cart_3", "; price war")
g = "global.pww_ui_mkt"
for i, r in enumerate(RES):
    dt(f"pww_ui_sl_mkt_band_{r}", [(cv(f"{g}_band_{r}", "=", j), f"pww_mkt_band_{b_}") for j, b_ in enumerate(BANDS)],
       "pww_ui_blank")
    dt(f"pww_ui_sl_mkt_c1_{r}", [(f"{cv(f'{g}_c1_{r}', '=', 1)} {cv(f'{g}_b1_{r}', '=', 'ROOT')}", "pww_ui_mkt_ourbuy"),
                                 (cv(f"{g}_c1_{r}", "=", 1), f"pww_ui_mkt_buyer_{r}"),
                                 (cv(f"{g}_c1_{r}", "=", 2), f"pww_ui_mkt_rivals_{r}"),
                                 (cv(f"{g}_c1_{r}", "=", 3), "pww_ui_mkt_quiet")], "pww_ui_blank")
    L(f"pww_ui_mkt_buyer_{r}", f", [?{g}_b1_{r}.GetAdjective] buying")
    L(f"pww_ui_mkt_rivals_{r}", f", [?{g}_b1_{r}.GetAdjective] and [?{g}_b2_{r}.GetAdjective] bidding")
    dt(f"pww_ui_sl_mkt_c2_{r}", [(cv(f"{g}_c2_{r}", "=", 1), f"pww_ui_mkt_contested_{r}")], "pww_ui_blank")
    L(f"pww_ui_mkt_contested_{r}", f"; [?{g}_ho_{r}.GetAdjective] output contested")
    # Groups in priority order: (presence trigger, clause defined_text). A line
    # carries the band and the first two present groups (more do not fit a row).
    groups = []
    if i > 0:
        groups.append((f"OR = {{ {cv(f'pww_stock_out_{r}', '>', 0.05)} AND = {{ {cv(f'pww_desp_{r}', '>', 24.999)} "
                       f"{cv(f'pww_stock_{r}', '>', 0.999)} }} }}", f"pww_ui_sl_mkt_c4_{r}"))
        groups.append((cv(f"{g}_c3_{r}", ">", 0), f"pww_ui_sl_mkt_c3_{r}"))
    groups.append((f"{cv(f'{g}_c1_{r}', '>', 0)} {cv(f'{g}_c1_{r}', '<', 3)}", f"pww_ui_sl_mkt_c1_{r}"))
    groups.append((cv(f"{g}_c2_{r}", "=", 1), f"pww_ui_sl_mkt_c2_{r}"))
    # "quiet trading" only stands alone: it never follows a real clause
    quiet = cv(f"{g}_c1_{r}", "=", 3)
    for gi, (_, gdt) in enumerate(groups):
        L(f"pww_ui_mkt_g{gi}_{r}", f"[{gdt}]")
    dt(f"pww_ui_sl_mkt_x1_{r}", [(p, f"pww_ui_mkt_g{gi}_{r}") for gi, (p, _) in enumerate(groups)]
       + [(quiet, "pww_ui_mkt_quiet")], "pww_ui_blank")
    dt(f"pww_ui_sl_mkt_x2_{r}", [(f"{p} OR = {{ {' '.join(f'AND = {{ {q} }}' for q, _ in groups[:gi])} }}",
                                  f"pww_ui_mkt_g{gi}_{r}")
                                 for gi, (p, _) in enumerate(groups) if gi > 0], "pww_ui_blank")
    pieces = f"[pww_ui_sl_mkt_band_{r}][pww_ui_sl_mkt_x1_{r}][pww_ui_sl_mkt_x2_{r}]"
    if i > 0:
        dt(f"pww_ui_sl_mkt_c3_{r}", [(cv(f"{g}_c3_{r}", "=", c), f"pww_ui_mkt_cart_{c}") for c in (1, 2, 3)],
           "pww_ui_blank")
        # our own reserve, only where it matters: we are drawing on it, or short and holding some
        dt(f"pww_ui_sl_mkt_c4_{r}", [
            (cv(f"pww_stock_out_{r}", ">", 0.05), f"pww_ui_mkt_draw_{r}"),
            (f"{cv(f'pww_desp_{r}', '>', 24.999)} {cv(f'pww_stock_{r}', '>', 0.999)}", f"pww_ui_mkt_hold_{r}"),
        ], "pww_ui_blank")
        L(f"pww_ui_mkt_draw_{r}", f"; drawing our reserve, [?pww_stock_days_{r}|0] days left")
        L(f"pww_ui_mkt_hold_{r}", f"; our reserve covers [?pww_stock_days_{r}|0] days")
    L(f"pww_ui_mkt_line_{r}", f"{RES_NAME[i]}: {pieces}.")
L("pww_ui_mkt_quiet", ", quiet trading")
L("pww_ui_mkt_ourbuy", ", mostly our own buying")


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
    for r in range(NNA):
        y = (NSIT + r) * AROW          # moved up to (pww_ui_ns + r) rows by pww_ui_layout
        b += btn(f"pww_ui_na{r}_btn", 0, y, "GFX_pww_ui_alert_row", size=(AW, AROW - 2), tip="pww_ui_news_alert_tt",
                 click="click_default")
        b += tb(f"pww_ui_na{r}_txt", 10, y + 4, f"[pww_ui_sl_n{r}]", AW - 20)
    return b


# =========================================================================== Dossier
# A card over the diplomacy tab body, starting below the party box so the
# toggle (party box corner) is never covered. Children placed outside the
# diplomacy view's bounds are clipped (tried: x 534 did not render), so it
# stays inside. Its own close button; its background takes the mouse so
# clicks never reach the vanilla actions underneath.
OW = 514
OX, OY = 8, 152                      # parent (diplomacy view) coordinates
TOGGLE = (416, 116)                  # dossier toggle: party box corner
L("pww_ui_dos_btn", "[pww_ui_sl_dos_btn]")
L("pww_ui_dos_btn_plain", "Dossier")
L("pww_ui_dos_btn_hot", "§YDossier§!")
L("pww_ui_dos_btn_close", "Close")
L("pww_ui_dos_btn_tt", "Commercial dossier on [FROM.GetName]: what they produce and need, reserves, our trade bond, their exports, their agreements, and any demand or Situation between us.")
L("pww_ui_dos_close_tt", "Close the dossier.")
L("pww_dossier_title", "Commercial Dossier: [FROM.GetName]")
L("pww_ui_dos_imports", "Import reliance: [pww_ui_sl_dos_imp]")
IMP = ["Self-sufficient", "Light", "Moderate", "§YHeavy§!", "§ODependent§!"]
for i, t in enumerate(IMP):
    L(f"pww_ui_imp_{i}", t)
L("pww_ui_imp_tt", "Share of their resource use met by imports and supply agreements.")
PRESS = ["§gnone§!", "tight", "§Yshort§!", "§Osevere§!", "§Rdesperate§!"]
for i, t in enumerate(PRESS):
    L(f"pww_ui_press_{i}", t)
dt("pww_ui_sl_dos_btn", [("ROOT = { has_country_flag = pww_ui_dos_open }", "pww_ui_dos_btn_close"),
                         (f"OR = {{ check_variable = {{ pww_ui_rd_viewer = ROOT }} check_variable = {{ pww_ui_pr_viewer = ROOT }} check_variable = {{ pww_ui_st_viewer = ROOT }} }}",
                          "pww_ui_dos_btn_hot")], "pww_ui_dos_btn_plain")
dt("pww_ui_sl_dos_imp", [(cv("pww_ui_imp_band", "=", i), f"pww_ui_imp_{i}") for i in range(5)], "pww_ui_imp_0")
# Resource cells (viewer independent, pww_ui_country_res_lines): net = output
# beyond their own use before any trade (bal + exports - imports), unsold =
# positive balance, short = negative balance. Line 1 the net, line 2 what
# happens to it.
for i, r in enumerate(RES):
    v = f"pww_ui_rs_{r}"
    dt(f"pww_ui_sl_rn_{r}", [(cv(f"{v}_net", ">", 0.5), f"pww_ui_rn_pos_{r}"),
                             (cv(f"{v}_net", "<", -0.5), f"pww_ui_rn_neg_{r}")], "pww_ui_rn_zero")
    L(f"pww_ui_rn_pos_{r}", f"§G+[?{v}_net|0]§!")
    L(f"pww_ui_rn_neg_{r}", f"§O[?{v}_net|0]§!")
    dt(f"pww_ui_sl_rw_{r}", [
        (f"{cv(v + '_bal', '<', -0.5)}", f"pww_ui_rw_short_{r}"),
        (f"{cv(v + '_net', '>', 0.5)} {cv(v + '_bal', '>', 0.5)}", f"pww_ui_rw_unsold_{r}"),
        (cv(v + "_net", ">", 0.5), "pww_ui_rw_sold"),
        (cv(v + "_net", "<", -0.5), "pww_ui_rw_imports"),
    ], "pww_ui_blank")
    L(f"pww_ui_rw_short_{r}", f"§Rshort [?{v}_short|0]§!")
    L(f"pww_ui_rw_unsold_{r}", f"§g[?{v}_bal|0] unsold§!")
    dt(f"pww_ui_sl_press_{r}", [(cv(f"pww_desp_{r}", ">", t), f"pww_ui_press_{j}") for j, t in
                                [(4, 79), (3, 59), (2, 39), (1, 19)]], "pww_ui_press_0")
    dt(f"pww_ui_sl_rtt_{r}", [(f"{cv(v + '_bal', '>', 0.5)}", f"pww_ui_rtt_unsold_{r}"),
                              (f"{cv(v + '_bal', '<', -0.5)}", f"pww_ui_rtt_short_{r}")], "pww_ui_rtt_even")
    L(f"pww_ui_rtt_unsold_{r}", f"[?{v}_bal|0] a day finds no buyer.")
    L(f"pww_ui_rtt_short_{r}", f"§RShort [?{v}_short|0] a day§! even after imports.")
    L(f"pww_ui_rs_{r}_tt", f"§H{RES_NAME[i]}§!: [FROM.GetName]\\nOutput [?{v}_prod|0] a day, own use [?{v}_use|0].\\n"
                           f"Imports [?{v}_imp|0], exports [?{v}_exp|0].\\n[pww_ui_sl_rtt_{r}]\\n"
                           f"How hard pressed for it: [pww_ui_sl_press_{r}].[pww_ui_sl_rcap_{r}]")
    # production capacity (capacity lane): mines idle below 1, expanding when the trend is 2
    cap = f"pww_cap_{r}"
    dt(f"pww_ui_sl_rcap_{r}", [
        (f"has_variable = {cap} {cv(f'pww_cap_trend_{r}', '=', 2)}", f"pww_ui_rcap_up_{r}"),
        (f"has_variable = {cap} {cv(cap, '<', 0.995)}", f"pww_ui_rcap_idle_{r}"),
        (f"has_variable = {cap} {cv(cap, '>', 1.005)}", f"pww_ui_rcap_high_{r}"),
    ], "pww_ui_blank")
    L(f"pww_ui_rcap_idle_{r}", f"\\n§YMines idle:§! working at [?{cap}|%0] of capacity for want of buyers.")
    L(f"pww_ui_rcap_up_{r}", f"\\n§GExpanding:§! output at [?{cap}|%0] of the old capacity, and rising.")
    L(f"pww_ui_rcap_high_{r}", f"\\nOutput at [?{cap}|%0] of the old capacity after new investment.")
L("pww_ui_rn_zero", "§g·§!")
L("pww_ui_rw_sold", "§gall sold§!")
L("pww_ui_rw_imports", "§gimported§!")
L("pww_ui_rtt_even", "Supply and use balance.")
# bond (viewer dependent, stored on the target as var@viewer by pww_ui_views)
L("pww_ui_dos_bond", "Trade bond: [pww_ui_sl_dos_bondw]")
dt("pww_ui_sl_dos_bondw", [(cv("pww_ui_vb@ROOT", "=", i), f"pww_ui_dos_bondw_{i}") for i in range(REL_BANDS)],
   "pww_ui_dos_bondw_none")
for i in range(REL_BANDS):
    L(f"pww_ui_dos_bondw_{i}", f"§H$pww_rel_band_{i}$§!")
L("pww_ui_dos_bondw_none", "§gunknown§!")
dt("pww_ui_sl_dos_bond0", [(cv("pww_ui_vb0@ROOT", "=", i), f"pww_rel_band_{i}") for i in range(REL_BANDS)],
   "pww_ui_blank")
dt("pww_ui_sl_dos_bond1", [(cv("pww_ui_vb1@ROOT", "=", i), f"pww_rel_band_{i}") for i in range(REL_BANDS)],
   "pww_ui_blank")
L("pww_ui_dos_bond_tt", "§HTrade bond§!\\nTheir deliveries to us: [pww_ui_sl_dos_bond0]\\nOur deliveries to them: [pww_ui_sl_dos_bond1]\\n\\nBonds grow with every month of honoured deliveries and sour after a default, cutoff or walkout. A strong bond allows locked contracts and makes the buyer costly to poach.")
# reserves sentence (viewer independent)
RVB = ["thin", "some", "ample", "deep"]
for i, w in enumerate(RVB):
    L(f"pww_ui_rvb_{i}", w)
for j in range(NRV):
    dt(f"pww_ui_sl_rv{j}_b", [(cv(f"pww_ui_rv{j}_b", "=", i), f"pww_ui_rvb_{i}") for i in range(4)], "pww_ui_blank")
    res_lc_dt(f"pww_ui_sl_rv{j}_r", f"pww_ui_rv{j}_res")
rv = lambda j: f"[pww_ui_sl_rv{j}_b] [pww_ui_sl_rv{j}_r]"
L("pww_ui_dos_rsv_0", "Reserves: none to speak of.")
L("pww_ui_dos_rsv_1", f"Reserves: {rv(0)}.")
L("pww_ui_dos_rsv_2", f"Reserves: {rv(0)} and {rv(1)}.")
L("pww_ui_dos_rsv_3", f"Reserves: {rv(0)}, {rv(1)} and {rv(2)}.")
dt("pww_ui_sl_dos_rsv", [(cv("pww_ui_nrv", "=", n), f"pww_ui_dos_rsv_{n}") for n in (3, 2, 1)], "pww_ui_dos_rsv_0")
L("pww_ui_dos_rsv_tt", "Strategic reserves, in days of their own use: deep 90 or more, ample 45, some 15, thin under 15. Deepest first.")
# exports and delivery route to us
for j in (1, 2):
    res_lc_dt(f"pww_ui_sl_dos_x{j}", f"pww_ui_x{j}")
L("pww_ui_dos_exp_0", "Exports nothing to speak of.")
L("pww_ui_dos_exp_1", "Main export: [pww_ui_sl_dos_x1]. [pww_ui_sl_dos_route]")
L("pww_ui_dos_exp_2", "Main exports: [pww_ui_sl_dos_x1], [pww_ui_sl_dos_x2]. [pww_ui_sl_dos_route]")
dt("pww_ui_sl_dos_exp", [(cv("pww_ui_x2", ">", -1), "pww_ui_dos_exp_2"), (cv("pww_ui_x1", ">", -1), "pww_ui_dos_exp_1")],
   "pww_ui_dos_exp_0")
COSTW = ["next to no delivery cost", "modest delivery cost", "costly to deliver", "very costly to deliver"]
for i, w in enumerate(COSTW):
    L(f"pww_ui_dos_cost_{i}", w)
dt("pww_ui_sl_dos_cost", [(cv("pww_ui_vc@ROOT", "=", i), f"pww_ui_dos_cost_{i}") for i in range(4)], "pww_ui_blank")
L("pww_ui_dos_route_0", "Reaches us overland, [pww_ui_sl_dos_cost].")
L("pww_ui_dos_route_1", "Reaches us by sea, [pww_ui_sl_dos_cost].")
L("pww_ui_dos_route_2", "§RNo safe route to us.§!")
dt("pww_ui_sl_dos_route", [(cv("pww_ui_vr@ROOT", "=", i), f"pww_ui_dos_route_{i}") for i in range(3)], "pww_ui_blank")
L("pww_ui_dos_exp_tt", "Their largest sales abroad, and how a shipment from them would reach us: delivery cost on top of the price, from distance, convoys and raiding.")
# known agreement rows (target perspective: "they")
L("pww_ui_dos_nag_0", "§gNo long-term trade agreements with anyone.§!")
L("pww_ui_dos_kmore", "§g...and [?pww_ui_nk_more|0] more agreements§!")
L("pww_ui_lock_1", "§glocked§!")
L("pww_ui_lock_0", "§gopen§!")
L("pww_ui_dos_poach", "Poach")
for k in range(NK):
    v = f"pww_ui_k{k}"
    res_lc_dt(f"pww_ui_sl_k{k}_res_lc", f"{v}_res")
    dt(f"pww_ui_sl_k{k}", [
        (f"{cv(v + '_kind', '>', 0)} {cv(v + '_side', '=', 1)}", f"pww_ui_k{k}_lease_in"),
        (cv(v + "_kind", ">", 0), f"pww_ui_k{k}_lease_out"),
        (cv(v + "_side", "=", 1), f"pww_ui_k{k}_buy"),
    ], f"pww_ui_k{k}_sell")
    L(f"pww_ui_k{k}_lease_in", f"Leases [?{v}_state.GetName] from [?{v}_cp.GetFlag] [?{v}_cp.GetName]")
    L(f"pww_ui_k{k}_lease_out", f"[?{v}_state.GetName] leased to [?{v}_cp.GetFlag] [?{v}_cp.GetName]")
    L(f"pww_ui_k{k}_buy", f"Buys [?{v}_amt|0] [pww_ui_sl_k{k}_res_lc] from [?{v}_cp.GetFlag] [?{v}_cp.GetName]")
    L(f"pww_ui_k{k}_sell", f"Sells [?{v}_amt|0] [pww_ui_sl_k{k}_res_lc] to [?{v}_cp.GetFlag] [?{v}_cp.GetName]")
    dt(f"pww_ui_sl_k{k}_st", [(cv(f"{v}_st", "=", s), key) for s, key in STATUS.items()], "pww_ui_blank")
    dt(f"pww_ui_sl_k{k}_lock", [(cv(f"{v}_com", "=", 1), "pww_ui_lock_1")], "pww_ui_lock_0")
    # leases (kind > 0) carry no lock word
    dt(f"pww_ui_sl_k{k}_right", [(cv(f"{v}_kind", ">", 0), f"pww_ui_k{k}_right_lease")], f"pww_ui_k{k}_right")
    L(f"pww_ui_k{k}_right", f"[pww_ui_sl_k{k}_lock]{SEP}[pww_ui_sl_k{k}_st]")
    L(f"pww_ui_k{k}_right_lease", f"[pww_ui_sl_k{k}_st]")
    bond_dt(f"pww_ui_sl_k{k}_bondw", f"{v}_bond")
    dt(f"pww_ui_sl_k{k}_term", [(cv(v + "_open", "=", 1), "pww_ui_term_open"),
                                (cv(v + "_com", "=", 1), f"pww_ui_k{k}_locked")], f"pww_ui_k{k}_runs")
    L(f"pww_ui_k{k}_locked", f"Locked until [?{v}_end.GetDateStringNoHourLong]")
    L(f"pww_ui_k{k}_runs", f"Runs until [?{v}_end.GetDateStringNoHourLong]")
    L(f"pww_ui_k{k}_tt", f"§H[pww_ui_sl_k{k}]§!\\n[pww_ui_sl_k{k}_term].\\n"
                         f"Bond between the two: [pww_ui_sl_k{k}_bondw].\\n[pww_ui_sl_k{k}_st]")
    L(f"pww_ui_k{k}_poach_tt", f"§HPoach this supplier§!\\n[FROM.GetName] buys [pww_ui_sl_k{k}_res_lc] from "
                               f"[?{v}_cp.GetName] ([pww_ui_sl_k{k}_bondw]). Beat that deal and the buyer switches "
                               f"to us; a deep bond makes the switch dearer.\\n\\nClick to mark this deal and close "
                               f"the dossier, then use §H$PWW_DIPLO_POACH_SUPPLIER_TITLE$§! in the actions list.")
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

DOS_ROW = 18
DOS_K = 172                          # first agreement row
DOS_FLOW = {}                        # element -> offset below the last agreement row
# the demand block sits under the last agreement row (per target: pww_ui_dossier_layout)
DOS_BLOCK = {0: 18, 1: 72}           # demand block height: 0 quiet line, 1 demand/Situation lines
DOS_PAD = 14                         # space under the last line


def dos_height(rows, block):
    return DOS_K + rows * DOS_ROW + 2 + 8 + DOS_BLOCK[block] + DOS_PAD


def poach_cond(k):
    """Mirrors pww_diplo_poach_supplier's visibility (active, open-ended supply
    deal the target buys from a third party) plus: we produce the resource."""
    v = f"pww_ui_k{k}"
    produces = " ".join(f"AND = {{ {cv(v + '_res', '=', i)} ROOT = {{ pww_core_produces_{RES[i]} = yes }} }}"
                        for i in SRES)
    return (f"check_variable = {{ pww_ui_nk > {k} }} {cv(v + '_side', '=', 1)} {cv(v + '_kind', '=', 0)} "
            f"{cv(v + '_st', '=', 1)} {cv(v + '_com', '=', 0)} NOT = {{ check_variable = {{ {v}_cp = ROOT }} }} "
            f"OR = {{ {produces} }}")


DOS_BG = [(rows, block) for rows in range(1, NK + 2) for block in DOS_BLOCK]


def dossier_body():
    # backgrounds first (drawn under everything); one per content height
    b = "".join(icon(f"pww_ui_dos_bg_{r}_{q}", 0, 0, f"GFX_pww_ui_dos_bg_{r}_{q}", solid=True) for r, q in DOS_BG)
    b += tb("pww_ui_dos_title", 14, 11, "pww_dossier_title", OW - 60, h=20, font=F18)
    b += btn("pww_ui_dos_close", OW - 37, 8, "GFX_closebutton", tip="pww_ui_dos_close_tt", click="click_close")
    # resources: seven equal cells, icon over the net figure and what becomes of it
    cw = (OW - 24) // 7
    for i, r in enumerate(RES):
        cx = 12 + i * cw
        tip = f"pww_ui_rs_{r}_tt"
        b += icon(f"pww_ui_dos_{r}_icon", cx + (cw - 27) // 2, 38, "GFX_resources_strip", frame=i + 1, tip=tip)
        b += tb(f"pww_ui_dos_{r}_net", cx, 64, f"[pww_ui_sl_rn_{r}]", cw, fmt="centre", tip=tip)
        b += tb(f"pww_ui_dos_{r}_word", cx, 81, f"[pww_ui_sl_rw_{r}]", cw, fmt="centre", tip=tip)
    y = 108
    b += tb("pww_ui_dos_imp", 14, y, "pww_ui_dos_imports", 220, tip="pww_ui_imp_tt")
    b += tb("pww_ui_dos_bond", OW - 14 - 220, y, "pww_ui_dos_bond", 220, fmt="right", tip="pww_ui_dos_bond_tt")
    b += tb("pww_ui_dos_rsv", 14, y + 18, "[pww_ui_sl_dos_rsv]", OW - 28, tip="pww_ui_dos_rsv_tt")
    b += tb("pww_ui_dos_exp", 14, y + 36, "[pww_ui_sl_dos_exp]", OW - 28, tip="pww_ui_dos_exp_tt")
    b += icon("pww_ui_dos_div0", 4, DOS_K - 10, "GFX_pww_ui_divider", scale=f"{(OW - 8) / 514:.3f}")
    b += tb("pww_ui_dos_nag0", 14, DOS_K, "pww_ui_dos_nag_0", OW - 28)
    for k in range(NK):
        yy = DOS_K + k * DOS_ROW
        b += tb(f"pww_ui_dos_k{k}", 14, yy, f"[pww_ui_sl_k{k}]", OW - 28 - 150, tip=f"pww_ui_k{k}_tt")
        b += tb(f"pww_ui_dos_k{k}_st", OW - 14 - 146, yy, f"[pww_ui_sl_k{k}_right]", 146, fmt="right",
                tip=f"pww_ui_k{k}_tt")
        b += btn(f"pww_ui_dos_k{k}_poach", OW - 14 - 58, yy - 1, "GFX_pww_ui_alert_row", text="pww_ui_dos_poach",
                 size=(58, 20), tip=f"pww_ui_k{k}_poach_tt", click="click_default")
    y0 = DOS_K + NK * DOS_ROW + 2      # static position (three rows)

    def f(name, off, s):
        DOS_FLOW[name] = off
        return s
    b += f("pww_ui_dos_kmore", -DOS_ROW - 2, tb("pww_ui_dos_kmore", 14, y0 - DOS_ROW - 2, "pww_ui_dos_kmore", OW - 28))
    b += f("pww_ui_dos_div", 0, icon("pww_ui_dos_div", 4, y0, "GFX_pww_ui_divider", scale=f"{(OW - 8) / 514:.3f}"))
    y = y0 + 8
    # our demand (readout), their demand on us, a shared Situation
    b += f("pww_ui_dos_rd_head", 8, tb("pww_ui_dos_rd_head", 12, y, "pww_ui_rd_head", OW - 24, tip="pww_ui_rd_head_tt"))
    b += f("pww_ui_dos_rd_for", 26, tb("pww_ui_dos_rd_for", 12, y + 18, "pww_ui_rd_for", OW - 24, tip="pww_ui_rd_for_tt"))
    b += f("pww_ui_dos_rd_hold", 44, tb("pww_ui_dos_rd_hold", 12, y + 36, "pww_ui_rd_hold", OW - 24,
                                         tip="pww_ui_rd_hold_tt"))
    b += f("pww_ui_dos_rd_more", 62, tb("pww_ui_dos_rd_more", 12, y + 54, "pww_ui_rd_more", OW - 24))
    b += f("pww_ui_dos_pr_head", 8, tb("pww_ui_dos_pr_head", 12, y, "pww_ui_pr_head", OW - 24, h=34))
    b += f("pww_ui_dos_st", 44, tb("pww_ui_dos_st", 12, y + 36, "pww_ui_dos_st", OW - 24, h=34))
    b += f("pww_ui_dos_quiet", 8, tb("pww_ui_dos_quiet", 12, y, "pww_ui_dos_quiet", OW - 24))
    assert y + DOS_BLOCK[1] + DOS_PAD <= dos_height(NK + 1, 1), y
    return b


def dossier_toggle_body():
    return btn("pww_ui_dos_toggle", 0, 0, "GFX_button_94x31", text="pww_ui_dos_btn", tip="pww_ui_dos_btn_tt",
               click="click_default")


# --------------------------------------------------------------------------- GUI file
desk = desk_body()
gui = ["# Power Without War: UI lane layout (generated by tools/pww_ui_gen.py).\n",
       "# Trade Desk (two windows with identical bodies: one rides on the trade view,\n",
       "# one floats when opened from the alert strip), the trade view button, the\n",
       "# alert strip on the top bar, and the Dossier inside the diplomacy tab.\n",
       "guiTypes = {\n"]
gui.append(window("pww_ui_desk_trade", 696, 0, DW, DESK_HS[0], desk))
gui.append(window("pww_ui_desk_float", 683, 78, DW, DESK_HS[0], desk))
gui.append(window("pww_ui_desk_button", 496, 6, 148, 34, desk_button_body()))
gui.append(window("pww_ui_alerts", -710, 90, AW, (NSIT + NNA) * AROW, alert_body(), orientation="UPPER_RIGHT"))
gui.append(window("pww_ui_dossier", OX, OY, OW, dos_height(1, 0), dossier_body()))  # smallest card: the backgrounds size the rest
gui.append(window("pww_ui_dossier_toggle", TOGGLE[0], TOGGLE[1], 94, 31, dossier_toggle_body()))
gui.append("}\n")

# content-sized backgrounds: dossier (rows 1..NK+1, demand block), desk (height steps)
def panel_bg(name, w, h):
    return ("\tcorneredTileSpriteType = {\n"
            f"\t\tname = \"{name}\"\n"
            f"\t\tsize = {{ x = {w} y = {h} }}\n"
            "\t\ttextureFile = \"gfx//interface//tiles//tiled_window_1b_border.dds\"\n"
            "\t\tborderSize = { x = 64 y = 64 }\n\t\ttilingCenter = yes\n\t}\n")


DOS_BG_GFX = ("".join(panel_bg(f"GFX_pww_ui_dos_bg_{r}_{q}", OW, dos_height(r, q)) for r, q in DOS_BG)
              + "".join(panel_bg(f"GFX_pww_ui_desk_bg_{h}", DW, h) for h in DESK_HS))

gfx = f"""# Power Without War: UI lane sprites (vanilla textures only).
spriteTypes = {{
	corneredTileSpriteType = {{
		name = "GFX_pww_ui_alert_row"
		size = {{ x = 32 y = 32 }}
		textureFile = "gfx/interface/tiles/tiled_mini_dialog.dds"
		borderSize = {{ x = 12 y = 12 }}
		effectFile = "gfx/FX/buttonstate.lua"
	}}
	spriteType = {{
		name = "GFX_pww_ui_divider"
		texturefile = "gfx/interface/divider.dds"
	}}
	corneredTileSpriteType = {{
		name = "GFX_pww_ui_bar_bg"
		size = {{ x = {BAR_W} y = {BAR_H} }}
		textureFile = "gfx/interface/construction_progressbar_bg.dds"
		borderSize = {{ x = 0 y = 0 }}
		tilingCenter = no
	}}
	corneredTileSpriteType = {{
		name = "GFX_pww_ui_bar_fill"
		size = {{ x = {BAR_W} y = {BAR_H} }}
		textureFile = "gfx/interface/construction_progressbar.dds"
		borderSize = {{ x = 0 y = 0 }}
		tilingCenter = no
	}}
{DOS_BG_GFX}}}
"""


# --------------------------------------------------------------------------- scripted GUIs
def desk_triggers():
    t = []
    for name in VIS:
        tab = TABOF[name]
        parts = []
        if tab >= 0:
            parts.append(ON_TAB.format(t=tab))
        if VIS[name]:
            parts.append(VIS[name])
        if parts:
            t.append(f"\t\t\t{name}_visible = {{ {' '.join(parts)} }}\n")
    return "".join(t)


def desk_properties():
    # one block per element: a repeated element key overrides the earlier one
    props = {}
    for t in range(len(TABS)):
        props.setdefault(f"pww_ui_tab{t}", []).append(f"frame = ROOT.pww_ui_tabf{t}")
    for k in range(NC):
        props.setdefault(f"pww_ui_dc{k}_icon", []).append(f"frame = ROOT.pww_ui_c{k}_frame")
    for k in range(NO):
        props.setdefault(f"pww_ui_do{k}_icon", []).append(f"frame = ROOT.pww_ui_o{k}_frame")
    for k in range(NRS):
        props.setdefault(f"pww_ui_dr{k}_icon", []).append(f"frame = ROOT.pww_ui_r{k}_frame")
        props.setdefault(f"pww_ui_dr{k}_fill", []).append(f"x = ROOT.pww_ui_r{k}_fx")
    for name in FLOW:
        props.setdefault(name, []).append(f"y = ROOT.{uy(name)}")
    return "".join(f"\t\t\t{n} = {{ {' '.join(v)} }}\n" for n, v in props.items())


def desk_effects():
    disarm = "\t\t\t\tclear_variable = pww_ui_end_arm\n"
    close = ("\t\t\t\tclr_country_flag = pww_ui_desk_open\n\t\t\t\tclr_country_flag = pww_ui_desk_float\n"
             "\t\t\t\tset_variable = { pww_ui_focus = -1 }\n" + disarm + "\t\t\t\tadd_to_variable = { pww_ui_dirty = 1 }\n")
    e = f"\t\t\tpww_ui_desk_close_click = {{\n{close}\t\t\t}}\n"
    for t in range(len(TABS)):
        e += (f"\t\t\tpww_ui_tab{t}_click = {{\n\t\t\t\tset_variable = {{ pww_ui_tab = {t} }}\n{disarm}"
              f"\t\t\t\tpww_ui_refresh = yes\n\t\t\t}}\n")
    e += ("\t\t\tpww_ui_desk_pg_next_click = {\n\t\t\t\tadd_to_variable = { pww_ui_page = 1 }\n"
          "\t\t\t\tif = { limit = { NOT = { check_variable = { pww_ui_page < pww_ui_npages } } } set_variable = { pww_ui_page = 0 } }\n"
          + disarm + "\t\t\t\tpww_ui_refresh = yes\n\t\t\t}\n")
    e += ("\t\t\tpww_ui_desk_pg_prev_click = {\n\t\t\t\tsubtract_from_variable = { pww_ui_page = 1 }\n"
          "\t\t\t\tif = { limit = { check_variable = { pww_ui_page < 0 } } set_variable = { pww_ui_page = pww_ui_npages } subtract_from_variable = { pww_ui_page = 1 } }\n"
          + disarm + "\t\t\t\tpww_ui_refresh = yes\n\t\t\t}\n")
    # End / Break: arm on the first click, end on the second (the player is the
    # one ending it: a locked contract is his breach)
    for k in range(NAG):
        e += (f"\t\t\tpww_ui_dl{k}_end_click = {{\n"
              f"\t\t\t\tif = {{\n\t\t\t\t\tlimit = {{ has_variable = pww_ui_end_arm check_variable = {{ pww_ui_end_arm = pww_ui_l{k}_id }} }}\n"
              f"\t\t\t\t\tset_temp_variable = {{ pww_l_ag = pww_ui_l{k}_id }}\n"
              f"\t\t\t\t\tset_temp_variable = {{ pww_l_by = THIS }}\n"
              f"\t\t\t\t\tset_temp_variable = {{ pww_l_cause = 0 }}\n"
              f"\t\t\t\t\tpww_ledger_withdraw = yes\n"
              f"\t\t\t\t\tlog = \"[GetDateText] PWW_UI end [THIS.GetTag] agreement [?pww_ui_l{k}_id|0]\"\n"
              f"\t\t\t\t\tclear_variable = pww_ui_end_arm\n"
              f"\t\t\t\t}}\n\t\t\t\telse = {{\n\t\t\t\t\tset_variable = {{ pww_ui_end_arm = pww_ui_l{k}_id }}\n\t\t\t\t}}\n"
              f"\t\t\t\tpww_ui_refresh = yes\n\t\t\t}}\n")
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
    sg.append("\t\tproperties = {\n" + desk_properties() + "\t\t}\n")
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
					set_variable = { pww_ui_news_ack = global.num_days }
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
    f"\t\t\t\tset_variable = {{ pww_ui_tab = 0 }}\n"
    f"\t\t\t\tpww_ui_refresh = yes\n\t\t\t}}\n" for k in range(NSIT))
al_tr = "".join(
    f"\t\t\tpww_ui_al{k}_{e}_visible = {{ check_variable = {{ pww_ui_ns > {k} }} }}\n"
    for k in range(NSIT) for e in ("btn", "txt", "date"))
al_tr += "".join(f"\t\t\tpww_ui_na{r}_{e}_visible = {{ check_variable = {{ pww_ui_nfresh > {r} }} }}\n"
                 for r in range(NNA) for e in ("btn", "txt"))
NEWS_ACK = "\t\t\t\tset_variable = { pww_ui_news_ack = global.num_days }\n"
al_fx += "".join(f"\t\t\tpww_ui_na{r}_btn_click = {{\n\t\t\t\tclr_country_flag = pww_ui_desk_open\n"
                 f"\t\t\t\tset_country_flag = pww_ui_desk_float\n\t\t\t\tset_variable = {{ pww_ui_tab = 0 }}\n"
                 f"{NEWS_ACK}\t\t\t\tpww_ui_refresh = yes\n\t\t\t}}\n" for r in range(NNA))
al_props = "".join(f"\t\t\tpww_ui_na{r}_{e} = {{ y = ROOT.pww_uy_na{r}{'_t' if e == 'txt' else ''} }}\n"
                   for r in range(NNA) for e in ("btn", "txt"))
sg.append(f"""	pww_ui_alerts_gui = {{
		context_type = player_context
		window_name = "pww_ui_alerts"
		parent_window_token = top_bar
		visible = {{ OR = {{ check_variable = {{ pww_ui_ns > 0 }} check_variable = {{ pww_ui_nfresh > 0 }} }} }}
		dirty = pww_ui_dirty
		effects = {{
{al_fx}		}}
		triggers = {{
{al_tr}		}}
		properties = {{
{al_props}		}}
		ai_enabled = {{ always = no }}
	}}
""")
foreign = "NOT = { tag = ROOT } ROOT = { is_ai = no }"
dos_tr = ["\t\t\tpww_ui_dos_nag0_visible = { check_variable = { pww_ui_nk = 0 } }\n",
          "\t\t\tpww_ui_dos_kmore_visible = { check_variable = { pww_ui_nk_more > 0 } }\n"]
for k in range(NK):
    on = f"check_variable = {{ pww_ui_nk > {k} }}"
    # NOT with several children is NOR in Paradox script: wrap the conjunction in AND
    dos_tr += [f"\t\t\tpww_ui_dos_k{k}_visible = {{ {on} }}\n",
               f"\t\t\tpww_ui_dos_k{k}_st_visible = {{ {on} NOT = {{ AND = {{ {poach_cond(k)} }} }} }}\n",
               f"\t\t\tpww_ui_dos_k{k}_poach_visible = {{ {poach_cond(k)} }}\n"]
rd = "check_variable = { pww_ui_rd_viewer = ROOT }"
pr = "check_variable = { pww_ui_pr_viewer = ROOT }"
st = "check_variable = { pww_ui_st_viewer = ROOT }"
# background by content height: rows (pww_ui_dos_rows, layout) and block (viewer)
quiet = f"NOT = {{ {rd} }} NOT = {{ {pr} }} NOT = {{ {st} }}"
for r, q in DOS_BG:
    blk = quiet if q == 0 else f"OR = {{ {rd} {pr} {st} }}"
    dos_tr.append(f"\t\t\tpww_ui_dos_bg_{r}_{q}_visible = {{ {cv('pww_ui_dos_rows', '=', r)} {blk} }}\n")
for e in ("head", "for", "hold", "more"):
    dos_tr.append(f"\t\t\tpww_ui_dos_rd_{e}_visible = {{ {rd} }}\n")
dos_tr.append(f"\t\t\tpww_ui_dos_pr_head_visible = {{ {pr} NOT = {{ {rd} }} }}\n")
dos_tr.append(f"\t\t\tpww_ui_dos_st_visible = {{ {st} NOT = {{ {rd} }} }}\n")
dos_tr.append(f"\t\t\tpww_ui_dos_quiet_visible = {{ NOT = {{ {rd} }} NOT = {{ {pr} }} NOT = {{ {st} }} }}\n")
# the demand block flows under the last agreement row: y vars live on the target
dos_props = "".join(f"\t\t\t{n} = {{ y = {uy(n)} }}\n" for n in DOS_FLOW)
# HOOK (valuation lane): the Poach button marks the deal on the viewer
# (ROOT.pww_ui_poach_ag = ledger id, ROOT.pww_ui_poach_target = the buyer)
# and closes the dossier so the actions list (Poach Supplier) is in view.
dos_fx = "".join(
    f"\t\t\tpww_ui_dos_k{k}_poach_click = {{\n"
    f"\t\t\t\tset_temp_variable = {{ pww_ui_pk = pww_ui_k{k}_id }}\n"
    f"\t\t\t\tset_temp_variable = {{ pww_ui_pt = THIS }}\n"
    f"\t\t\t\tROOT = {{\n\t\t\t\t\tset_variable = {{ pww_ui_poach_ag = pww_ui_pk }}\n"
    f"\t\t\t\t\tset_variable = {{ pww_ui_poach_target = pww_ui_pt }}\n"
    f"\t\t\t\t\tclr_country_flag = pww_ui_dos_open\n\t\t\t\t\tadd_to_variable = {{ pww_ui_dirty = 1 }}\n\t\t\t\t}}\n"
    f"\t\t\t\tadd_to_variable = {{ pww_ui_dirty = 1 }}\n"   # the toggle's label reads its dirty on the target
    f"\t\t\t}}\n" for k in range(NK))
# The diplomacy-context GUIs read their dirty variable on THIS (the target):
# every click that changes what they show bumps it there as well as on ROOT,
# or the window keeps its old state (the close button "did nothing").
dos_close = ("\t\t\t\tROOT = {\n\t\t\t\t\tclr_country_flag = pww_ui_dos_open\n"
             "\t\t\t\t\tadd_to_variable = { pww_ui_dirty = 1 }\n\t\t\t\t}\n"
             "\t\t\t\tadd_to_variable = { pww_ui_dirty = 1 }\n")
sg.append(f"""	pww_ui_dossier_gui = {{
		context_type = diplomacy_target_context
		window_name = "pww_ui_dossier"
		parent_window_token = selected_country_view_diplomacy
		visible = {{ {foreign} ROOT = {{ has_country_flag = pww_ui_dos_open }} }}
		dirty = pww_ui_dirty
		effects = {{
			pww_ui_dos_close_click = {{
{dos_close}			}}
{dos_fx}		}}
		triggers = {{
{''.join(dos_tr)}		}}
		properties = {{
{dos_props}		}}
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
				if = {{
					limit = {{ ROOT = {{ has_country_flag = pww_ui_dos_open }} }}
{dos_close}				}}
				else = {{
					pww_ui_country_summary = yes
					ROOT = {{
						set_country_flag = pww_ui_dos_open
						pww_ui_refresh = yes
						add_to_variable = {{ pww_ui_dirty = 1 }}
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
      "# Power Without War: UI lane helpers (generated by tools/pww_ui_gen.py).\n",
      "# Called only from pww_ui_effects.txt. Slot stores read the pww_ui_t_* temps\n",
      "# that pww_ui_load_sit / pww_ui_load_ag / pww_ui_load_cartel fill; the slot\n",
      "# index comes from pww_ui_ns (situations), pww_ui_lslot (ledger), pww_ui_nk\n",
      "# (dossier) or pww_ui_nc (cartels).\n",
      "###############################################################################\n\n"]
SIT_F = ["id", "seat", "tmpl", "res", "days", "phase", "tstate", "pledge", "dev", "hasp", "cl", "ho", "pa", "date",
         "kind"]
AG_F = ["id", "st", "kind", "res", "amt", "side", "cp", "state", "civ", "pay", "wepay", "end", "open", "com", "bond",
        "route", "dsh"]
CART_F = ["id", "res", "frame", "status", "anchor", "pct", "cb", "n", "nm", "leader", "me", "quota", "sold", "room",
          "over", "sb", "conf", "short"] + [f"m{j}" for j in range(NM)]


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
fx.append(store("pww_ui_store_cart_slot", "pww_ui_c", NC, "pww_ui_nc", CART_F))

NEWS_F = ["nk", "res", "amt", "cp", "side", "civ", "pay", "wepay", "kind", "state", "end", "com", "date", "day"]
nf = ["# Viewer scope. In temps pww_ui_t_* (pww_ui_load_ag) plus pww_ui_t_nk, _date,\n",
      "# _day. Shifts the news slots down one and writes slot 0 (newest first).\n",
      "pww_ui_news_insert = {\n"]
for j in range(NN - 1, 0, -1):
    nf += [f"\tset_variable = {{ pww_ui_n{j}_{f_} = pww_ui_n{j - 1}_{f_} }}\n" for f_ in NEWS_F]
nf += [f"\tset_variable = {{ pww_ui_n0_{f_} = pww_ui_t_{f_} }}\n" for f_ in NEWS_F]
nf.append(f"\tadd_to_variable = {{ pww_ui_nn = 1 }}\n\tclamp_variable = {{ var = pww_ui_nn min = 0 max = {NN} }}\n}}\n\n")
nf.append("# Viewer scope. pww_ui_nfresh = news rows newer than the last look at the desk\n"
          "# (pww_ui_news_ack) and at most ten days old (newest first, so a prefix);\n"
          "# pww_uy_na<r> places the alert rows under the situation rows.\npww_ui_news_fresh = {\n"
          "\tset_variable = { pww_ui_nfresh = 0 }\n\tset_temp_variable = { pww_ui_old = global.num_days }\n"
          "\tsubtract_from_temp_variable = { pww_ui_old = 10 }\n")
for j in range(NNA):
    prev = "" if j == 0 else f" check_variable = {{ pww_ui_nfresh = {j} }}"
    nf.append(f"\tif = {{\n\t\tlimit = {{ check_variable = {{ pww_ui_nn > {j} }}{prev} "
              f"check_variable = {{ pww_ui_n{j}_day > pww_ui_news_ack }} check_variable = {{ pww_ui_n{j}_day > pww_ui_old }} }}\n"
              f"\t\tadd_to_variable = {{ pww_ui_nfresh = 1 }}\n\t}}\n")
for r in range(NNA):
    nf.append(f"\tset_variable = {{ pww_uy_na{r} = pww_ui_ns }}\n\tadd_to_variable = {{ pww_uy_na{r} = {r} }}\n"
              f"\tmultiply_variable = {{ pww_uy_na{r} = {AROW} }}\n"
              f"\tset_variable = {{ pww_uy_na{r}_t = pww_uy_na{r} }}\n\tadd_to_variable = {{ pww_uy_na{r}_t = 4 }}\n")
nf.append("}\n\n")
fx.extend(nf)
OPP_F = ["res", "kind", "amt", "c1", "a1", "c2", "a2", "n"]
fx.append(store("pww_ui_store_opp_slot", "pww_ui_o", NO, "pww_ui_no", OPP_F,
                "\t\tset_variable = { pww_ui_o{k}_frame = pww_ui_t_res }\n"
                "\t\tadd_to_variable = { pww_ui_o{k}_frame = 1 }\n"))

# Viewer scope. Opportunities: resources we are short of (with the two
# countries holding the most unsold output) first, then our own unsold output
# (with the two countries importing most of it). Oil surplus is left out: spare oil
# becomes fuel. Countries at war with us are skipped.
opp = ["# Viewer scope. Opportunities slots pww_ui_o<k>_* (see the loc header); count pww_ui_no.\n",
       "pww_ui_load_opps = {\n\tset_variable = { pww_ui_no = 0 }\n"]
for kind, idx in ((0, range(len(RES))), (1, SRES)):
    for i_ in idx:
        r = RES[i_]
        mine = f"check_variable = {{ resource@{r} < -0.5 }}" if kind == 0 else f"check_variable = {{ resource@{r} > 4.999 }}"
        if kind == 0:
            # sellers: output nobody buys (positive balance)
            scan = (f"\t\tevery_country = {{\n\t\t\tlimit = {{ exists = yes NOT = {{ tag = PREV }} NOT = {{ has_war_with = PREV }} "
                    f"check_variable = {{ resource@{r} > 0.999 }} }}\n"
                    f"\t\t\tset_temp_variable = {{ pww_ui_t_v = resource@{r} }}\n\t\t\tpww_ui_opp_insert = yes\n\t\t}}\n")
        else:
            # buyers: what they import plus any shortfall left (AI countries cover
            # their gaps with vanilla imports, so a negative balance is rare)
            scan = (f"\t\tevery_country = {{\n\t\t\tlimit = {{ exists = yes NOT = {{ tag = PREV }} NOT = {{ has_war_with = PREV }} }}\n"
                    f"\t\t\tset_temp_variable = {{ pww_ui_t_v = resource_imported@{r} }}\n"
                    f"\t\t\tif = {{ limit = {{ check_variable = {{ resource@{r} < 0 }} }} subtract_from_temp_variable = {{ pww_ui_t_v = resource@{r} }} }}\n"
                    f"\t\t\tif = {{ limit = {{ check_variable = {{ pww_ui_t_v > 0.999 }} }} pww_ui_opp_insert = yes }}\n\t\t}}\n")
        opp.append(
            f"\tif = {{\n\t\tlimit = {{ check_variable = {{ pww_ui_no < {NO} }} {mine} }}\n"
            f"\t\tset_temp_variable = {{ pww_ui_t_res = {i_} }}\n"
            f"\t\tset_temp_variable = {{ pww_ui_t_kind = {kind} }}\n"
            f"\t\tset_temp_variable = {{ pww_ui_t_amt = resource@{r} }}\n"
            + ("\t\tmultiply_temp_variable = { pww_ui_t_amt = -1 }\n" if kind == 0 else "")
            + "\t\tpww_ui_opp_clear = yes\n" + scan
            + "\t\tpww_ui_store_opp_slot = yes\n\t\tadd_to_variable = { pww_ui_no = 1 }\n\t}\n")
opp.append("}\n\n")
opp.append("pww_ui_opp_clear = {\n\tset_temp_variable = { pww_ui_t_n = 0 }\n"
           "\tset_temp_variable = { pww_ui_t_a1 = 0 }\n\tset_temp_variable = { pww_ui_t_a2 = 0 }\n"
           "\tset_temp_variable = { pww_ui_t_c1 = 0 }\n\tset_temp_variable = { pww_ui_t_c2 = 0 }\n}\n\n")
opp.append("# Country scope (a candidate). In temp pww_ui_t_v; keeps the top two in\n"
           "# pww_ui_t_c1/_a1 and _c2/_a2, count in pww_ui_t_n (max 2).\npww_ui_opp_insert = {\n"
           "\tif = {\n\t\tlimit = { check_variable = { pww_ui_t_v > pww_ui_t_a1 } }\n"
           "\t\tset_temp_variable = { pww_ui_t_c2 = pww_ui_t_c1 }\n\t\tset_temp_variable = { pww_ui_t_a2 = pww_ui_t_a1 }\n"
           "\t\tset_temp_variable = { pww_ui_t_c1 = THIS }\n\t\tset_temp_variable = { pww_ui_t_a1 = pww_ui_t_v }\n\t}\n"
           "\telse_if = {\n\t\tlimit = { check_variable = { pww_ui_t_v > pww_ui_t_a2 } }\n"
           "\t\tset_temp_variable = { pww_ui_t_c2 = THIS }\n\t\tset_temp_variable = { pww_ui_t_a2 = pww_ui_t_v }\n\t}\n"
           "\tif = { limit = { check_variable = { pww_ui_t_n < 2 } } add_to_temp_variable = { pww_ui_t_n = 1 } }\n}\n\n")
opp.append("# Country scope. In temp pww_ui_t_res (1..6). Out pww_ui_t_prod (1 = we produce it).\n"
           "pww_ui_produces = {\n\tset_temp_variable = { pww_ui_t_prod = 0 }\n"
           + "".join(f"\tif = {{ limit = {{ check_variable = {{ pww_ui_t_res = {i_} }} pww_core_produces_{RES[i_]} = yes }} "
                     f"set_temp_variable = {{ pww_ui_t_prod = 1 }} }}\n" for i_ in SRES) + "}\n\n")
fx.extend(opp)

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
# cartel member flags: temp pww_ui_t_nm is the next free flag slot
fx.append("# In temp pww_ui_mv (country), pww_ui_t_nm (next flag slot). Out pww_ui_t_m<j>.\n"
          "pww_ui_cart_add_flag = {\n" + "".join(
              f"\t{'if' if j == 0 else 'else_if'} = {{ limit = {{ check_variable = {{ pww_ui_t_nm = {j} }} }} "
              f"set_temp_variable = {{ pww_ui_t_m{j} = pww_ui_mv }} }}\n" for j in range(NM))
          + f"\tif = {{ limit = {{ check_variable = {{ pww_ui_t_nm < {NM} }} }} add_to_temp_variable = {{ pww_ui_t_nm = 1 }} }}\n}}\n\n")
# per-resource readers (variable names carry the resource name)
fx.append("# Country scope. In temp pww_ui_t_res (1..6). Out pww_ui_t_short (1 = we are\n"
          "# short of it: core deficit, or a negative balance).\npww_ui_short_of = {\n\tset_temp_variable = { pww_ui_t_short = 0 }\n"
          + "".join(f"\tif = {{ limit = {{ check_variable = {{ pww_ui_t_res = {i} }} OR = {{ pww_core_has_deficit_{RES[i]} = yes "
                    f"check_variable = {{ resource@{RES[i]} < 0 }} }} }} set_temp_variable = {{ pww_ui_t_short = 1 }} }}\n"
                    for i in SRES) + "}\n\n")
rs = ["# Country scope (the viewer). Fills the Reserves tab slots pww_ui_r<k>_*: one\n",
      "# per stored resource with stock, intake or draw (nothing stored and nothing\n",
      "# moving is hidden). pww_ui_nr = rows. Fill bar x = fill% of the bar - bar width.\n",
      "pww_ui_load_reserves = {\n\tset_variable = { pww_ui_nr = 0 }\n",
      "\tif = {\n\t\tlimit = { has_global_flag = pww_stock_loaded }\n"]
for i in SRES:
    r = RES[i]
    rs.append(f"""		if = {{
			limit = {{
				OR = {{
					check_variable = {{ pww_stock_{r} > 0.999 }}
					check_variable = {{ pww_stock_in_{r} > 0.05 }}
					check_variable = {{ pww_stock_out_{r} > 0.05 }}
				}}
			}}
			set_temp_variable = {{ pww_ui_t_res = {i} }}
			set_temp_variable = {{ pww_ui_t_stock = pww_stock_{r} }}
			set_temp_variable = {{ pww_ui_t_cap = pww_stock_cap_{r} }}
			set_temp_variable = {{ pww_ui_t_fill = pww_stock_fill_{r} }}
			set_temp_variable = {{ pww_ui_t_days = pww_stock_days_{r} }}
			set_temp_variable = {{ pww_ui_t_in = pww_stock_in_{r} }}
			set_temp_variable = {{ pww_ui_t_out = pww_stock_out_{r} }}
			pww_ui_store_rsv_slot = yes
			add_to_variable = {{ pww_ui_nr = 1 }}
		}}
""")
rs.append("\t}\n}\n\n")
fx.extend(rs)
RSV_F = ["res", "stock", "cap", "fill", "days", "in", "out"]
fx.append(store("pww_ui_store_rsv_slot", "pww_ui_r", NRS, "pww_ui_nr", RSV_F,
                "\t\tset_variable = { pww_ui_r{k}_frame = pww_ui_t_res }\n"
                "\t\tadd_to_variable = { pww_ui_r{k}_frame = 1 }\n"
                f"\t\tset_variable = {{ pww_ui_r{{k}}_fx = pww_ui_t_fill }}\n"
                f"\t\tclamp_variable = {{ var = pww_ui_r{{k}}_fx min = 0 max = 100 }}\n"
                f"\t\tmultiply_variable = {{ pww_ui_r{{k}}_fx = {BAR_W / 100} }}\n"
                f"\t\tsubtract_from_variable = {{ pww_ui_r{{k}}_fx = {BAR_W} }}\n"))
# dossier: the target's reserves (deepest three) and main exports (viewer independent)
rv_fx = ["# Country scope (the dossier target). Reserve words: the three resources with\n",
         "# the most days of own use in store (band 0 thin, 1 some 15+, 2 ample 45+, 3\n",
         "# deep 90+) in pww_ui_rv<j>_res / _b, count pww_ui_nrv. Main exports: the two\n",
         "# resources with the largest exports plus unsold output, pww_ui_x1 / _x2 (-1).\n",
         "pww_ui_country_trade_words = {\n\tset_variable = { pww_ui_nrv = 0 }\n"]
for j in range(NRV):
    rv_fx.append(f"\tset_temp_variable = {{ pww_ui_rvd{j} = 0 }}\n\tset_variable = {{ pww_ui_rv{j}_res = -1 }}\n")
rv_fx.append("\tif = {\n\t\tlimit = { has_global_flag = pww_stock_loaded }\n")
for i in SRES:
    r = RES[i]
    rv_fx.append(f"\t\tif = {{\n\t\t\tlimit = {{ check_variable = {{ pww_stock_{r} > 0.999 }} }}\n"
                 f"\t\t\tset_temp_variable = {{ pww_ui_cd = pww_stock_days_{r} }}\n"
                 f"\t\t\tset_temp_variable = {{ pww_ui_cr = {i} }}\n\t\t\tpww_ui_rv_insert = yes\n\t\t}}\n")
rv_fx.append("\t}\n")
for j in range(NRV):
    rv_fx.append(f"""	if = {{
		limit = {{ check_variable = {{ pww_ui_rv{j}_res > -1 }} }}
		add_to_variable = {{ pww_ui_nrv = 1 }}
		set_variable = {{ pww_ui_rv{j}_b = 0 }}
		if = {{ limit = {{ check_variable = {{ pww_ui_rvd{j} > 89.999 }} }} set_variable = {{ pww_ui_rv{j}_b = 3 }} }}
		else_if = {{ limit = {{ check_variable = {{ pww_ui_rvd{j} > 44.999 }} }} set_variable = {{ pww_ui_rv{j}_b = 2 }} }}
		else_if = {{ limit = {{ check_variable = {{ pww_ui_rvd{j} > 14.999 }} }} set_variable = {{ pww_ui_rv{j}_b = 1 }} }}
	}}
""")
rv_fx.append("\tset_variable = { pww_ui_x1 = -1 }\n\tset_variable = { pww_ui_x2 = -1 }\n"
             "\tset_temp_variable = { pww_ui_xv1 = 0.999 }\n\tset_temp_variable = { pww_ui_xv2 = 0.999 }\n")
for i, r in enumerate(RES):
    rv_fx.append(f"""	set_temp_variable = {{ pww_ui_xv = resource_exported@{r} }}
	set_temp_variable = {{ pww_ui_xu = resource@{r} }}
	if = {{ limit = {{ check_variable = {{ pww_ui_xu > 0 }} }} add_to_temp_variable = {{ pww_ui_xv = pww_ui_xu }} }}
	if = {{
		limit = {{ check_variable = {{ pww_ui_xv > pww_ui_xv1 }} }}
		set_temp_variable = {{ pww_ui_xv2 = pww_ui_xv1 }}
		set_variable = {{ pww_ui_x2 = pww_ui_x1 }}
		set_temp_variable = {{ pww_ui_xv1 = pww_ui_xv }}
		set_variable = {{ pww_ui_x1 = {i} }}
	}}
	else_if = {{
		limit = {{ check_variable = {{ pww_ui_xv > pww_ui_xv2 }} }}
		set_temp_variable = {{ pww_ui_xv2 = pww_ui_xv }}
		set_variable = {{ pww_ui_x2 = {i} }}
	}}
""")
rv_fx.append("}\n\n")
fx.extend(rv_fx)
ins = ["# In temps pww_ui_cd (days), pww_ui_cr (resource). Keeps pww_ui_rv0..2 sorted\n",
       "# by days, deepest first.\npww_ui_rv_insert = {\n"]
for j in range(NRV):
    kw = "if" if j == 0 else "else_if"
    shift = "".join(f"\t\tset_variable = {{ pww_ui_rv{m}_res = pww_ui_rv{m - 1}_res }}\n"
                    f"\t\tset_temp_variable = {{ pww_ui_rvd{m} = pww_ui_rvd{m - 1} }}\n" for m in range(NRV - 1, j, -1))
    ins.append(f"\t{kw} = {{\n\t\tlimit = {{ OR = {{ check_variable = {{ pww_ui_rv{j}_res < 0 }} "
               f"check_variable = {{ pww_ui_cd > pww_ui_rvd{j} }} }} }}\n{shift}"
               f"\t\tset_variable = {{ pww_ui_rv{j}_res = pww_ui_cr }}\n\t\tset_temp_variable = {{ pww_ui_rvd{j} = pww_ui_cd }}\n\t}}\n")
ins.append("}\n\n")
fx.extend(ins)

# Overview layout: section bases from the row counts, then one y per flowing element
lay = ["# Viewer scope. Overview tab layout: sections stack from the content top and\n",
       "# skip when empty (no reserved space). Reserves footer sits under the last row.\n",
       "pww_ui_layout = {\n",
       f"\tset_temp_variable = {{ pww_ui_yy = {CY} }}\n",
       "\tset_temp_variable = { pww_ui_yb_sit = pww_ui_yy }\n",
       "\tif = {\n\t\tlimit = { check_variable = { pww_ui_ns > 0 } }\n",
       f"\t\tset_temp_variable = {{ pww_ui_yh = pww_ui_ns }}\n\t\tmultiply_temp_variable = {{ pww_ui_yh = {SIT_ROW} }}\n",
       f"\t\tadd_to_temp_variable = {{ pww_ui_yh = {HDR + GAP} }}\n\t\tadd_to_temp_variable = {{ pww_ui_yy = pww_ui_yh }}\n\t}}\n",
       "\tset_temp_variable = { pww_ui_yb_news = pww_ui_yy }\n",
       "\tif = {\n\t\tlimit = { check_variable = { pww_ui_nn > 0 } }\n",
       f"\t\tset_temp_variable = {{ pww_ui_yh = pww_ui_nn }}\n\t\tmultiply_temp_variable = {{ pww_ui_yh = {NEWS_ROW} }}\n",
       f"\t\tadd_to_temp_variable = {{ pww_ui_yh = {HDR + GAP} }}\n\t\tadd_to_temp_variable = {{ pww_ui_yy = pww_ui_yh }}\n\t}}\n",
       "\tset_temp_variable = { pww_ui_yb_opp = pww_ui_yy }\n",
       "\tif = {\n\t\tlimit = { check_variable = { pww_ui_no > 0 } }\n",
       f"\t\tset_temp_variable = {{ pww_ui_yh = pww_ui_no }}\n\t\tmultiply_temp_variable = {{ pww_ui_yh = {OPP_ROW} }}\n",
       f"\t\tadd_to_temp_variable = {{ pww_ui_yh = {HDR + GAP} }}\n\t\tadd_to_temp_variable = {{ pww_ui_yy = pww_ui_yh }}\n\t}}\n",
       "\tset_temp_variable = { pww_ui_yb_cart = pww_ui_yy }\n",
       "\tif = {\n\t\tlimit = { check_variable = { pww_ui_nc > 0 } }\n",
       f"\t\tset_temp_variable = {{ pww_ui_yh = pww_ui_nc }}\n\t\tmultiply_temp_variable = {{ pww_ui_yh = {CART_ROW} }}\n",
       f"\t\tadd_to_temp_variable = {{ pww_ui_yh = {HDR + GAP} }}\n\t\tadd_to_temp_variable = {{ pww_ui_yy = pww_ui_yh }}\n\t}}\n",
       "\tset_temp_variable = { pww_ui_yb_mkt = pww_ui_yy }\n",
       "\tset_temp_variable = { pww_ui_yb_rsv = pww_ui_nr }\n",
       f"\tmultiply_temp_variable = {{ pww_ui_yb_rsv = {RSV_ROW} }}\n",
       f"\tadd_to_temp_variable = {{ pww_ui_yb_rsv = {RSV_Y + 8} }}\n",
       "\tif = { limit = { check_variable = { pww_ui_nr = 0 } } add_to_temp_variable = { pww_ui_yb_rsv = 30 } }\n"]
for name, (sec, off) in FLOW.items():
    lay.append(f"\tset_variable = {{ {uy(name)} = pww_ui_yb_{sec} }}\n")
    if off:
        lay.append(f"\tadd_to_variable = {{ {uy(name)} = {off} }}\n")
# desk height: the open tab's last line plus a margin, rounded up to a step
PAD = 16
lay.append("\t# desk height for the open tab (pww_ui_desk_h, one of the background steps)\n"
           "\tif = {\n\t\tlimit = { check_variable = { pww_ui_tab = 1 } }\n"
           "\t\tset_temp_variable = { pww_ui_rows = 0 }\n"
           + "".join(f"\t\tif = {{ limit = {{ check_variable = {{ pww_ui_l{k}_on = 1 }} }} add_to_temp_variable = {{ pww_ui_rows = 1 }} }}\n"
                     for k in range(NAG))
           + f"\t\tset_temp_variable = {{ pww_ui_need = pww_ui_rows }}\n"
           f"\t\tmultiply_temp_variable = {{ pww_ui_need = {LED_ROW} }}\n"
           f"\t\tadd_to_temp_variable = {{ pww_ui_need = {LED_Y + PAD} }}\n"
           f"\t\tif = {{ limit = {{ check_variable = {{ pww_ui_rows = 0 }} }} set_temp_variable = {{ pww_ui_need = {LED_Y + 40 + PAD} }} }}\n"
           "\t}\n"
           "\telse_if = {\n\t\tlimit = { check_variable = { pww_ui_tab = 2 } }\n"
           f"\t\tset_temp_variable = {{ pww_ui_need = pww_ui_yb_rsv }}\n"
           f"\t\tadd_to_temp_variable = {{ pww_ui_need = {36 + PAD} }}\n"
           "\t}\n"
           "\telse = {\n"
           "\t\tset_temp_variable = { pww_ui_need = pww_ui_yb_mkt }\n"
           f"\t\tadd_to_temp_variable = {{ pww_ui_need = {26 + 7 * MKT_ROW + PAD} }}\n"
           f"\t\tif = {{ limit = {{ NOT = {{ has_global_flag = pww_ui_mkt_ready }} }} set_temp_variable = {{ pww_ui_need = pww_ui_yb_mkt }} add_to_temp_variable = {{ pww_ui_need = {28 + 36 + PAD} }} }}\n"
           "\t}\n"
           f"\tset_variable = {{ pww_ui_desk_h = {DESK_HS[-1]} }}\n")
for h in reversed(DESK_HS[:-1]):
    lay.append(f"\tif = {{ limit = {{ NOT = {{ check_variable = {{ pww_ui_need > {h} }} }} }} set_variable = {{ pww_ui_desk_h = {h} }} }}\n")
lay.append("}\n\n")
fx.extend(lay)
fx.append("# Country scope (a dossier target, viewer independent). The demand block\n"
          "# sits under the last agreement row (one row when there are none, plus the\n"
          "# '...and N more' row). pww_ui_dos_rows picks the background height.\n"
          "pww_ui_dossier_layout = {\n"
          "\tset_variable = { pww_ui_dos_rows = pww_ui_nk }\n"
          "\tif = { limit = { check_variable = { pww_ui_dos_rows < 1 } } set_variable = { pww_ui_dos_rows = 1 } }\n"
          "\tif = { limit = { check_variable = { pww_ui_nk_more > 0 } } add_to_variable = { pww_ui_dos_rows = 1 } }\n"
          "\tset_temp_variable = { pww_ui_yd = pww_ui_dos_rows }\n"
          f"\tmultiply_temp_variable = {{ pww_ui_yd = {DOS_ROW} }}\n"
          f"\tadd_to_temp_variable = {{ pww_ui_yd = {DOS_K + 2} }}\n"
          + "".join(f"\tset_variable = {{ {uy(n)} = pww_ui_yd }}\n" + (f"\tadd_to_variable = {{ {uy(n)} = {o} }}\n" if o else "")
                    for n, o in DOS_FLOW.items()) + "}\n\n")
worst = CY + HDR + NSIT * SIT_ROW + GAP + HDR + NN * NEWS_ROW + GAP + HDR + NO * OPP_ROW + GAP + HDR + NC * CART_ROW + GAP + 26 + 7 * MKT_ROW
assert worst <= DH - 8, worst

# market report, one block per resource
mk = ["# Global market report (any scope). Bands from the two most desperate buyers\n",
      "# of each resource among active traders and human players (core desperation;\n",
      "# raw desperation names minors nobody trades with); causes from those buyers, live\n",
      "# Situations over the resource and the cartel holding it (c3: 1 conference,\n",
      "# 2 in force, 3 price war after a collapse).\npww_ui_market_report = {\n",
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
		limit = {{
			exists = yes
			has_variable = pww_desp_{r}
			OR = {{
				has_country_flag = pww_is_active_trader
				is_ai = no
			}}
		}}
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
    if i > 0:
        mk.append(f"""	set_variable = {{ {g}_c3_{r} = 0 }}
	if = {{
		limit = {{ has_global_flag = pww_cartel_loaded }}
		set_temp_variable = {{ pww_ui_cid = global.pww_cart_by_res^{i} }}
		if = {{
			limit = {{ check_variable = {{ pww_ui_cid > -1 }} }}
			set_variable = {{ {g}_c3_{r} = 1 }}
			if = {{
				limit = {{ check_variable = {{ global.pww_cart_status^pww_ui_cid = 1 }} }}
				set_variable = {{ {g}_c3_{r} = 2 }}
			}}
		}}
		else_if = {{
			limit = {{ any_country = {{ pww_cartel_pricewar_{r} = yes }} }}
			set_variable = {{ {g}_c3_{r} = 3 }}
		}}
	}}
""")
mk.append("}\n\n")
fx.extend(mk)
res_lines = ["# Country scope (a dossier target, viewer independent). Per resource r, daily\n",
             "# units: pww_ui_rs_<r>_prod / _imp / _exp / _bal (balance: + unsold, - short),\n",
             "# _use (prod + imp - exp - bal), _net (bal + exp - imp: spare before any\n",
             "# trade), _short (-bal when short, else 0).\npww_ui_country_res_lines = {\n"]
for r in RES:
    v = f"pww_ui_rs_{r}"
    res_lines.append(f"""	set_variable = {{ {v}_prod = resource_produced@{r} }}
	set_variable = {{ {v}_imp = resource_imported@{r} }}
	set_variable = {{ {v}_exp = resource_exported@{r} }}
	set_variable = {{ {v}_bal = resource@{r} }}
	set_variable = {{ {v}_use = {v}_prod }}
	add_to_variable = {{ {v}_use = {v}_imp }}
	subtract_from_variable = {{ {v}_use = {v}_exp }}
	subtract_from_variable = {{ {v}_use = {v}_bal }}
	set_variable = {{ {v}_net = {v}_bal }}
	add_to_variable = {{ {v}_net = {v}_exp }}
	subtract_from_variable = {{ {v}_net = {v}_imp }}
	set_variable = {{ {v}_short = 0 }}
	if = {{ limit = {{ check_variable = {{ {v}_bal < 0 }} }} subtract_from_variable = {{ {v}_short = {v}_bal }} }}
	# what an importer holds over is what it bought, not output it could sell:
	# unsold counts only output beyond its own use (bal capped at net)
	if = {{
		limit = {{ check_variable = {{ {v}_bal > {v}_net }} }}
		set_variable = {{ {v}_bal = {v}_net }}
		if = {{ limit = {{ check_variable = {{ {v}_bal < 0 }} }} set_variable = {{ {v}_bal = 0 }} }}
	}}
""")
res_lines.append("}\n\n")
fx.extend(res_lines)
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
print(f"ok: {len(loc)} loc keys, {len(sl)} defined_texts, {len(FLOW)} flowing elements")
