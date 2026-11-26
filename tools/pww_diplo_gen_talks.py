"""Trade talks screen generator (diplomacy lane). Imported by
tools/pww_diplo_gen_gui.py, which writes the files. Builds:
  - the send window pww_diplo_send_offer (Propose Trade Deal, Lease Mines)
  - the receive window pww_diplo_recv_offer (an AI proposal to a human)
  - their scripted GUI effects and triggers, scripted localisation
  - mod/common/scripted_effects/pww_diplo_bundle_gen.txt: the display mirror
    (pww_diplo_bundle_mirror) and the copy to the receiver
    (pww_diplo_bundle_copy_display)
  - trade talks UI loc (TALKS_LOC, merged by tools/pww_diplo_gen_loc.py)

Layout grid: the vanilla popup is 584 wide. The other diplomacy windows align
content with the Cancel/Send buttons (x 77..509); the trade table needs the
width for its hint lines ("We're short 30 · they have 112 spare"), so it uses
a symmetric 40 px margin (x 40..544): two 244-wide columns with a 16 px
gutter centred on the frame. No layout engine: every position is computed
here.
"""

GL, GR = 40, 544
CW = GR - GL
COLW = 244
COLX = (GL, GR - COLW)
FONT = "hoi_16mbs"
ROW_Y0 = 66          # first item row
ROW_H = 40           # two text lines per item
TERMS_Y = 232
MENU_Y = 46
H_SEND = 486
H_RECV = 470

RES = ["Oil", "Aluminium", "Rubber", "Tungsten", "Steel", "Chromium", "Coal"]
RES_LC = [r.lower() for r in RES]
EQ = ["Rifles", "Support equipment", "Artillery", "Anti-tank guns", "Anti-air guns", "Trucks", "Convoys", "Trains"]
EQ_LC = ["rifles", "support equipment", "artillery guns", "anti-tank guns", "anti-air guns", "trucks", "convoys", "trains"]
LIC = ["Rifles", "Support equipment", "Artillery", "Anti-tank guns", "Anti-air guns", "Trucks", "Light tanks", "Fighters"]
LIC_LC = ["rifles", "support equipment", "artillery", "anti-tank guns", "anti-air guns", "trucks", "light tanks", "fighters"]
LEN = ["6 months", "1 year", "2 years", "5 years"]
LEN_WORDS = ["six months", "one year", "two years", "five years"]
RES_ICON = [f"£resources_strip|{i + 1}" for i in range(7)]
KIND_ICON = {1: "£civ_factory", 2: "£pol_power", 4: "£production_cost", 5: "£tech_mod"}

# Hidden wants and red lines as clue chips (trade talks meanings).
WANT_CHIP = ["arms (rifles and guns)", "civilian factories", "coal", "trucks and transport",
             "a production licence", "a six-month trial", "a resource they lack",
             "to keep most of their output", "political power"]
RL_CHIP = ["lease out a mine", "sign for two years or more", "sell most of their output",
           "deal in political power", "sign in public", "sell more than 45% of their output",
           "cross [?pww_dd_patron.GetName]", "sign a deal either side may end"]
PAT_WORDS = ["§Rnearly gone§!", "§Orunning thin§!", "§Ysteady§!", "§Gpatient§!"]

L = {}   # loc key -> text


def side_of(n):
    return 0 if n < 4 else 1


def slot_xy(n, recv=False):
    s = side_of(n)
    col = (1 - s) if recv else s
    return COLX[col], ROW_Y0 + (n % 4) * ROW_H


def R(cond):
    return f"ROOT = {{ {cond} }}"


def cv(var, op, val):
    return f"check_variable = {{ {var} {op} {val} }}"


class B:
    """Collects one window's elements, effects and triggers."""

    def __init__(self, g, prefix):
        self.g, self.p = g, prefix
        self.body = ""
        self.eff = []
        self.trg = []

    def tb(self, key, x, y, text, w, h=18, font=FONT, fmt="left", vis=None, tooltip=None):
        name = f"{self.p}_{key}"
        self.body += (f'\t\tinstantTextBoxType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
                      f'\t\t\tfont = "{font}"\n\t\t\ttext = "{text}"\n\t\t\tmaxWidth = {w}\n\t\t\tmaxHeight = {h}\n'
                      f'\t\t\tformat = {fmt}\n\t\t\tfixedsize = yes\n')
        if tooltip:
            self.body += f'\t\t\tpdx_tooltip = "{tooltip}"\n'
        self.body += "\t\t}\n"
        if vis:
            self.vis(key, vis)

    def btn(self, key, x, y, sprite, w=None, h=None, text=None, vis=None, click=None, enabled=None, tooltip=None):
        name = f"{self.p}_{key}"
        self.body += f'\t\tbuttonType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tquadTextureSprite = "{sprite}"\n'
        if w:
            self.body += f"\t\t\tsize = {{ x = {w} y = {h} }}\n"
        if text:
            self.body += f'\t\t\tbuttonText = "{text}"\n\t\t\tbuttonFont = "{FONT}"\n'
        if tooltip:
            self.body += f'\t\t\tpdx_tooltip = "{tooltip}"\n'
        self.body += "\t\t}\n"
        if vis:
            self.vis(key, vis)
        if click:
            self.eff.append(f"\t\t\t{name}_click = {{\n{click}\t\t\t}}\n")
        if enabled:
            self.trg.append(f"\t\t\t{name}_click_enabled = {{ {enabled} }}\n")

    def vis(self, key, cond):
        self.trg.append(f"\t\t\t{self.p}_{key}_visible = {{ {cond} }}\n")

    def window(self, name, h):
        return (f'\tcontainerWindowType = {{\n\t\tname = "{name}"\n\t\tposition = {{ x = 0 y = 0 }}\n'
                f'\t\tsize = {{ width = 584 height = {h} }}\n\t\tmoveable = no\n\t\torientation = center\n\t\tclipping = no\n\n'
                + self.body + "\t}\n\n")


def root_do(*lines):
    inner = "".join(f"\t\t\t\t\t{x}\n" for x in lines)
    return f"\t\t\t\tROOT = {{\n{inner}\t\t\t\t}}\n"


MENU_CLOSED = R(cv("pww_dbm_side", "<", 0))
MENU_OPEN = R(cv("pww_dbm_side", ">", -1))


# ----------------------------------------------------------------------------
# Scripted localisation helpers
# ----------------------------------------------------------------------------
SL = []
_SL_NAMES = set()


def dt(name, cases, default=None):
    if name in _SL_NAMES:
        return
    _SL_NAMES.add(name)
    s = f"defined_text = {{\n\tname = {name}\n"
    for trig, key in cases:
        s += f"\ttext = {{\n\t\ttrigger = {{ {trig} }}\n\t\tlocalization_key = {key}\n\t}}\n"
    if default:
        s += f"\ttext = {{\n\t\tlocalization_key = {default}\n\t}}\n"
    SL.append(s + "}\n")


def loc(key, text):
    assert "—" not in text, key
    L[key] = text
    return key


loc("pww_dt_empty", "")


def num(var, dec=0):
    return f"[?ROOT.{var}|{dec}]"


# ----------------------------------------------------------------------------
# Per-slot scripted loc (shared by send and receive)
# ----------------------------------------------------------------------------
def kind_is(n, k):
    return R(cv(f"pww_dbk_{n}", "=", k))


def build_slot_loc():
    for n in range(8):
        a, x = f"pww_dba_{n}", f"pww_dbx_{n}"
        # Name (row line 1)
        cases = [(kind_is(n, 1), loc("pww_dt_nm_civ", "£civ_factory Civilian factories")),
                 (kind_is(n, 2), loc("pww_dt_nm_pp", "£pol_power Political power"))]
        for r in range(7):
            cases.append((R(f"{cv(f'pww_dbk_{n}', '=', 3)} {cv(x, '=', r)}"),
                          loc(f"pww_dt_nm_res_{r}", f"{RES_ICON[r]} {RES[r]}")))
            cases.append((R(f"{cv(f'pww_dbk_{n}', '=', 6)} {cv(x, '=', r)}"),
                          loc(f"pww_dt_nm_rights_{r}", f"{RES_ICON[r]} {RES[r]} mine lease")))
        for e in range(8):
            cases.append((R(f"{cv(f'pww_dbk_{n}', '=', 4)} {cv(x, '=', e)}"),
                          loc(f"pww_dt_nm_eq_{e}", f"£production_cost {EQ[e]}")))
            cases.append((R(f"{cv(f'pww_dbk_{n}', '=', 5)} {cv(x, '=', e)}"),
                          loc(f"pww_dt_nm_lic_{e}", f"£tech_mod Licence: {LIC[e]}")))
        dt(f"pww_dt_sl_nm_{n}", cases, "pww_dt_empty")
        # Amount (stepper value)
        dt(f"pww_dt_sl_am_{n}", [
            (kind_is(n, 2), loc(f"pww_dt_am_pp_{n}", f"§Y{num(a, 2)}§!")),
        ], loc(f"pww_dt_am_{n}", f"§Y{num(a)}§!"))
        # Lease state line
        loc(f"pww_dt_state_{n}", f"[?ROOT.pww_dbs_{n}.GetName] · {num(f'pww_dbu_{n}')} a day")
        # Summary list item and separator
        cases = [(R(f"{cv(f'pww_dbk_{n}', '=', 1)} {cv(a, '=', 1)}"),
                  loc(f"pww_dt_li_civ1_{n}", "§Y1 civilian factory§!")),
                 (kind_is(n, 1), loc(f"pww_dt_li_civ_{n}", f"§Y{num(a)} civilian factories§!")),
                 (kind_is(n, 2), loc(f"pww_dt_li_pp_{n}", f"§Y{num(a, 2)} political power§! a day"))]
        for r in range(7):
            cases.append((R(f"{cv(f'pww_dbk_{n}', '=', 3)} {cv(x, '=', r)}"),
                          loc(f"pww_dt_li_res_{r}_{n}", f"§Y{num(a)} {RES_LC[r]}§! a day")))
            cases.append((R(f"{cv(f'pww_dbk_{n}', '=', 6)} {cv(x, '=', r)}"),
                          loc(f"pww_dt_li_rights_{r}_{n}", f"the §Y{RES_LC[r]} mines of [?ROOT.pww_dbs_{n}.GetName]§!")))
        for e in range(8):
            cases.append((R(f"{cv(f'pww_dbk_{n}', '=', 4)} {cv(x, '=', e)}"),
                          loc(f"pww_dt_li_eq_{e}_{n}", f"§Y{num(a)} {EQ_LC[e]}§! in three shipments")))
            cases.append((R(f"{cv(f'pww_dbk_{n}', '=', 5)} {cv(x, '=', e)}"),
                          loc(f"pww_dt_li_lic_{e}", f"a §Ylicence to build {LIC_LC[e]}§!")))
        dt(f"pww_dt_sl_li_{n}", cases, "pww_dt_empty")
        i = n % 4
        if i == 0:
            dt(f"pww_dt_sl_sep_{n}", [], "pww_dt_empty")
        else:
            last = R(cv(f"pww_dbk_{n + 1}", "=", 0)) if i < 3 else "always = yes"
            dt(f"pww_dt_sl_sep_{n}", [(R(cv(f"pww_dbk_{n}", "=", 0)), "pww_dt_empty"),
                                      (last, loc("pww_dt_sep_and", " and "))], loc("pww_dt_sep_comma", ", "))


build_slot_loc()


def side_list(s):
    return "".join(f"[pww_dt_sl_sep_{n}][pww_dt_sl_li_{n}]" for n in range(4 * s, 4 * s + 4))


def build_hint_loc(n, recv):
    """Line 2 of an item row. Perspective: 'we' is the sender (send GUI) or the
    receiver (receive GUI). Sender-side figures: ss/sp, target: ts/tp."""
    tag = "r" if recv else "s"
    s = side_of(n)
    we_give = (s == 0) != recv
    us_sh, us_sp = ("pww_dbts", "pww_dbtp") if recv else ("pww_dbss", "pww_dbsp")
    th_sh, th_sp = ("pww_dbss", "pww_dbsp") if recv else ("pww_dbts", "pww_dbtp")
    nm = f"pww_dt_sl_hi{tag}_{n}"
    f = f"pww_dbf_{n}"
    # resource parts
    if we_give:
        a_cases = [(R(cv(f"{us_sp}_{n}", ">", 0.5)), loc(f"pww_dt_h{tag}_a_sp_{n}", f"We have {num(f'{us_sp}_{n}')} spare"))]
        a_def = loc("pww_dt_h_a_nosp", "We have none spare")
        b_cases = [(R(cv(f"{th_sh}_{n}", ">", 0.5)), loc(f"pww_dt_h{tag}_b_sh_{n}", f"they're short {num(f'{th_sh}_{n}')}"))]
        b_def = loc("pww_dt_h_b_enough", "they have enough")
    else:
        a_cases = [(R(cv(f"{us_sh}_{n}", ">", 0.5)), loc(f"pww_dt_h{tag}_a_sh_{n}", f"We're short {num(f'{us_sh}_{n}')}"))]
        a_def = loc("pww_dt_h_a_enough", "We have enough")
        b_cases = [(R(cv(f"{th_sp}_{n}", ">", 0.5)), loc(f"pww_dt_h{tag}_b_sp_{n}", f"they have {num(f'{th_sp}_{n}')} spare"))]
        b_def = loc("pww_dt_h_b_nosp", "they have none spare")
    dt(f"pww_dt_sl_h{tag}a_{n}", a_cases, a_def)
    dt(f"pww_dt_sl_h{tag}b_{n}", b_cases, b_def)
    loc(f"pww_dt_h{tag}_res_{n}", f"§g[pww_dt_sl_h{tag}a_{n}] · [pww_dt_sl_h{tag}b_{n}]§!")
    giver_us = we_give
    who = "We" if giver_us else "They"
    cases = [
        (kind_is(n, 1), loc(f"pww_dt_h{tag}_civ_{n}", f"§g{who} have {num(f)} free§!")),
        (kind_is(n, 2), loc(f"pww_dt_h{tag}_pp_{n}", f"§gPer day · {who.lower()} gain {num(f, 2)} a day§!")),
        (kind_is(n, 3), f"pww_dt_h{tag}_res_{n}"),
        (kind_is(n, 4), loc(f"pww_dt_h{tag}_eq_{n}", f"§gIn three shipments · {who.lower()} hold {num(f)}§!")),
        (kind_is(n, 5), loc(f"pww_dt_h{tag}_lic_{s}", "§gThey may build our design§!" if giver_us else "§gWe may build their design§!")),
    ]
    dt(nm, cases, "pww_dt_empty")
    return nm


def build_rows(b, recv):
    """Item rows. Send: steppers and remove; receive: read-only."""
    tag = "r" if recv else "s"
    for n in range(8):
        x, y = slot_xy(n, recv)
        k = f"pww_dbk_{n}"
        closed = "" if recv else MENU_CLOSED + " "
        stepk = R(f"{cv(k, '>', 0)} {cv(k, '<', 5)}")
        widek = R(cv(k, ">", 4))
        hint = build_hint_loc(n, recv)
        if recv:
            b.tb(f"i{n}_nm", x, y + 1, f"[pww_dt_sl_nm_{n}]", COLW - 72, vis=stepk)
            b.tb(f"i{n}_am", x + COLW - 70, y + 1, f"[pww_dt_sl_am_{n}]", 70, fmt="right", vis=stepk)
            b.tb(f"i{n}_nmw", x, y + 1, f"[pww_dt_sl_nm_{n}]", COLW, vis=widek)
        else:
            b.tb(f"i{n}_nm", x, y + 1, f"[pww_dt_sl_nm_{n}]", COLW - 92, vis=closed + stepk)
            b.tb(f"i{n}_nmw", x, y + 1, f"[pww_dt_sl_nm_{n}]", COLW - 20, vis=closed + widek)
            stp = lambda d: root_do(f"set_temp_variable = {{ pww_dba_n = {n} }}",
                                    f"set_temp_variable = {{ pww_dba_dir = {d} }}",
                                    "pww_diplo_bundle_step = yes", "pww_diplo_offer_changed = yes")
            b.btn(f"i{n}_mi", x + COLW - 90, y + 2, "GFX_pww_diplo_prev", vis=closed + stepk, click=stp(-1))
            b.tb(f"i{n}_am", x + COLW - 74, y + 1, f"[pww_dt_sl_am_{n}]", 38, fmt="centre", vis=closed + stepk)
            b.btn(f"i{n}_pl", x + COLW - 36, y + 2, "GFX_pww_diplo_next", vis=closed + stepk, click=stp(1))
            b.btn(f"i{n}_x", x + COLW - 16, y + 2, "GFX_closebutton_16", vis=closed + R(cv(k, ">", 0)),
                  click=root_do(f"set_temp_variable = {{ pww_dba_n = {n} }}", "pww_diplo_bundle_remove = yes",
                                "pww_diplo_offer_changed = yes"), tooltip="pww_dt_tt_remove")
        lease = R(cv(k, "=", 6))
        b.tb(f"i{n}_hi", x, y + 20, f"[{hint}]", COLW, vis=closed + R(f"{cv(k, '>', 0)} {cv(k, '<', 6)}"))
        if recv:
            b.tb(f"i{n}_lst", x, y + 20, f"pww_dt_state_{n}", COLW, vis=lease)
        else:
            stp = lambda d: root_do(f"set_temp_variable = {{ pww_dba_n = {n} }}",
                                    f"set_temp_variable = {{ pww_dba_dir = {d} }}",
                                    "pww_diplo_bundle_step = yes", "pww_diplo_offer_changed = yes")
            b.btn(f"i{n}_lmi", x, y + 21, "GFX_pww_diplo_prev", vis=closed + lease, click=stp(-1))
            b.tb(f"i{n}_lst", x + 18, y + 20, f"pww_dt_state_{n}", COLW - 54, fmt="centre", vis=closed + lease)
            b.btn(f"i{n}_lpl", x + COLW - 36, y + 21, "GFX_pww_diplo_next", vis=closed + lease, click=stp(1))


# ----------------------------------------------------------------------------
# Send window
# ----------------------------------------------------------------------------
def party_header(b, recv):
    us, them = ("THIS", "ROOT") if recv else ("ROOT", "THIS")
    b.tb("us", GL, 2, loc(f"pww_dt_us_{int(recv)}", f"[{us}.GetFlag] [{us}.GetName]"), 220, font="hoi_18mbs")
    b.tb("us_sub", GL, 22, loc("pww_dt_you", "§gYou§!"), 220)
    b.tb("and", 262, 10, loc("pww_dt_and", "§gand§!"), 60, fmt="centre")
    b.tb("them", GR - 220, 2, loc(f"pww_dt_them_{int(recv)}", f"[{them}.GetName] [{them}.GetFlag]"), 220, font="hoi_18mbs", fmt="right")
    b.tb("them_sub", GR - 220, 22, f"[pww_dt_sl_top_{int(recv)}]", 220, fmt="right")


def divider(b, key, y, vis=None):
    b.body += (f'\t\ticonType = {{\n\t\t\tname = "{b.p}_{key}"\n\t\t\tposition = {{ x = {GL} y = {y} }}\n'
               f'\t\t\tspriteType = "GFX_divider"\n\t\t\tscale = {CW / 514:.3f}\n\t\t}}\n')
    if vis:
        b.vis(key, vis)


MENU_PAGES = {0: 6, 1: 7, 2: 8, 3: 8, 4: 7}
P0_KIND = [None, 1, 2, None, None, None]   # direct adds on page 0
P0_PAGE = [1, None, None, 2, 3, 4]


def menu(b):
    side, page = "pww_dbm_side", "pww_dbm_page"
    # Panel height follows the page: rows plus the Back row.
    for p_set, rows, back in (((0,), 6, 0), ((1, 4), 7, 1), ((2, 3), 8, 1)):
        h = 34 + rows * 22 + (26 if back else 0) + 8
        pv = " ".join(cv(page, "=", p) for p in p_set)
        b.btn(f"mbg{rows}", GL, MENU_Y, "GFX_pww_dt_menu", w=CW, h=h, vis=MENU_OPEN + " " + R(f"OR = {{ {pv} }}"))
    b.tb("mtitle", GL + 12, MENU_Y + 9, "[pww_dt_sl_mtitle]", 300, font="hoi_18mbs", vis=MENU_OPEN)
    b.btn("mclose", GR - 26, MENU_Y + 10, "GFX_closebutton_16", vis=MENU_OPEN,
          click=root_do("set_variable = { pww_dbm_side = -1 }", "set_variable = { pww_dbm_page = 0 }",
                        "add_to_variable = { pww_diplo_dirty = 1 }"))
    for j in range(8):
        y = MENU_Y + 34 + j * 22
        conds = [cv(page, '=', p) for p, c in MENU_PAGES.items() if c > j]
        vis = MENU_OPEN + " " + R(f"OR = {{ {' '.join(conds)} }}")
        click = []
        for s in (0, 1):
            for p, c in MENU_PAGES.items():
                if j >= c:
                    continue
                if p == 0:
                    if P0_PAGE[j] is not None:
                        act = f"set_variable = {{ pww_dbm_page = {P0_PAGE[j]} }} pww_diplo_menu_enable = yes add_to_variable = {{ pww_diplo_dirty = 1 }}"
                    else:
                        act = (f"set_temp_variable = {{ pww_dba_side = {s} }} set_temp_variable = {{ pww_dba_kind = {P0_KIND[j]} }} "
                               f"set_temp_variable = {{ pww_dba_x = 0 }} pww_diplo_bundle_add = yes "
                               f"set_variable = {{ pww_dbm_side = -1 }} pww_diplo_offer_changed = yes")
                else:
                    kind = {1: 3, 2: 4, 3: 5, 4: 6}[p]
                    act = (f"set_temp_variable = {{ pww_dba_side = {s} }} set_temp_variable = {{ pww_dba_kind = {kind} }} "
                           f"set_temp_variable = {{ pww_dba_x = {j} }} pww_diplo_bundle_add = yes "
                           f"set_variable = {{ pww_dbm_side = -1 }} set_variable = {{ pww_dbm_page = 0 }} pww_diplo_offer_changed = yes")
                click.append(f"\t\t\t\t\tif = {{ limit = {{ {cv('pww_dmc_s', '=', s)} {cv('pww_dmc_p', '=', p)} }} {act} }}\n")
        b.btn(f"m{j}", GL + 8, y, "GFX_pww_dt_menurow", w=CW - 16, h=20, vis=vis,
              click=("\t\t\t\tROOT = {\n\t\t\t\t\tset_temp_variable = { pww_dmc_s = pww_dbm_side }\n"
                     "\t\t\t\t\tset_temp_variable = { pww_dmc_p = pww_dbm_page }\n" + "".join(click) + "\t\t\t\t}\n"),
              enabled=R(cv(f"pww_dbm_en_{j}", "=", 1)))
        b.tb(f"m{j}_l", GL + 16, y + 1, f"[pww_dt_sl_ml_{j}]", 210, vis=vis)
        b.tb(f"m{j}_h", GL + 226, y + 1, f"[pww_dt_sl_mh_{j}]", CW - 242, fmt="right", vis=vis)
    for yb_rows, pv in ((7, "OR = { check_variable = { pww_dbm_page = 1 } check_variable = { pww_dbm_page = 4 } }"),
                        (8, "OR = { check_variable = { pww_dbm_page = 2 } check_variable = { pww_dbm_page = 3 } }")):
        yb = MENU_Y + 34 + yb_rows * 22 + 4
        b.btn(f"mback{yb_rows}", GL + 8, yb, "GFX_pww_dt_menurow", w=120, h=20, text="pww_dt_back",
              vis=MENU_OPEN + " " + R(pv),
              click=root_do("set_variable = { pww_dbm_page = 0 }", "pww_diplo_menu_enable = yes",
                            "add_to_variable = { pww_diplo_dirty = 1 }"))
    loc("pww_dt_back", "Back")


def menu_loc():
    dt("pww_dt_sl_mtitle", [(R(cv("pww_dbm_side", "=", 0)), loc("pww_dt_mtitle_0", "Add to our side")),
                            ], loc("pww_dt_mtitle_1", "Ask for something"))
    p0_label = ["Resource", "Civilian factories", "Political power per day", "Equipment shipment",
                "Production licence", "Mine lease"]
    p0_icon = ["£resources_strip|5", "£civ_factory", "£pol_power", "£production_cost", "£tech_mod", "£resources_strip|4"]
    for j in range(8):
        lab, hint = [], []
        off = R(cv(f"pww_dbm_en_{j}", "=", 0))
        for s in (0, 1):
            sd = cv("pww_dbm_side", "=", s)
            g = f"pww_dmg{s}"
            # page 0
            if j < 6:
                pg = f"{sd} {cv('pww_dbm_page', '=', 0)}"
                k_on = loc(f"pww_dt_ml_p0_{j}", f"{p0_icon[j]} {p0_label[j]}")
                k_off = loc(f"pww_dt_ml_p0_{j}_off", f"§g{p0_label[j]}§!")
                lab += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), k_off), (R(pg), k_on)]
                if s == 0:
                    texts = [("from our surplus", "we produce nothing spare"),
                             (f"we have {num(g + '_civ')} free", "none free"),
                             (f"we gain {num(g + '_pp', 2)} a day", "already listed"),
                             ("rifles, guns, trucks", "our stockpile is empty"),
                             ("let them build our designs", "nothing we can license"),
                             ("lease them one of our mines", "we own no producing mines")]
                else:
                    texts = [("what they produce", "they produce nothing"),
                             (f"they have {num(g + '_civ')} free", "none free"),
                             (f"they gain {num(g + '_pp', 2)} a day", "already listed"),
                             ("what they've built", "their stockpile is empty"),
                             ("build their designs", "nothing they can license"),
                             ("lease one of their mines", "they own no producing mines")]
                on_t, off_t = texts[j]
                if j in (1, 2):
                    hint.append((R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)} {cv(f'pww_dmh_has{j}', '=', 1)}"),
                                 loc("pww_dt_mh_listed", "§Ralready on the table§!")))
                hint += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), loc(f"pww_dt_mh_p0_{s}_{j}_off", f"§R{off_t}§!")),
                         (R(pg), loc(f"pww_dt_mh_p0_{s}_{j}", f"§g{on_t}§!"))]
            # page 1: resources
            if j < 7:
                pg = f"{sd} {cv('pww_dbm_page', '=', 1)}"
                lab += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), loc(f"pww_dt_ml_res_{j}_off", f"§g{RES[j]}§!")),
                        (R(pg), loc(f"pww_dt_ml_res_{j}", f"{RES_ICON[j]} {RES[j]}"))]
                # sender figures: pww_dmg0_r<j>_sh / _sp ; target: pww_dmg1_...
                us, th = "pww_dmg0", "pww_dmg1"
                if s == 1:
                    a = [(R(cv(f"{us}_r{j}_sh", ">", 0.5)), loc(f"pww_dt_mh_r1a_{j}", f"we're short {num(f'{us}_r{j}_sh')}"))]
                    a_def = loc("pww_dt_mh_enough", "we have enough")
                    bb = [(R(cv(f"{th}_r{j}_sp", ">", 0.5)), loc(f"pww_dt_mh_r1b_{j}", f"they have {num(f'{th}_r{j}_sp')} spare"))]
                    b_def = loc("pww_dt_mh_they_nosp", "they have none spare")
                    off_t = "they produce none"
                else:
                    a = [(R(cv(f"{us}_r{j}_sp", ">", 0.5)), loc(f"pww_dt_mh_r0a_{j}", f"we have {num(f'{us}_r{j}_sp')} spare"))]
                    a_def = loc("pww_dt_mh_we_nosp", "we have none spare")
                    bb = [(R(cv(f"{th}_r{j}_sh", ">", 0.5)), loc(f"pww_dt_mh_r0b_{j}", f"they're short {num(f'{th}_r{j}_sh')}"))]
                    b_def = loc("pww_dt_mh_they_enough", "they have enough")
                    off_t = "we produce none"
                dt(f"pww_dt_sl_mra_{s}_{j}", a, a_def)
                dt(f"pww_dt_sl_mrb_{s}_{j}", bb, b_def)
                hint += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), loc(f"pww_dt_mh_r{s}_{j}_off", f"§R{off_t}§!")),
                         (R(pg), loc(f"pww_dt_mh_r{s}_{j}", f"§g[pww_dt_sl_mra_{s}_{j}] · [pww_dt_sl_mrb_{s}_{j}]§!"))]
            # page 2: equipment
            pg = f"{sd} {cv('pww_dbm_page', '=', 2)}"
            who = "we hold" if s == 0 else "they hold"
            lab += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), loc(f"pww_dt_ml_eq_{j}_off", f"§g{EQ[j]}§!")),
                    (R(pg), loc(f"pww_dt_ml_eq_{j}", f"£production_cost {EQ[j]}"))]
            hint += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), loc(f"pww_dt_mh_eq{s}_{j}_off", "§Rnot enough in stock§!")),
                     (R(pg), loc(f"pww_dt_mh_eq{s}_{j}", f"§g{who} {num(f'pww_dmg{s}_e{j}')}§!"))]
            # page 3: licences
            pg = f"{sd} {cv('pww_dbm_page', '=', 3)}"
            lab += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), loc(f"pww_dt_ml_lic_{j}_off", f"§g{LIC[j]}§!")),
                    (R(pg), loc(f"pww_dt_ml_lic_{j}", f"£tech_mod {LIC[j]}"))]
            hint += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), loc(f"pww_dt_mh_lic{s}_{j}_off", "§Rnot researched§!")),
                     (R(pg), loc(f"pww_dt_mh_lic{s}", "§gour design§!" if s == 0 else "§gtheir design§!"))]
            # page 4: mine leases
            if j < 7:
                pg = f"{sd} {cv('pww_dbm_page', '=', 4)}"
                lab += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), f"pww_dt_ml_res_{j}_off"),
                        (R(pg), f"pww_dt_ml_res_{j}")]
                hint += [(R(f"{pg} {cv(f'pww_dbm_en_{j}', '=', 0)}"), loc("pww_dt_mh_nomine", "§Rno producing mines§!")),
                         (R(pg), loc(f"pww_dt_mh_st{s}_{j}", f"§g{num(f'pww_dmg{s}_s{j}')} producing states§!"))]
        dt(f"pww_dt_sl_ml_{j}", lab, "pww_dt_empty")
        dt(f"pww_dt_sl_mh_{j}", hint, "pww_dt_empty")


def terms(b, recv):
    y = TERMS_Y
    if recv:
        b.tb("terms", GL, y + 2, "[pww_dt_sl_rterms]", CW, fmt="centre")
        cases = []
        for i, w in enumerate(LEN):
            for bd, bt in ((0, "Either side may end it"), (1, "Fixed contract")):
                cases.append((R(f"{cv('pww_do_len', '=', i)} {cv('pww_do_bind', '=', bd)}"),
                              loc(f"pww_dt_rterms_{i}_{bd}", f"§gLength§! {w}   §gBinding§! {bt}")))
        dt("pww_dt_sl_rterms", cases, "pww_dt_empty")
        return
    vis = MENU_CLOSED
    b.tb("len_l", GL, y + 3, loc("pww_dt_len", "§gLength§!"), 60, vis=vis)
    bw = (CW - 62) // 4 - 4
    for i, w in enumerate(LEN):
        x = GL + 62 + i * (bw + 4)
        on = R(cv("pww_do_len", "=", i))
        off = R(f"NOT = {{ {cv('pww_do_len', '=', i)} }}")
        loc(f"pww_dt_len_{i}", w)
        b.btn(f"len{i}_on", x, y, "GFX_pww_dt_seg_on", w=bw, h=22, text=loc(f"pww_dt_len_on_{i}", f"§Y{w}§!"), vis=vis + " " + on)
        b.btn(f"len{i}_off", x, y, "GFX_pww_dt_seg", w=bw, h=22, text=f"pww_dt_len_{i}", vis=vis + " " + off,
              click=root_do(f"set_variable = {{ pww_do_len = {i} }}", "pww_diplo_offer_changed = yes"))
    y2 = y + 26
    b.tb("bind_l", GL, y2 + 3, loc("pww_dt_bind", "§gBinding§!"), 60, vis=vis)
    half = (CW - 62) // 2 - 2
    widths = [(GL + 62, half, "Either side may end it"), (GL + 62 + half + 4, CW - 62 - half - 4, "Fixed contract")]
    for i, (x, w, t) in enumerate(widths):
        on = R(cv("pww_do_bind", "=", i))
        off = R(f"NOT = {{ {cv('pww_do_bind', '=', i)} }}")
        loc(f"pww_dt_bind_{i}", t)
        b.btn(f"bind{i}_on", x, y2, "GFX_pww_dt_seg_on", w=w, h=22, text=loc(f"pww_dt_bind_on_{i}", f"§Y{t}§!"), vis=vis + " " + on)
        b.btn(f"bind{i}_off", x, y2, "GFX_pww_dt_seg", w=w, h=22, text=f"pww_dt_bind_{i}", vis=vis + " " + off,
              click=root_do(f"set_variable = {{ pww_do_bind = {i} }}", "pww_diplo_offer_changed = yes"),
              enabled=R(cv("pww_do_once", "=", 0)) if i == 0 else None,
              tooltip="pww_dt_tt_fixed" if i == 0 else None)
    b.tb("note", GL, y2 + 24, loc("pww_dt_note_once", "§gShipments, licences and mine leases need a fixed contract.§!"),
         CW, vis=vis + " " + R(cv("pww_do_once", "=", 1)))


def summary_loc():
    term = [(R(cv("pww_do_len", "=", i)), loc(f"pww_dt_term_{i}", w)) for i, w in enumerate(LEN_WORDS)]
    dt("pww_dt_sl_term", term, "pww_dt_empty")
    for recv in (0, 1):
        get_s, pay_s = (0, 1) if recv else (1, 0)
        dt(f"pww_dt_sl_get_{recv}", [(R(cv(f"pww_do_n{get_s}", "=", 0)),
                                      loc(f"pww_dt_get_none_{recv}", "§gNothing comes to us yet.§!" if recv else "§gAsk them for something.§!"))],
           loc(f"pww_dt_get_{recv}", f"You get {side_list(get_s)} for [pww_dt_sl_term]."))
        dt(f"pww_dt_sl_pay_{recv}", [(R(cv(f"pww_do_n{pay_s}", "=", 0)),
                                      loc(f"pww_dt_pay_none_{recv}", "§gThey ask nothing of us.§!" if recv else "§gOffer something in return.§!"))],
           loc(f"pww_dt_pay_{recv}", f"You pay {side_list(pay_s)}."))
        loc(f"pww_dt_summary_{recv}", f"[pww_dt_sl_get_{recv}] [pww_dt_sl_pay_{recv}]")
    # Market figures: one decimal, whole numbers without it; 1 factory singular.
    for v in ("v0", "v1", "m0"):
        dt(f"pww_dt_sl_f_{v}", [
            (R(cv(f"pww_dbm_{v}_one", "=", 1)), loc(f"pww_dt_f_{v}_one", "§Y1§! factory")),
            (R(cv(f"pww_dbm_{v}_int", "=", 1)), loc(f"pww_dt_f_{v}_int", f"§Y{num(f'pww_dbm_{v}')}§! factories")),
        ], loc(f"pww_dt_f_{v}", f"§Y{num(f'pww_dbm_{v}', 1)}§! factories"))
    # Send perspective
    one = R(f"{cv('pww_dbm_one', '=', 1)}")
    first = [(R(f"{cv('pww_do_frame', '=', 0)} {cv('pww_dbm_one', '=', 1)}"),
              loc("pww_dt_mk_buy_one", "At market, [pww_dt_sl_li_4] costs [pww_dt_sl_f_v1].")),
             (R(cv("pww_do_frame", "=", 0)), loc("pww_dt_mk_buy", "At market, what you ask for costs [pww_dt_sl_f_v1].")),
             (R(f"{cv('pww_do_frame', '=', 1)} {cv('pww_dbm_one0', '=', 1)}"),
              loc("pww_dt_mk_sell_one", "At market, [pww_dt_sl_li_0] is worth [pww_dt_sl_f_v0].")),
             (R(cv("pww_do_frame", "=", 1)), loc("pww_dt_mk_sell", "At market, what you give is worth [pww_dt_sl_f_v0]."))]
    dt("pww_dt_sl_mk_first", first, loc("pww_dt_mk_mixed", "At market, you give [pww_dt_sl_f_m0] and get [pww_dt_sl_f_v1]."))
    verdict = []
    for fr, words in ((0, ("Your offer is §Rbelow market§!.", "Your offer is §Yat market§!.", "Your offer is §Gabove market§!.")),
                      (1, ("Your price is §Rabove market§!.", "Your price is §Yat market§!.", "Your price is §Gbelow market§!.")),
                      (2, ("The deal §Rfavours you§!.", "The deal is §Yeven§!.", "The deal §Gfavours them§!."))):
        for mk, w in zip((-1, 0, 1), words):
            verdict.append((R(f"{cv('pww_do_frame', '=', fr)} {cv('pww_do_mk', '=', mk)}"), loc(f"pww_dt_mkv_{fr}_{mk + 1}", w)))
    dt("pww_dt_sl_mk_verdict", verdict, "pww_dt_empty")
    loc("pww_dt_market_0", "§g[pww_dt_sl_mk_first]§! [pww_dt_sl_mk_verdict]")
    # Receive perspective: raw market both ways.
    rv = [(R(cv("pww_dbm_rmk", "=", -1)), loc("pww_dt_rmk_0", "Their offer is §Rbelow market§!.")),
          (R(cv("pww_dbm_rmk", "=", 0)), loc("pww_dt_rmk_1", "Their offer is §Yat market§!."))]
    dt("pww_dt_sl_rmk", rv, loc("pww_dt_rmk_2", "Their offer is §Gabove market§!."))
    loc("pww_dt_market_1", "§gAt market, you give [pww_dt_sl_f_v1] and get [pww_dt_sl_f_v0].§! [pww_dt_sl_rmk]")
    # Invalid reasons (send)
    inv = {51: "Put something on each side of the table.",
           52: "A trade deal needs a resource or a mine lease on one side.",
           53: "They produce none of a resource you ask for.",
           54: "We produce none of a resource we offer.",
           56: "We do not have that many free civilian factories.",
           57: "They do not have that many free civilian factories.",
           58: "We do not hold that much equipment.",
           59: "They do not hold that much equipment.",
           60: "We have not researched a design we offer to license.",
           61: "They have not researched a design we ask to license.",
           62: "There is no producing state for that mine lease.",
           63: "Lease Mines needs a mine lease on their side."}
    dt("pww_dt_sl_invalid", [(R(cv("pww_do_valid", "=", c)), loc(f"pww_dt_invalid_{c}", f"§R{t}§!")) for c, t in inv.items()],
       "pww_dt_empty")
    # Party header surplus line
    for recv in (0, 1):
        g = "pww_dmg0" if recv else "pww_dmg1"
        cases = [(R(cv(f"{g}_top", "=", r)), loc(f"pww_dt_top_{recv}_{r}", f"§g{RES[r]} surplus: {num(g + '_topa')}§!"))
                 for r in range(7)]
        dt(f"pww_dt_sl_top_{recv}", cases, loc("pww_dt_top_none", "§gNo resource surplus§!"))


def envoy_loc():
    chips = []
    dt("pww_dt_sl_c_rl", [(R(cv("pww_dd_rl", "=", i)), loc(f"pww_dt_c_rl_{i}", f"§RWon't:§! {t}     "))
                          for i, t in enumerate(RL_CHIP)], "pww_dt_empty")
    dt("pww_dt_sl_c_floor", [(R(cv("pww_dd_floor", "=", 1)), loc("pww_dt_c_floor", "§RWon't:§! go below market     "))],
       "pww_dt_empty")
    dt("pww_dt_sl_c_want", [(R(cv("pww_dd_want", "=", i)), loc(f"pww_dt_c_want_{i}", f"§GWants:§! {t}     "))
                            for i, t in enumerate(WANT_CHIP)], "pww_dt_empty")
    dt("pww_dt_sl_c_pat", [(R(cv("pww_dd_closed", "=", 1)), loc("pww_dt_c_closed", "§RTalks closed§!"))]
       + [(R(cv("pww_dd_pat", "=", i)), loc(f"pww_dt_c_pat_{i}", f"§gPatience:§! {w}")) for i, w in enumerate(PAT_WORDS)],
       "pww_dt_empty")
    loc("pww_dt_chips", "[pww_dt_sl_c_rl][pww_dt_sl_c_floor][pww_dt_sl_c_want][pww_dt_sl_c_pat]")
    loc("pww_dt_envoy", "\"[pww_diplo_sl_o_line]\"")
    dt("pww_dt_sl_round", [(R(cv("pww_dd_closed", "=", 1)), loc("pww_dt_round_closed", "§RTalks closed§!"))]
       + [(R(cv("pww_dd_round", "=", i)), loc(f"pww_dt_round_{i}", f"§gRound§! {i + 1} §gof 4§!")) for i in range(4)],
       "pww_dt_round_3")
    # Receive GUI lines (an AI sender answering a human counter)
    loc("pww_dt_rline_96", "[ROOT.GetName] has redrafted the terms after our counter.")
    loc("pww_dt_rline_97", "[ROOT.GetName] will not move further. These are their terms.")
    dt("pww_dt_sl_rline", [(R(cv("pww_dd_line", "=", 96)), "pww_dt_rline_96"),
                           (R(cv("pww_dd_line", "=", 97)), "pww_dt_rline_97")],
       loc("pww_dt_rline_0", "[ROOT.GetName] tables these terms."))


def build_send(effects, triggers):
    b = B("pww_diplo_send_offer_gui", "pww_so")
    party_header(b, False)
    divider(b, "div0", 36)
    b.tb("h0", COLX[0], 46, loc("pww_dt_h_give", "§gWE GIVE§!"), COLW, vis=MENU_CLOSED)
    b.tb("h1", COLX[1], 46, loc("pww_dt_h_get", "§gTHEY GIVE§!"), COLW, vis=MENU_CLOSED)
    build_rows(b, False)
    for s in (0, 1):
        for c in range(4):
            y = ROW_Y0 + c * ROW_H + 2
            b.btn(f"add{s}_{c}", COLX[s], y, "GFX_pww_dt_add", w=COLW, h=22,
                  text=loc(f"pww_dt_add_{s}", "+ Add to our side" if s == 0 else "+ Ask for something"),
                  vis=MENU_CLOSED + " " + R(cv(f"pww_do_n{s}", "=", c)),
                  click=root_do(f"set_variable = {{ pww_dbm_side = {s} }}", "set_variable = { pww_dbm_page = 0 }",
                                "pww_diplo_bundle_mirror = yes", "add_to_variable = { pww_diplo_dirty = 1 }"))
    terms(b, False)
    menu(b)
    divider(b, "div1", 306)
    b.tb("sum", GL, 314, "pww_dt_summary_0", CW, h=52)
    b.tb("mkt", GL, 366, "pww_dt_market_0", CW, h=34, vis=R(cv("pww_do_valid", "=", 0)))
    b.tb("inv", GL, 366, "[pww_dt_sl_invalid]", CW, h=34, vis=R(f"NOT = {{ {cv('pww_do_valid', '=', 0)} }}"))
    divider(b, "div2", 400)
    b.tb("envoy", GL, 408, "pww_dt_envoy", CW, h=36)
    b.tb("chips", GL, 446, "pww_dt_chips", CW, h=18)
    # Centred above the gap between the vanilla Cancel and Send buttons.
    b.tb("round", 200, 468, "[pww_dt_sl_round]", 184, fmt="centre")
    effects[b.g] = b.eff
    triggers[b.g] = b.trg
    return b.window("pww_diplo_send_offer", H_SEND)


def build_recv(effects, triggers):
    b = B("pww_diplo_recv_offer_gui", "pww_ro")
    party_header(b, True)
    divider(b, "div0", 36)
    b.tb("h0", COLX[0], 46, "pww_dt_h_give", COLW)
    b.tb("h1", COLX[1], 46, "pww_dt_h_get", COLW)
    build_rows(b, True)
    terms(b, True)
    divider(b, "div1", 258)
    b.tb("sum", GL, 266, "pww_dt_summary_1", CW, h=52)
    b.tb("mkt", GL, 318, "pww_dt_market_1", CW)
    divider(b, "div2", 340)
    b.tb("line", GL, 350, "[pww_dt_sl_rline]", CW, h=36)
    # Counter marks: decline with one marked to send it back as a counter.
    y = 388
    for v, t in ((1, "Counter: ask them to pay more"), (2, "Counter: give them less"), (3, "Counter: a shorter term")):
        on = cv("pww_dr_counter", "=", v)
        click = (f"\t\t\t\tif = {{ limit = {{ {on} }} set_variable = {{ pww_dr_counter = 0 }} }}\n"
                 f"\t\t\t\telse = {{ set_variable = {{ pww_dr_counter = {v} }} }}\n"
                 f"\t\t\t\tadd_to_variable = {{ pww_diplo_dirty = 1 }}\n")
        b.btn(f"c{v}_off", GL, y + 2, "GFX_pww_diplo_box_off", vis=f"NOT = {{ {on} }}", click=click)
        b.btn(f"c{v}_on", GL, y + 2, "GFX_pww_diplo_box_on", vis=on, click=click)
        b.tb(f"c{v}_l", GL + 22, y + 1, loc(f"pww_dt_counter_{v}", t), CW - 22)
        y += 22
    b.tb("hint", GL, y + 2, loc("pww_dt_counter_hint", "§gAccept signs these terms. Decline with a counter marked sends it back.§!"), CW)
    effects[b.g] = b.eff
    triggers[b.g] = b.trg
    return b.window("pww_diplo_recv_offer", H_RECV)


loc("pww_dt_tt_remove", "Take this item off the table.")
loc("pww_dt_tt_fixed", "Equipment shipments, licences and mine leases are one-time or irreversible: they need a fixed contract.")

summary_loc()
envoy_loc()
menu_loc()
# Run the layout builders once so every label they create is in L for the
# loc generator (the GUI generator runs them again; dt() ignores repeats).
build_send({}, {})
build_recv({}, {})

SPRITES = """	corneredTileSpriteType = {
		name = "GFX_pww_dt_seg"
		size = { x = 90 y = 22 }
		textureFile = "gfx/interface/diplo_countrylist_entry.dds"
		borderSize = { x = 8 y = 8 }
		effectFile = "gfx/FX/buttonstate.lua"
	}
	corneredTileSpriteType = {
		name = "GFX_pww_dt_seg_on"
		size = { x = 90 y = 22 }
		textureFile = "gfx/interface/button_123x34.dds"
		borderSize = { x = 8 y = 8 }
		effectFile = "gfx/FX/buttonstate.lua"
	}
	corneredTileSpriteType = {
		name = "GFX_pww_dt_add"
		size = { x = 208 y = 22 }
		textureFile = "gfx/interface/diplo_countrylist_entry.dds"
		borderSize = { x = 8 y = 8 }
		effectFile = "gfx/FX/buttonstate.lua"
	}
	corneredTileSpriteType = {
		name = "GFX_pww_dt_menu"
		size = { x = 432 y = 236 }
		textureFile = "gfx/interface/tiles/tiled_window_1b_border.dds"
		borderSize = { x = 12 y = 12 }
	}
	corneredTileSpriteType = {
		name = "GFX_pww_dt_menurow"
		size = { x = 416 y = 20 }
		textureFile = "gfx/interface/diplo_countrylist_entry.dds"
		borderSize = { x = 6 y = 6 }
		effectFile = "gfx/FX/buttonstate.lua"
	}
"""


# ----------------------------------------------------------------------------
# Display mirror effects (scripted effects file)
# ----------------------------------------------------------------------------
def mirror_effects():
    o = ["###############################################################################\n"
         "# Power Without War: trade talks display mirror (GENERATED by\n"
         "# tools/pww_diplo_gen_talks.py; edit the generator, not this file).\n"
         "#\n"
         "# pww_diplo_bundle_mirror (sender scope): copies the bundle arrays into plain\n"
         "# per-slot variables the GUI and scripted loc read (pww_dbk_<n> kind,\n"
         "# pww_dbx_<n>, pww_dba_<n> amount, pww_dbs_<n> lease state, pww_dbu_<n> lease\n"
         "# output, pww_dbf_<n> the giver's figure: free factories, political power a\n"
         "# day or stock; resource rows pww_dbss/sp (sender short/spare) and\n"
         "# pww_dbts/tp (target)), the market figures (pww_dbm_v0/v1/m0 with _int and\n"
         "# _one flags, pww_dbm_one / one0, pww_dbm_rmk) and the add-menu figures\n"
         "# (pww_dmg<side>_*: civ, pp, r<res>_sp/_sh, e<eq>, s<res>, top/topa) and\n"
         "# enabled rows pww_dbm_en_<row>. Side 0 figures are the sender's, side 1 the\n"
         "# target's.\n"
         "# pww_diplo_bundle_copy_display (sender scope): copies everything the receive\n"
         "# GUI reads to pww_do_target.\n"
         "###############################################################################\n"]
    m = ["pww_diplo_bundle_mirror = {\n\tpww_diplo_bundle_ensure = yes\n"]
    for n in range(8):
        giver = "THIS" if n < 4 else "var:pww_do_target"
        m.append(f"\tset_variable = {{ pww_dbk_{n} = pww_dob_k^{n} }}\n"
                 f"\tset_variable = {{ pww_dbx_{n} = pww_dob_x^{n} }}\n"
                 f"\tset_variable = {{ pww_dba_{n} = pww_dob_a^{n} }}\n"
                 f"\tset_variable = {{ pww_dbf_{n} = 0 }}\n")
        m.append(f"\tif = {{\n\t\tlimit = {{ check_variable = {{ pww_dbk_{n} = 1 }} }}\n"
                 f"\t\t{giver} = {{ set_temp_variable = {{ pww_dgm_f = num_of_civilian_factories_available_for_projects }} }}\n"
                 f"\t\tset_variable = {{ pww_dbf_{n} = pww_dgm_f }}\n\t}}\n")
        m.append(f"\telse_if = {{\n\t\tlimit = {{ check_variable = {{ pww_dbk_{n} = 2 }} }}\n"
                 f"\t\t{giver} = {{ set_temp_variable = {{ pww_dgm_f = political_power_daily }} }}\n"
                 f"\t\tset_variable = {{ pww_dbf_{n} = pww_dgm_f }}\n\t}}\n")
        m.append(f"\telse_if = {{\n\t\tlimit = {{ check_variable = {{ pww_dbk_{n} = 3 }} }}\n"
                 f"\t\tset_temp_variable = {{ pww_dg_res = pww_dbx_{n} }}\n"
                 f"\t\tpww_diplo_read_res = yes\n"
                 f"\t\tset_temp_variable = {{ pww_dgm_n = pww_dg_net }}\n"
                 f"\t\tpww_diplo_mirror_net = yes\n"
                 f"\t\tset_variable = {{ pww_dbss_{n} = pww_dgm_sh }}\n\t\tset_variable = {{ pww_dbsp_{n} = pww_dgm_sp }}\n"
                 f"\t\tvar:pww_do_target = {{ pww_diplo_read_res = yes }}\n"
                 f"\t\tset_temp_variable = {{ pww_dgm_n = pww_dg_net }}\n"
                 f"\t\tpww_diplo_mirror_net = yes\n"
                 f"\t\tset_variable = {{ pww_dbts_{n} = pww_dgm_sh }}\n\t\tset_variable = {{ pww_dbtp_{n} = pww_dgm_sp }}\n\t}}\n")
        m.append(f"\telse_if = {{\n\t\tlimit = {{ check_variable = {{ pww_dbk_{n} = 4 }} }}\n"
                 f"\t\tset_temp_variable = {{ pww_dg_eq = pww_dbx_{n} }}\n"
                 f"\t\t{giver} = {{ pww_diplo_read_equip = yes }}\n"
                 f"\t\tset_variable = {{ pww_dbf_{n} = pww_dg_stock }}\n\t}}\n")
        m.append(f"\telse_if = {{\n\t\tlimit = {{ check_variable = {{ pww_dbk_{n} = 6 }} }}\n"
                 f"\t\tset_variable = {{ pww_dbs_{n} = pww_dob_s^{n} }}\n"
                 f"\t\tset_variable = {{ pww_dbu_{n} = pww_dob_v^{n} }}\n"
                 f"\t\tmultiply_variable = {{ pww_dbu_{n} = 8 }}\n\t}}\n")
    # market figures
    for v, src in (("v0", "pww_do_mk_v0"), ("v1", "pww_do_mk_v1"), ("m0", "pww_do_mk_m0")):
        m.append(f"\tset_temp_variable = {{ pww_dgm_v = {src} }}\n"
                 f"\tmultiply_temp_variable = {{ pww_dgm_v = 10 }}\n\tround_temp_variable = pww_dgm_v\n"
                 f"\tdivide_temp_variable = {{ pww_dgm_v = 10 }}\n"
                 f"\tset_variable = {{ pww_dbm_{v} = pww_dgm_v }}\n"
                 f"\tset_temp_variable = {{ pww_dgm_i = pww_dgm_v }}\n\tround_temp_variable = pww_dgm_i\n"
                 f"\tset_variable = {{ pww_dbm_{v}_int = 0 }}\n\tset_variable = {{ pww_dbm_{v}_one = 0 }}\n"
                 f"\tif = {{ limit = {{ check_variable = {{ pww_dgm_i = pww_dgm_v }} }} set_variable = {{ pww_dbm_{v}_int = 1 }} }}\n"
                 f"\tif = {{ limit = {{ check_variable = {{ pww_dgm_v = 1 }} }} set_variable = {{ pww_dbm_{v}_one = 1 }} }}\n")
    m.append("\tset_variable = { pww_dbm_one = 0 }\n"
             "\tif = { limit = { check_variable = { pww_do_n1 = 1 } check_variable = { pww_dbk_4 = 3 } } set_variable = { pww_dbm_one = 1 } }\n"
             "\tset_variable = { pww_dbm_one0 = 0 }\n"
             "\tif = { limit = { check_variable = { pww_do_n0 = 1 } check_variable = { pww_dbk_0 = 3 } } set_variable = { pww_dbm_one0 = 1 } }\n"
             "\t# Receive view: raw market both ways.\n"
             "\tset_temp_variable = { pww_dgm_d = pww_do_mk_v0 }\n"
             "\tsubtract_from_temp_variable = { pww_dgm_d = pww_do_mk_v1 }\n"
             "\tset_temp_variable = { pww_dgm_t = pww_do_mk_v1 }\n"
             "\tmultiply_temp_variable = { pww_dgm_t = 0.05 }\n"
             "\tif = { limit = { check_variable = { pww_dgm_t < 0.05 } } set_temp_variable = { pww_dgm_t = 0.05 } }\n"
             "\tset_variable = { pww_dbm_rmk = 0 }\n"
             "\tif = { limit = { check_variable = { pww_dgm_d > pww_dgm_t } } set_variable = { pww_dbm_rmk = 1 } }\n"
             "\tmultiply_temp_variable = { pww_dgm_d = -1 }\n"
             "\tif = { limit = { check_variable = { pww_dgm_d > pww_dgm_t } } set_variable = { pww_dbm_rmk = -1 } }\n")
    # menu figures per side
    for s in (0, 1):
        sc = "THIS" if s == 0 else "var:pww_do_target"
        g = f"pww_dmg{s}"
        m.append(f"\t{sc} = {{\n"
                 f"\t\tset_temp_variable = {{ pww_dgm_c = num_of_civilian_factories_available_for_projects }}\n"
                 f"\t\tset_temp_variable = {{ pww_dgm_p = political_power_daily }}\n\t}}\n"
                 f"\tset_variable = {{ {g}_civ = pww_dgm_c }}\n\tset_variable = {{ {g}_pp = pww_dgm_p }}\n"
                 f"\tset_variable = {{ {g}_top = -1 }}\n\tset_variable = {{ {g}_topa = 0 }}\n")
        for r in range(7):
            m.append(f"\tset_temp_variable = {{ pww_dg_res = {r} }}\n"
                     f"\t{sc} = {{ pww_diplo_read_res = yes }}\n"
                     f"\tset_temp_variable = {{ pww_dgm_n = pww_dg_net }}\n\tpww_diplo_mirror_net = yes\n"
                     f"\tset_variable = {{ {g}_r{r}_sh = pww_dgm_sh }}\n\tset_variable = {{ {g}_r{r}_sp = pww_dgm_sp }}\n"
                     f"\tset_variable = {{ {g}_r{r}_pr = pww_dg_prod }}\n"
                     f"\tif = {{ limit = {{ check_variable = {{ pww_dgm_sp > {g}_topa }} }} set_variable = {{ {g}_topa = pww_dgm_sp }} set_variable = {{ {g}_top = {r} }} }}\n"
                     f"\tset_temp_variable = {{ pww_dg_slot = 0 }}\n"
                     f"\t{sc} = {{ pww_diplo_pick_state_scope = yes }}\n"
                     f"\tset_variable = {{ {g}_s{r} = pww_dg_nstates }}\n")
        for e in range(8):
            m.append(f"\tset_temp_variable = {{ pww_dg_eq = {e} }}\n"
                     f"\t{sc} = {{ pww_diplo_read_equip = yes }}\n"
                     f"\tset_variable = {{ {g}_e{e} = pww_dg_stock }}\n\tset_variable = {{ {g}_l{e} = pww_dg_tech }}\n"
                     f"\tpww_diplo_equip_step = yes\n\tset_variable = {{ {g}_q{e} = pww_dg_step }}\n")
    # enabled rows for the open menu
    m.append("\tpww_diplo_menu_enable = yes\n}\n\n")
    # Net helper
    m.append("# in pww_dgm_n (net balance). out pww_dgm_sh (shortfall), pww_dgm_sp (spare),\n# both rounded and never negative.\n"
             "pww_diplo_mirror_net = {\n\tset_temp_variable = { pww_dgm_sp = pww_dgm_n }\n\tround_temp_variable = pww_dgm_sp\n"
             "\tset_temp_variable = { pww_dgm_sh = pww_dgm_sp }\n\tmultiply_temp_variable = { pww_dgm_sh = -1 }\n"
             "\tclamp_temp_variable = { var = pww_dgm_sp min = 0 max = 99999 }\n"
             "\tclamp_temp_variable = { var = pww_dgm_sh min = 0 max = 99999 }\n}\n\n")
    # Menu enable flags
    en = ["# Sender scope. pww_dbm_en_<row> for the open menu side and page.\npww_diplo_menu_enable = {\n"]
    for j in range(9):
        en.append(f"\tset_variable = {{ pww_dbm_en_{j} = 0 }}\n")
    for s in (0, 1):
        g = f"pww_dmg{s}"
        lo, hi = (0, 4) if s == 0 else (4, 8)
        # page 0
        en.append(f"\tif = {{\n\t\tlimit = {{ check_variable = {{ pww_dbm_side = {s} }} check_variable = {{ pww_dbm_page = 0 }} }}\n")
        en.append("\t\tset_temp_variable = { pww_dgm_hc = 0 }\n\t\tset_temp_variable = { pww_dgm_hp = 0 }\n")
        en.append(f"\t\tfor_loop_effect = {{\n\t\t\tstart = {lo}\n\t\t\tend = {hi}\n\t\t\tvalue = pww_dgm_i\n"
                  "\t\t\tif = { limit = { check_variable = { pww_dob_k^pww_dgm_i = 1 } } set_temp_variable = { pww_dgm_hc = 1 } }\n"
                  "\t\t\tif = { limit = { check_variable = { pww_dob_k^pww_dgm_i = 2 } } set_temp_variable = { pww_dgm_hp = 1 } }\n\t\t}\n")
        anyres = " ".join(f"check_variable = {{ {g}_r{r}_pr > 0.999 }}" for r in range(7))
        anyeq = " ".join(f"check_variable = {{ {g}_e{e} > {g}_q{e} }}" for e in range(8))
        anylic = " ".join(f"check_variable = {{ {g}_l{e} = 1 }}" for e in range(8))
        anyst = " ".join(f"check_variable = {{ {g}_s{r} > 0 }}" for r in range(7))
        en.append("\t\tset_variable = { pww_dmh_has1 = pww_dgm_hc }\n\t\tset_variable = { pww_dmh_has2 = pww_dgm_hp }\n")
        en.append(f"\t\tif = {{ limit = {{ OR = {{ {anyres} }} }} set_variable = {{ pww_dbm_en_0 = 1 }} }}\n"
                  f"\t\tif = {{ limit = {{ check_variable = {{ {g}_civ > 0.999 }} check_variable = {{ pww_dgm_hc = 0 }} }} set_variable = {{ pww_dbm_en_1 = 1 }} }}\n"
                  f"\t\tif = {{ limit = {{ check_variable = {{ pww_dgm_hp = 0 }} }} set_variable = {{ pww_dbm_en_2 = 1 }} }}\n"
                  f"\t\tif = {{ limit = {{ OR = {{ {anyeq} }} }} set_variable = {{ pww_dbm_en_3 = 1 }} }}\n"
                  f"\t\tif = {{ limit = {{ OR = {{ {anylic} }} }} set_variable = {{ pww_dbm_en_4 = 1 }} }}\n"
                  f"\t\tif = {{ limit = {{ OR = {{ {anyst} }} }} set_variable = {{ pww_dbm_en_5 = 1 }} }}\n\t}}\n")
        for p, test in ((1, lambda j: f"check_variable = {{ {g}_r{j}_pr > 0.999 }}"),
                        (2, lambda j: f"NOT = {{ check_variable = {{ {g}_e{j} < {g}_q{j} }} }}"),
                        (3, lambda j: f"check_variable = {{ {g}_l{j} = 1 }}"),
                        (4, lambda j: f"check_variable = {{ {g}_s{j} > 0 }}")):
            en.append(f"\tif = {{\n\t\tlimit = {{ check_variable = {{ pww_dbm_side = {s} }} check_variable = {{ pww_dbm_page = {p} }} }}\n")
            for j in range(MENU_PAGES[p]):
                en.append(f"\t\tif = {{ limit = {{ {test(j)} }} set_variable = {{ pww_dbm_en_{j} = 1 }} }}\n")
            en.append("\t}\n")
    en.append("}\n\n")
    # Copy for the receive GUI
    names = []
    for n in range(8):
        names += [f"pww_dbk_{n}", f"pww_dbx_{n}", f"pww_dba_{n}", f"pww_dbf_{n}", f"pww_dbss_{n}", f"pww_dbsp_{n}",
                  f"pww_dbts_{n}", f"pww_dbtp_{n}", f"pww_dbu_{n}"]
    names += ["pww_do_len", "pww_do_bind", "pww_do_n0", "pww_do_n1", "pww_do_frame", "pww_do_mk", "pww_do_valid",
              "pww_dbm_rmk", "pww_dbm_one", "pww_dbm_one0", "pww_dd_line", "pww_dd_round", "pww_dd_closed"]
    for v in ("v0", "v1", "m0"):
        names += [f"pww_dbm_{v}", f"pww_dbm_{v}_int", f"pww_dbm_{v}_one"]
    for s in (0, 1):
        names += [f"pww_dmg{s}_top", f"pww_dmg{s}_topa"]
    cp = ["pww_diplo_bundle_copy_display = {\n\tvar:pww_do_target = {\n"]
    for nm in names:
        cp.append(f"\t\tset_variable = {{ {nm} = PREV.{nm} }}\n")
    for n in range(8):
        cp.append(f"\t\tif = {{ limit = {{ PREV = {{ check_variable = {{ pww_dbk_{n} = 6 }} }} }} set_variable = {{ pww_dbs_{n} = PREV.pww_dbs_{n} }} }}\n")
    cp.append("\t}\n}\n")
    return "".join(o + m + en + cp)
