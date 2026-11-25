# Standings, Agreement States, UI Headers, and Alert Strip

Player-facing localisation bible for Standings and Chronicle (section 7.15), Agreement lifecycle states (section 7.3 / `AGENTS.md`), Trade Desk and Dossier headers/empty states (section 9), and top-bar Alert Strip rows (section 9).

Tone: terse, period-flavored, zero fluff, no em dashes, no exclamation marks.

---

## 1. Standings & Chronicle

Standings replace passive buff spirits. Each is earned through Situation outcomes, recorded with a short chronicle entry, and unlocks one concrete diplomatic option.

### Core Standings (from section 7.15)
| Loc Key | Name | Option Granted |
|---|---|---|
| `pww_standing_honest_broker` | `Honest Broker` | `Mediate other powers' Situations as a neutral seat.` |
| `pww_standing_wolfram_master` | `Master of the Wolfram Trade` | `Call a Producers' Conference to coordinate tungsten withholding and auction terms.` |
| `pww_standing_concessionaire` | `The Concessionaire` | `Hosts accept settlement in kind more readily after nationalization disputes.` |
| `pww_standing_arsenal_neutrality` | `Arsenal of Neutrality` | `Both warring blocs must approach you through back channels rather than public ultimatums.` |

### Additional Standings (Phase 2 to 4 ready)
| Loc Key | Name | Option Granted |
|---|---|---|
| `pww_standing_patron_small` | `Patron of the Small Powers` | `Underwrite two threatened holders simultaneously at reduced political power upkeep.` |
| `pww_standing_clearing_architect` | `Architect of the Clearing House` | `Offer extended clearing credit terms that deepen counterparty reliance.` |
| `pww_standing_sea_warden` | `Warden of the Approaches` | `Declare naval quarantines with faster strangulation ramp.` |
| `pww_standing_iron_creditor` | `Iron Creditor` | `Punish embargo-breakers with sharper Credibility gains.` |

### Short Chronicle Templates
Each earned Standing displays a one-line historical record of how it was won.

| Loc Key | Template |
|---|---|
| `pww_chronicle_header` | `Diplomatic Chronicle` |
| `pww_chronicle_entry_generic` | `[pww_year]: Earned [pww_standing_name] in [pww_sit_name] ([pww_outcome_short]).` |
| `pww_chronicle_wolfram_split` | `[pww_year]: Divided Guarda and Lisbon wolfram between [pww_claimant.GetName] and [pww_patron.GetName] without breaking neutrality.` |
| `pww_chronicle_wolfram_ger` | `[pww_year]: Secured Portuguese wolfram concessions over [pww_patron.GetAdjective] opposition.` |
| `pww_chronicle_wolfram_eng` | `[pww_year]: Underwrote Lisbon and denied Iberian wolfram to [pww_claimant.GetName] without war.` |
| `pww_chronicle_wolfram_por` | `[pww_year]: Outlasted [pww_claimant.GetAdjective] pressure and kept Portuguese mines under domestic control.` |
| `pww_chronicle_empty` | `No Standings recorded. Outcomes of major Situations are inscribed here.` |

---

## 2. Agreement Lifecycle States, Vehicles & Bands

Matches the exact ledger status enum in `AGENTS.md`: `0 draft`, `1 active`, `2 suspended`, `3 completed`, `4 terminated`, `5 defaulted`, `6 nationalized`, `7 reserved`.

### Lifecycle Statuses
| Enum | Loc Key | Label | Tooltip |
|---|---|---|---|
| 0 | `pww_ag_status_draft` | `Draft` | `Terms are under negotiation and not yet binding.` |
| 1 | `pww_ag_status_active` | `§GActive§!` | `Deliveries and payments are flowing on schedule.` |
| 2 | `pww_ag_status_suspended` | `§YSuspended§!` | `Flows are paused due to interdiction, quarantine, or provisional truce. Resolve before the window closes.` |
| 3 | `pww_ag_status_completed` | `Completed` | `Agreement ran its full term and closed cleanly.` |
| 4 | `pww_ag_status_terminated` | `Terminated` | `Ended cleanly by war, capitulation, or unresolved suspension without default.` |
| 5 | `pww_ag_status_defaulted` | `§RDefaulted§!` | `Breached deliberately. Remaining tranches forfeited; Reliability damaged.` |
| 6 | `pww_ag_status_nationalized` | `§RNationalized§!` | `Seized by the host state. Settlement and escalation options are open.` |
| 7 | `pww_ag_status_reserved` | `§HReserved§!` | `Conditional pledge. Activates automatically if the named trigger fires.` |
| - | `pww_ag_status_renewed` | `§GRenewed§!` | `Extended for a fresh term upon expiry.` |

### Contract Vehicles & Types
| Loc Key | Label | Tooltip |
|---|---|---|
| `pww_ag_vehicle_supply` | `Supply Agreement` | `Flexible volume contract drawn from surplus and delivered through the ledger.` |
| `pww_ag_vehicle_lease` | `Named-State Lease` | `Timed resource rights over specific producing states. Visible on the map.` |
| `pww_ag_type_noncommittal` | `Non-committal` | `Flow-only arrangement. Either side may end it without default.` |
| `pww_ag_type_committal` | `Committal` | `Fixed term up to five years. May include tranched arms, licenses, or leases.` |

### Held Pool Stances & Stock Bands (section 7.5)
| Loc Key | Label | Tooltip |
|---|---|---|
| `pww_stance_open` | `Open` | `Surplus flows normally to the open market.` |
| `pww_stance_contracts` | `Contracts First` | `Surplus feeds the Held pool to supply signed agreements and auction lots.` |
| `pww_stance_withhold` | `Withhold` | `Surplus accumulates in the Held pool; nothing is released to open trade.` |
| `pww_held_band_0` | `Empty` | `No reserve held back from the market.` |
| `pww_held_band_1` | `Thin reserve` | `Roughly a month of output held in reserve.` |
| `pww_held_band_2` | `A few months' output` | `Enough stock to cushion a brief disruption or back a small auction.` |
| `pww_held_band_3` | `A war chest` | `Near storage cap. Monthly decay is biting into excess tonnage.` |

### Valuation Bands (section 7.1)
| Loc Key | Label |
|---|---|
| `pww_val_band_trivial` | `Trivial` |
| `pww_val_band_small` | `Small` |
| `pww_val_band_fair` | `Fair` |
| `pww_val_band_large` | `Large` |
| `pww_val_band_huge` | `Huge` |

---

## 3. Trade Desk Headers & Empty States (`trade_tab`)

| Section | Header Key | Header Text | Empty-State Key | Empty-State Text |
|---|---|---|---|---|
| Window Title | `pww_desk_title` | `Trade Desk` | - | - |
| Situations Board | `pww_desk_sec_situations` | `Active Situations` | `pww_desk_empty_situations` | `No contested Situations in your seats. Watch the market report for emerging shortages.` |
| Agreements Ledger | `pww_desk_sec_ledger` | `Agreements Ledger` | `pww_desk_empty_ledger` | `No active agreements. Open talks through any country's diplomacy panel.` |
| Held Pool & Stances | `pww_desk_sec_held` | `Held Pool & Market Stance` | `pww_desk_empty_held` | `All resources are set to Open. Switch a resource to Contracts First or Withhold to build a reserve.` |
| Wishlist | `pww_desk_sec_wishlist` | `Import Wishlist` | `pww_desk_empty_wishlist` | `No priorities set. Rank needed resources here so foreign offers lean toward them.` |
| Monthly Market Report | `pww_desk_sec_market` | `Monthly Market Report` | `pww_desk_empty_market` | `First monthly report posts at the turn of the month.` |
| Standings | `pww_desk_sec_standings` | `Standings & Chronicle` | `pww_desk_empty_standings` | `No Standings earned yet.` |
| Deny List | `pww_desk_sec_deny` | `Rationing & Deny List` | `pww_desk_empty_deny` | `No buyers denied. Naming a country steers open-market exports away from them.` |

### Situations Board Row Template
| Loc Key | Template |
|---|---|
| `pww_desk_sit_row` | `[pww_sit_title] ([pww_seat_label]) | Due: [pww_deadline_date] | [pww_latest_dev]` |
| `pww_seat_claimant` | `Claimant` |
| `pww_seat_holder` | `Holder` |
| `pww_seat_patron` | `Patron` |

---

## 4. Dossier Headers & Empty States (`diplomacy_target_context`)

| Section | Header Key | Header Text | Empty-State Key | Empty-State Text |
|---|---|---|---|---|
| Window Title | `pww_dossier_title` | `Commercial Dossier: [FROM.GetName]` | - | - |
| Shortages & Reliance | `pww_dossier_sec_shortages` | `Shortages & Import Reliance` | `pww_dossier_empty_shortages` | `No acute resource deficits observed in [FROM.GetName].` |
| Known Agreements | `pww_dossier_sec_agreements` | `Known Agreements` | `pww_dossier_empty_agreements` | `No mod-tracked agreements on file for [FROM.GetName].` |
| Resource Rights | `pww_dossier_sec_rights` | `Resource Rights & Concessions` | `pww_dossier_empty_rights` | `No foreign resource leases held in [FROM.GetName].` |
| Route Investments | `pww_dossier_sec_routes` | `Route Investments` | `pww_dossier_empty_routes` | `No foreign corridors or terminals built here.` |
| Coercion Readout | `pww_dossier_sec_readout` | `Coercion Assessment` | `pww_dossier_empty_readout` | `No active demand against [FROM.GetName].` |
| Reputations | `pww_dossier_sec_rep` | `How [FROM.GetCapitalName] Sees Us` | `pww_dossier_empty_rep` | `No standing diplomatic assessment yet.` |
| Situations | `pww_dossier_sec_sits` | `Live Situations` | `pww_dossier_empty_sits` | `[FROM.GetName] is not seated in any active Situation.` |

---

## 5. Top-Bar Alert Strip Row Templates (`top_bar`)

One compact row per live Situation in the player's seats, updated in place. Never spams popups.

| Loc Key | Situation State | Row Text |
|---|---|---|
| `pww_alert_claimant_active` | Claimant, active | `[pww_sit_title]: [pww_holder.GetName] is [pww_target_state] ([?pww_days_left]d)` |
| `pww_alert_claimant_cornered` | Claimant, target Cornered | `§R[pww_sit_title]: [pww_holder.GetName] is Cornered§! ([?pww_days_left]d)` |
| `pww_alert_claimant_fold` | Claimant, target Ready to fold | `§G[pww_sit_title]: [pww_holder.GetName] ready to fold§! ([?pww_days_left]d)` |
| `pww_alert_holder_demand` | Holder, facing demand | `§Y[pww_sit_title]: [pww_claimant.GetName] demands answer§! ([?pww_days_left]d)` |
| `pww_alert_holder_auction` | Holder, auction open | `§H[pww_sit_title]: Write lots for bidding§! ([?pww_days_left]d)` |
| `pww_alert_patron_open` | Patron, holder unpledged | `[pww_sit_title]: [pww_holder.GetName] under pressure from [pww_claimant.GetName] ([?pww_days_left]d)` |
| `pww_alert_patron_pledged` | Patron, pledge active | `§H[pww_sit_title]: Underwriting [pww_holder.GetName]§! ([?pww_days_left]d)` |
| `pww_alert_quarantine_live` | Quarantine active | `§OQuarantine: [pww_target.GetName] approaches held§!` |
| `pww_alert_lease_expiring` | Lease nearing expiry | `§YLease expiring: [pww_holder.GetName] ([?pww_days_left]d)§!` |
| `pww_alert_suspended_window` | Agreement suspended | `§YSuspended contract: [pww_counterparty.GetName] ([?pww_days_left]d to resolve)§!` |
| `pww_alert_settlement_due` | Nationalization settlement | `§RSettlement demanded: [pww_host.GetName] ([?pww_days_left]d)§!` |
