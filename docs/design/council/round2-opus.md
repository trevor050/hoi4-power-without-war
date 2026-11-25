# Council Review, Round 2: Claude Opus 5.5

Reviewer: `opus`. Inputs: the design document, round 1 reviews from `opus`, `sol` and `neon`, and fresh checks against the v1.20 install (cited inline and collected in section 6).

The three round 1 reviews agree on more than they disagree. All three replace `create_import` contracts with mod-owned flows. All three replace the vanilla blockade with a mod-owned quarantine. All three add a public versus back-channel choice. Each also found something the other two missed. Sol found that the target has no winning move. Neon found that the peaceful run has no third act and that coal is missing. I found that there is no core loop and no pairwise trade visibility. This round combines them into one design and states where I now think differently.

---

## 1. Synthesis: where fixes competed, what wins

### S1. The core loop: one framework, three seats

Three framings of the same need:
- Mine: a **Situations board** of contestable prizes with clocks.
- Sol: **one demand, one deadline**, playable from both seats, with a credible way for the target to prevail.
- Neon: **historical flashpoints**, a **Crisis Table** where regional majors react, and a wartime **Neutral Tightrope**.

Each is incomplete alone. My board was written from the claimant's chair. Sol's crisis has no generator for the open world. Neon's flashpoints are hand-authored, and its Crisis Table is a second system bolted onto coercion.

**Combined: a Situation is a three-seat crisis.**
- **Claimant:** wants the prize (oil, ore, a route, a base, a closure).
- **Holder:** owns the prize and decides who gets it.
- **Patron:** a third power with a stake, who can underwrite the holder, compete with the claimant, or stay out.

Each Situation has exactly one prize (named states, a named route, or a named flow), one deadline, and at least one decisive move for each seat. The player can sit in any seat, and the AI fills the others. Neon's Crisis Table becomes the patron seat's entry point instead of a separate mechanic. The Neutral Tightrope becomes the wartime state in which the player is Holder in two or three Situations at once, with both blocs as Claimants.

**Design rule (from Sol, promoted to a ship gate):** a Situation template does not ship until a human Holder can win it in playtest without outside help, by stalling, splitting, finding a patron, or making a smaller concession. If the Holder seat cannot win, the Claimant seat is not a game either. It is a meter.

Why this beats each version alone: one framework covers the coercing major, the neutral profiteer, the spoiler patron and the small state playing the target. It also keeps noise bounded, because noise is capped by the number of live Situations in the player's seats, not by event throttling.

### S2. Contracts: mod-owned flows, Sol's lifecycle, Neon's delivery modifier

Converged: contracts are scripted flows, and vanilla trade is the background market. Here is the best combined specification:

- **Delivery:** seller gets `country_resource_cost_<res> = N`, buyer gets `country_resource_<res> = N`, both through variable-driven dynamic modifiers. Neon was right about the seller side. `country_resource_cost_rubber` is localised as "Rubber Consumption" (`localisation/english/modifiers_l_english.yml` line 1413), and vanilla already uses it through a variable to "sell" Indonesian rubber off the books (`common/decisions/INS.txt` line 2347 and `common/dynamic_modifiers/TAOG_dynamic_modifiers.txt` line 95). That is a direct vanilla precedent for exactly this mechanic, and it avoids my round 1 guess that a negative `country_resource_<res>` would behave.
- **Ongoing payment:** `civilian_factory_use` on the payer, with `cic_to_target_factor` or `add_offsite_building` to the receiver (unchanged from round 1; Neon independently verified `cic_to_target_factor` inside `targeted_modifier` in `common/decisions/SWI.txt`).
- **Irreversible payment (tech, ships, equipment): Sol's tranches.** A first batch on signing, more after a quarter of service, the final item at a late milestone. This replaces the design's "owe the undelivered remainder" penalty, which a player would simply price in. Neon's split between **licenses and tech bonuses** (`create_production_license`, `add_tech_bonus`) for ordinary deals and full `set_technology` only as a final tranche of a mega-deal slots straight into the tranche schedule and also fixes the 1918-rifles-for-Ploiești exploit.
- **Clearing credit: Neon's `add_equipment_subsidy` with `seller_tags = { ROOT }`** (`documentation/effects_documentation.md` line 1234). It replaces my hidden "blocked credit" variable. It is native, the receiving AI already knows how to spend it on the International Market, and it locks the receiver into the payer's arms ecosystem with no custom AI conversion code. This is Schacht's mechanism, built from a single effect.
- **Lifecycle: Sol's states.** Active, Suspended (deliveries and payments pause, with a dated window to reroute or reduce), Terminated (clean), Defaulted (a deliberate breach, which loses remaining tranches and costs Reliability). A blockade by a third party produces Suspended first, not instant termination. That gives the victim a playable window, which is better than the design's "the deal is lost".

### S3. Coercion: the demand is the unit, the channel is the choice

Converged on channel choice. The pieces combine as follows:
- **One demand, one deadline** (Sol). Pressure is built *for* a named demand, not in the abstract.
- **Channel is chosen per demand** (all three). Back channel has a lower ceiling and no pride penalty. Public has a higher ceiling, puts Credibility at stake, and triggers the rally effect.
- **Every pressure source is tagged quiet or loud** (Neon). Dependency, single-resource cutoffs, subsidy withdrawal and envoy leverage are quiet. Demonstrations, embargoes, quarantines and blacklists are loud.
- **New interaction: loud tools leak.** Using a loud source during a back-channel demand forces the crisis public after a short delay. The player can escalate, but escalating changes the game they are playing: the ceiling rises, the target's pride engages, and the patron seat is alerted. This turns "stack every source" into a real trade-off without any hard rule against stacking.
- **Readout:** Neon's two lists ("working for you" and "why they are holding out"), with my deltas ("Strained → Wavering: your cruisers off Lisbon") and the top reason in each list always shown.
- **Neon's "Cornered" state** as a visible fifth stage before the breaking point, replacing my "telegraphed" hidden threshold. Cornered is where the best decision of the campaign lives: push, take a smaller concession, or offer a fig leaf.

### S4. Demonstrations: the Committed Force

Sol said assign a force to one crisis for a minimum time and cap what force alone can do. Neon said ramp over 30 to 60 days with upkeep. Combined:
- A **Committed Force** is a named fleet, air wing or army group assigned to one Situation. It ramps pressure over 30 to 60 days, costs fuel and command power upkeep, and counts for no other Situation.
- **Force alone tops out at Wavering** (Sol's cap). Folding requires at least one non-force lever: cutting the target's alternatives, dependency, a patron backing down, or a fig leaf.

That cap is the structural answer to Neon's "1936 Home Fleet farms every minor" exploit (Neon 2.2). A big navy can bring five minors to Wavering. It cannot close any of them without doing the economic and diplomatic work, and each committed squadron is absent from everywhere else.

### S5. The monopoly payoff: one Held pool, not three systems

Three proposals: my rationing, premium and preclusive buying; Neon's per-resource Market Stance and Strategic Reserves; Sol's "dependence runs both ways, a cartel that blacklists a customer finances a competing mine."

Neon's Stance and Reserves are really one mechanic, and treating them as one fixes a problem with each:
- **The Held pool.** Moving a resource to Held applies `country_resource_cost_<res>` to the holder's surplus (only when `resource@X > 0`) and accrues it into a per-resource variable. Held stock is physical: it feeds contracts, auction lots and preclusive denial, and is never shown as a number (shown as bands: "a few months' output", "a war chest").
- **Stances** become how surplus flows: *Open* (vanilla market), *Contracts first* (surplus goes to Held, and contracts draw from Held), *Withhold* (Held accumulates and nothing is sold).
- **Decay and a cap** stop banking: Held stock loses a few percent a month (storage, spoilage, theft) and is capped at a few months of production. Hoarding cheap 1936 tungsten for a 1942 auction is possible but costly, which is exactly the speculator's gamble Neon wanted.
- **Deny list:** naming a buyer applies a trade-only opinion modifier (`trade = yes`) that steers vanilla trade away from them. This is the rationing weapon.
- **Sol's counterweight:** every denied buyer with real desperation spawns a Situation of its own (develop a concession elsewhere, synthetic substitutes, pressure a host). Holding a monopoly is a defensive game.

### S6. The UI map: three reviewers, one surface

- **Trade Desk:** attach with `parent_window_token = trade_tab`. This token exists (`common/scripted_guis/_documentation.md`, the token list around line 32). Players already open the trade screen to think about resources, so the Desk lives where the question is asked. This beats a free-floating window or a top-bar launcher.
- **Alert strip:** `parent_window_token = top_bar` (Neon), with **one row per live Situation**, showing the next response date (Sol). Bids, breaches and replies update the same row.
- **Dossier:** `context_type = diplomacy_target_context` (Neon), so it opens on the country the player has selected.
- **Bilateral actions:** scripted diplomatic actions (mine). They appear in that same diplomacy panel, so Neon's "one seamless screen" and my native AI and multiplayer pipe are the same surface. `receive_scripted_gui` is the Holder-seat screen.
- **Decisions:** timed missions only (Neon): ultimatum deadlines, construction, repayment schedules. The decision timer is vanilla's best countdown widget.
- **Map mode** (Neon): live Situations, concessions and Committed Forces drawn on the map.

R56 overrides `countrydiplomacyview.gui`, so both `diplomacy_target_context` and the scripted diplomatic action buttons need a Phase 0 render test under R56 plus the UI mods.

### S7. Quarantine AI: `naval_dominance` in peace, `naval_blockade` in war

All three converged on a mod-owned quarantine checked with `has_naval_control`. I proposed driving AI fleets with the `naval_blockade` AI strategy, and Neon proposed `naval_dominance` (both are in `common/ai_strategy/_documentation.md`, lines 673 and 695). Neon is probably right for peacetime. A blockade-type strategy plausibly drives raiding missions that need a war, while dominance just puts the fleet in the region and holds control, which is what a quarantine needs. I am guessing either way: Phase 0 should test both in peacetime. The working assumption is `naval_dominance` while at peace and `naval_blockade` only once at war.

### S8. Nationalization settlement

Sol is right that the design's Demand Repayment (locking the host's factories) gives the victim nothing. Combine Sol's settlement menu with real transfers:
- **Staged compensation:** `cic_to_target_factor` toward the victim for a term, or `add_cic`, as Neon suggested, for lump sums.
- **Settlement in kind:** the host completes a named project at its own expense for the victim (a refinery or a port upgrade), or sells the nationalized output to the victim below market for a term. This is the Mexican 1940 to 1942 settlement pattern, and it is the most interesting option because it keeps the relationship alive.
- **Carry disputes forward once** (Sol): a single nationalization produces a single grievance and at most one war justification.

---

## 2. Building on others

### B1. Conditional contracts (from Sol's "protection as a commercial counteroffer")

This is the most important new mechanic of round 2. Sol's patron offers a **reserved agreement that activates only if the target refuses the demand**: "If Berlin cuts you off, London buys your output." Pushed further:
- It is the Patron seat's main move, and it is what makes the Holder seat winnable. The coercer sees it directly as a holdout reason: "London has promised to buy the unused output."
- It gives the Claimant real counterplay without a war: outbid the pledge, pressure the patron to withdraw it, or **make the pledge undeliverable**. A quarantine of the target's sea approaches puts the pledged deal into Suspended, and the holdout reason weakens. Quarantine, patron pledges and the contract lifecycle meet in one chain.
- It costs the patron something real: if the pledge triggers, the patron must take delivery and pay, possibly for ore it does not need. Pledging carelessly is how a patron gets dragged into a dispute, which is historically right.
- Build: a contract record with `state = reserved` and a trigger condition naming the demand ID, so no new system is needed.

### B2. Seller-written auctions, made concrete by Portugal's two states (from Sol)

Sol proposed that the seller writes the lots: exclusive supply, a split award, or a bridge contract. Vanilla Portugal makes this concrete: tungsten sits in two named states, Guarda (95, `history/states/181-Guarda.txt`) and Lisbon (32, `history/states/112-Lisbon.txt`). A split award is therefore a real map choice: Guarda to Berlin, Lisbon to London, or the reverse. That is what Salazar actually did, playing both sides until the June 1944 embargo. Pushed further:
- Buyers bid with term cards (tranches, a clearing subsidy, a project, a pledge to buy surplus).
- An **exclusivity clause** in the winning bid creates a future breach Situation if the seller later sells to the other side, which is the source of the drama.
- The auction stops being a window and becomes the Holder seat's signature move in any Situation where two Claimants compete.

### B3. Timed clauses as the master fig leaf (from Sol's Burma Road precedent)

Sol's 90-day route closure generalizes: **any demand can be accepted as temporary**, with a default reversion date.
- "Temporary" is the strongest face-saver in the game, so it is the natural exit from Cornered.
- The reversion date is a scheduled second decision (renew, let it lapse, or escalate). That is content the world generates for free.
- It replaces my "recently humiliated" timer as the main answer to coercion cycling: re-demanding before expiry breaks the temporary deal, which costs Credibility.

### B4. Rights reconciliation, both directions (from Neon)

Neon's periodic check of tracked rights against `has_resources_rights` should also **adopt** rights that vanilla or R56 content grants (Persia, Iraq and Mexico focus chains) into the ledger as concessions. Then a rights change made by any focus, in any playset, becomes mod content. Sol's "import historical rights only when the playset grants them" falls out of the same pass. See D4 for classifying removals correctly.

### B5. Coal as the quiet weapon (from Neon)

Coal matters for more than completeness. Energy shortfall degrades all of a country's factories gradually through `energy_ratio` instead of idling one production line, so a coal cutoff is the ideal **back-channel** tool: it hurts everywhere, nobody sees a fleet, and a proud dictatorship can concede it quietly. Two anchors come with it: Italy's coal (the March 1940 Rotterdam colliers, with Germany switching to the Brenner railway) and the Swedish coal-for-ore barter. The Italian coal crisis is also the best showcase for rail corridors whenever those get built.

### B6. Dependency is a pair (from Sol)

Sol's "dependence runs both ways" is the right shape for 6.13. Track two values per pair: their reliance on you as a buyer and your reliance on them as a supplier. Germany's Balkan clearing system trapped the Balkans and Germany alike, since Germany needed Romanian oil. Cashing in dependency is then a gamble on which side needs the other more. With the Neon subsidy (S2), dependency gets a native accelerator: every unspent clearing subsidy raises the receiver's reliance on the payer.

### B7. Intel buys warning time (my P5, reshaped by Neon's legibility point)

Neon's point that the readout must explain cause makes my "Strained?" low-intel display look wrong: a question mark is frustrating, not fun. Better: everyone sees the state and the top reason. Intel (`civilian_intel`) adds the *second and third* reasons and, more importantly, **advance warning of Cornered**. With good intel you see "Cornered in about three weeks at this pace," so intel becomes the instrument that lets you push closer to the edge. That gives La Résistance agencies a strong peacetime job.

---

## 3. Changing my mind

**Concede to Neon:**
- The seller-side delivery modifier is `country_resource_cost_<res>`, not a negative `country_resource_<res>`. Verified (S2).
- `add_equipment_subsidy` replaces my hidden clearing-balance variable (my N5). Native beats custom.
- AI quarantine fleets use `naval_dominance` in peacetime (S7).
- A top-bar alert is feasible without overriding `topbar.gui` (`parent_window_token = top_bar`). My round 1 "optional, skip if it needs an override" undersold it.

**Concede to Sol:**
- My review was written from the coercer's chair, and that is its biggest flaw. N12, "playing the target," was an afterthought in round 1. It is now the ship gate for every Situation (S1).
- Tranches and the Suspended state replace the design's breach penalties, which I had left in place.
- My plan only locked the host's factories under Demand Repayment. Sol's settlement menu is better (S8).

**Drop or demote from my round 1:**
- **Navicerts (N4):** move to the wartime phase. It is deep, UK-centric content, not slice material.
- **Smuggling (N6):** wartime phase, after the Held pool exists to supply middlemen.
- **"Strained?" low-intel display:** replaced by B7.
- **"Recently humiliated" timer as the main anti-cycling rule:** demoted behind timed clauses (B3). Keep it as a short secondary timer.

**Strengthen:**
- **Bands over CFE (P10).** With the slice in view, I would go further: the slice needs bands for five item types (resource flows, PP flows, licenses, equipment tranches, named-state leases) and nothing else.
- **Kill most of 6.3 (the net-margin default market).** It is the most expensive system to build and the least visible to the player. Vanilla auto-import plus trade-only opinion nudges from contracts, the Deny list and reputations deliver 90% of its value. Sol made the same call ("keep vanilla auto-import as the ordinary lane").

---

## 4. My design, end to end

### 4.1 The core loop at three timescales

| Scale | What the player does | Where |
|---|---|---|
| **Glance (monthly, 30 seconds)** | Read the market report ("Tungsten: frantic, German buying. Coal: tight.") and the alert strip. Nothing demands action unless a Situation is live in one of your seats. | Trade Desk header, alert strip |
| **Situation (2 to 6 months)** | Choose your seat's moves: back channel or public, commit a force, offer or pledge a contract, write lots, offer a fig leaf, or walk away. Spend PP, command power, committed forces and contract capacity. | Dossier, diplomatic actions, decision timers |
| **Campaign (years)** | Manage the portfolio: concessions and their nationalization risk, dependency pairs, Reliability, Credibility, regional Alarm, renewals coming due, and earned Standings. | Trade Desk, map mode |

The glance layer keeps the default low-micro. The Situation layer is where all decisions live. The campaign layer is what makes 1941 different from 1937.

### 4.2 The systems that matter, ranked

1. **Situations:** three seats, one prize, one deadline. A generator ("desperate buyer + scarce seller + rival") plus 8 to 12 historical anchors with dynamic triggers and fallback dates.
2. **The Agreements ledger:** mod-owned flows, tranches, lifecycle states, conditional (reserved) agreements, timed clauses. The ledger is the source of truth.
3. **Demands and pressure:** channels, quiet and loud tags with leaking, Committed Forces with the force-only cap, a two-list readout with deltas, the Cornered state, fig leaves.
4. **Rights and concessions:** named-state leases, two-way reconciliation, nationalization with a settlement menu.
5. **The Held pool and Market Stance:** the low-micro monopoly layer, the Deny list, the monthly market report.
6. **Reputations:** Reliability, Credibility, and a regional **Alarm** (Neon's "Economic Predator" scoped by region, see D1).
7. **Standings:** the campaign's milestones (see D2).

Later phases: route investments, the Quarantine at full depth, preclusive buying, smuggling, navicerts, AI-initiated coercion beyond the anchors.

### 4.3 First playable slice: "The Wolfram Question"

**Trigger:** Germany's tungsten deficit is high and its largest supplier is cut off (China at war with Japan), or a fallback date of 1 January 1938. This is historically right: Chinese tungsten reached Germany until the 1937 war, and the scramble for Iberian wolfram followed.

**Prize:** the tungsten of Guarda (95) and Lisbon (32), as named-state leases. These are the vanilla values; R56 replaces state history (Sol verified this in its descriptor), so recheck under the playset.

**Seats:** Germany (Claimant), Portugal (Holder), United Kingdom (Patron, with the Anglo-Portuguese alliance as its holdout card). All three are playable, and the AI fills the other two.

**Systems exercised (and nothing else):**
- **Back-channel offer:** a lease on Guarda paid in a clearing subsidy (`add_equipment_subsidy`, seller Germany) with a licence tranche.
- **Public demand:** Germany commits a surface squadron to the Atlantic regions off Lisbon. Pressure ramps, stops at Wavering, and the demand leaks public if Germany adds an embargo.
- **Patron pledge:** the UK posts a reserved agreement to buy Portugal's output if Portugal refuses. The coercer sees "London has promised to buy the unused output."
- **Seller-written lots:** Portugal opens a split auction (Guarda / Lisbon / exclusive / bridge).
- **Cornered and fig leaves:** Portugal's breaking point is not war but invoking the alliance, which drags the UK in and hands Germany a Credibility choice.
- **Outcome and renewal:** the lease runs one year, and expiry is the second act (renew, outbid, or lose it).
- **Reputations:** Reliability and Credibility move and are visible through other mouths ("Lisbon doubts Berlin would really embargo").

**Excluded:** the net-margin market, investments, Quarantine (beyond the Committed Force), Held pool decay, AI-to-AI generation, coal. Each is either not needed to prove the loop or provable later.

**What the slice proves (pass criteria):**
1. Each seat wins at least once across a set of playtests, and the Holder can win without the UK's pledge in at least one line.
2. Every player move changes the readout, with a stated cause.
3. The whole Situation produces at most one alert row and one resolution popup.
4. An all-AI run reaches a plausible historical-looking outcome (a split, or a lease to Germany, with British grievance).
5. Contract flows survive save and reload, and a capitulation or tag switch, with clean cleanup.

**Slices 2 and 3**, each chosen to prove a different axis:
- **Romanian Oil (1938 to 1940):** concessions held by foreign companies, the Iron Guard as an ideology-drift Situation, land-power coercion (Germany has no Black Sea navy, so its pressure is border posture and dependency), nationalization and settlement. This proves coercion without ships.
- **Mexico Expropriates (1938):** nationalization, Quarantine at full depth, the democratic pretext rule (D1), and the Good Neighbor choice for the USA. This proves the top rungs of the ladder.

---

## 5. Disagreements, each with the alternative

### D1. Neon: democracies cannot launch loud coercion against a target with no world tension unless they have a casus

A hard lock is a greyed-out button, which works against "decisions, not buttons." It also erases real history: the 1930s democracies did lean on Latin American and Middle Eastern states, just with pretexts.

**Alternative: a pretext economy.** Pretexts come from Situations: nationalization, a breached contract, mistreated nationals, a seized ship. A democracy with a pretext coerces loudly at normal cost. Without one it may still go loud, but it pays stability and war support, and the target gains an automatic rally reason ("Washington's threats have united the country"). Neon's 1936 farming concern is answered structurally instead, by the force-only cap (S4), by Committed Forces being single-use, and by **regional Alarm**: Neon's "Economic Predator" scoped by region, so bullying Venezuela alarms Washington but not Ankara.

### D2. Neon: hegemony milestones with percentage thresholds and a hegemon national spirit

"Control 40% of global extraction" gives the player a number to grind toward, which is the spreadsheet anti-goal. A stat-buff spirit as the reward is a passive buff disguised as content, the design's other anti-goal.

**Alternative: Standings that grant options, earned through Situation outcomes** (Sol's story-shaped milestones carrying Neon's ambition). Examples:
- **Honest Broker:** resolved three Situations as Patron without breaching. You can now mediate other powers' Situations as a neutral seat and take a commission flow.
- **Master of the Wolfram Trade:** held the decisive Holder seat through a renewal against two Claimants. You can now call a Producers' Conference, a cartel Situation with every other producer of that resource.
- **The Concessionaire:** held concessions in four countries through a nationalization wave. Hosts now accept settlement-in-kind more readily.
- **Arsenal of Neutrality:** stayed out of the war while supplying both blocs through 1943. Both blocs must use back channels with you, since loud demands cost them double.

Each one is a new verb, never a percentage. Standings are recorded with a one-paragraph account of how they were earned (Sol), which also gives the player the "Economic Victory" moment Neon asked for.

### D3. Neon: "Withheld" spikes global scarcity

Vanilla's price is fixed, so withholding raises no price. It only matters inside the mod's desperation model. Left as a standalone stance, Withhold is also a free banking exploit. **Alternative:** the unified Held pool with decay and a cap (S5). Withholding then has a real cost and a real use: a war chest that becomes auction lots when buyers are desperate.

### D4. Neon: every vanished right is an external nationalization

This misfires on peace deals, puppeting, friendly state transfers, and states whose resource drops to zero (where `has_resources_rights` returns false, as Sol and Neon both noted). False nationalizations would generate bogus grievances and war justifications. **Alternative:** classify the cause in order. An owner change (`on_state_control_changed`) produces a Concession Fate Situation (Neon's own good idea). War between holder and host suspends the right. A state with zero resources means a paused, depleted mine (Sol). Only a vanished right with none of these causes counts as nationalization.

### D5. Sol: AI declares war only with a military plan and an expectation of support or survival

This is a good default, but it rules out the design's own precedents. Japan in 1941 had no credible expectation of survival in a long war; it went to war because the embargo left it nothing to lose. **Alternative:** two routes to war. The *calculated* route is Sol's rule. The *desperate* route opens when the target's desperation for an embargoed resource crosses a runway threshold (fuel days, oil deficit relative to consumption). Both always pass through a visible Cornered state, so the player is never blindsided, and the desperate route is the one a reckless embargo invites.

### D6. Sol: a non-committal agreement built around an observed import

Exporter-level delivery is not measurable: there is no pairwise trade trigger or variable (verified in round 1, `dynamic_variables_documentation.md` lines 783 to 787, aggregates only). That branch cannot be built. **Alternative:** every agreement is a mod flow, including the "light" non-committal ones. Vanilla trade stays the anonymous background, shown in the dossier only as the target's aggregate import reliance.

### D7. Neon: Brokered pulls half the surplus off the market via `country_resource_cost`

As written, the removed resource disappears unless a contract happens to take it, which wastes output. **Alternative:** same modifier, but the removed amount accrues into the Held pool (S5), so nothing is lost and contracts draw from a real stock.

---

## 6. Engine notes added this round

| Finding | Source | Consequence |
|---|---|---|
| `country_resource_cost_<res>` is "<Resource> Consumption" and is driven by variables in vanilla | `localisation/english/modifiers_l_english.yml` 1413 to 1414; `common/decisions/INS.txt` 2347; `common/dynamic_modifiers/TAOG_dynamic_modifiers.txt` 95 to 96 | Seller-side contract delivery and the Held pool use this, with vanilla precedent |
| `trade_tab` is a valid `parent_window_token` | `common/scripted_guis/_documentation.md` (token list, about line 32) | The Trade Desk attaches to the vanilla trade screen, with no override |
| `add_equipment_subsidy` takes `cic`, `equipment_type`, and `seller_tags` or `seller_trigger` | `documentation/effects_documentation.md` 1234 | Clearing credit is native (S2) |
| `naval_dominance` and `naval_blockade` AI strategies both take a region id | `common/ai_strategy/_documentation.md` 673, 695 | Test both in peacetime, and default to dominance (S7) |
| `EMBARGO_THREAT_THRESHOLD = 30` (Neon's finding, confirmed) | `common/defines/00_defines.lua` 272 | The vanilla embargo *diplomatic action* is gated like the blockade. Phase 0 must test whether the `send_embargo` *effect* bypasses it. If it does not, the escalation ladder's rung 2 must also be mod-owned. |
| Portuguese tungsten: Guarda 95, Lisbon 32. Spanish: León 10, Salamanca 10, Valladolid 10, Extremadura 4 | `history/states/181-Guarda.txt`, `112-Lisbon.txt`, `174-Leon.txt`, `788-Salamanca.txt`, `791-Valladolid.txt`, `170-Extremadura.txt` | Named-state lots for the slice. R56 replaces state history, so recheck there. |

---

## 7. Recommended decisions for the lead

1. **Adopt the three-seat Situation as the mod's core loop**, with "the Holder can win" as the ship gate for every template.
2. **Adopt the combined Agreements ledger:** `country_resource_cost` / `country_resource` flows, tranches, Sol's lifecycle states, reserved (conditional) agreements, timed clauses, and `add_equipment_subsidy` for clearing credit.
3. **Adopt the combined pressure model:** one demand, one deadline; channel choice; quiet and loud tags with leaking; Committed Forces with the force-only cap at Wavering; the two-list readout with deltas; a visible Cornered state.
4. **Cut the net-margin default market (6.3) to trade-only opinion nudges**, and replace monopoly, stance and reserves with the single Held pool.
5. **Build "The Wolfram Question" as the first slice**, playable from all three seats, after a Phase 0 that adds these tests: the `send_embargo` threshold, `naval_dominance` versus `naval_blockade` in peacetime, `trade_tab` and `diplomacy_target_context` rendering under R56, and survival of `country_resource_cost` flows across save and reload.
