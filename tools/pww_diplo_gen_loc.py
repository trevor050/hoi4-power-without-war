"""Diplomacy lane generator: python tools/pww_diplo_gen_loc.py
Build the diplomacy lane's localisation from docs/content plus lane UI text."""
import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pww_diplo_gen_talks as talks

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_MAIN = os.path.join(REPO, "mod", "localisation", "english", "pww_diplo_l_english.yml")
OUT_ENV = os.path.join(REPO, "mod", "localisation", "english", "pww_diplo_envoys_l_english.yml")


def table_rows(md, section_start, section_end=None):
    """Yield (key, text) from markdown tables: first backticked key, last backticked text."""
    s = md
    if section_start:
        i = s.index(section_start)
        s = s[i:]
    if section_end and section_end in s:
        s = s[: s.index(section_end)]
    for line in s.splitlines():
        if not line.startswith("| `pww_"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        key = cells[0].strip("`")
        texts = [c for c in cells[1:] if c.startswith("`") and c.endswith("`")]
        yield key, cells, texts


def esc(t):
    # The content bible's GetCapitalName is not a loc function: vanilla uses
    # Capital.GetCapitalVictoryPointName (the capital city's name).
    t = t.replace(".GetCapitalName]", ".Capital.GetCapitalVictoryPointName]")
    return t.replace('"', '\\"').replace(chr(10), chr(92) + "n")


env_md = open(os.path.join(REPO, "docs", "content", "envoys.md"), encoding="utf-8").read()
wq_md = open(os.path.join(REPO, "docs", "content", "wolfram_question.md"), encoding="utf-8").read()

env = {}
# Envoy lines, red lines and wants are shown in the sender's GUI: THIS is the
# other side, ROOT is us. Patron and rival names come from pww_dd_patron.
for key, cells, texts in table_rows(env_md, "## 1. Envoy", None):
    t = texts[-1].strip("`")
    t = t.replace("[FROM.", "[THIS.").replace("[pww_patron.", "[?pww_dd_patron.").replace("[pww_rival.", "[?pww_dd_patron.")
    env[key] = t

main = {}
# Section 2 actions (sender side): FROM is the target -> THIS
for key, cells, texts in table_rows(wq_md, "## 2. Scripted Diplomatic Actions", "## 3. Receiver-Screen"):
    t = texts[-1].strip("`")
    main[key] = t.replace("[FROM.", "[THIS.")
# Section 3 receiver: FROM is the sender -> ROOT; ROOT (us) -> THIS
for key, cells, texts in table_rows(wq_md, "## 3. Receiver-Screen", "## 4. Seller-Written"):
    if len(texts) == 2 and key.startswith("pww_rcv_move_"):
        label, desc = texts[0].strip("`"), texts[1].strip("`")
        for k, t in ((key, label), (key + "_desc", desc)):
            t = t.replace("[ROOT.", "[THIS.").replace("[FROM.", "[ROOT.")
            main[k] = t
        continue
    t = texts[-1].strip("`")
    t = t.replace("[ROOT.", "[THIS.").replace("[FROM.", "[ROOT.")
    main[key] = t
# Section 4 lots
for key, cells, texts in table_rows(wq_md, "## 4. Seller-Written", "## 5. Fig Leaves"):
    if len(texts) == 2:
        main[key] = texts[0].strip("`")
        main[key + "_desc"] = texts[1].strip("`")
    else:
        main[key] = texts[-1].strip("`")
# Section 5 fig leaves (shown in the sender's GUI and tooltips)
for key, cells, texts in table_rows(wq_md, "## 5. Fig Leaves", "## 6. Resolution"):
    main[key] = texts[0].strip("`")
    main[key + "_desc"] = texts[1].strip("`").replace("[FROM.", "[THIS.")

# Placeholders the lanes do not provide as variables
main["pww_rcv_proposal_desc"] = main["pww_rcv_proposal_desc"].replace("[pww_res_name]", "[pww_diplo_sl_r_res]")
for k in ("pww_rcv_demand_quiet_desc", "pww_rcv_demand_public_desc"):
    main[k] = (main[k].replace("[pww_prize_name]", "[pww_diplo_sl_rd_res] output")
               .replace("before [pww_deadline_date]", "before the decision date")
               .replace("by [pww_deadline_date]", "by the decision date"))
main["pww_rcv_join_embargo_desc"] = (main["pww_rcv_join_embargo_desc"]
                                     .replace("[pww_target.GetName]", "[?pww_de_target.GetName]")
                                     .replace("before [pww_deadline_date]", "within the month"))
main["pww_auction_winner_line"] = main["pww_auction_winner_line"].replace("[pww_lot_name]", "the awarded lot").replace("[pww_winner.GetName]", "[?pww_dd_winner.GetName]")
main["pww_rcv_move_call_patron_desc"] = "Request an urgent commercial backstop or diplomatic intervention from our patrons."

ui = {
    # Action names and descriptions: the diplomacy panel looks up
    # <KEY>_TITLE and <KEY>_ACTION_DESC in upper case (and the bare upper key).
    # Send descriptions
    "pww_diplo_offer_send_desc": "Table these terms with [THIS.GetName].",
    "pww_diplo_lease_send_desc": "Table this concession request with [THIS.GetName].",
    "pww_diplo_demand_send_desc": "Deliver this demand to [THIS.GetName].",
    "pww_diplo_pledge_send_desc": "Offer [THIS.GetName] this commercial backstop.",
    "pww_diplo_quarantine_send_desc": "$pww_act_quarantine_desc$",
    "pww_diplo_settlement_send_desc": "$pww_act_demand_settlement_desc$",
    "pww_diplo_embargo_send_desc": "Ask [THIS.GetName] to join our embargo.",
    "pww_diplo_bid_send_desc": "Submit this bid to [THIS.GetName].",
    "pww_diplo_offer_receive_desc": "$pww_rcv_proposal_desc$",
    "pww_diplo_lease_receive_desc": "$pww_rcv_lease_desc$",
    # Player feedback after the answer
    "pww_diplo_offer_accept_title": "Terms Signed",
    "pww_diplo_offer_accept_desc": "[THIS.GetName] has signed. The agreement is entered in our ledger.",
    "pww_diplo_offer_reject_title": "Terms Refused",
    "pww_diplo_offer_reject_desc": "[THIS.GetName] declined this draft.\n\n[pww_diplo_sl_o_line]\n\n[pww_dt_chips]",
    "pww_diplo_demand_accept_title": "Demand Accepted",
    "pww_diplo_demand_accept_desc": "[THIS.GetName] has acceded to our demand.",
    "pww_diplo_demand_reject_title": "Demand Refused",
    "pww_diplo_demand_reject_desc": "[THIS.GetName] has not yielded. The decision date still stands.",
    "pww_diplo_pledge_accept_title": "Backstop Accepted",
    "pww_diplo_pledge_accept_desc": "[THIS.GetName] has accepted our underwriting. It costs nothing unless they are refused and cut off.",
    "pww_diplo_pledge_reject_title": "Backstop Declined",
    "pww_diplo_pledge_reject_desc": "[THIS.GetName] prefers to remain uncommitted.",
    "pww_diplo_settle_accept_title": "Settlement Agreed",
    "pww_diplo_settle_accept_desc": "[THIS.GetName] has agreed to settle the seized concessions.",
    "pww_diplo_settle_reject_title": "Settlement Refused",
    "pww_diplo_settle_reject_desc": "[THIS.GetName] stands by the seizure. We hold a justification against them.",
    "pww_diplo_embargo_accept_title": "Embargo Joined",
    "pww_diplo_embargo_accept_desc": "[THIS.GetName] has closed its ports to [?pww_de_target.GetName].",
    "pww_diplo_embargo_reject_title": "Embargo Refused",
    "pww_diplo_embargo_reject_desc": "[THIS.GetName] keeps its ports open.",
    # AI acceptance reasons (fuzzy hints)
    "pww_diplo_acc_terms": "What they give against what they get",
    "pww_diplo_acc_need": "How badly they need it",
    "pww_diplo_acc_want": "Something they quietly want",
    "pww_diplo_acc_sweeteners": "Sweeteners and face-saving",
    "pww_diplo_acc_red_line": "A clause they cannot sign",
    "pww_diplo_acc_trust": "Our record of keeping terms",
    "pww_diplo_acc_relations": "Relations",
    "pww_diplo_acc_patron": "A patron stands behind them",
    "pww_diplo_acc_reserve": "Their own asking price",
    "pww_diplo_acc_repeat": "Nothing has changed since the last draft",
    "pww_diplo_acc_unworkable": "The terms cannot be carried out",
    "pww_diplo_acc_pressure": "How hard they are pressed",
    "pww_diplo_acc_face": "Room to save face",
    "pww_diplo_acc_underwritten": "Underwritten by a patron",
    "pww_diplo_acc_credibility": "Whether they believe us",
    "pww_diplo_acc_underwriting": "Free cover against coercion",
    "pww_diplo_acc_claimant_friend": "The coercer is a friend of theirs",
    "pww_diplo_acc_grievance": "The grievance is real",
    "pww_diplo_acc_strength": "Balance of power",
    "pww_diplo_acc_bloc": "Bloc loyalty",
    "pww_diplo_acc_view": "Their view of both sides",
    "pww_diplo_acc_lost_trade": "Trade they would lose",
    # Labels
    "pww_diplo_lbl_deal": "Deal",
    "pww_diplo_lbl_res": "Resource",
    "pww_diplo_lbl_qty": "Quantity",
    "pww_diplo_lbl_district": "District",
    "pww_diplo_lbl_dur": "Term",
    "pww_diplo_lbl_pay": "Payment",
    "pww_diplo_lbl_price": "Price",
    "pww_diplo_lbl_sweet": "Sweetener",
    "pww_diplo_lbl_fig": "Fig leaf",
    "pww_diplo_lbl_demand": "Demand",
    "pww_diplo_lbl_against": "Against",
    "pww_diplo_lbl_embargo_on": "Embargo on",
    "pww_diplo_lbl_lot": "Lot",
    "pww_diplo_lbl_less": "Take less: halve the demand",
    "pww_diplo_lbl_counter_price": "Ask a better price",
    "pww_diplo_lbl_counter_amount": "Ask a smaller share",
    "pww_diplo_lbl_counter_term": "Ask a shorter term",
    # Values
    "pww_diplo_v_empty": "",
    "pww_diplo_v_none": "None",
    "pww_diplo_v_dir_0": "We buy",
    "pww_diplo_v_dir_1": "We sell",
    "pww_diplo_v_rdir_0": "They buy from us",
    "pww_diplo_v_rdir_1": "They sell to us",
    "pww_diplo_v_lease": "Lease of rights",
    "pww_diplo_v_lease_rcv": "Lease of our rights",
    "pww_diplo_v_res_0": "Oil",
    "pww_diplo_v_res_1": "Aluminium",
    "pww_diplo_v_res_2": "Rubber",
    "pww_diplo_v_res_3": "Tungsten",
    "pww_diplo_v_res_4": "Steel",
    "pww_diplo_v_res_5": "Chromium",
    "pww_diplo_v_res_6": "Coal",
    "pww_diplo_v_amt_0": "Small",
    "pww_diplo_v_amt_1": "Fair",
    "pww_diplo_v_amt_2": "Large",
    "pww_diplo_v_amt_3": "Generous",
    "pww_diplo_v_dur_0": "Open-ended",
    "pww_diplo_v_dur_1": "Six months",
    "pww_diplo_v_dur_2": "One year",
    "pww_diplo_v_dur_3": "Three years",
    "pww_diplo_v_dur_4": "Five years",
    "pww_diplo_v_pay_0": "Civilian factories",
    "pww_diplo_v_pay_1": "Political power",
    "pww_diplo_v_pay_2": "Clearing credit",
    "pww_diplo_v_pay_3": "Equipment tranches",
    "pww_diplo_v_pay_4": "Production license",
    "pww_diplo_v_price_0": "Below market",
    "pww_diplo_v_price_1": "At market",
    "pww_diplo_v_price_2": "Above market",
    "pww_diplo_v_sweet_0": "None",
    "pww_diplo_v_sweet_1": "Coal bundle",
    "pww_diplo_v_sweet_2": "Technical mission",
    "pww_diplo_v_sweet_3": "Arms gift",
    "pww_diplo_v_state": "[?pww_do_state_s.GetName]",
    "pww_diplo_v_rstate": "[?pww_dr_state.GetName]",
    "pww_diplo_v_dm_state": "[?pww_dm_state_s.GetName]",
    "pww_diplo_v_dtype_0": "Output share",
    "pww_diplo_v_dtype_1": "Named-state lease",
    "pww_diplo_v_vs_any": "Any coercer",
    "pww_diplo_v_vs_named": "[?pww_dp_claimant.GetName]",
    "pww_diplo_v_de_target": "[?pww_de_target.GetName]",
    "pww_diplo_v_round_0": "First draft",
    "pww_diplo_v_round_1": "Second draft",
    "pww_diplo_v_round_2": "Third draft",
    "pww_diplo_v_round_3": "Final draft",
    "pww_diplo_v_round_closed": "§RTalks closed§!",
    "pww_diplo_v_no_standing": "No standing demand. Sending one sets a decision date in 120 days.",
    "pww_diplo_v_standing_0": "Standing demand. They are §R$pww_state_defiant$§!; sending again presses for an answer.",
    "pww_diplo_v_standing_1": "Standing demand. They are §Y$pww_state_strained$§!; sending again presses for an answer.",
    "pww_diplo_v_standing_2": "Standing demand. They are §Y$pww_state_wavering$§!; sending again presses for an answer.",
    "pww_diplo_v_standing_3": "Standing demand. They are §O$pww_state_cornered$§!: push, take less, or offer a fig leaf.",
    "pww_diplo_v_standing_4": "Standing demand. They are §G$pww_state_ready_to_fold$§!.",
    # GUI text
    "pww_diplo_gui_offer_title": "Terms for [THIS.GetName]",
    "pww_diplo_gui_lease_title": "Concession terms for [THIS.GetName]",
    "pww_diplo_gui_bands": "We give §Y[pww_diplo_sl_o_give]§!, we get §Y[pww_diplo_sl_o_get]§!",
    "pww_diplo_gui_rbands": "We give §Y[pww_diplo_sl_r_give]§!, we get §Y[pww_diplo_sl_r_get]§!",
    "pww_diplo_gui_demand_quiet_title": "Private demand to [THIS.GetName]",
    "pww_diplo_gui_demand_public_title": "Public ultimatum to [THIS.GetName]",
    "pww_diplo_gui_embargo_title": "[THIS.GetName] to close its ports to",
    "pww_diplo_gui_pledge_title": "Underwriting for [THIS.GetName]",
    "pww_diplo_gui_pledge_exposure": "Our exposure if called: §Y[pww_diplo_sl_dp_band]§!",
    "pww_diplo_gui_bid_title": "Bid to [THIS.GetName]",
    "pww_diplo_gui_counter_hint": "§gMark one change and decline: the mark is sent back as our counter-draft.§!",
    "pww_diplo_gui_move_hint": "§gAccept accedes to the demand. Decline answers with the marked move.§!",
    "pww_diplo_gui_settle_desc": "[ROOT.GetName] demands satisfaction for the seized concessions. Choose a settlement, or decline to refuse.",
    "pww_diplo_gui_settle_hint": "§gDeclining refuses compensation and hands [ROOT.GetName] a war justification.§!",
    "pww_diplo_rcv_terms_share": "[ROOT.GetName] demands a §Y[pww_diplo_sl_rd_amt]§! share of our [pww_diplo_sl_rd_res] for [pww_diplo_sl_rd_dur].[pww_diplo_sl_rd_fig]",
    "pww_diplo_rcv_terms_lease": "[ROOT.GetName] demands rights over [?pww_dr_state.GetName] for [pww_diplo_sl_rd_dur].[pww_diplo_sl_rd_fig]",
    "pww_diplo_rcv_with_fig": " They offer a face-saving formula: [pww_diplo_sl_rd_figname].",
    "pww_rcv_move_refuse": "Refuse Outright",
    "pww_rcv_move_refuse_desc": "Turn the demand down without a counter. A patron's pledge, if any, comes into force.",
    "pww_rcv_move_stall": "Ask for Time",
    "pww_rcv_move_stall_desc": "Adjourn for technical review. Only possible on the back channel, and not forever.",
    "pww_diplo_tt_fig": "A face-saving formula. It costs us little and lets them sign without looking weak.",
    "pww_diplo_tt_fig_demand": "Offer a face-saving formula with the demand. It cuts humiliation for a small cost.",
    "pww_diplo_tt_sweet": "A coal bundle needs our own coal surplus. Missions and arms are paid a month after signing.",
    "pww_diplo_tt_less": "Halve the demand. A smaller concession is easier to swallow.",
    # Invalid reasons
    "pww_diplo_invalid_1": "§RThey produce none of this resource.§!",
    "pww_diplo_invalid_2": "§RThey have no district producing it.§!",
    "pww_diplo_invalid_3": "§RTranches and licenses need a fixed term.§!",
    "pww_diplo_invalid_4": "§RWe have no coal surplus to bundle.§!",
    "pww_diplo_invalid_5": "§RA lease needs a fixed term.§!",
    "pww_diplo_invalid_6": "§RWe produce none of this resource.§!",
    "pww_diplo_invalid_11": "§RThey produce none of this resource.§!",
    "pww_diplo_invalid_12": "§RWe already underwrite as many countries as we can carry.§!",
    "pww_diplo_invalid_13": "§RWe already cover them against this coercer.§!",
    "pww_diplo_invalid_21": "§RThey produce none of this resource.§!",
    "pww_diplo_invalid_22": "§RThey have no district producing it.§!",
    "pww_diplo_invalid_23": "§RThe demand could not be issued. Change the terms.§!",
    "pww_diplo_invalid_31": "§RWe are not embargoing anyone.§!",
    "pww_diplo_invalid_32": "§RThey cannot embargo themselves.§!",
    "pww_diplo_invalid_41": "§RNothing open to bid on.§!",
    # Envoy-style lines of the lane's own
    "pww_diplo_line_signed": "The protocol is signed and initialled in both capitals.",
    "pww_diplo_line_failed": "Our ministry could not register the terms as drafted. The delegation awaits a corrected text.",
    "pww_diplo_line_closed": "Talks are broken off. Their delegation will not receive ours again for some months.",
    "pww_diplo_line_auction": "[THIS.GetCapitalName] has opened its output to all bidders. Our draft is set aside; submit a bid instead.",
    "pww_diplo_line_opening": "Talks are open. Their delegation awaits our first draft.",
    "pww_diplo_line_expired": "The talks have lapsed without a signature.",
    # Auction lots (generic)
    "pww_diplo_lot_kind_0": "Lease: [?pww_db_state_s.GetName]",
    "pww_diplo_lot_kind_1": "Split half: [?pww_db_state_s.GetName]",
    "pww_diplo_lot_kind_2": "Exclusive national lease",
    "pww_diplo_lot_kind_3": "Bridge contract",
    "pww_diplo_lot_desc_0": "Named-state rights over [?pww_db_state_s.GetName] for [pww_diplo_sl_db_term].",
    "pww_diplo_lot_desc_1": "One half of a divided allocation: the other half goes to a different buyer.",
    "pww_diplo_lot_desc_2": "All exportable [pww_diplo_sl_db_res] under one flag for [pww_diplo_sl_db_term]. Exclusivity is binding.",
    "pww_diplo_lot_desc_3": "A short supply contract with no named-state rights.",
}

# Titles fit the vanilla diplomatic actions list (about 18 characters).
ACTIONS = {
    "pww_diplo_propose_agreement": ("Propose Trade Deal", "$pww_act_propose_agreement_desc$"),
    "pww_diplo_lease_rights": ("Lease Mines", "$pww_act_lease_rights_desc$"),
    "pww_diplo_demand_quiet": ("Demand (Quiet)", "$pww_act_demand_quiet_desc$"),
    "pww_diplo_demand_public": ("Demand (Public)", "$pww_act_demand_public_desc$"),
    "pww_diplo_pledge_support": ("Pledge Support", "$pww_act_pledge_support_desc$"),
    "pww_diplo_quarantine": ("Quarantine", "$pww_act_quarantine_desc$"),
    "pww_diplo_demand_settlement": ("Demand Settlement", "$pww_act_demand_settlement_desc$"),
    "pww_diplo_join_embargo": ("Join Our Embargo", "$pww_act_join_embargo_desc$"),
    "pww_diplo_submit_bid": ("Submit Bid", "Bid once on a lot this country has put up. The holder awards each lot when bidding closes."),
}
for k, (t, d) in ACTIONS.items():
    K = k.upper()
    ui[K] = t
    ui[K + "_TITLE"] = t
    ui[K + "_ACTION_DESC"] = d

# Trade talks screen text (generated with its layout)
for k, v in talks.L.items():
    if k in ui:
        raise SystemExit("duplicate " + k)
    ui[k] = v

for k, v in ui.items():
    if k in main:
        raise SystemExit("duplicate " + k)
    main[k] = v


def write(path, d, header):
    lines = ["l_english:", f" # {header}"]
    for k, v in d.items():
        assert "\u2014" not in v, k
        lines.append(f' {k}:0 "{esc(v)}"')
    with open(path, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


write(OUT_MAIN, main, "Power Without War: diplomacy lane (actions, GUIs, lots, fig leaves). Source: docs/content/wolfram_question.md sections 2 to 5, plus lane UI text.")
write(OUT_ENV, env, "Power Without War: envoy reports, red lines, hidden wants. Source: docs/content/envoys.md (FROM -> THIS: shown in the sender's GUI).")
print(len(main), len(env))
