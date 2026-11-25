# Readouts: Target States, Causes, Cornered Warnings, and Intel

Player-facing localisation bible for the Coercion Readout (Dossier and Situation panel).
Tone: terse, diplomatic-cable, 1936 to 1945. No em dashes, no exclamation marks, no numeric scores.
Scope conventions: `ROOT` is the player (usually Claimant when viewing a target); `FROM` is the target country; `pww_patron` is the target's patron scope; `pww_rival` is a competing claimant; `pww_state` is a dynamically resolved state scope.

---

## 1. Target States

Shown as the headline state of a coercion target. Every state transition appends the top cause line.

| Loc Key | Text |
|---|---|
| `pww_state_defiant` | `§RDefiant§!` |
| `pww_state_defiant_desc` | `[FROM.GetName] sees no reason to yield and treats our approach with open contempt.` |
| `pww_state_strained` | `§OStrained§!` |
| `pww_state_strained_desc` | `The pressure is telling in [FROM.GetCapitalName], though the cabinet still holds its line.` |
| `pww_state_wavering` | `§YWavering§!` |
| `pww_state_wavering_desc` | `Ministers in [FROM.GetCapitalName] are divided; a further turn of the screw or a face-saving exit could decide it.` |
| `pww_state_cornered` | `§tCornered§!` |
| `pww_state_cornered_desc` | `[FROM.GetName] is running out of room. Push without an exit and they may fight rather than submit.` |
| `pww_state_ready_to_fold` | `§GReady to fold§!` |
| `pww_state_ready_to_fold_desc` | `[FROM.GetCapitalName] has concluded that resistance costs more than compliance.` |

### Readout Headers & Transition Lines

| Loc Key | Text |
|---|---|
| `pww_readout_header_for` | `Working for you` |
| `pww_readout_header_against` | `Why they are holding out` |
| `pww_readout_shift_up` | `[pww_prev_state] -> [pww_curr_state]: [pww_shift_cause]` |
| `pww_readout_shift_down` | `[pww_prev_state] -> [pww_curr_state]: [pww_shift_cause]` |
| `pww_readout_intel_locked` | `Further factors obscured. Raise civilian intel on [FROM.GetName] to see more.` |
| `pww_readout_empty_for` | `No active leverage is telling on [FROM.GetCapitalName].` |
| `pww_readout_empty_against` | `[FROM.GetName] has nothing left to lean on.` |

---

## 2. Cause Lines: "Working for you" (34 lines)

Each line maps to a concrete mechanic in section 7.8, 7.9, 7.11, or 7.12.

### Committed Forces (Loud)
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_for_fleet_station` | Committed naval squadron on station | `Our squadron off the [FROM.GetAdjective] coast is concentrating minds in [FROM.GetCapitalName].` |
| `pww_cause_for_fleet_ramping` | Committed naval squadron ramping (30 to 60d) | `Our naval presence off [FROM.GetName] grows heavier by the week.` |
| `pww_cause_for_air_based` | Committed air group based in nearby region | `[ROOT.GetAdjective] bombers within range of [FROM.GetCapitalName] weigh on their cabinet.` |
| `pww_cause_for_air_access` | Air group using neighbor air base access | `Forward-based [ROOT.GetAdjective] aircraft have stripped [FROM.GetName] of depth.` |
| `pww_cause_for_border_mass` | Committed army group on border states | `[ROOT.GetAdjective] divisions massed along the [FROM.GetAdjective] frontier.` |
| `pww_cause_for_border_ramping` | Border posture ramping | `Fresh [ROOT.GetAdjective] deployments on the border keep [FROM.GetCapitalName] on edge.` |

### Quiet Economic & Resource Levers
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_for_dep_buyer` | Dependency pair: target relies on us as buyer | `[FROM.GetName] cannot easily replace [ROOT.GetAdjective] purchases.` |
| `pww_cause_for_dep_supplier` | Dependency pair: target relies on us as supplier | `[FROM.GetAdjective] industry depends on deliveries from [ROOT.GetName].` |
| `pww_cause_for_clearing_debt` | Unredeemed clearing credit balance | `Clearing balances in [ROOT.GetCapitalName] tie [FROM.GetAdjective] exporters to our terms.` |
| `pww_cause_for_cutoff_oil` | Single-resource cutoff (oil) | `Our oil cutoff is draining [FROM.GetAdjective] fuel reserves.` |
| `pww_cause_for_cutoff_coal` | Single-resource cutoff (coal) | `Cutting [ROOT.GetAdjective] coal has darkened [FROM.GetAdjective] power stations.` |
| `pww_cause_for_cutoff_metal` | Single-resource cutoff (steel/tungsten/aluminium/chromium) | `Suspended [ROOT.GetAdjective] metal deliveries are slowing [FROM.GetAdjective] mills.` |
| `pww_cause_for_cutoff_rubber` | Single-resource cutoff (rubber) | `Our rubber halt has pinched [FROM.GetAdjective] transport and ordnance plants.` |
| `pww_cause_for_energy_shortage` | Target `energy_ratio` low | `[FROM.GetName] faces a creeping energy shortage.` |
| `pww_cause_for_subsidy_pulled` | Subsidy withdrawal | `Withdrawing [ROOT.GetAdjective] arms subsidies left a gap in [FROM.GetAdjective] procurement.` |
| `pww_cause_for_market_closed` | Market access withdrawal / Deny list | `Closing [ROOT.GetAdjective] markets has left [FROM.GetAdjective] surplus unsold.` |
| `pww_cause_for_envoy_leverage` | Quiet envoy leverage | `Quiet representations from our legation are finding sympathetic ears in [FROM.GetCapitalName].` |

### Escalation Ladder (Loud)
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_for_embargo` | Active embargo | `Our embargo is biting into [FROM.GetAdjective] trade.` |
| `pww_cause_for_join_embargo` | Third parties complied with "Join our embargo" | `Third-party embargoes are closing [FROM.GetName]'s remaining outlets.` |
| `pww_cause_for_quarantine` | Active Quarantine controlling sea approaches | `Our quarantine has halted [FROM.GetAdjective] sea-borne contracts.` |
| `pww_cause_for_strangulation` | Rising quarantine/embargo strangulation | `Sustained interdiction is starving [FROM.GetAdjective] ports and depots.` |
| `pww_cause_for_convoy_pinch` | Target convoy threat / shipping loss | `Exposed sea lanes leave [FROM.GetName] unable to move its own cargo.` |

### Patrons & Rivals
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_for_patron_backed_down` | Patron withdrew pledge | `[pww_patron.GetName] stepped back, leaving [FROM.GetCapitalName] exposed.` |
| `pww_cause_for_patron_blocked` | Quarantine suspended patron's reserved deal | `Our quarantine has rendered [pww_patron.GetAdjective] commercial support undeliverable.` |
| `pww_cause_for_no_patron` | No major power stepped in as patron | `No outside power has offered to underwrite [FROM.GetName].` |
| `pww_cause_for_rival_outbid` | Competing claimant outbid or withdrew | `With [pww_rival.GetName] out of the bidding, [FROM.GetName] has no second offer.` |

### Terms, Fig Leaves & Channel
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_for_fig_leaf` | Fig leaf offered (cuts humiliation) | `Our face-saving formula lets [FROM.GetCapitalName] yield without public disgrace.` |
| `pww_cause_for_timed_clause` | Temporary reversion date offered | `A fixed reversion date makes the concession easier for [FROM.GetName] to swallow.` |
| `pww_cause_for_quiet_channel` | Back-channel lets dictatorship concede quietly | `Private talks allow [FROM.GetCapitalName] to bend without losing face at home.` |

### Target Weakness, Reputation & Clock
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_for_credibility_high` | Coercer high Credibility | `[FROM.GetCapitalName] remembers that [ROOT.GetName] carries out its threats.` |
| `pww_cause_for_target_at_war` | Target distracted by another war | `[FROM.GetName] is already committed to a war and cannot afford a second front.` |
| `pww_cause_for_low_stability` | Target low stability | `Domestic unrest in [FROM.GetName] leaves the government little margin for a crisis.` |
| `pww_cause_for_idle_mills` | Target idle military factories / acute deficit | `Idle plants in [FROM.GetName] make a drawn-out standoff untenable.` |
| `pww_cause_for_clock_short` | Decision date imminent | `The decision date is days away and [FROM.GetCapitalName] has no counter-plan ready.` |

---

## 3. Cause Lines: "Why they are holding out" (34 lines)

Each line maps to a concrete resistance factor in section 7.8, 7.9, 7.11, or 7.12.

### Patrons, Allies & Alternatives
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_against_patron_pledge` | Patron reserved agreement active | `[pww_patron.GetName] has pledged to buy [FROM.GetAdjective] output if we cut them off.` |
| `pww_cause_against_guarantee` | External guarantee / alliance | `[FROM.GetName] leans on its guarantee from [pww_patron.GetName].` |
| `pww_cause_against_faction` | Target belongs to a major faction | `Faction backing shields [FROM.GetCapitalName] from isolated pressure.` |
| `pww_cause_against_alt_buyers` | Open-market alternatives available | `Other buyers still take [FROM.GetAdjective] exports without conditions.` |
| `pww_cause_against_rival_bid` | Rival claimant competing | `[pww_rival.GetName] is bidding against us, keeping [FROM.GetCapitalName] in play.` |
| `pww_cause_against_land_route` | Overland corridor bypasses sea pressure | `Overland rail links blunt our pressure on [FROM.GetAdjective] ports.` |

### Regime, Pride & Pretext
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_against_rally_effect` | Public ultimatum triggered democratic rally | `Our public ultimatum rallied [FROM.GetAdjective] opinion behind the government.` |
| `pww_cause_against_no_pretext` | Democratic coercer went loud without pretext | `Acting without a pretext handed [FROM.GetCapitalName] an easy cry of aggression.` |
| `pww_cause_against_dictator_pride` | Dictatorship resists public humiliation | `The regime in [FROM.GetCapitalName] cannot bow to an open ultimatum and survive.` |
| `pww_cause_against_demand_size` | Prize is large or vital | `We are asking for too much of [FROM.GetName]'s vital output at once.` |
| `pww_cause_against_humiliation` | Humiliating terms (permanent rights, no fig leaf) | `The terms read as a surrender of sovereignty rather than a commercial deal.` |
| `pww_cause_against_recent_humiliation` | Target recently folded to another demand | `[FROM.GetName] yielded recently and will not endure a second humiliation.` |
| `pww_cause_against_high_stability` | High domestic stability | `A steady domestic front lets [FROM.GetCapitalName] absorb the strain.` |
| `pww_cause_against_high_war_support` | High war support / mobilized public | `Public resolve in [FROM.GetName] favors defiance over concession.` |
| `pww_cause_against_hardened` | Target chose "Harden and mobilize" | `[FROM.GetName] has called up reserves and staked its honor on refusal.` |

### Limits of Force & Channel
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_against_force_cap` | Force alone tops out at Wavering | `§YArms alone will not break them§!; they still need an economic pinch or a face-saving exit.` |
| `pww_cause_against_force_ramping` | Committed forces still building pressure | `Our committed forces have only begun to make their weight felt.` |
| `pww_cause_against_fleet_contested` | Naval squadron lacks sea control | `Our ships off [FROM.GetName] do not yet command the approaches.` |
| `pww_cause_against_air_range` | Air group lacks forward basing | `Our air units are too distant to threaten [FROM.GetCapitalName] credibly.` |
| `pww_cause_against_border_thin` | Border posture outweighed by defenders | `[FROM.GetAdjective] divisions on the frontier match our posture.` |
| `pww_cause_against_quiet_ceiling` | Back-channel ceiling reached | `Quiet diplomacy has reached its limit; [FROM.GetCapitalName] will not move further in private.` |
| `pww_cause_against_quarantine_lapsed` | Quarantine lapsed after losing sea control | `Our quarantine lapsed when naval control slipped, restoring [FROM.GetAdjective] confidence.` |
| `pww_cause_against_embargo_ignored` | Third parties ignored "Join our embargo" | `Neutrals ignored our embargo call and continue trading with [FROM.GetName].` |

### Reputation & Regional Alarm
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_against_credibility_low` | Coercer low Credibility | `[FROM.GetCapitalName] doubts [ROOT.GetName] will carry out its threats.` |
| `pww_cause_against_reliability_low` | Coercer low Reliability | `[FROM.GetName] fears we will break the deal as soon as they sign.` |
| `pww_cause_against_regional_alarm` | High Regional Alarm | `Neighboring capitals are alarmed by our pressure and encourage [FROM.GetName] to stand firm.` |
| `pww_cause_against_coercer_distracted` | Coercer tied down in war | `[FROM.GetCapitalName] sees our forces tied down elsewhere.` |

### Target Cushion & Stalling
| Loc Key | Mechanic | Text |
|---|---|---|
| `pww_cause_against_held_stock` | Target holds a Held pool stockpile | `Stockpiles in [FROM.GetName] cushion the short-term shock.` |
| `pww_cause_against_coal_ok` | Target has adequate energy reserves | `[FROM.GetAdjective] power and fuel stocks are holding steady.` |
| `pww_cause_against_stalling` | Back-channel stalling | `[FROM.GetCapitalName] is dragging out talks to run down the clock.` |
| `pww_cause_against_provisional` | Target accepted 90-day provisional suspension | `A provisional suspension bought [FROM.GetName] ninety days to look for help.` |
| `pww_cause_against_small_lot` | Target offered a smaller lot | `[FROM.GetName] hopes a smaller counter-offer will satisfy us.` |
| `pww_cause_against_own_fig_leaf` | Target proposed its own fig leaf | `[FROM.GetCapitalName] insists on its own wording to protect domestic prestige.` |
| `pww_cause_against_patron_called` | Target appealed to a patron | `[FROM.GetName] is awaiting word from [pww_patron.GetName] before answering.` |

---

## 4. "Cornered" Warning Lines (18 lines)

Shown when a target reaches `Cornered`. Guides the core decision: push, take less, or offer a fig leaf.

### Calculated War Risk (target has a plan or expects backing)
| Loc Key | Text |
|---|---|
| `pww_cornered_calc_plan` | `§R[FROM.GetName] is cornered and has staff plans ready.§! One more turn of the screw may bring war.` |
| `pww_cornered_calc_patron` | `[FROM.GetCapitalName] believes [pww_patron.GetName] will come in if shots are fired. Take less or offer a fig leaf.` |
| `pww_cornered_calc_frontier` | `[FROM.GetAdjective] divisions are moving into war stations along the frontier. Pushing now risks a shooting war.` |
| `pww_cornered_calc_mobilizing` | `Quiet mobilization orders are circulating in [FROM.GetCapitalName]. They will fight if left no exit.` |
| `pww_cornered_calc_pride` | `[FROM.GetName] cannot yield to this demand in public without collapsing. Offer a face-saving exit or prepare for war.` |
| `pww_cornered_calc_alliance` | `Their general staff counts on allied intervention to survive a clash. Do not assume they will fold.` |

### Desperate War Risk (resource/fuel runway expiring)
| Loc Key | Text |
|---|---|
| `pww_cornered_desp_fuel` | `§R[FROM.GetAdjective] fuel reserves are down to months.§! Left with nothing to lose, they may strike first.` |
| `pww_cornered_desp_embargo` | `The embargo has backed [FROM.GetName] against the wall. A starved power rarely surrenders quietly.` |
| `pww_cornered_desp_quarantine` | `Quarantine is choking [FROM.GetAdjective] industry. Expect a breakout attempt if terms stay this harsh.` |
| `pww_cornered_desp_runway` | `[FROM.GetCapitalName] calculates that waiting another season means ruin anyway. War is becoming their least bad choice.` |
| `pww_cornered_desp_coal` | `With energy failing across [FROM.GetName], the cabinet is openly weighing desperate measures.` |
| `pww_cornered_desp_isolation` | `Cut off from every supplier, [FROM.GetName] sees no peaceful path out of this crisis.` |

### Decision-Point Prompts (Push / Settle / Fig Leaf)
| Loc Key | Text |
|---|---|
| `pww_cornered_choice_fig_leaf` | `[FROM.GetName] is at the breaking point. A small fig leaf now may close the deal without a shot.` |
| `pww_cornered_choice_temporary` | `A timed reversion clause would let [FROM.GetCapitalName] sign today and save face tomorrow.` |
| `pww_cornered_choice_smaller_lot` | `Taking a smaller lot now locks in gains before [FROM.GetName] does something irreversible.` |
| `pww_cornered_choice_push` | `They are cornered and isolated. Holding firm may break them, though the risk of war is live.` |
| `pww_cornered_choice_patron_watch` | `[pww_patron.GetName] is watching [FROM.GetCapitalName] closely. Pushing past this line may draw them in.` |
| `pww_cornered_choice_cabinet_split` | `Moderates in [FROM.GetCapitalName] are begging for a pretext to sign; hardliners are waiting for an excuse to fight.` |

---

## 5. Intel Advance-Warning Lines (14 lines)

Unlocked by `civilian_intel` and `network_strength` (section 7.8). Gives lead time before a target hits `Cornered` or makes a hidden move.

| Loc Key | Trigger / Signal | Text |
|---|---|---|
| `pww_intel_cornered_3w` | Pace toward Cornered (~21d) | `§HIntel:§! [FROM.GetName] will be §tCornered§! in about three weeks at this pace.` |
| `pww_intel_cornered_2w` | Pace toward Cornered (~14d) | `§HIntel:§! [FROM.GetCapitalName] is roughly two weeks from the breaking point.` |
| `pww_intel_cornered_1w` | Pace toward Cornered (~7d) | `§HIntel:§! Expect [FROM.GetName] to reach §tCornered§! within days unless terms soften.` |
| `pww_intel_war_plan` | Calculated war route forming | `§HIntel:§! The [FROM.GetAdjective] general staff has updated contingency orders against [ROOT.GetName].` |
| `pww_intel_runway_short` | Desperate war route forming | `§HIntel:§! [FROM.GetAdjective] strategic stocks are nearing the threshold where their cabinet favors war.` |
| `pww_intel_patron_talks` | Target courting a patron | `§HIntel:§! [FROM.GetAdjective] envoys are pressing [pww_patron.GetName] for a commercial backstop.` |
| `pww_intel_patron_wavering` | Patron considering withdrawal | `§HIntel:§! [pww_patron.GetCapitalName] is balking at the cost of underwriting [FROM.GetName].` |
| `pww_intel_leak_imminent` | Loud tool leaking quiet demand | `§HIntel:§! Foreign press have wind of our pressure; the back channel will not stay private much longer.` |
| `pww_intel_fig_leaf_ready` | Target receptive to fig leaf | `§HIntel:§! [FROM.GetCapitalName] is looking for a face-saving wording to accept without a cabinet crisis.` |
| `pww_intel_stall_detected` | Target stalling for time | `§HIntel:§! [FROM.GetAdjective] negotiators have orders to delay until the decision date passes.` |
| `pww_intel_split_lot_prep` | Target preparing split auction | `§HIntel:§! [FROM.GetCapitalName] is drafting separate lots to play us against [pww_rival.GetName].` |
| `pww_intel_nationalize_risk` | Host weighing nationalization | `§HIntel:§! Ministers in [FROM.GetCapitalName] are reviewing legal grounds to seize foreign concessions.` |
| `pww_intel_cabinet_softening` | Target nearing Ready to fold | `§HIntel:§! Resistance inside the [FROM.GetAdjective] cabinet is crumbling; one steady push should settle it.` |
| `pww_intel_third_party_cheat` | Neutral ignoring embargo | `§HIntel:§! Cargo bound for [FROM.GetName] is still clearing neutral ports despite our embargo.` |
