# The Wolfram Question (1937 to 1938): Complete Text Bible

Phase 1 vertical slice (section 12).
Seats: **Germany** (Claimant), **Portugal** (Holder), **United Kingdom** (Patron).
Prize: Portugal's dynamically resolved tungsten states (vanilla: Guarda and Lisbon).
Historical grounding: António de Oliveira Salazar's Estado Novo, the 1386 Anglo-Portuguese Alliance, Panasqueira and Beira Baixa wolfram mines, Krupp and Rheinmetall armor-piercing shell production after the China war cuts Asian tungsten shipments.

Tone: period-flavored, terse, diplomatic-cable voice. No em dashes, no exclamation marks.

---

## 1. Situation Card (Title & Description per Seat)

| Loc Key | Seat | Text |
|---|---|---|
| `pww_sit_wolfram_title` | All | `The Wolfram Question` |
| `pww_sit_wolfram_subtitle` | All | `Portuguese Tungsten Allocation` |
| `pww_sit_wolfram_prize` | All | `Prize: [pww_holder.GetAdjective] tungsten output (Guarda and Lisbon)` |
| `pww_sit_wolfram_desc_claimant` | Claimant (Germany) | `Fighting in China has severed our Asian wolfram supply. Without Iberian tungsten, armor-piercing shell and tool-steel output will stall. Salazar is cautious, proud, and bound to London by a five-hundred-year alliance. Secure the mines by clearing credit, quiet pressure, or open force before the decision date.` |
| `pww_sit_wolfram_desc_holder` | Holder (Portugal) | `Berlin is hungry for our wolfram and London is determined to deny it to them. Both powers have sent trade delegations to Lisbon. Yield outright to Germany and Britain may cut our Atlantic lifeline; defy Berlin carelessly and German cruisers may appear off the Tagus. Split the lots, play both capitals, or extract a real price for our ore.` |
| `pww_sit_wolfram_desc_patron` | Patron (United Kingdom) | `German agents are pressing Lisbon for exclusive rights to Portuguese wolfram, vital to the Wehrmacht's high-velocity shells. Our oldest ally cannot hold out on sentiment alone. Underwrite Salazar's unsold output with a commercial pledge, bid for the mines directly, or let Berlin tighten its grip on Iberia.` |
| `pww_sit_wolfram_desc_observer` | Observer (Fallback) | `Berlin and London are competing for control of Portugal's tungsten output while Lisbon seeks to preserve its neutrality and profit from both.` |

### Opening Situation Alert / Brief
| Loc Key | Text |
|---|---|
| `pww_sit_wolfram_open_ger` | `Chinese wolfram shipments have dried up. The Ministry of Economics has turned its eyes to Portugal.` |
| `pww_sit_wolfram_open_por` | `German and British envoys have both requested urgent audiences on wolfram export allocations.` |
| `pww_sit_wolfram_open_eng` | `German clearing agents are moving on Portuguese wolfram. Lisbon is looking to London.` |

---

## 2. Scripted Diplomatic Actions (Sender Side)

Covers all seven actions in section 9 (with Quiet and Public variants for Issue Demand). Usable globally and in The Wolfram Question.

### 2.1 Propose Agreement
| Loc Key | Text |
|---|---|
| `pww_act_propose_agreement_title` | `Propose Commercial Agreement` |
| `pww_act_propose_agreement_desc` | `Open formal talks for a supply contract in civilian factories, equipment tranches, or clearing credit. Non-committal flows can end at any time; fixed terms run up to five years.` |
| `pww_act_propose_agreement_wolfram_hint` | `Offer Salazar clearing credit redeemable in German arms, or civilian works, in exchange for steady wolfram deliveries.` |

### 2.2 Lease Rights
| Loc Key | Text |
|---|---|
| `pww_act_lease_rights_title` | `Negotiate Resource Lease` |
| `pww_act_lease_rights_desc` | `Seek a timed named-state concession (up to five years) granting direct resource rights. Prestigious and visible on the map, but carries nationalization risk and stirs rivals.` |
| `pww_act_lease_rights_wolfram_hint` | `Direct rights over the Beira Baixa and Tagus districts will feed our mills directly, though Lisbon guards its sovereignty jealously.` |

### 2.3 Issue Demand (Quiet / Back Channel)
| Loc Key | Text |
|---|---|
| `pww_act_demand_quiet_title` | `Issue Demand (Back Channel)` |
| `pww_act_demand_quiet_desc` | `Deliver a private demand with a fixed decision date. Lower ceiling than an ultimatum, but avoids public humiliation and lets authoritarian cabinets bend without losing face. Loud pressure tools will leak this channel to the press.` |
| `pww_act_demand_quiet_wolfram_hint` | `Salazar can concede quietly through commercial protocols where he would never bow to a public threat.` |

### 2.4 Issue Demand (Public Ultimatum)
| Loc Key | Text |
|---|---|
| `pww_act_demand_public_title` | `Issue Demand (Public Ultimatum)` |
| `pww_act_demand_public_desc` | `Put a named demand on the public record with a firm deadline. Higher leverage, but stakes your Credibility, alerts patrons, and rallies democratic publics against you.` |
| `pww_act_demand_public_wolfram_hint` | `An open ultimatum to Lisbon will bring Whitehall into the room at once. Make sure you can carry it through.` |
| `pww_act_demand_leak_notice` | `§RChannel leaked:§! Open naval or trade pressure has exposed our private demand to [FROM.GetName]. The dispute is now public.` |

### 2.5 Pledge Support (Patron)
| Loc Key | Text |
|---|---|
| `pww_act_pledge_support_title` | `Pledge Commercial Support` |
| `pww_act_pledge_support_desc` | `Sign a reserved agreement underwriting [FROM.GetName]'s output if a coercer cuts them off. Costs nothing unless triggered, but binds real factories or equipment if [FROM.GetCapitalName] calls it in.` |
| `pww_act_pledge_support_wolfram_hint` | `Assure Lisbon that Britain will buy its unsold wolfram if Berlin imposes an embargo or withdraws clearing credit.` |

### 2.6 Declare Quarantine
| Loc Key | Text |
|---|---|
| `pww_act_quarantine_title` | `Declare Naval Quarantine` |
| `pww_act_quarantine_desc` | `Declare a peacetime naval quarantine on [FROM.GetName]. Costs political power upkeep. While your committed ships hold naval control of their sea approaches, their exposed sea contracts are suspended and strangulation rises. Losing sea control lapses the quarantine.` |
| `pww_act_quarantine_wolfram_hint` | `Holding the Atlantic approaches off Lisbon will sever maritime deliveries and test whether London's pledge can actually reach port.` |

### 2.7 Demand Settlement (Post-Nationalization)
| Loc Key | Text |
|---|---|
| `pww_act_demand_settlement_title` | `Demand Settlement` |
| `pww_act_demand_settlement_desc` | `Confront [FROM.GetName] over seized concessions. Forces a choice between staged factory compensation, settlement in kind, reversal, or open refusal.` |

### 2.8 Join Our Embargo
| Loc Key | Text |
|---|---|
| `pww_act_join_embargo_title` | `Request Embargo Compliance` |
| `pww_act_join_embargo_desc` | `Call on [FROM.GetName] to embargo our target by a set deadline. Punishing non-compliance raises Credibility at the cost of Reliability.` |

---

## 3. Receiver-Screen Text (Holder & Patron Responses)

Shown in the receiver GUI when a human (or inspected AI) receives an action.

### 3.1 Receiving Propose Agreement / Lease Rights
| Loc Key | Text |
|---|---|
| `pww_rcv_proposal_title` | `Commercial Proposal from [FROM.GetName]` |
| `pww_rcv_proposal_desc` | `[FROM.GetCapitalName] has tabled terms for [pww_res_name] deliveries. Review the payment bundle, duration, and tranches before answering.` |
| `pww_rcv_lease_title` | `Concession Request from [FROM.GetName]` |
| `pww_rcv_lease_desc` | `[FROM.GetName] seeks named-state resource rights over our producing districts. Granting a lease brings heavy returns, though foreign flags on home soil carry political cost.` |
| `pww_rcv_btn_accept` | `Sign Agreement` |
| `pww_rcv_btn_counter` | `Send Counter-Draft` |
| `pww_rcv_btn_refuse` | `Decline` |

### 3.2 Receiving Issue Demand (Quiet)
| Loc Key | Text |
|---|---|
| `pww_rcv_demand_quiet_title` | `Private Demand from [FROM.GetName]` |
| `pww_rcv_demand_quiet_desc` | `Through confidential channels, [FROM.GetCapitalName] demands a concession on [pww_prize_name] before [pww_deadline_date]. The matter has not yet reached the press.` |

### 3.3 Receiving Issue Demand (Public)
| Loc Key | Text |
|---|---|
| `pww_rcv_demand_public_title` | `Public Ultimatum from [FROM.GetName]` |
| `pww_rcv_demand_public_desc` | `[FROM.GetName] has publicly demanded [pww_prize_name] by [pww_deadline_date]. Foreign chanceries are watching how [ROOT.GetCapitalName] answers.` |

### 3.4 Target Move Buttons (Receiver GUI for Demands, section 7.8)
| Loc Key | Button Label | Tooltip / Description |
|---|---|---|
| `pww_rcv_move_fold` | `Accede to Demand` | `Grant [FROM.GetName]'s terms and close the crisis. Committed forces withdraw once the ink dries.` |
| `pww_rcv_move_small_lot` | `Offer Smaller Named Lot` | `Counter with a partial allocation (such as one district or a reduced output share) to test whether [FROM.GetCapitalName] will settle.` |
| `pww_rcv_move_provisional` | `Propose 90-Day Provisional Suspension` | `Accept a temporary ninety-day arrangement to buy time, cool the crisis, and seek outside support.` |
| `pww_rcv_move_fig_leaf` | `Propose Face-Saving Formula` | `Offer the substance under a joint commission, temporary reversion date, or commercial cover to shield domestic pride.` |
| `pww_rcv_move_call_patron` | `Appeal to Patron` | `Request an urgent commercial backstop or diplomatic intervention from [pww_patron.GetName].` |
| `pww_rcv_move_harden` | `Harden and Mobilize` | `Reject the pressure publicly, call up reserves, and stake national honor on holding out. Raises resistance and warns [FROM.GetName] that pushing further risks war.` |

### 3.5 Receiving Pledge Support (Holder receives from Patron)
| Loc Key | Text |
|---|---|
| `pww_rcv_pledge_title` | `Commercial Backstop from [FROM.GetName]` |
| `pww_rcv_pledge_desc` | `[FROM.GetCapitalName] offers to underwrite our unsold output if foreign pressure cuts our markets. Accepting strengthens our hand against coercion.` |
| `pww_rcv_pledge_accept` | `Accept Underwriting` |
| `pww_rcv_pledge_decline` | `Remain Uncommitted` |

### 3.6 Receiving Declare Quarantine
| Loc Key | Text |
|---|---|
| `pww_rcv_quarantine_title` | `[FROM.GetAdjective] Naval Quarantine` |
| `pww_rcv_quarantine_desc` | `[FROM.GetName] has declared a quarantine across our sea approaches. Exposed maritime contracts are suspended while their ships hold the coast.` |

### 3.7 Receiving Demand Settlement (Host after Nationalization)
| Loc Key | Text |
|---|---|
| `pww_rcv_settlement_title` | `Settlement Demand from [FROM.GetName]` |
| `pww_rcv_settlement_desc` | `[FROM.GetCapitalName] demands satisfaction for the seized concessions. Choose how [ROOT.GetCapitalName] will answer.` |
| `pww_rcv_settle_cic` | `Staged Factory Compensation` |
| `pww_rcv_settle_cic_desc` | `Dedicate a share of civilian capacity to [FROM.GetName] over a fixed term to close the grievance.` |
| `pww_rcv_settle_kind` | `Settlement in Kind` |
| `pww_rcv_settle_kind_desc` | `Deliver output below market or complete a named project for [FROM.GetName] over the settlement term.` |
| `pww_rcv_settle_reverse` | `Reverse Nationalization` |
| `pww_rcv_settle_reverse_desc` | `Restore the seized rights at a heavy domestic stability and political power cost.` |
| `pww_rcv_settle_refuse` | `Refuse Compensation` |
| `pww_rcv_settle_refuse_desc` | `Stand by the seizure. Escalates the dispute and hands [FROM.GetName] a war justification.` |

### 3.8 Receiving Join Our Embargo
| Loc Key | Text |
|---|---|
| `pww_rcv_join_embargo_title` | `Embargo Request from [FROM.GetName]` |
| `pww_rcv_join_embargo_desc` | `[FROM.GetCapitalName] asks us to embargo [pww_target.GetName] before [pww_deadline_date]. Refusal may draw [FROM.GetAdjective] retaliation.` |
| `pww_rcv_join_embargo_accept` | `Join the Embargo` |
| `pww_rcv_join_embargo_refuse` | `Keep Our Ports Open` |

---

## 4. Seller-Written Auction Lots (Portugal)

When Germany and Britain both bid, Portugal writes the lots (section 7.10).

| Loc Key | Lot | Title | Description |
|---|---|---|---|
| `pww_lot_wolfram_guarda` | Guarda | `The Guarda & Panasqueira Lot` | `Interior wolfram concessions centered on Beira Baixa. Rich veins suited to overland or northern dispatch; keeps Lisbon's coastal trade separate.` |
| `pww_lot_wolfram_lisbon` | Lisbon | `The Lisbon & Tagus Export Lot` | `Coastal export allocation clearing through the port of Lisbon. Naturally favors the power that commands the Atlantic approaches.` |
| `pww_lot_wolfram_exclusive` | Exclusive | `Exclusive National Wolfram Lease` | `All exportable Portuguese tungsten under a single flag for a fixed term. Commands the highest bid, but guarantees fury from the losing capital.` |
| `pww_lot_wolfram_split` | Split | `The Divided Allocation (Guarda / Lisbon)` | `Salazar's balancing formula: Guarda to one buyer, Lisbon to the other. Neither power wins a monopoly, and Portugal keeps both at the table.` |
| `pww_lot_wolfram_bridge` | Bridge | `Six-Month Bridge Contract` | `A short commercial stopgap with no named-state rights. Buys Lisbon time to watch the European balance before committing the mines.` |

### Auction UI Helpers
| Loc Key | Text |
|---|---|
| `pww_auction_header` | `Lisbon Wolfram Allocation` |
| `pww_auction_bid_once` | `Each bidder submits one term bundle per lot. Violating an exclusivity clause opens a breach crisis.` |
| `pww_auction_winner_line` | `Awarded to [pww_winner.GetName] under [pww_lot_name].` |

---

## 5. Fig Leaves (Face-Saving Sweeteners)

Offered by Claimant or proposed by Holder to cut humiliation (section 7.8).

| Loc Key | Name | Description |
|---|---|---|
| `pww_figleaf_token_purchase` | `Nominal Purchase Supplement` | `Add a modest commercial payment so [FROM.GetCapitalName] can present the concession as an ordinary sale.` |
| `pww_figleaf_joint_commission` | `Joint Technical Commission` | `Place deliveries under a bilateral mining board with equal [FROM.GetAdjective] representation.` |
| `pww_figleaf_sovereignty_note` | `Public Assurance of Sovereignty` | `Attach a formal declaration affirming [FROM.GetName]'s full title over its subsoil and ports.` |
| `pww_figleaf_timed_reversion` | `Fixed Reversion Date` | `Frame the arrangement as strictly temporary, expiring automatically unless renewed by mutual consent. Breaking it early costs Credibility.` |
| `pww_figleaf_clearing_cover` | `Commercial Clearing Protocol` | `Fold the allocation into a routine bilateral clearing schedule rather than a standalone political protocol.` |
| `pww_figleaf_neutral_transit` | `Neutral Registry Clause` | `Route shipments under neutral customs paperwork so third capitals have less pretext to protest.` |

---

## 6. Resolution Popups (All Five Outcomes)

One Situation produces at most one resolution popup (section 12 pass criterion 3).

### Outcome 1: Split Award (Guarda / Lisbon Split)
| Loc Key | Text |
|---|---|
| `pww_res_wolfram_split_title` | `The Wolfram Accord: Output Divided` |
| `pww_res_wolfram_split_desc` | `After weeks of quiet bargaining in Lisbon, Salazar has divided Portugal's tungsten output between the two rival capitals. Guarda's interior ore moves under one contract while Lisbon's coastal allocation answers to the other. Neither Berlin nor London secured a monopoly, and Portugal has turned great-power hunger into a steady stream of factories and arms without breaking its neutrality.` |
| `pww_res_wolfram_split_opt_ger` | `Half the ore is better than idle shell plants.` |
| `pww_res_wolfram_split_opt_por` | `Both giants pay; Lisbon answers to neither.` |
| `pww_res_wolfram_split_opt_eng` | `Berlin did not get the whole field.` |

### Outcome 2: Lease to Germany
| Loc Key | Text |
|---|---|
| `pww_res_wolfram_ger_title` | `German Concessions in Beira Baixa` |
| `pww_res_wolfram_ger_desc` | `Portugal has granted Germany a timed lease over its principal wolfram districts. German engineers are already inspecting rail sidings toward the Spanish frontier, and clearing credits have begun flowing into Lisbon's accounts. In Whitehall, the Foreign Office views the signature as a sharp blow to the Anglo-Portuguese alliance.` |
| `pww_res_wolfram_ger_opt_ger` | `The shell plants will not want for tungsten.` |
| `pww_res_wolfram_ger_opt_por` | `We took the terms we could live with.` |
| `pww_res_wolfram_ger_opt_eng` | `A bitter setback on the Tagus.` |

### Outcome 3: Lease to Britain
| Loc Key | Text |
|---|---|
| `pww_res_wolfram_eng_title` | `London Secures the Portuguese Mines` |
| `pww_res_wolfram_eng_desc` | `Backed by British underwriting and the weight of the 1386 alliance, Lisbon has placed its wolfram output under British lease. Ships clearing the Tagus now carry ore bound strictly for British foundries, leaving German procurement offices scrambling for substitutes and eyeing alternate routes across Iberia.` |
| `pww_res_wolfram_eng_opt_ger` | `We will find another way into Iberia.` |
| `pww_res_wolfram_eng_opt_por` | `Our oldest ally paid its way.` |
| `pww_res_wolfram_eng_opt_eng` | `Denial without a shot fired.` |

### Outcome 4: Portugal Holds Out
| Loc Key | Text |
|---|---|
| `pww_res_wolfram_por_title` | `Lisbon Keeps Its Mines` |
| `pww_res_wolfram_por_desc` | `The decision date has passed with no foreign flag over Guarda or Lisbon. Whether by stalling the delegations, playing rival bids off against one another, or leaning on commercial pledges, Salazar has kept Portuguese tungsten in Portuguese hands. Foreign buyers will pay open terms on Lisbon's schedule, or go without.` |
| `pww_res_wolfram_por_opt_ger` | `Salazar outlasted us this round.` |
| `pww_res_wolfram_por_opt_por` | `Portugal is not for sale.` |
| `pww_res_wolfram_por_opt_eng` | `Neutrality held firm.` |

### Outcome 5: Crisis Goes to War
| Loc Key | Text |
|---|---|
| `pww_res_wolfram_war_title` | `The Wolfram Crisis Breaks Into War` |
| `pww_res_wolfram_war_desc` | `Cornered beyond endurance and left with no exit it could sign, diplomacy has collapsed into open hostilities. Trade delegations have been recalled, ports are sealed, and what began as a dispute over tungsten tonnage will now be settled by arms.` |
| `pww_res_wolfram_war_opt_all` | `So ends the peace.` |

---

## 7. Lease Renewal Text (1-Year Expiry)

One-year leases create a scheduled second decision where rivals can outbid (section 7.6, 12).

| Loc Key | Text |
|---|---|
| `pww_renew_wolfram_alert` | `Portuguese wolfram lease expires in [?pww_days_left] days.` |
| `pww_renew_wolfram_title` | `Renewal of the Portuguese Wolfram Lease` |
| `pww_renew_wolfram_desc_holder` | `The one-year concession granted to [pww_lessee.GetName] is coming due. Lisbon may renew on current terms, demand a richer bundle, open a fresh auction to rival bidders, or let the rights revert to Portuguese hands.` |
| `pww_renew_wolfram_desc_lessee` | `Our tungsten lease in [pww_holder.GetName] is due to expire. Rival envoys are already calling at the Portuguese foreign ministry; renew promptly or risk losing the mines.` |
| `pww_renew_wolfram_desc_rival` | `[pww_lessee.GetAdjective] rights in Portugal are nearing expiry. This is our opening to outbid them before Lisbon signs another term.` |
| `pww_renew_btn_extend` | `Renew on Current Terms` |
| `pww_renew_btn_rebid` | `Open Fresh Auction` |
| `pww_renew_btn_reclaim` | `Let Lease Revert` |
| `pww_renew_btn_outbid` | `Submit Rival Bid` |
