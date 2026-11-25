# Power Without War: Design Document (v2)

Working title. A Hearts of Iron IV (v1.20 "Operation Postern") mod.

Status: v2, revised after a two-round council review (Claude Opus 5.5, GPT-6.2 Sol, Gemini 4 Neon), 2026-11-25. Reviews are in `docs/design/council/`. Section 13 records what changed and why.

## 1. Intent

HoI4 is excellent while you are fighting and dull while you are not. This mod makes the non-combat game a real game: becoming rich and powerful through trade, resources, logistics, and coercion, without going to war.

Two halves of one fantasy:

1. **The trade empire.** Corner markets, sign contracts, lease mines, invest in routes, profit from the war's hunger for oil and metal, and turn that into factories, technology, equipment, and influence.
2. **Power without war.** Use military and economic weight without firing a shot. Squeeze a country until giving you its oil fields is the least bad option, then pull your ships back and collect for years. Or play the other side: the small neutral surviving between giants, or the patron who spoils a rival's shakedown.

Historical grounding is a pillar: the Wolfram War, the Statutory List, Schacht's clearing agreements, the Soviet-Baltic pacts, Romanian oil-for-arms, the US embargo on Japan, the Mexican expropriation, the Burma Road closure, the Italian coal crisis of 1940.

## 2. Pillars

1. **Decisions, not buttons.** Every lever has a cost, a risk, and a counterplay.
2. **Physical, not financial.** No currency. Value is computed internally and never shown as a number.
3. **Legible fuzziness.** The player reads states and causes ("Strained → Wavering: your cruisers off Lisbon"), never scores.
4. **Hard but fair, from every seat.** Claimant, holder, and patron each have winning moves. No crisis is a meter.
5. **Alive but not noisy.** The world generates crises; the player sees only the few in their seats.
6. **Low micro by default.** Vanilla trade runs the background market. The mod's layer is deliberate and high-value.

## 3. Goals, non-goals, anti-goals

**Goals**
- A peaceful or neutral playthrough is a complete, gripping campaign from 1936 through 1945, and a warring power can finance itself through trade and coercion.
- Coercion short of war is a full toolkit with real escalation, risk, payoff, and counterplay.
- The player can sit in any seat of a crisis: coercer, target, or patron.
- Resource rights become the most valuable and contested asset in the world.
- The AI participates at a moderate level, and AIs stop tolerating absurd deficits.

**Non-goals**
- A currency or treasury.
- Rewriting or monitoring vanilla trade. It is the anonymous background market.
- A rival-seller AI economist.
- New map, new countries, or focus tree rewrites.

**Anti-goals**
- Spreadsheet play: grinding toward a number or reading a meter.
- Popup spam.
- Exploits: farmable negotiation, deal-and-run heists, coercion cycling, teleporting demonstrations.
- Passive buffs disguised as content (including milestone rewards).
- Breaking or being broken by The Road to 56 and common UI mods.

## 4. Engine facts and constraints

Verified in the v1.20 install and the test playset unless marked "test".

**Trade engine.** Fixed price (`cic = 0.125`, 8 units per civilian factory). Seller choice driven by `NTrade` defines (opinion, distance, loyalty, anti-monopoly, party support). Player auto-import is new in v1.20 (`NTrade.AUTO_IMPORT_*`). The AI cancels trades delivering under 80% (`NAI.MIN_DELIVERED_TRADE_FRACTION = 0.8`). **There is no pairwise trade trigger or variable**: only country aggregates (`resource_exported@X`, `resource_imported@X`, `resource@X`, `resource_produced@X`, `resource_consumed@X`). `create_import` exists (used once, in German start history) but nothing can observe or check it. **Consequence: the mod never builds on or monitors vanilla trade relationships.**

**Seven resources.** oil, aluminium, rubber, tungsten, steel, chromium, **coal**. Coal feeds the energy system (`RESOURCE_TO_ENERGY_COEFFICIENT = 9.0`; `energy_ratio`; `ENERGY_SCALE_PER_TRADE_FACTORY_EXPORT = 0.25`, so export-trade factories raise energy cost).

**Mod-owned resource and factory flows (the contract substrate).**
- `country_resource_cost_<res>` (seller; localised "<Resource> Consumption") and `country_resource_<res>` (buyer), both variable-driven inside dynamic modifiers, with vanilla precedent (`common/decisions/INS.txt:2347`, `common/dynamic_modifiers/TAOG_dynamic_modifiers.txt:95-96`, `wuw_dynamic_modifiers.txt:915`).
- `civilian_factory_use` (payer), `add_offsite_building` and `cic_to_target_factor` (receiver; the latter verified inside `targeted_modifier`, `common/decisions/SWI.txt`).
- Equipment: `send_equipment`, `add_equipment_subsidy` (with `seller_tags`), `create_production_license`, `add_tech_bonus`, `set_technology`, `create_purchase_contract` (no vanilla usage; test).
- Test: whether a seller-side `country_resource_cost` actually removes supply from the seller's exportable pool or only raises its consumption.

**Resource rights.** `give_resource_rights` (filterable by resource), `remove_resource_rights` (state-scoped; strips all of the holder's rights in that state), `has_resources_rights` (false if the state has no resource). Vanilla grants a few at start via on_actions (UK and USA in Mexico, UK in Iraq, Italy in Albania, Japan in North Sakhalin) and flips them via focuses and events. Peace conferences already grant timed rights for 1,825 days (`NPeace.PEACE_TIMED_EFFECT_LENGTH_RESOURCE_RIGHTS`). Test: whether rights deliveries use convoys.

**Blockade and embargo.** The vanilla blockade diplomatic action requires the target to have generated 15 world tension; the embargo action requires 30 (`EMBARGO_THREAT_THRESHOLD`). Typical coercion targets generate none. No blockade trigger, effect, or on_action exists. `send_embargo` exists as an effect (test: whether it bypasses the threshold). AI strategies `naval_dominance` and `naval_blockade` both take a region and can be added from script.

**Presence detection.** `ships_in_area` (region, own ships; test: ships in port), `ships_in_state_ports`, `has_naval_control` and `has_enemy_naval_control` (region; includes friendly forces), `naval_strength_ratio`, `num_planes_stationed_in_regions` (based planes only, not missions), `divisions_in_border_state`, `num_divisions_in_states`, `convoy_threat`, `civilian_intel`, `network_strength`.

**Interaction surfaces.**
- `common/scripted_diplomatic_actions`: custom diplomatic actions with a sender GUI, a receiver GUI, `ai_desire`, `ai_acceptance`, PP and CP costs, sent, complete, and reject effects. Used by Kaiserreich and others.
- Scripted GUI attachment without overriding vanilla files: `parent_window_token = trade_tab`, `top_bar`, `selected_country_view_diplomacy` with `context_type = diplomacy_target_context`. Mandatory `dirty` variables to avoid per-tick re-evaluation.
- `common/map_modes` supports additive scripted map modes.
- Trade-only opinion modifiers (`trade = yes`) steer vanilla trade without touching diplomatic opinion.
- Lifecycle on_actions: `on_state_control_changed`, `on_annex`, `on_capitulation`, `on_civil_war_end`, `on_ruling_party_change`, `on_government_change`. No trade-related on_actions; everything polls.

**Road to 56 (test playset).** Replaces `history/states` (1,143 states vs 1,081) and `map/strategicregions` (298 vs 304; region 279 is Gulf of Bothnia in vanilla and Rio Grande do Norte in R56). Doubles opinion range to ±200. No `NTrade`, `NMarket`, or blockade define overrides. **Consequence: no hardcoded state or region IDs; resolve at startup.**

## 5. Approach

Chosen by the user: hybrid UI leaning toward custom screens. Refined by the council into a lean surface (section 9): native scripted diplomatic actions for every bilateral interaction, two custom GUIs (Trade Desk, Dossier), a top-bar alert strip, decisions only for countdowns. Build order is vertical: prove one complete crisis before widening (section 12).

## 6. Core loop: Situations

The mod's spine. A **Situation** is a contested prize with three seats and a clock.

- **Prize:** exactly one: named states' output, a named route, a named flow, a base, a closure.
- **Seats:**
  - **Claimant:** wants the prize.
  - **Holder:** owns it and decides who gets it.
  - **Patron:** a third power with a stake, who can underwrite the holder, compete, or stay out.
- **Clock:** one decision date. Each seat has at least one decisive move before it.
- The player can occupy any seat; AI fills the rest.
- **Noise cap:** at most 2 to 4 Situations live in the player's seats. More run in the background between AIs.

**Sources:**
- **Historical anchors** (8 to 12) with dynamic triggers and fallback dates. Examples: the Wolfram Question (Iberia), Schacht's Balkan clearing, Mexico expropriates, Romanian oil, Swedish ore and the Narvik question, the Italian coal lifeline, the Burma Road, Japan's oil clock, the Baltic pacts.
- **A generator:** desperate buyer plus scarce seller plus rival; an expiring lease; a nationalization; a big oil strike.
- **Chains (later phase):** outcomes spawn successor Situations 6 to 18 months later (a won wolfram auction leads to "Spanish re-exports to Berlin").

**Ship gate:** no Situation template ships until a human Holder can win it in playtest without outside help, by stalling, splitting, finding a patron, or a smaller concession.

**Timescales:**

| Scale | Player activity |
|---|---|
| Glance (monthly, 30 seconds) | Read the market report and the alert strip. Nothing demands action unless a Situation is live in your seat. |
| Situation (2 to 6 months) | Choose your seat's moves: channel, committed force, offers, pledges, lots, fig leaves, walking away. |
| Campaign (years) | Manage concessions and nationalization risk, dependency pairs, reputations, renewals, Standings. |

## 7. Systems

### 7.1 Valuation (hidden, banded)

Items are valued in civilian-factory-equivalents internally, but only resources and civilian-factory flows get precise values. Everything else maps to a **band** (Trivial, Small, Fair, Large, Huge) via short rule tables. Examples: tech band from years behind times wishlist match; equipment band from shortage times obsolescence. Resource values drift with world desperation, so 1936 and 1942 differ sharply. Players only ever see bands and words.

### 7.2 Desperation (hidden, per country per resource)

Computed from deficit relative to consumption, duration of the deficit, fuel runway, idle military factories, war status, and recent supply losses. Lumpy or short deficits are filtered out. Drives offers, acceptance, bidding, escalation, and the AI desperation ladder (7.13). Coal desperation reads `energy_ratio`.

### 7.3 Agreements ledger

The mod owns every agreement. The ledger is the source of truth.

**Vehicles**
- **Supply agreement:** flexible quantity of one resource. Seller gets `country_resource_cost_<res>`, buyer gets `country_resource_<res>`, sized by variables.
- **Named-state lease:** `give_resource_rights` on named states. One mod lease per (holder, state); skip states where that holder already holds a vanilla right. Map-visible, prestigious, high nationalization exposure. This is also the monopoly vehicle: leasing every producer of a resource makes you its seller.

**Payments**
- **Flows:** civilian factories (`civilian_factory_use` on the payer; `add_offsite_building` or `cic_to_target_factor` to the receiver), political power per day (matched debit and credit), ideology influence per day (capped at 0.01 to 0.03 per day and scaled down near the giver's elections).
- **Irreversible items in tranches:** equipment (`send_equipment`), licenses (`create_production_license`), tech bonuses (`add_tech_bonus`), full tech (`set_technology`, final tranche of mega-deals only, never ahead of time, prerequisites required). First tranche on signing, more after service, last at a late milestone. Nothing irreversible is fully paid on day one.
- **Clearing credit:** `add_equipment_subsidy` with the payer as the only seller. The receiver can only spend it on the payer's arms. This is Schacht's mechanism, native.

**Contract types (user design, preserved)**
- **Non-committal:** flows only; either side may end it any time.
- **Committal:** fixed term up to 5 years; may include tranched irreversible items and leases.

**Lifecycle states**
- **Active.**
- **Suspended:** deliveries and payments pause, with a dated window to reroute, reduce, or find protection. Caused by third-party quarantine, occupation of a route, or a provisional suspension.
- **Completed / Renewed.**
- **Terminated:** clean end (capitulation, civil war split, involuntary war, an unresolved suspension).
- **Defaulted:** a deliberate breach. The breaching party forfeits remaining tranches and loses Reliability. Starting a war to escape, or blockading your own counterparty through a friend, subject, or faction member, is a default.
- **Nationalized:** see 7.7.

**Special clauses**
- **Reserved (conditional) agreements:** activate only if a condition fires ("London buys your output if Berlin cuts you off"). The patron's main move.
- **Timed clauses:** any concession can be accepted as temporary with a reversion date, which creates a scheduled second decision.
- **Physical risk:** sea agreements hold convoys in escrow and check naval control on the route weekly. Raiding and quarantine reduce or suspend delivery.

**Validation:** every acceptance rechecks owner, availability, and terms, and applies once (no double awards from simultaneous or stale acceptances, including in multiplayer).

### 7.4 Offers, wishlist, and negotiation

- Desperate countries approach the player; cash-poor ones offer in kind. AI offers are sent through scripted diplomatic actions (`ai_desire`) only when the sender has a concrete reason (supply loss, expiry, patron commitment) and the seller has capacity.
- **Wishlist:** the player ranks what they need; offers lean toward it.
- **Negotiation is over terms, not sliders.** An offer is a bundle of term cards in bands (resource, amount band, duration, payment type, sweeteners). Maximum 3 counters, and the decision date still bites. Each reply reveals one concrete red line or hidden want ("rights are off the table, an output share is possible"). Asking for a red line spends patience; offering a hidden want restores it. Repeating an equivalent offer gets the same answer.
- Hidden values are seeded when talks open (no reroll by reloading).
- Political demands (influence, guarantees, ministers) are player-initiated only.
- **Popups only for consequential choices:** a threatened lease, an ultimatum, an imminent deadline that closes an option. Routine offers wait in the Desk.

### 7.5 The Held pool and market stance (the monopoly layer)

Per resource, a stance:
- **Open:** surplus flows to vanilla trade.
- **Contracts first:** surplus moves into a Held pool that agreements and auction lots draw from.
- **Withhold:** the Held pool accumulates and nothing is sold.

Moving surplus to Held applies `country_resource_cost_<res>` to the surplus (only when `resource@X > 0`) and accrues it. Held stock decays a few percent per month and is capped at a few months of output, so speculation is possible but costly. Shown only in bands ("a few months' output", "a war chest").

- **Deny list:** naming a buyer applies trade-only opinion penalties that steer vanilla trade away from them. This is rationing.
- **Preclusive buying (later phase):** buy output you do not need, purely to deny it to a named enemy.
- **Counterweight:** every denied, desperate buyer spawns its own Situation (develop elsewhere, substitute, pressure a host). Holding a monopoly is a defensive game.

### 7.6 Resource rights

- Historical starting concessions are permanent; hosts are trapped and seek escape through content.
- All other rights are leases (up to 5 years), including war-won rights, which align with vanilla's 1,825-day peace rights. Expiry is a renegotiation moment where rivals can outbid.
- **Reconciliation, both directions:** a periodic check adopts rights granted by vanilla or R56 content into the ledger, and classifies vanished rights by cause, in order:
  1. Owner change (a Concession Fate Situation: the new owner honors or seizes).
  2. War between holder and host (suspend).
  3. Depleted state (pause).
  4. Otherwise, nationalization.
- **Concession gambles (later phase):** a new concession rolls a seeded output band at completion; rare big strikes (Dammam No. 7, Burgan) spawn rival bids and nationalization pressure.

### 7.7 Nationalization

- The host can seize investments and rights; the AI is weighted against it and pushed toward it by ideology change, resentment, desperation, and relations.
- The victim jumps up the escalation ladder: an immediate embargo is available, quarantine conditions ease, and **Demand Settlement** opens.
- **Settlement options for the host:**
  - **Staged compensation:** factories toward the victim via `cic_to_target_factor` for a term.
  - **Settlement in kind:** the host completes a named project for the victim, or sells the nationalized output to the victim below market for a term (the Mexican 1940 to 1942 pattern).
  - **Reversal:** cancel the nationalization at a stability and political power cost.
  - **Refusal:** escalation, and a war justification for the victim.
- One nationalization produces one grievance and at most one war justification.
- Symmetric between AIs.

### 7.8 Coercion

**The unit is a demand.** One named demand, one decision date. Pressure is built for that demand.

**Channel, chosen per demand:**
- **Back channel (quiet):** lower ceiling, no pride penalty, lets dictatorships concede quietly, the target can stall.
- **Public ultimatum (loud):** higher ceiling, Credibility at stake, triggers the democratic rally effect, alerts patrons.
- **Loud tools leak:** using a loud pressure source during a back-channel demand forces it public after a short delay.

**Pressure sources, each tagged quiet or loud:**
- **Quiet:** dependency, single-resource cutoffs (including coal against energy-poor targets), subsidy withdrawal, market access withdrawal, envoy leverage.
- **Loud:** naval demonstration, air demonstration, border posture, embargo, "Join our embargo", quarantine.

**Committed Forces:** a named fleet, air group, or army group is assigned to one demand. Pressure ramps over 30 to 60 days, costs fuel and command power upkeep, and counts for no other demand. Air demonstrations need planes based in nearby regions, so the coercer may first need air base access from a neighbor. **Force alone tops out at Wavering**: folding requires at least one non-force lever (cutting alternatives, dependency, a patron backing down, a fig leaf).

**Resistance:** allies, guarantees, patron pledges, alternatives, pride (stability, war support, ideology), regime constraint (dictatorships resist public humiliation; democracies harden as pressure becomes visible), demand size and humiliation, and recent humiliation.

**Target states (shown):** Defiant, Strained, Wavering, Cornered, Ready to fold.
- Every change shows its cause.
- The readout has two lists: "working for you" and "why they are holding out", with the top reason in each always shown.
- **Cornered** is the visible stage before a breaking point, where the campaign's best decision lives: push, take less, or offer a fig leaf.
- Intel (`civilian_intel`) reveals the second and third reasons and gives advance warning of Cornered ("Cornered in about three weeks at this pace").

**Target moves (AI and human, via the receiver GUI):** fold; offer a smaller named lot; accept a 90-day provisional suspension; offer a fig leaf of its own; call a patron; harden and mobilize.

**Fig leaves:** face-saving sweeteners (token purchase, joint commission, public assurance, "temporary") that cut humiliation for a small cost. Temporary acceptance is the master fig leaf, and re-demanding before it expires breaks it and costs Credibility.

**Routes to war, always through a visible Cornered:**
- **Calculated:** the target has a military plan and expects support or survival.
- **Desperate:** desperation for an embargoed resource crosses a runway threshold (the Japan 1941 route).
- Refusal or expiry alone never fires a war.

**Cost and guardrails:**
- Political power, command power, fuel, world tension, third-party opinion.
- **Regional Alarm:** bullying in a region makes that region's majors guarantee and intervene more readily.
- **Pretexts for democracies:** a democracy with a pretext (nationalization, breach, a seized ship) coerces at normal cost; without one it can still go loud, but pays stability and war support and hands the target a rally reason. No hard lock.

**Aftermath:** once accepted, forces can withdraw; the agreement runs its term.

### 7.9 Patrons

The patron seat is where democracies and rival majors play peacetime spoiler.
- **Commercial counteroffer:** a reserved agreement that activates if the target refuses ("London buys your unsold output"). It shows up for the claimant as a holdout reason.
- It costs the patron real factories or equipment if triggered, so patrons cannot backstop everyone. A claimant can open two crises in one patron's sphere to force a choice.
- **Claimant counterplay:** outbid the pledge, pressure the patron to withdraw, or make it undeliverable (quarantine suspends the pledged deal).

### 7.10 Auctions (seller-written)

When two or more claimants want a holder's output, the holder writes the lots:
- an exclusive lease;
- a split award (for Portugal, Guarda to one buyer and Lisbon to the other: what Salazar actually did);
- a short bridge contract.

Buyers bid once per lot with term cards. An exclusivity clause creates a future breach Situation if violated. Losing bidders react through the escalation ladder.

### 7.11 Escalation ladder

1. **Targeted cutoff:** suspend the mod agreements the dispute concerns.
2. **Embargo:** `send_embargo` if it bypasses the world-tension gate (test); otherwise a mod-owned embargo (all agreements suspended, trade-only opinion penalty).
3. **"Join our embargo":** a scripted diplomatic action asking named third parties to embargo the target by a deadline; compliance checked with `is_embargoing`. Credibility rises when you punish non-compliance, even at a Reliability cost.
4. **Quarantine** (mod-owned, after Roosevelt's 1937 speech): a declared action with PP upkeep. Each week, while the quarantiner holds naval control of the target's resolved sea approaches with its own committed ships, the target's exposed sea agreements are suspended and strangulation rises. Losing control lapses it. AI quarantiners get `naval_dominance` in peace (test against `naval_blockade`). The vanilla blockade action is left untouched.
5. **Casus belli:** sustained quarantine or embargo strangulation grants the victim a war justification via `create_wargoal`. Force majeure does not apply when the blockader is the counterparty, its subject, or a faction member.

### 7.12 Reputations and dependency

- **Reliability:** do you honor deals? Gain weighted by value times term, with diminishing returns per counterparty per year.
- **Credibility:** are your threats real?
- **Regional Alarm:** how predatory you look in each region.
- Reputations are shown only through other mouths ("Lisbon doubts Berlin would really embargo").
- **Dependency is a pair:** their reliance on you as a buyer, and your reliance on them as a supplier. Clearing credit raises the receiver's reliance. In war, an unredeemed clearing balance can flip into a grievance if the payer cannot deliver arms.

### 7.13 AI participation

- Situational priority: rich, resource-heavy, peaceful countries lean in; those arming for war rarely invest; those at war almost never.
- Each AI has a coercion budget (majors at most one active campaign, most minors zero).
- **Desperation ladder** for desperate AIs:
  1. Procure (send a contract proposal).
  2. Substitute (synthetic refinery build targets, cut production of the starved equipment).
  3. Rebalance or invest (trade law, foreign mine, corridor).
  4. Coerce (open a Situation against a weak producer).

### 7.14 Route investments (later phase)

Rail corridor, port terminal, pipeline, concession, as in v1. Construction locks the investor's own civilian factories for a period; the physical building appears in the host state on completion, after an ownership and consent check; large projects are staged so occupation leaves finished parts on the map. Payoff is delivered through the mod's agreements: lower convoy burden, and a corridor keeps eligible agreements running during sea interdiction. Whether vanilla routing uses new rail is a test; the design does not depend on it.

### 7.15 The wartime game and Standings

- **Neutral Tightrope:** once a world war starts, neutrals become the main prize. A neutral player sits as Holder in several Situations at once with both blocs as Claimants. Navicerts and smuggling arrive here (later phases).
- **Standings** replace milestone buffs. They are earned through Situation outcomes, recorded with a short account of how, and each grants a new option, never a stat. Examples:
  - **Honest Broker:** mediate other powers' Situations as a neutral seat.
  - **Master of the Wolfram Trade:** call a Producers' Conference.
  - **The Concessionaire:** hosts accept settlement in kind more readily.
  - **Arsenal of Neutrality:** both blocs must use back channels with you.

## 8. Map and ID resolution

- Never hardcode state or region IDs.
- At startup, resolve producing states, coastal states, ports, sea approaches, and air-basing regions from triggers (owner, resource, coastal, adjacency, continent).
- Where hand-authored sea chokepoints are unavoidable, keep a small verified set and an explicit Road to 56 mapping branch.
- Normalize opinion inputs to ±100 so formulas behave the same under R56's ±200.

## 9. UI surfaces

- **Scripted diplomatic actions** (diplomacy panel): Propose Agreement, Lease Rights, Issue Demand (quiet or public), Pledge Support, Declare Quarantine, Demand Settlement, Join Our Embargo. The sender GUI is the negotiation screen; the receiver GUI is the holder's response screen (human targets included).
- **Trade Desk** (scripted GUI on `trade_tab`): Situations board (one row per live Situation, showing outcome at stake, decision date, latest development), agreements ledger, Held pool and stances, wishlist, monthly market report in words ("Tungsten: frantic, German buying. Coal: tight.").
- **Dossier** (scripted GUI on `diplomacy_target_context`): the target's shortages, aggregate import reliance, mod-known agreements, rights, investments, readout lists, and Situation entry points.
- **Alert strip** (`top_bar`): one row per live Situation in the player's seats, updated in place.
- **Decisions:** countdowns only (deadlines, construction, settlement schedules).
- **Map mode** (later phase): live Situations, concessions, committed forces, desperation.
- All scripted GUIs use `dirty` variables. No vanilla GUI file is overwritten. All randomness happens in effects, never in GUI properties, and is seeded.

## 10. Compatibility

- Additive files only, with a unique prefix.
- One late-loading defines file, documented.
- Dynamic ID resolution and opinion normalization (section 8).
- Render tests of every surface under R56 (which overrides `countrydiplomacyview.gui`) plus common UI mods.

## 11. Performance

- Staggered evaluation: each country gets a tick bucket and roughly 2 to 3 countries are processed per day.
- Full bilateral evaluation is limited to 15 to 20 active traders.
- Desperation is computed only for countries with a filtered deficit or a live Situation.
- Fixed-index arrays per resource. No nested every_country on daily ticks.
- Benchmark late-game tick time against the same save without the mod.

## 12. Phasing

**Phase 0: engine spike (throwaway test mod).** Tests:
1. Seller `country_resource_cost` plus buyer `country_resource` flows: actual production, exportable supply, export laws, auto-import interaction, save and reload.
2. `civilian_factory_use` plus `add_offsite_building` (including removal) versus `cic_to_target_factor` in a dynamic modifier with `scope`.
3. Scripted diplomatic actions (sender and receiver GUIs, `ai_desire`) under R56's diplomacy view.
4. `send_equipment` tranches, `add_equipment_subsidy`, and `create_purchase_contract` with zero civilian factories.
5. `give_resource_rights` and removal: convoys, occupation, safe cleanup with one lease per (holder, state).
6. `ships_in_area` in port versus at sea; `has_naval_control`; `num_planes_stationed_in_regions`; AI `naval_dominance` versus `naval_blockade` in peacetime.
7. `send_embargo` against a target below the world-tension threshold.
8. `trade_tab`, `top_bar`, and `diplomacy_target_context` attachments with R56 and the UI playset.
9. Dynamic resolution of Portugal's tungsten states and sea approaches under vanilla and R56.

**Phase 1: "The Wolfram Question" (vertical slice).**
- **Trigger:** Germany's tungsten desperation after its Chinese supply is cut, or a 1 January 1938 fallback date.
- **Prize:** Portugal's tungsten states, resolved dynamically (vanilla: Guarda 95, Lisbon 32).
- **Seats:** Germany (Claimant), Portugal (Holder), United Kingdom (Patron, with the Anglo-Portuguese alliance). All three are playable.
- **Systems in the slice:** the agreements ledger (supply agreement, named-state lease, tranches, lifecycle, reserved agreements, timed clauses); back-channel offer with clearing credit; public demand with a committed squadron, ramp, and the Wavering cap; a leak on embargo; the patron pledge; seller-written split auction; Cornered and fig leaves; a one-year lease and its renewal; Reliability and Credibility; seven-resource schema; Trade Desk, Dossier, alert strip.
- **Pass criteria:**
  1. Each seat wins at least once across playtests, and the holder can win without the patron in at least one line.
  2. Every move changes the readout with a stated cause.
  3. One Situation produces at most one alert row and one resolution popup.
  4. An all-AI run reaches a plausible outcome.
  5. Agreements survive save and reload, capitulation, and tag switches, with no double awards.
  6. Works in vanilla and in the R56 playset.

**Phase 2:** Romanian Oil (land-power coercion: border posture and dependency, the Iron Guard, nationalization and settlement) and Mexico Expropriates (nationalization, full Quarantine, democratic pretexts, the Good Neighbor choice). Coal and the Italian coal crisis. Held pool decay, preclusive buying.

**Phase 3:** the Situation generator and chains, AI-to-AI Situations, route investments, concession gambles, map mode.

**Phase 4:** the wartime game: Neutral Tightrope, navicerts, smuggling, Standings.

## 13. Council decisions log

| Decision | Source | Reason |
|---|---|---|
| Situations with three seats as the core loop; the holder-can-win ship gate | Opus, Sol, Neon (merged by Opus) | v1 had sixteen systems and nothing to do on a quiet day; v1 coercion gave the target no winning move |
| Mod-owned agreements; never observe vanilla trade | All three | No pairwise trade visibility exists; contracts that die silently are the worst possible bug |
| Seller side uses `country_resource_cost_<res>` | Neon, confirmed by Opus | Vanilla precedent (Indonesian rubber) |
| Tranches; Suspended state; defaults forfeit tranches | Sol | v1 allowed sign, take tech, declare war, keep everything |
| Settlement menu replaces "lock the host's factories" | Sol | v1 repayment gave the victim nothing |
| Scripted diplomatic actions; two custom GUIs | Opus, adopted by Neon | Native AI, multiplayer, and human-as-target support; far less fragile UI |
| Mod-owned Quarantine | All three | Vanilla blockade and embargo actions are gated by world tension that typical targets never generate |
| Coal and energy | Opus, Neon | Seventh resource in v1.20; the best quiet weapon |
| One demand, one deadline; channel choice; loud leaks; committed forces with the Wavering cap | Sol, Opus, Neon | Stops "stack everything, click demand" and fleet teleport farming |
| Patron pledges as reserved agreements | Sol, extended by Opus and Neon | Gives democracies a peacetime game and the holder a way to win |
| Pretext economy instead of a democratic hard lock | Opus, Sol | A greyed-out button violates "decisions, not buttons" |
| Standings that grant options instead of percentage milestones and buff spirits | Opus, Sol | Percentage goals are grind; buff spirits are passive buffs |
| One Held pool with decay and cap | Opus (from Neon's stances and reserves) | Withholding otherwise raises no price and is a free banking exploit |
| Bands instead of full valuation; negotiation over term cards, seeded | Opus, adopted by Neon | Scope control; avoids slider play and save-scumming |
| Ideology drift capped at 0.01 to 0.03 per day | Opus | v1's 0.1 per day is about 36 points a year, enough to flip a minor in one contract |
| Dynamic ID resolution; opinion normalization | Neon, Sol | R56 replaces states and regions and doubles the opinion range |
| Two routes to war, always through Cornered | Opus | Sol's plan-only rule would exclude the Japan 1941 case |
| Vertical slice first | Sol, adopted by Opus and Neon | Horizontal phases hide whether the loop is fun |
| Net-margin default market reduced to trade-only opinion nudges | Opus, Sol | Pending user confirmation; see open questions |

## 14. Resolved questions

1. **The default market:** vanilla trade plus light nudges (trade-only opinion modifiers from agreements, the Deny list, and reputations). The designer confirmed this matches what was intended.
2. **Route investments:** Phase 3, at the lead's discretion.

## 15. Left to the builder

- Formulas and constants for desperation, pressure, resistance, patience, reputations, and band thresholds (tuned in playtests).
- GUI layouts and art.
- Variable and array structures.
- Which historical anchors and concessions beyond the slice, and their triggers.
