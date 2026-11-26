# Envoys: Negotiation Reports, Red Lines, and Hidden Wants

Player-facing localisation bible for post-round envoy reports (section 7.4).
Each report encodes exactly one hidden negotiation variable (patience, red line, hidden want, Reliability doubt, Credibility doubt, rival fear, or stalling). Maximum 3 counters per negotiation; every round teaches the player something concrete without showing numbers.

Tone: diplomatic cable from your legation or trade delegation. Terse, dry, observant. No em dashes, no exclamation marks.

---

## 1. Envoy Report Lines by Encoded Signal (50 lines)

### A. Low Patience (talks near collapse)
| Loc Key | Text |
|---|---|
| `pww_envoy_patience_low_1` | `Their delegation packed its papers early today. One more unacceptable draft will close the room.` |
| `pww_envoy_patience_low_2` | `The [FROM.GetAdjective] minister spoke through his teeth. We have one counter left at most.` |
| `pww_envoy_patience_low_3` | `[FROM.GetCapitalName] has instructed its envoys to break off talks if the next offer looks like the last.` |
| `pww_envoy_patience_low_4` | `Cordiality is gone. They are asking whether [ROOT.GetName] came to trade or to waste their week.` |
| `pww_envoy_patience_low_5` | `Their lead negotiator checked his watch twice and reminded us the decision date is ours to lose.` |
| `pww_envoy_patience_low_6` | `We are scraping the bottom of their goodwill. Soften the terms or drop the disputed clause.` |
| `pww_envoy_patience_low_7` | `The legation advises closing on the next round; [FROM.GetCapitalName] is ready to walk.` |

### B. Restored / High Patience (room to maneuver)
| Loc Key | Text |
|---|---|
| `pww_envoy_patience_high_1` | `The mood warmed noticeably when we tabled the revised terms. They want this signed.` |
| `pww_envoy_patience_high_2` | `Their delegation asked for an extra afternoon to draft annexes. We have their ear.` |
| `pww_envoy_patience_high_3` | `[FROM.GetCapitalName] sent back fresh instructions overnight. That offer landed where it mattered.` |
| `pww_envoy_patience_high_4` | `For the first time this week, their finance men stopped objecting and started penciling schedules.` |
| `pww_envoy_patience_high_5` | `We have room to press on secondary terms, provided we keep the core terms intact.` |

### C. Red Line Hit (non-negotiable touched; patience spent)
| Loc Key | Text |
|---|---|
| `pww_envoy_redline_1` | `Mention of that clause froze the table. Take it out or the talks end here.` |
| `pww_envoy_redline_2` | `Their envoy laid down his pen: his government cannot sign that wording and remain in office.` |
| `pww_envoy_redline_3` | `We struck a fixed boundary in [FROM.GetCapitalName]. No price will buy that concession.` |
| `pww_envoy_redline_4` | `They did not haggle over the clause; they crossed it out without comment.` |
| `pww_envoy_redline_5` | `Our legation confirms that point is non-negotiable. Asking again will only burn our remaining time.` |
| `pww_envoy_redline_6` | `The [FROM.GetAdjective] cabinet drew a hard line before the talks even opened. Drop that demand.` |
| `pww_envoy_redline_7` | `They treated the clause as an insult rather than a bargaining chip. Move off it at once.` |

### D. Hidden Want Hinted (what restores patience and closes the deal)
| Loc Key | Text |
|---|---|
| `pww_envoy_want_arms` | `Over brandy after the session, their colonel kept returning to the state of [FROM.GetAdjective] artillery.` |
| `pww_envoy_want_clearing` | `They care less for factories than for guaranteed access to [ROOT.GetAdjective] armaments.` |
| `pww_envoy_want_cic` | `Their treasury is starved for industrial capacity. Civilian works would move this faster than metal.` |
| `pww_envoy_want_coal` | `Their delegates quietly asked whether [ROOT.GetAdjective] coal could be folded into the protocol.` |
| `pww_envoy_want_tech` | `They lingered over our industrial licenses. Technical help carries double weight in [FROM.GetCapitalName].` |
| `pww_envoy_want_timed` | `They would yield much of the substance if the paper carries a firm reversion date.` |
| `pww_envoy_want_fig_leaf` | `Their resistance is mostly theatrical. Give them a joint commission to show the press and they will sign.` |
| `pww_envoy_want_split` | `They do not want to hand the whole field to one flag. A split lot would unlock the room.` |

### E. Doubts About Our Reliability (fear we will default)
| Loc Key | Text |
|---|---|
| `pww_envoy_rel_doubt_1` | `Their lawyers keep asking what happens if [ROOT.GetName] stops delivering after the first quarter.` |
| `pww_envoy_rel_doubt_2` | `[FROM.GetCapitalName] remembers broken contracts elsewhere. They want tranches tied to delivery.` |
| `pww_envoy_rel_doubt_3` | `They like the price, not the signature. Our reputation for keeping terms is costing us.` |
| `pww_envoy_rel_doubt_4` | `Their envoy asked bluntly whether a [ROOT.GetAdjective] promise outlasts a change of season.` |
| `pww_envoy_rel_doubt_5` | `Because they doubt our word, they are demanding heavier payment up front.` |
| `pww_envoy_rel_doubt_6` | `They prefer a non-committal arrangement until [ROOT.GetName] proves it honors its ledgers.` |

### F. Doubts About Our Credibility (do not believe our threats)
| Loc Key | Text |
|---|---|
| `pww_envoy_cred_doubt_1` | `They smiled politely at our warnings. [FROM.GetCapitalName] does not believe we will enforce them.` |
| `pww_envoy_cred_doubt_2` | `Our envoy's hint of retaliation drew a shrug. They think [ROOT.GetName] is bluffing.` |
| `pww_envoy_cred_doubt_3` | `They are pricing the deal as ordinary commerce, not as a demand backed by force.` |
| `pww_envoy_cred_doubt_4` | `[FROM.GetCapitalName] noted that our last ultimatum elsewhere went unenforced.` |
| `pww_envoy_cred_doubt_5` | `Words alone will not shift them; they are waiting to see whether we back the cable with action.` |

### G. Fear of a Rival or Patron (watching a third capital)
| Loc Key | Text |
|---|---|
| `pww_envoy_rival_1` | `Every time we press for exclusivity, their envoy glances at the cables from [pww_patron.GetCapitalName].` |
| `pww_envoy_rival_2` | `[FROM.GetCapitalName] fears that signing with us will trigger retaliation from [pww_rival.GetName].` |
| `pww_envoy_rival_3` | `They are not rejecting our terms on merit; they are waiting to see if [pww_patron.GetName] matches them.` |
| `pww_envoy_rival_4` | `Their minister admitted privately that he cannot afford to anger [pww_patron.GetName] without cover.` |
| `pww_envoy_rival_5` | `A rival delegation from [pww_rival.GetName] is staying two floors down in the same hotel.` |
| `pww_envoy_rival_6` | `They want wording vague enough that [pww_patron.GetCapitalName] cannot call it a breach of neutrality.` |

### H. Stalling, Clock-Watching & Repeated Offers
| Loc Key | Text |
|---|---|
| `pww_envoy_stall_1` | `They asked to adjourn for "technical review" for the second time. They are playing the clock.` |
| `pww_envoy_stall_2` | `Their delegation is stretching every paragraph, hoping the decision date passes without a signature.` |
| `pww_envoy_stall_3` | `We tabled an equivalent offer and received the exact same refusal. Something real has to change.` |
| `pww_envoy_stall_4` | `They are buying weeks, not bargaining. Waiting on a third power's reply is the obvious guess.` |
| `pww_envoy_stall_5` | `Their counter-draft changed three adjectives and nothing else. They expect us to lose interest.` |
| `pww_envoy_stall_6` | `The legation reports no serious intent to close unless we either improve the terms or turn up the heat.` |

### I. Trade Talks: Price Too Low (the main obstacle is the price)
| Loc Key | Text |
|---|---|
| `pww_envoy_price_low_1` | `Their trade ministry ran the numbers twice. Our price is below what the market pays them, and they will not sell at a loss.` |
| `pww_envoy_price_low_2` | `[FROM.GetCapitalName] calls our figure an insult to their mines. Come up to the going rate.` |
| `pww_envoy_price_low_3` | `They like the deal, not the price. Raise what we pay and the signature follows.` |
| `pww_envoy_price_low_4` | `Their negotiator tapped the market sheet and said nothing. We are asking too much for too little.` |
| `pww_envoy_price_low_5` | `Buyers elsewhere pay more for the same output. Until we match them, the answer stays no.` |
| `pww_envoy_price_low_6` | `The legation reports no objection to the terms, only to the sum. Pay closer to market.` |

### I2. Trade Talks: Too Little Trust for a Fixed Contract (bond under the lock threshold)
| Loc Key | Text |
|---|---|
| `pww_envoy_trust_lock_1` | `They will trade with us, but not bind themselves to a partner they hardly know. Let either side end it, or make the price impossible to refuse.` |
| `pww_envoy_trust_lock_2` | `Their ministry will not sign a fixed contract with a stranger. A record of honored deals would change that; so would a much better price.` |
| `pww_envoy_trust_lock_3` | `"Trust is earned in deliveries," their envoy said. An open deal first, or terms far above market.` |

### J. Trade Talks: Wants Hinted (items the trade talks table can carry)
| Loc Key | Text |
|---|---|
| `pww_envoy_want_transport` | `Their quartermaster asked twice about [ROOT.GetAdjective] lorries. Trucks would carry this deal further than coin.` |
| `pww_envoy_want_trial` | `They will not bind themselves for long to a partner they have not tried. A six-month trial would put them at ease.` |
| `pww_envoy_want_lack` | `Their ministry kept asking what we could spare of the materials they lack. Fill one of their shortfalls and the room warms.` |
| `pww_envoy_want_modest` | `They will not hand one buyer the bulk of their output. Ask for a smaller share and they will listen.` |
| `pww_envoy_want_goodwill` | `Their minister needs something to show the cabinet. A political payment would cover him at home.` |

---

## 2. Red-Line Reveal Templates

Shown in the negotiation card once discovered in a round. Short, concrete, unmistakable.

| Loc Key | Red Line Type | Text |
|---|---|---|
| `pww_redline_no_lease` | Named-state lease off the table | `§RRed line:§! Named-state rights are off the table; an output share is possible.` |
| `pww_redline_no_permanent` | No long/permanent term | `§RRed line:§! [FROM.GetName] refuses any term beyond a short renewable window.` |
| `pww_redline_no_exclusive` | No exclusivity clause | `§RRed line:§! Exclusive allocation is rejected; they will keep a share for other buyers.` |
| `pww_redline_no_political` | No political/ideological clause | `§RRed line:§! Political concessions are out of bounds; keep the paper strictly commercial.` |
| `pww_redline_no_public` | No public signing | `§RRed line:§! [FROM.GetCapitalName] will not sign under public ultimatums or press fanfare.` |
| `pww_redline_no_full_output` | No full-output surrender | `§RRed line:§! They will not commit their entire output; domestic mills must stay fed.` |
| `pww_redline_no_alliance_breach` | Cannot break patron treaty | `§RRed line:§! Nothing that formally breaches their treaty with [pww_patron.GetName].` |
| `pww_redline_no_credit_only` | Refuses pure clearing credit | `§RRed line:§! [FROM.GetName] will not accept clearing paper without hard delivery.` |

---

## 3. Hidden-Want Reveal Templates

Shown in the negotiation card once uncovered. Offering it restores patience and lifts acceptance.

| Loc Key | Hidden Want Type | Text |
|---|---|---|
| `pww_want_clearing_arms` | Clearing credit / arms | `§GHidden want:§! [FROM.GetName] is eager for arms credit redeemable in [ROOT.GetAdjective] ordnance.` |
| `pww_want_cic_flow` | Civilian factory flow | `§GHidden want:§! Civilian industrial allocation carries extra weight in [FROM.GetCapitalName].` |
| `pww_want_coal_supply` | Coal / energy relief | `§GHidden want:§! Bundling coal deliveries would unlock concessions elsewhere.` |
| `pww_want_equipment_tranche` | Direct equipment tranches | `§GHidden want:§! Staged deliveries of modern rifles or artillery will soften their line.` |
| `pww_want_tech_license` | Production license / tech bonus | `§GHidden want:§! A manufacturing license or technical mission is what their ministry truly wants.` |
| `pww_want_timed_reversion` | Timed reversion clause | `§GHidden want:§! Adding a fixed reversion date lets [FROM.GetCapitalName] sell this at home.` |
| `pww_want_fig_leaf` | Face-saving fig leaf | `§GHidden want:§! A joint commission or sovereignty assurance will bring them to the table.` |
| `pww_want_split_award` | Split lot arrangement | `§GHidden want:§! Accepting a split allocation lets them balance [ROOT.GetName] and [pww_rival.GetName].` |
| `pww_want_patron_cover` | Quiet commercial cover | `§GHidden want:§! Framing the deal as ordinary trade avoids a row with [pww_patron.GetName].` |
