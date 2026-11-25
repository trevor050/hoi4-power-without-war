# Reputation Voices: Through Other Mouths

Player-facing localisation bible for Reliability, Credibility, Regional Alarm, and Dependency Pairs (section 7.12).
Reputations are never displayed as numbers or progress bars. They appear as remarks from foreign chanceries, legations, and trade ministries.

Scope conventions: `ROOT` is the subject being spoken about (or the player viewing their own standing); `FROM` is the speaking/observing country; `pww_region` is a strategic region or regional label.

---

## 1. Reliability (Do You Honor Deals?)

Five bands from unblemished to pariah. Shown in Dossier, negotiation headers, and Trade Desk reputation summary.

### Band Labels (short header tags, if needed in Dossier)
| Band | Loc Key | Text |
|---|---|---|
| 4 (High) | `pww_rep_rel_band_4` | `§GWord as Good as Gold§!` |
| 3 (Solid) | `pww_rep_rel_band_3` | `Dependable` |
| 2 (Mixed) | `pww_rep_rel_band_2` | `§YCautiously Watched§!` |
| 1 (Low) | `pww_rep_rel_band_1` | `§OSuspect§!` |
| 0 (Pariah) | `pww_rep_rel_band_0` | `§RUntrusted§!` |

### Observer Lines (what `[FROM.GetName]` says about `[ROOT.GetName]`)
| Band | Loc Key | Text |
|---|---|---|
| 4 | `pww_rep_rel_4_a` | `"[ROOT.GetCapitalName] pays on the day it promises," notes the [FROM.GetAdjective] trade ministry.` |
| 4 | `pww_rep_rel_4_b` | `Merchants in [FROM.GetCapitalName] treat a [ROOT.GetAdjective] signature as settled coin.` |
| 4 | `pww_rep_rel_4_c` | `[FROM.GetName] accepts [ROOT.GetAdjective] clearing paper without asking for collateral.` |
| 3 | `pww_rep_rel_3_a` | `[FROM.GetCapitalName] regards [ROOT.GetName] as a steady partner so long as terms are clear.` |
| 3 | `pww_rep_rel_3_b` | `Envoys in [FROM.GetCapitalName] expect [ROOT.GetName] to honor ordinary commercial schedules.` |
| 3 | `pww_rep_rel_3_c` | `[FROM.GetAdjective] officials raise no special objection to long-term [ROOT.GetAdjective] contracts.` |
| 2 | `pww_rep_rel_2_a` | `[FROM.GetCapitalName] checks every annex twice before signing with [ROOT.GetName].` |
| 2 | `pww_rep_rel_2_b` | `"[ROOT.GetName] keeps the easy clauses," mutters the [FROM.GetAdjective] legation, "and revises the hard ones."` |
| 2 | `pww_rep_rel_2_c` | `[FROM.GetAdjective] ministers prefer staged tranches when dealing with [ROOT.GetCapitalName].` |
| 1 | `pww_rep_rel_1_a` | `[FROM.GetCapitalName] doubts [ROOT.GetName] will still honor the ledger next winter.` |
| 1 | `pww_rep_rel_1_b` | `"Do not hand [ROOT.GetName] anything you cannot take back," advises the [FROM.GetAdjective] foreign office.` |
| 1 | `pww_rep_rel_1_c` | `Recent defaults by [ROOT.GetName] have chilled commercial talks across [FROM.GetCapitalName].` |
| 0 | `pww_rep_rel_0_a` | `No cabinet in [FROM.GetCapitalName] will stake its industry on a [ROOT.GetAdjective] promise.` |
| 0 | `pww_rep_rel_0_b` | `"[ROOT.GetName] signs treaties to buy time, not to keep them," reads the [FROM.GetAdjective] brief.` |
| 0 | `pww_rep_rel_0_c` | `Only cash-on-delivery or force will extract a signature from [FROM.GetName] now.` |

---

## 2. Credibility (Are Your Threats Real?)

Five bands from iron to hollow. Governs whether targets believe ultimatums, embargoes, and quarantines.

### Band Labels
| Band | Loc Key | Text |
|---|---|---|
| 4 (Iron) | `pww_rep_cred_band_4` | `§GFeared§!` |
| 3 (Proven) | `pww_rep_cred_band_3` | `Taken Seriously` |
| 2 (Untested) | `pww_rep_cred_band_2` | `Untested` |
| 1 (Doubted) | `pww_rep_cred_band_1` | `§ODoubted§!` |
| 0 (Hollow) | `pww_rep_cred_band_0` | `§RHollow§!` |

### Observer Lines (what `[FROM.GetName]` says about `[ROOT.GetName]`)
| Band | Loc Key | Text |
|---|---|---|
| 4 | `pww_rep_cred_4_a` | `"When [ROOT.GetCapitalName] sets a date, the ships are already coaling," warns the [FROM.GetAdjective] attaché.` |
| 4 | `pww_rep_cred_4_b` | `[FROM.GetCapitalName] treats even a quiet [ROOT.GetAdjective] warning as a loaded gun.` |
| 4 | `pww_rep_cred_4_c` | `No minister in [FROM.GetName] expects [ROOT.GetName] to blink first.` |
| 3 | `pww_rep_cred_3_a` | `[FROM.GetCapitalName] assumes [ROOT.GetName] will enforce any deadline it puts in writing.` |
| 3 | `pww_rep_cred_3_b` | `Recent demonstrations proved [ROOT.GetName] is willing to pay the cost of pressure.` |
| 3 | `pww_rep_cred_3_c` | `The [FROM.GetAdjective] cabinet weighs [ROOT.GetAdjective] notes with genuine caution.` |
| 2 | `pww_rep_cred_2_a` | `[FROM.GetCapitalName] has yet to see whether [ROOT.GetName] backs its cables with steel.` |
| 2 | `pww_rep_cred_2_b` | `"They speak firmly, but we have not tested their nerve," reports the [FROM.GetAdjective] chancery.` |
| 2 | `pww_rep_cred_2_c` | `[FROM.GetName] is still taking the measure of [ROOT.GetAdjective] resolve.` |
| 1 | `pww_rep_cred_1_a` | `[FROM.GetCapitalName] doubts [ROOT.GetName] would really enforce an embargo.` |
| 1 | `pww_rep_cred_1_b` | `"Wait out the deadline and [ROOT.GetCapitalName] will find a pretext to move on," says the [FROM.GetAdjective] envoy.` |
| 1 | `pww_rep_cred_1_c` | `Unpunished refusals have left [FROM.GetName] skeptical of [ROOT.GetAdjective] ultimatums.` |
| 0 | `pww_rep_cred_0_a` | `[FROM.GetCapitalName] files [ROOT.GetAdjective] ultimatums with the morning newspapers.` |
| 0 | `pww_rep_cred_0_b` | `"Paper threats from [ROOT.GetCapitalName]," remarks the [FROM.GetAdjective] prime minister. "Let them shout."` |
| 0 | `pww_rep_cred_0_c` | `After repeated climb-downs, nobody in [FROM.GetName] expects [ROOT.GetName] to act.` |

---

## 3. Regional Alarm (How Predatory Do You Look Nearby?)

Five bands per region. High alarm makes regional majors guarantee targets and backstop Situations more readily.

### Band Labels
| Band | Loc Key | Text |
|---|---|---|
| 0 (Quiet) | `pww_rep_alarm_band_0` | `Quiet` |
| 1 (Watched) | `pww_rep_alarm_band_1` | `Watched` |
| 2 (Uneasy) | `pww_rep_alarm_band_2` | `§YUneasy§!` |
| 3 (Alarmed) | `pww_rep_alarm_band_3` | `§OAlarmed§!` |
| 4 (Closing Ranks) | `pww_rep_alarm_band_4` | `§RClosing Ranks§!` |

### Observer Lines (regional capitals speaking about `[ROOT.GetName]`)
| Band | Loc Key | Text |
|---|---|---|
| 0 | `pww_rep_alarm_0_a` | `Capitals near [FROM.GetName] treat [ROOT.GetAdjective] commerce as routine business.` |
| 0 | `pww_rep_alarm_0_b` | `No chancery in the region sees [ROOT.GetName] as a predator.` |
| 1 | `pww_rep_alarm_1_a` | `Neighboring ministries have begun tracking [ROOT.GetAdjective] trade delegations closely.` |
| 1 | `pww_rep_alarm_1_b` | `[FROM.GetCapitalName] notes a sharper edge to [ROOT.GetAdjective] diplomacy of late.` |
| 2 | `pww_rep_alarm_2_a` | `Smaller powers around [FROM.GetName] are quietly asking majors for commercial cover against [ROOT.GetName].` |
| 2 | `pww_rep_alarm_2_b` | `"First one mine, then the next," warns a circular from [FROM.GetCapitalName].` |
| 3 | `pww_rep_alarm_3_a` | `Regional powers view [ROOT.GetName]'s coercion as a direct threat to their sphere.` |
| 3 | `pww_rep_alarm_3_b` | `Guarantees and counter-pledges are being drafted across the region to blunt [ROOT.GetCapitalName].` |
| 4 | `pww_rep_alarm_4_a` | `Every major with a stake near [FROM.GetName] is prepared to step in against [ROOT.GetName].` |
| 4 | `pww_rep_alarm_4_b` | `"[ROOT.GetName] will not take another concession here without answering to us," cables [FROM.GetCapitalName].` |

---

## 4. Combined Reputation Remarks (Cross-Axis Voices)

Used in Dossier summaries when Reliability and Credibility diverge sharply.

| Profile | Loc Key | Text |
|---|---|---|
| High Cred, Low Rel | `pww_rep_combo_feared_untrusted` | `[FROM.GetCapitalName] fears [ROOT.GetAdjective] retaliation, but expects [ROOT.GetName] to break any promise the moment it suits them.` |
| High Rel, Low Cred | `pww_rep_combo_honest_soft` | `[FROM.GetName] trusts [ROOT.GetAdjective] contracts and ignores [ROOT.GetAdjective] threats.` |
| High Rel, High Cred | `pww_rep_combo_iron_bond` | `[FROM.GetCapitalName] knows [ROOT.GetName] keeps both its bargains and its warnings.` |
| Low Rel, Low Cred | `pww_rep_combo_spent` | `Neither [ROOT.GetAdjective] promises nor [ROOT.GetAdjective] threats carry weight in [FROM.GetCapitalName].` |

---

## 5. Dependency-Pair Voices

Shown in the Dossier to express mutual leverage without numeric percentages.

| Direction | Loc Key | Text |
|---|---|---|
| They rely on us as buyer | `pww_dep_voice_they_buyer` | `[FROM.GetAdjective] exporters lean heavily on [ROOT.GetAdjective] orders.` |
| They rely on us as supplier | `pww_dep_voice_they_supplier` | `[FROM.GetAdjective] plants would slow sharply if [ROOT.GetName] cut deliveries.` |
| We rely on them as supplier | `pww_dep_voice_we_supplier` | `Our own mills are exposed if [FROM.GetCapitalName] halts shipments.` |
| We rely on them as buyer | `pww_dep_voice_we_buyer` | `Our surplus depends on [FROM.GetAdjective] demand staying open.` |
| Mutual lock | `pww_dep_voice_mutual` | `Both [ROOT.GetCapitalName] and [FROM.GetCapitalName] would bleed if trade broke off.` |
| Clearing debt active | `pww_dep_voice_clearing` | `Unredeemed clearing balances tie [FROM.GetName] to [ROOT.GetAdjective] arms deliveries.` |
| Clearing grievance (war) | `pww_dep_voice_clearing_grievance` | `[FROM.GetCapitalName] is furious over clearing credits it can no longer redeem in [ROOT.GetAdjective] arms.` |
