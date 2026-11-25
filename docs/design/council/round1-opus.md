# Council Review, Round 1: Claude Opus 5.5

Reviewer: `opus`. Design reviewed: `docs/design/2026-11-25-power-without-war-design.md` (draft, 2026-11-25).

The design has the right fantasy and the right pillars. Its biggest risk is not any single system failing. The risk is that the systems all work and the player still has nothing to *do* on a quiet Tuesday in March 1937 except open an inbox. Most of my fixes push the design toward fewer, sharper decisions that come out of a living world, and toward building on engine hooks I verified in the v1.20 files. Several of those hooks change what is feasible, mostly for the better (see section 4).

---

## 1. Problems and fixes (ranked by impact on fun)

### P1. There is no core loop, only a catalog of systems (whole document, especially 6.3 to 6.16)

**Why it matters.** Section 6 describes sixteen systems, but nothing says what the player is doing minute to minute or what makes 1937 feel different from 1936. Without a loop, the likely experience is: open the Trade Desk, accept the best offer, close it. That is the "spreadsheet simulator" anti-goal with nicer art. The coercion pillar has the same gap. Nothing tells the player *who* is worth squeezing *now* or *why now*.

**Fix: a Situations board as the spine of the mod.** The world generates a small number of contestable **Situations** (2 to 4 live at once for the player, more in the background). Each is a prize with a clock, interested rivals, and several levers that work on it. Examples:

- *"Iberian wolfram is up for grabs"* (1937+, Spanish Civil War, Portugal). Rivals: GER, ENG. Levers: contracts, preclusive buying, rights lease, pressure on Portugal.
- *"Romanian oil is wavering"* (triggers when Romania's ruling party support shifts or the Iron Guard grows). Levers: oil-for-arms in-kind deal, guarantee, dependency, coercion.
- *"Mexico expropriates"* (1938, or earlier when Mexican resentment crosses a threshold). Levers: Demand Repayment, embargo, accepting compensation (the Good Neighbor route), or quietly buying the nationalized oil yourself as a third party.
- *"Swedish iron ore: the Narvik question"* (when war is near). Levers: transit rights, preclusive buying, naval pressure off Norway.
- *"The Burma Road"* (when CHI is at war with JAP). Levers: coercion on ENG or FRA to close it, or paying them to keep it open.

Situations are where every system meets: valuation, desperation, contracts, coercion and AI rivals all point at the same prize, so the player chooses *which* tools fit. They resolve, leave consequences, and spawn the next situation. They are the "alive but not noisy" mechanism: noise is capped by the number of live situations, not by event throttling.

*Build:* a situation is a country-scoped record in arrays (target tag, resource, rivals, deadline date, state flags), spawned by monthly checks against desperation and historical triggers. It is shown as cards in the Trade Desk, and each card opens the dossier or coercion view pre-focused on it. Historical situations are hand-written with dynamic triggers, not fixed dates. A generic generator ("a desperate buyer plus a scarce seller plus a rival") supplies the rest.

### P2. Contracts are built on a vanilla trade engine the mod cannot observe (6.3, 6.4, 6.7, 6.8, 6.12)

**Why it matters.** I found no trigger, dynamic variable or on_action that reports *pairwise* trade (who exports what to whom). Only aggregates exist: `resource_exported@X`, `resource_imported@X` (`documentation/dynamic_variables_documentation.md`, lines 783 to 787). There is also no trigger that checks whether a specific `create_import` trade still exists. As a result, several promised features cannot work as written:
- The dossier's "who they import from" (6.7).
- "Undercut their current steel suppliers by 30%" (6.7).
- Secondary sanctions: "embargo anyone who trades with the target" (6.12).
- Detecting that a contract was silently cancelled by auto-trade or by AI re-evaluation (unknown 1). The AI cancels trades that deliver less than 80% (`NAI.MIN_DELIVERED_TRADE_FRACTION = 0.8`, `00_defines.lua`). The player also now has **auto-import** (`NTrade.AUTO_IMPORT_*`, `00_defines.lua` lines 2337 to 2345), which shrinks and cancels trades on its own.

A contract that dies without the mod noticing is the worst possible bug for this design: the player sees "active contract" and gets nothing.

**Fix: the mod owns its contracts as scripted flows. Vanilla trade is the background market, not the contract layer.**
- **Resource delivery:** a dynamic modifier per contract slot whose values are variables. The seller gets `country_resource_<res> = -N` and the buyer gets `+N` (the `country_resource_<Resource>` modifier is documented in `modifiers_documentation.md` around line 2327, and dynamic modifiers accept variables). The flow is fully under script control: it can be paused by a blockade, reduced by raiding, and cancelled cleanly.
- **Civilian-factory payment:** the payer gets `civilian_factory_use = N` (`modifiers_documentation.md` line 2202), and the receiver gets the factories through `add_offsite_building` (industrial complex) or through `cic_to_target_factor` (localised "Civilian industry to target country", `localisation/english/modifiers_l_english.yml` line 1139). That second modifier is the native pipe vanilla uses for subjects (`cic_to_overlord_factor`, `common/autonomous_states/*.txt`).
- **In-kind (equipment) payment:** `create_purchase_contract` (`effects_documentation.md` line 3220). It is script-creatable, scopeable (`any_purchase_contract`, `seller`, `buyer`, `deal_completion`), and cancellable (`cancel_purchase_contract`). Equipment delivery, convoys and raiding then come from the vanilla International Market. This is the cleanest piece of the whole design to build.
- **Physicality preserved:** sea contracts hold **convoys in escrow**. The convoys are removed from the seller's stockpile at signing and returned at the end, minus losses. Each month, a contract whose route crosses a region where `has_enemy_naval_control` (or the blockader's `has_naval_control`) holds loses a fraction of that month's delivery. `convoy_threat` (0 to 1, `triggers_documentation.md` line 2364) gives a cheap raiding-risk input.
- **The ledger is the source of truth.** The dossier shows mod-known deals plus the target's aggregate import dependency (`resource_imported@X / resource_consumed@X`). This is honest, legible, and enough to drive decisions.
- Keep `create_import` only for the default-market nudges in 6.3, and only if Phase 0 shows it holds.

### P3. Six bespoke GUIs and a top-bar hook are the most fragile path, and an engine feature built for this already exists (5, 7, 8)

**Why it matters.** The design commits to six scripted GUIs plus a top-bar alert, in a playset of about 80 mods, many of them UI mods. R56 itself overrides `interface/countrydiplomacyview.gui`. The negotiation, ultimatum-received, AI-offers-to-player and AI-to-AI-deal flows are all "one country proposes, another answers," and HoI4 has an engine system for exactly that.

**Fix: use `common/scripted_diplomatic_actions` as the backbone.** The vanilla template (`common/scripted_diplomatic_actions/scripted_diplomatic_actions.txt`) supports the following:
- `send_scripted_gui`: a custom GUI where the sender builds terms before sending. **This is the negotiation screen**, opened from the diplomacy view.
- `receive_scripted_gui`: a custom GUI that the *receiver* sees instead of a yes/no popup. **This is the "ultimatum received" and "offer received" screen**, and it works for a human target, which matters for multiplayer and for the player-as-target fantasy.
- `ai_desire`, an `ai_will_do` block: the AI decides when to *send* the action. **This gives AI-to-AI deals and AIs approaching the player without a custom AI scheduler.**
- `ai_acceptance`: named conditions decide AI acceptance. With `show_acceptance_on_action_button = no`, the condition names can be fuzzy reason hints ("Counting on British support") instead of numbers.
- `cost` and `command_power`, plus `on_sent_effect`, `complete_effect`, `reject_effect`.

Kaiserreich, Cold War Iron Curtain and State Transfer Tool all ship scripted diplomatic actions (verified under `workshop/content/394360/*/common/scripted_diplomatic_actions`), so the system works in practice.

Resulting UI plan:
- **Diplomatic actions** (new, native home): Propose Contract, Lease Rights, Issue Demand (public or back channel), Declare Quarantine, Demand Repayment, Join Our Embargo.
- **Trade Desk** (one scripted GUI): Situations board, active contracts, rights, investments, wishlist, monthly market report.
- **Dossier** (one scripted GUI): opened from the Desk or a Situation card.
- **Auction**: becomes a Situation card type, not its own window.
- **Top-bar alert**: optional. If attaching it requires overriding `topbar.gui`, skip it and use the Desk's own alert badge on a decision-category button.

This cuts the custom screens from six to two, moves most interactions onto a surface every HoI4 player already knows, and gives the AI a native proposal system.

### P4. Coercion risks collapsing into "stack every pressure source, then click demand" (6.12)

**Why it matters.** If pressure is a sum, the optimal play is to max every source and send the largest demand the meter allows. That makes coercion a meter-filling button, which breaks the "decisions, not buttons" and "spreadsheet" anti-goals.

**Fix: make pressure a set of choices that interact with the target's regime and with each other.**
- **Channel choice at demand time.** *Back channel* (quiet): lower demand ceiling, no pride penalty, works well on dictatorships, and the target can stall. *Public ultimatum* (loud): higher ceiling, puts your Credibility at stake, triggers the democratic rally effect, and leaves dictatorships two options, a humiliating fold or defiance. The design already identifies the regime nuance. Making it a *choice the player makes* turns it into gameplay.
- **Visible versus quiet sources.** Naval and air demonstrations, blockade and public blacklists are visible: they add pressure and also add pride resistance against democracies. Dependency, targeted cutoffs and ministerial bribes are quiet. The best campaign against Sweden differs from the best against Romania.
- **Pressure decays unless maintained.** Demonstrations cost peacetime fuel (`NAI.PEACE_TIME_NAVY_FUEL_FACTOR`, `00_defines.lua`) and political power upkeep, so a campaign has a natural clock. Long campaigns let the target's patrons react (guarantees, alternative suppliers).
- **Fig leaves.** A demand can include a face-saving component: a token purchase, a "joint commission," a public non-aggression declaration. It costs the coercer a little and cuts humiliation, which is what makes dictatorships fold. Munich is the template: give the target something to say on the radio.
- **Telegraphed breaking point.** The breaking point stays hidden but is foreshadowed by escalating cue text ("their generals speak openly of war," "reservists recalled") and by real signals the player can see on the map: the target starts building forts and moving divisions to the border (`add_ai_strategy` on the target). The risk is that the target chooses war, as the design intends. The player should feel that risk coming, not get blindsided.

### P5. Fuzzy feedback is unlearnable unless it changes in response to the player (6.1, 6.2, 6.12)

**Why it matters.** "Hidden math, legible consequences" works only if the player can build a mental model. If the readout says "Strained" before and after the fleet arrives, the player learns nothing and the system feels random, which reads as unfair.

**Fix:**
- **Deltas, not states.** Every readout change carries its cause: "Your squadron off Constanța has shaken them: Strained → Wavering." Show the top two reason hints, ranked.
- **Intel sharpens the readout.** Use the `civilian_intel` dynamic variable (`dynamic_variables_documentation.md` line 198). With low intel the player sees "Strained?". With high intel they see "Strained, leaning toward folding; counting on Italian support." This gives La Résistance agencies and operatives a peacetime job, rewards investment, and makes uncertainty a mechanic instead of a UI choice.
- **Envoy reports** after each negotiation round: one line of character voice that encodes one hidden variable ("The minister kept glancing at the clock," meaning patience is low).

### P6. Negotiation as counter rounds risks becoming a slider minigame and a save-scum target (6.6)

**Why it matters.** Three counter rounds on numeric terms reduce to "counter at max, back off once," which is a spreadsheet. If hidden patience or acceptance is rolled on each attempt, reloading also beats it.

**Fix: negotiate over *what*, not *how much*.**
- An offer is a bundle of term cards: resource, amount band, duration, payment type, and optional sweeteners (tech, PP flow, a fig leaf).
- Each counter round reveals information: one red line ("rights are off the table; an output share is possible") or one hidden want ("they would trade for naval tech"). Asking for a red-line item spends a lot of patience. Asking for something they secretly want *restores* it.
- Amounts come in bands (Small / Fair / Large / Generous), never sliders. This matches the fuzzy pillar and avoids "drag to max."
- Seed the counterparty's hidden values when talks open and store the seed in a variable, so reloading the counter screen does not reroll them.

### P7. The monopoly payoff is undefined because vanilla pays a fixed price (6.4 monopoly, 6.8)

**Why it matters.** Section 4 correctly notes that every buyer pays the same fixed price. Owning all tungsten therefore does not make you richer per unit, and `ANTI_MONOPOLY_TRADE_FACTOR = -100` past a 50% share pushes buyers away. Without a designed payoff, cornering a market is a big effort for a flat reward.

**Fix: make the payoff power over *who* gets the resource, which is what made the Wolfram War matter.**
- **Rationing:** a monopolist chooses which buyers receive output (scripted flows from P2). Excluded buyers' desperation rises. Excluding an enemy is a real strategic weapon.
- **Premium:** with real market power, the mod's contract valuation lets the holder demand a premium above fixed price, paid through the P2 payment channels. Premium scales with buyer desperation and the holder's share.
- **Preclusive buying** (new lever, see N2): pay over the odds for output you do not need, purely to deny it.
- **Monopoly invites counterplay.** Rival majors open Situations to break it: outbidding at lease expiry, pressuring a host to nationalize, smuggling through neutrals (N6). Holding a monopoly should be a defensive game, not a passive buff.

### P8. Blockade mechanics block the coercion fantasy in the typical case (6.12, 6.14)

**Why it matters.** Vanilla requires the target to have *generated* at least 15 world tension (`NDiplomacy.NAVAL_BLOCKADE_THREAT_THRESHOLD = 15`, `00_defines.lua` line 283). Typical coercion targets (Venezuela, Romania, Portugal, Iran) generate none, so the player cannot blockade them at all. The engine also offers no blockade trigger, no blockade effect and no blockade on_action (I searched `effects_documentation.md`, `triggers_documentation.md`, `dynamic_variables_documentation.md` and `common/on_actions/_documentation.md`). Force majeure (6.4) and "blockade grants a war justification" (6.14) therefore cannot detect a vanilla blockade.

**Fix: a mod-owned blockade, the "Quarantine."** The name comes from Roosevelt's Quarantine Speech of October 1937.
- It is a scripted diplomatic action ("Declare Quarantine") with PP cost and upkeep. It can be sent only at escalation stage 3 or later (flag-gated), so it stays inside the dispute system.
- Its effect is simulated and verifiable. Each week, for the strategic regions on the target's sea approaches (a hand-authored list per coastal country), the mod checks `QUARANTINER = { has_naval_control = <region> }` (`triggers_documentation.md` line 4429). While control holds: the target's sea contracts (P2) are suspended; trade-only opinion modifiers (`trade = yes`, `common/opinion_modifiers/00_opinion_modifiers.txt` header) between the target and its non-adjacent partners steer vanilla trade away; and the target's "strangulation" counter rises. It is breakable exactly as designed: lose naval control and the quarantine lapses.
- AI quarantiners receive `ai_strategy = { type = naval_blockade target_country = X id = <region> value = 100 }` (`common/ai_strategy/_documentation.md` line 695), so their fleets physically show up.
- Force majeure and casus belli key off the mod's own flags.
- The vanilla blockade diplomatic action stays untouched. Leave the threshold define alone, so the mod does not make every AI blockade-happy.

### P9. AI deficit intolerance needs a concrete actuator (3 goals, 6.2, 6.16)

**Why it matters.** "AI stops running 200 mils at -200 steel" is a stated goal, but desperation is only a score. Something has to act on it. The vanilla AI already caps trade at 80% of factories (`NAI.TRADEABLE_FACTORIES_FRACTION = 0.8`), so the bottleneck is often civilian factories or convoys, not willingness.

**Fix: a desperation response ladder, applied by script to the most desperate AIs during the monthly pass.**
1. **Procure:** the AI sends a Propose Contract action to the best-scoring seller (P3 `ai_desire`). Accepted contracts become scripted flows (P2), which bypass the AI's own trade budgeting.
2. **Substitute:** `add_ai_strategy` with `building_target` for synthetic refineries (oil and rubber), and `equipment_production_factor` down on the equipment that eats the missing resource.
3. **Rebalance:** when deficits are chronic, the AI switches its trade law, or a mod idea nudges conversions.
4. **Grab:** at extreme desperation and war-readiness, the AI opens a coercion Situation against a weak producer. The mod's own AI then generates historically flavored crises (Japan in 1941).

This makes the "fix the AI" goal also a source of content: desperate AIs create the Situations the player can exploit.

### P10. Valuing everything in CFE is a scope trap (6.1)

**Why it matters.** A full valuation engine for tech-years, ideology drift, ministers, bases and transit is a huge tuning surface. It can absorb most of the build budget before anything is fun, and since the values are hidden the precision buys little.

**Fix:** value in **bands** (Trivial / Small / Fair / Large / Huge), each mapping to a CFE range. Compute precise CFE only for resources and civilian-factory flows, where real numbers exist. Everything else gets a band from a short rule table (for example, tech value = band from (years behind) × (wishlist match)). The player only ever sees bands anyway, and tuning becomes "move this item up one band."

### P11. Ideology-drift payments are too strong as specified (6.4)

**Why it matters.** `~0.1/day` of drift is about 36 percentage points a year, enough to flip most minors within one contract. It would be the dominant payment and a backdoor to coups.

**Fix:** cap drift payments around 0.01 to 0.03 per day. Scale them down further as the target's election approaches (`days_until_next_election`, `dynamic_variables_documentation.md` line 259). The giver's government reacts when its own ruling party falls below a threshold: the AI requests renegotiation, which creates a Situation. Make drift a flavor payment that adds up over years, consistent with how Comintern and German cultural influence actually worked.

### P12. The mega-deal threshold breaks for importers (6.5)

**Why it matters.** "Above ~25% of the player's output of that resource" is undefined or zero for a player who imports the resource, and importers are the most common case.

**Fix:** a mega-deal is any proposal worth at least a Large band relative to the player's total civilian factories, *or* one that covers at least 25% of the player's consumption of that resource, *or* any proposal from a major. Everything else goes to the Desk silently.

---

## 2. Things not considered

| Gap | Proposed handling |
|---|---|
| **Coal is a seventh resource and drives energy in v1.20** (`common/resources/00_resources.txt`; `NProduction.ENERGY_RESOURCE = "coal"`, `RESOURCE_TO_ENERGY_COEFFICIENT = 9.0`, `00_defines.lua` lines 24 and 627). Section 9 says six resources. | Include coal everywhere. It also unlocks a strong historical Situation: the **Italian coal crisis of March 1940**, when Britain stopped seaborne German coal to Italy from Rotterdam and Germany switched to rail over the Brenner. That is a perfect showcase for rail corridors. |
| **Peace conferences already grant 5-year timed resource rights** (`NPeace.PEACE_TIMED_EFFECT_LENGTH_RESOURCE_RIGHTS = 1825`, `00_defines.lua` line 80). Section 6.10 says rights become permanent only through war. | Align with vanilla: war-won rights are also 5-year leases, which feed into the renewal and renegotiation system. "Renewal at gunpoint" becomes a late-game Situation. |
| **Player auto-import (new in v1.20) competes with mod steering.** | Treat auto-import as the player's default market (pillar 6, low micro). Scripted contract flows change the resource balance, so auto-import adjusts on its own. Test in Phase 0 that auto-import does not cancel the mod's nudged `create_import` trades. |
| **No pairwise trade visibility affects secondary sanctions.** | Redefine secondary sanctions as **"Join our embargo"**: a scripted diplomatic action asking third parties to embargo the target. Compliance is checkable with `is_embargoing`. Non-compliant countries can then be targeted. Credibility rises when you actually punish non-compliance. Historically this matches the ABCD line better than firm-level blacklists. |
| **Force-majeure exploit.** The player gets a friend or puppet to quarantine their own counterparty, voiding a contract penalty-free and gaining a war justification. | Force majeure applies only if the blockader is not the contract party, its subject, or a faction member. If it is, the breach counts as the party's own and costs Reliability. |
| **Reliability farming** through many tiny honored contracts. | Reliability gain is weighted by value × term and has diminishing returns per counterparty per year. A loss is weighted by the value of the breached deal. |
| **Coercion cycling.** Demand, withdraw, re-demand the same target to stack concessions. | Each accepted demand adds a "recently humiliated" timer to the target that raises resistance and breaking-point risk for about 2 years. A second demand inside the window is possible but dangerous, which is historically accurate (Czechoslovakia 1938 to 1939). |
| **Demonstration by proxy.** Counting allies' ships in `ships_in_area`. | Count only the coercer's own ships at full weight, faction members' ships at reduced weight, and only if the faction member has agreed (a scripted "Join the demonstration" action). This creates diplomatic play rather than an exploit. |
| **Air demonstration requires basing** (`num_planes_stationed_in_regions` counts planes *based* in regions, not missions; `triggers_documentation.md` line 6946). | Turn the constraint into content: to demonstrate air power against Romania you need air bases in a nearby region, so you first negotiate air base access with Hungary or Bulgaria. The vanilla `air_base_access` diplomatic action already exists (used as a `diplo_action_desire` target in `common/ai_strategy`). |
| **State ownership changes** (Spanish Civil War, partitions, annexations) orphan rights, concessions and contracts. | Hook `on_state_control_changed` and `on_annex`. Rights in a state that changes owner become a Situation ("the new government in Burgos reviews foreign concessions"). The new owner can confirm (gaining Reliability with the holder) or nationalize. |
| **Tag switches, civil wars, capitulations.** | Contracts end with no penalty on capitulation or civil-war split. Escrowed convoys are returned to whichever party still exists. Use `on_capitulation` and `on_civil_war_end`. |
| **Multiplayer.** Hidden RNG in GUI code can desync. A human target needs real choices, not an AI acceptance roll. Human-to-human contracts need trust. | Do all randomness in effects (not GUI properties) and seed it at talk start (P6). Human targets receive the `receive_scripted_gui` screen. Human-to-human contracts still use Reliability, but its effects hit only AI third parties' trust. |
| **The wartime phase is under-designed.** Historically the trade game *peaked* during the war (the Wolfram War, Swedish ore, Turkish chromium, Argentine beef and wheat). | Add an explicit wartime mode: once a world war starts, neutrals become the main prize. Offers to them escalate from both sides, preclusive buying unlocks, and a "neutral's dilemma" readout appears in their dossier. "Play a neutral to 1945 and come out rich" becomes a headline playstyle. |
| **Lend-lease undercuts contracts.** Free lend-lease to a target removes their desperation. | Treat incoming lend-lease as "patron support" in the target's resistance and in contract valuation. A rival's lend-lease shows up as a reason hint ("American aid has emboldened them"). |
| **International Market access as leverage.** | `has_market_access_with` (`triggers_documentation.md` line 4190) lets "revoke market access" be a cheap quiet pressure source against equipment-hungry minors. |
| **AI coercing the player relentlessly.** | Each AI gets a coercion budget (active campaigns at most 1 for majors, 0 for most minors). Pick targets by expected value and avoid humans by default unless the human is the best target (a game rule could raise this). |
| **Performance with 7 resources and about 80 active countries.** | Stagger the monthly passes by country index across days (`on_daily` with a modulo on a stored index). Compute desperation only for countries with a deficit or a live Situation. Store per-resource values in fixed-index arrays. Never run `every_country` inside `every_country` on a daily tick. |
| **Onboarding.** Players will not discover the system. | Start with a historical opening Situation for each major plus a few key minors (see N1), each with a one-screen explainer when it first opens. No standalone tutorial. |

---

## 3. New ideas

**N1. Historical opening Situations as the tutorial.** Each major (and Sweden, Romania, Turkey, Portugal, Spain and Mexico) starts with one live Situation that teaches one lever. GER: *Schacht's New Plan*, building clearing-agreement dependency in the Balkans. ENG: *Iberian wolfram*. USA: *the Mexican oil question*. JAP: *the oil question* (a desperation clock). SOV: *Baltic mutual assistance pacts* (coercion without war). ITA: *the coal lifeline* (energy dependency). *Build:* scripted Situations with dynamic triggers and a fallback date. They reuse the generic Situation framework.

**N2. Preclusive buying (the Wolfram War).** Pay above market for a resource you do not need, specifically to deny it to a named enemy. The payoff is that the enemy's desperation rises and its production suffers. This is the most historical and most fun way to wage economic war without firing a shot, and it gives rich neutral-friendly powers (ENG, USA) a real peacetime offensive. *Build:* a contract variant with the buyer marked as `denial_target`. The flow can go to the player's stockpile or be "destroyed." Valuation adds a denial bonus scaled by the enemy's desperation for that resource.

**N3. Quarantine** (see P8). Roosevelt's 1937 language for the mod-owned blockade. *Build:* scripted diplomatic action plus weekly `has_naval_control` checks plus AI `naval_blockade` strategy.

**N4. Navicerts (wartime British system).** If you hold naval control of a chokepoint (Gibraltar, the Channel, Suez), neutrals whose sea trade crosses it must accept your "navicert" quotas, or their cargoes get seized. You ration how much Spain, Sweden or Turkey can import, which stops re-export to your enemy. This is the strongest UK fantasy in the setting. *Build:* hand-authored chokepoint regions per neutral. A scripted diplomatic action offers a quota (a cap on imports). Refusal makes the mod suspend that neutral's sea contracts and apply trade-opinion penalties while you hold control.

**N5. Clearing balances (Schacht for real).** Instead of paying in civilian factories, you pay a target in *blocked credit*. That credit can only be spent on your equipment through purchase contracts, so the target is locked into buying from you. This is the mechanism behind 6.13 Dependency, with teeth and historical accuracy. *Build:* a hidden per-pair variable that accrues per contract. It shows to the player only as a band ("Sofia holds large unspent credits with us"). The target AI periodically converts it into `create_purchase_contract` with you as seller. Large balances raise Dependency.

**N6. Smuggling and transshipment.** Embargoed or quarantined countries buy through neutral middlemen (Spain to Germany, Sweden to Germany). The middleman profits but risks the Statutory List. A player neutral can *be* the middleman, a lucrative and risky playstyle for SWI, POR, SPR and SWE. *Build:* an AI middleman scores (profit minus blacklist risk) each quarter and spawns a paired flow (buy from A, sell to B). The victim power gets a Situation: "Spanish re-exports are feeding Germany."

**N7. Concession gambles (oil strikes).** Concessions have a hidden geological outcome. Most produce modest output, a few hit big: Dammam No. 7 (Saudi Arabia, March 1938) and Burgan (Kuwait, 1938). That gives investment real variance and real stories. *Build:* at completion, roll once (seeded) for an output band, then `add_resource` to the state with `give_resource_rights` to the investor. A big strike immediately raises nationalization pressure and rival interest, spawning a Situation.

**N8. Public versus back-channel demands** (see P4). The single most important new decision in coercion. *Build:* two variants of the Issue Demand scripted diplomatic action sharing one valuation, differing in ceiling, pride modifiers and Credibility stakes.

**N9. Fig leaves** (see P4). Sweeteners whose purpose is face, not value. *Build:* a small set of term cards (token purchase, joint commission, public guarantee of the target's independence, a statement of friendship) that cut the humiliation term in the resistance math.

**N10. The monthly market report.** One Trade Desk panel with prices as words: "Tungsten: frantic. Rubber: glut. Oil: tightening (Japanese buying)." It refreshes monthly and never pops up. It gives the player a reason to look without nagging. *Build:* scripted localisation over the per-resource global desperation aggregate, with a cause hint drawn from the largest desperate buyer.

**N11. Reputation through other mouths.** Reliability and Credibility stay hidden, but the dossier carries one rotating line from the counterparty's perspective: "Ankara says our word is good," "Lisbon doubts we would really embargo Britain." *Build:* scripted localisation keyed on reputation bands with the observing country.

**N12. Playing the target.** A player as Romania, Sweden, Turkey or Venezuela should face AI coercion with real choices: fold, stall, play patrons against each other, porcupine. The design lists these responses for the AI. Give them to the human as `receive_scripted_gui` options with real consequences, and the mod gains a second playstyle for free: the small neutral surviving between giants.

---

## 4. Engine notes

Verified against the v1.20 install unless marked as a guess.

1. **Scripted diplomatic actions exist and are moddable** (`common/scripted_diplomatic_actions/scripted_diplomatic_actions.txt`, a commented template). They support send and receive scripted GUIs, `ai_desire`, `ai_acceptance`, PP and CP costs, and effects for sent, complete and reject. Several workshop mods use them, including Kaiserreich (`1521695605`), Cold War Iron Curtain (`1458561226`) and State Transfer Tool (`1368778634`). *Guess, test in Phase 0:* that they render correctly under R56's `interface/countrydiplomacyview.gui` override (`workshop/content/394360/820260968/interface/countrydiplomacyview.gui`).
2. **`create_purchase_contract`** (`effects_documentation.md` line 3220) is script-creatable with seller, buyer, civilian factories and equipment lists. The `PURCHASE_CONTRACT` scope has `cancel_purchase_contract`, and the triggers `seller`, `buyer`, `deal_completion` and `contract_contains_equipment` (`triggers_documentation.md` line 515). `NMarket.MAX_CIV_FACTORIES_PER_CONTRACT = 15`. This is the ideal vehicle for in-kind and equipment payments.
3. **`create_import` has no observability.** Vanilla uses it only in `history/countries/GER - Germany.txt` (line 497, oil from SOV). It has no documented parameters beyond the example (`resource`, `factories`, `exporter`), no trigger checks it, and no pairwise trade variable exists (only `resource_exported@X` and `resource_imported@X`, `dynamic_variables_documentation.md` lines 783 to 787).
4. **Civilian factory transfer modifiers:** `cic_to_target_factor` ("Civilian industry to target country", `modifiers_l_english.yml` lines 1139 and 1140) and `cic_to_overlord_factor` (used in `common/autonomous_states/*.txt`). `civilian_factory_use` (`modifiers_documentation.md` line 2202) locks factories. Together they cover payments and Demand Repayment (6.11). Repayment can actually *transfer* factories to the victim instead of just locking them, which feels much better.
5. **Targeted modifiers:** `targeted_modifier = { tag = X ... }` works in ideas (`common/ideas/argentina.txt` around line 1166, `trade_cost_for_target_factor = -0.2` toward ENG). In dynamic modifiers it is questionable: `common/dynamic_modifiers/aat_dynamic_modifiers.txt` line 751 has the comment "for targeted_modifier when it works." However, `add_dynamic_modifier` accepts `scope = TAG`, "the dynamic variable will target that scope" (`effects_documentation.md`). *Test in Phase 0* whether a country-scoped dynamic modifier with `scope = TARGET` applies `cic_to_target_factor` and `extra_trade_to_target_factor` toward that target. If it does, one variable-driven dynamic modifier per pair replaces a mountain of per-tag ideas.
6. **Trade-only opinion modifiers** (`trade = yes`, documented in the header of `common/opinion_modifiers/00_opinion_modifiers.txt`, examples `embargo` with value -150 and `sov_ger_treaty_trade` with value +10). With `NTrade.RELATION_TRADE_FACTOR = 1`, each point maps directly to trade factor without touching diplomatic opinion. This is the cleanest default-market steering lever. Opinion modifiers have fixed values, so use a binary ladder (for example ±5, 10, 20, 40, 80) to encode any value.
7. **Unknown 5 resolved, mostly:**
   - `ships_in_area = { type = <category> area = <strategic region id> size > N }` (`common/ai_strategy/ENG.txt` line 1348). It works at strategic-region granularity and checks the scope country's own ships.
   - `ships_in_state_ports = { type state size }` (`triggers_documentation.md` line 7607) enables a "port visit" demonstration, which is classic gunboat diplomacy and requires docking rights.
   - `num_planes_stationed_in_regions = { value regions = { ... } }` (`triggers_documentation.md` line 6946) counts *based* planes, not missions.
   - `has_naval_control` and `has_enemy_naval_control` take a region ID (lines 4429 and 3841).
   - `naval_strength_ratio` and `naval_strength_comparison` handle the "compared to the target's navy" check.
   - `divisions_in_border_state` and `divisions_in_state` handle military posture.
   - *Guess:* whether `ships_in_area` counts ships docked in ports inside the region.
8. **No blockade hooks.** I found no blockade trigger, effect or on_action. `NDiplomacy.NAVAL_BLOCKADE_THREAT_THRESHOLD = 15` requires the target to have generated tension (`00_defines.lua` line 283). `has_added_tension_amount` exists to check this. *Guess, test:* whether `add_named_threat` (country-scoped, "Adds country threat") attributes generated tension to the scope country, which would let a defiant nationalizer become blockade-eligible under vanilla rules.
9. **No trade-related on_actions** (`common/on_actions/_documentation.md`: nothing for embargo, guarantee, trade or market). Everything must poll. `on_state_control_changed`, `on_annex`, `on_capitulation`, `on_ruling_party_change` and `on_government_change` exist for the lifecycle hooks in section 2.
10. **v1.20 player auto-import** (`NTrade.AUTO_IMPORT_DEFICIT_TOLERANCE`, `AUTO_IMPORT_TARGET_MARGIN`, `AUTO_IMPORT_DEFAULT_BUDGET_FRACTION = 0.25`, `00_defines.lua` lines 2337 to 2345) and `NAVAL_ROUTE_ACCESS_AVOID_COST_MULT` (player-marked regions to avoid). Both interact with 6.3 and need a Phase 0 check.
11. **AI trade defines:** `NAI.TRADEABLE_FACTORIES_FRACTION = 0.8`, `MIN_DELIVERED_TRADE_FRACTION = 0.8` and `SEA_PATH_LENGTH_SCORE_BASE = -30` (`00_defines.lua` lines 2414 to 2416). The 80% delivery rule means raiding and quarantine naturally cause AI trade cancellation, which is desirable.
12. **AI strategy hooks:** `naval_blockade` (`common/ai_strategy/_documentation.md` line 695), `diplo_action_desire` and `diplo_action_acceptance`. Vanilla uses the last two with targets such as `docking_rights`, `air_base_access`, `military_access`, `market_access_rights` and `guarantee`. *Guess:* whether `diplo_action_desire` accepts a scripted diplomatic action key as its target. If it does, it is a strong lever for focusing AI behavior.
13. **`civilian_intel`** is a dynamic variable (`dynamic_variables_documentation.md` line 198). It supports the intel-gated readout (P5).
14. **CIC / "Economic Capacity Surplus"** (`add_cic`, `add_equipment_subsidy`, `CIC_BANK_HEADER`) is a vanilla stock of civilian capacity used by the market and subsidies (`common/decisions/ARG.txt` line 923, `common/decisions/CHI_decisions.txt` line 5515). It is shown to players as a number, so it conflicts with pillar 2 if surfaced. It is still a useful *hidden* sink or source, for example paying an AI seller by `add_cic` as part of an in-kind deal. Use it sparingly and never as a player-facing treasury.
15. **R56 defines** (`820260968/common/defines/r56_defines.lua`) contain no `NTrade`, `NMarket` or blockade overrides (grep found none), so the mod's defines file will not collide there.

**Proposed additions to Phase 0:** (7) targeted dynamic modifier via `scope =`; (8) scripted diplomatic actions under R56's diplomacy view; (9) `country_resource_<res>` driven by variables in a dynamic modifier, and its interaction with auto-import; (10) `add_offsite_building` with negative levels for removal; (11) `ships_in_area` counting ships in port; (12) `add_named_threat` attribution.

---

## 5. Top 5

1. **Make scripted diplomatic actions the backbone** for proposals, demands, Quarantine, Demand Repayment and Join Our Embargo, with send and receive scripted GUIs as the negotiation and response screens and `ai_desire` as the AI-to-AI engine. Reduce bespoke GUIs to the Trade Desk and the dossier (P3).
2. **Make contracts mod-owned scripted flows:** `country_resource_<res>` dynamic modifiers for delivery; `civilian_factory_use` plus `cic_to_target_factor` or `add_offsite_building` for payment; `create_purchase_contract` for in-kind deals; convoys held in escrow and naval-control checks for physical risk. The ledger is the source of truth (P2).
3. **Build the Situations board as the core loop**, seeded by historical opening Situations per major (P1, N1). This is what turns the systems into a game and keeps the world alive but quiet.
4. **Rebuild coercion around choices, not sums:** public versus back channel, visible versus quiet pressure, fig leaves, decaying pressure, a telegraphed breaking point, and an intel-gated readout via `civilian_intel`. Ground every pressure source in a verified trigger, and replace the vanilla blockade dependency with the mod-owned Quarantine (P4, P5, P8).
5. **Give monopoly and wartime a real payoff:** preclusive buying, rationing, navicerts, and an explicit wartime-neutrals phase where Swedish ore, Turkish chromium and Iberian wolfram become the main prizes (P7, N2, N4).
