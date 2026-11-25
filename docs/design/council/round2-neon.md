# Council Review, Round 2: Cross-Pollination

Reviewer: `neon`
Date: 2026-11-25
Inputs reviewed: `docs/design/2026-11-25-power-without-war-design.md`, `round1-brief.md`, `round1-opus.md`, `round1-sol.md`, `round1-neon.md`, plus targeted v1.20 and Road to 56 file checks.

Reading all three reviews side by side makes one thing jump out: every major failure mode of the original draft now has a real solution, and the strongest version of this mod is not any single reviewer's blueprint. Opus cracked the structural spine (Situations board + `scripted_diplomatic_actions`), Sol cracked the lifecycle integrity and playability discipline (tranche settlement, target winning moves, commercial patron counteroffers, one-story vertical slice), and my Round 1 caught v1.20's concrete mechanical landscape (`coal` and energy scaling, `country_resource_cost_<res>`, additive UI and map mode, late-game neutral sinks). Below is how those pieces fit together, where I changed my mind, where I push back, and the end-to-end design I would ship.

---

## 1. Synthesis

Where reviewers proposed competing fixes for the same problem, here is the combination that beats each individual proposal.

### 1.1 Contract substrate: Two mod-owned physical vehicles, zero reliance on pairwise vanilla trade
- **The fork:** Opus proposed dynamic modifiers using `country_resource_<res> = -N`, `cic_to_target_factor`, `create_purchase_contract` for equipment, and escrowed convoys. Sol proposed named-state `give_resource_rights` leases for equipment in tranches, plus cancellable side-payments riding on observed vanilla imports if native imports do not lock. I proposed `country_resource_cost_<res>` (seller) + `country_resource_<res>` (buyer), `civilian_factory_use` + `add_offsite_building`, and `add_equipment_subsidy`.
- **Best combination:** Leave vanilla trade and v1.20 player auto-import as the unmonitored background market, and run all mod deals on **two clean, mod-owned vehicles**:
  1. **Bilateral Supply Contracts (flexible tonnage/quotas, non-committal or fixed-term):** Resource transfer via `country_resource_cost_<res>` (positive variable on seller, verified in `common/dynamic_modifiers/TAOG_dynamic_modifiers.txt:95-96` and `common/decisions/INS.txt:2347`) and `country_resource_<res>` (buyer, `common/dynamic_modifiers/wuw_dynamic_modifiers.txt:915`). CIV payment via `civilian_factory_use` (payer) + `add_offsite_building` (receiver). Equipment and tech settled in **Sol's milestone tranches** (`send_equipment`, `add_tech_bonus`, `create_production_license`, and verified `add_equipment_subsidy` for clearing credits) so war exits cannot farm upfront unlocks. Sea contracts use **Opus's escrowed convoys** and weekly `has_naval_control` checks so raiding and quarantines physically hurt delivery.
  2. **Named-State Concessions (prestige & monopoly leases):** Built on `give_resource_rights`, strictly obeying **Sol's invariant of one mod-managed lease per `(holder, state)`**, skipping states where that holder already has a vanilla right (verified in `documentation/effects_documentation.md:6211-6218` and `events/BFTB_Turkey.txt:3035`: `remove_resource_rights = <state_id>` is called on the holder and strips *all* rights they hold in that state with no resource filter).
- **Why this beats every single-reviewer version:** It supports both flexible quotas ("70% of oil") and map-visible state concessions, eliminates pairwise-vanilla observability bugs, blocks upfront-transfer exploits, preserves real convoy and sea-lane risk, and uses only verified v1.20 script patterns.

### 1.2 UI and AI proposal backbone: Scripted diplomatic actions + one Trade Desk + additive map presence
- **The fork:** Opus moved bilateral actions to `common/scripted_diplomatic_actions` (cutting custom screens from six to two: Trade Desk + Dossier). Sol collapsed notifications into one Trade Desk with a single stateful row per crisis and a consequential-choice popup rule. I pushed `parent_window_token = top_bar` alerts, `dirty` flags, dropping the awkward Decisions split for coercion actions, and adding an "Economic Leverage" custom map mode.
- **Best combination:**
  - **Bilateral actions & AI initiation:** Adopt **Opus's `scripted_diplomatic_actions`** (`send_scripted_gui`, `receive_scripted_gui`, `ai_desire`, `ai_acceptance`) for Propose Contract, Lease Rights, Issue Demand, Declare Quarantine, Demand Repayment, and Join Our Embargo. This solves human-as-target gameplay, multiplayer networking, and AI-to-AI deal initiation in one native layer.
  - **Hubs:** Keep just **two scripted GUIs** (Trade Desk + Country Dossier), both strictly gated by **mandatory `dirty` variables** (`common/scripted_guis/_documentation.md:102-105`). Inside the Trade Desk, adopt **Sol's stateful crisis rows** (bids, ultimatums, and breaches update one row with its active deadline instead of spawning five alerts) and **Sol's consequential-choice popup rule** (interrupt only for threatened leases, ultimatums, or imminent deadlines, not routine major-power offers).
  - **Map and top bar:** Attach one compact alert badge via **`parent_window_token = top_bar`** (zero edits to `topbar.gui`), plus the additive **"Economic Leverage" `scripted_map_modes` view** in Phase 2/3 so the map itself stays alive during peace.

### 1.3 Coercive crisis structure: Sustained choices, target counterplay, and patron backstops
- **The fork:** Opus focused on public vs. back-channel demands, fig leaves, decaying pressure, and `civilian_intel`-sharpened deltas. Sol focused on giving the target a real winning move, a single deadline per demand, single-crisis fleet commitment, and a protector's commercial counteroffer. I focused on distinct quiet vs. loud toolkits, a 30-to-60-day demonstration ramp, a pre-war "Knife-Edge" warning state, and 1936 anti-farming guardrails (democratic domestic limits + coercive infamy).
- **Best combination:** Combine all three into a **three-beat Coercive Crisis**:
  1. **Commitment & Channel:** Forces commit to *one* crisis at a time (Sol) and ramp pressure over 30 to 60 days while paying upkeep (Neon/Opus), killing flying-circus micro. The coercer picks **Back-Channel** (quiet, face-saving, moderate ceiling, powered by Dependency/cutoffs/intel) or **Public Ultimatum** (loud, high ceiling, Credibility on the line, democratic rally risk), optionally adding **Opus's Fig Leaf** to cut humiliation.
  2. **Counterplay Window (one deadline):** The target is never a passive acceptance roll. Before the deadline, the target (AI or human via `receive_scripted_gui`) picks one concrete counterplay move from **Sol**: fold, offer a smaller named-state deal, announce a **90-day Temporary Route Suspension**, harden/mobilize, or call a patron. Simultaneously, regional majors get a **Crisis Alert** where a patron can attach **Sol's Commercial Counteroffer** (a real reserved contract buying the target's boycotted output or replacing cut-off supply if the target refuses).
  3. **Brinkmanship & Readout:** The coercer sees **Opus's cause-linked deltas** sharpened by `civilian_intel` plus **my "Knife-Edge" pre-war warning** (backed by Opus's visible border/fort movement on the map), then decides whether to pocket a smaller settlement, escalate to Quarantine, or gamble on war.

### 1.4 Blockade / Quarantine under Road to 56's map overrides
- **The fork:** All three reviewers independently rejected vanilla's 15%-WT blockade gate (`NDiplomacy.NAVAL_BLOCKADE_THREAT_THRESHOLD = 15`) in favor of a mod-owned **Quarantine / Sea Interdiction** driven by `has_naval_control` and `ai_strategy = { type = naval_blockade / naval_dominance }`. However, Opus proposed hand-authored per-country strategic region lists while Sol flagged that R56 replaces `history/states` and `map/strategicregions`.
- **Verified ground truth & best combination:** Checking `workshop/content/394360/820260968/descriptor.mod:14-15` and diffing the installed folders directly confirms that R56 ships **1,143 states** (vs. vanilla's **1,081**) and **298 strategic regions** (vs. vanilla's **304**), renumbering land strategic regions from ID 275 onward. Crucially, among sea/coastal regions, **only one ID differs**: vanilla `279-Gulf of Bothnia.txt` becomes `279-Rio Grande do Norte.txt` in R56 (breaking Swedish iron-ore sea checks if hardcoded!). All other sea regions below 275 match.
  - Therefore: resolve all **land states and air-basing regions dynamically** at `on_startup` (by owner, resource output, coastal status, adjacency, and continent, never hardcoded vanilla state IDs). Use a compact, verified list of **sea chokepoints/approaches** below ID 275 plus one explicit R56-detection branch for the Gulf of Bothnia / Baltic.

### 1.5 Secondary sanctions & bilateral reputation tension
- **The fork:** Opus replaced unobservable firm-level blacklists with a verifiable **"Join Our Embargo"** scripted diplomatic action (`is_embargoing`). Sol added named-partner targeting, deadlines, bidirectional dependency costs, and the insight that punishing a non-complier by breaking an existing deal earns Credibility while costing Reliability.
- **Best combination:** Use Opus's verifiable **"Join Our Embargo"** diplomatic action scoped to Sol's **named partners and fixed deadline**, and explicitly wire the **Credibility vs. Reliability tradeoff**: backing down from your own blacklist threat tanks Credibility; following through by breaking an active contract with a major third party raises Credibility while taking a real Reliability hit. That single tension turns blacklists into a genuine grand-strategy dilemma instead of a free button.

---

## 2. Build on others

Five high-leverage ideas from Opus and Sol, pushed a step further into system interactions.

### 2.1 Turn Opus's Situations Board into "Situation Chains"
Opus's Situations board (2 to 4 live contestable prizes with clocks and rivals) fixes the core-loop vacuum. Push it further by making **Situation outcomes spawn downstream Situations** 6 to 18 months later rather than vanishing into history:
- Win the **Iberian Wolfram** auction via preclusive buying -> Germany's tungsten desperation crosses a threshold -> spawns **"Spanish Re-Exports to Berlin"** (Opus N6 smuggling) -> if Britain imposes **Navicerts** (Opus N4) without offering Sol's **Commercial Counteroffer** to cushion Madrid's economy, resentment rises -> spawns **"Iberian Nationalization / Closure Crisis."**
- Hit a major **Oil Strike** on a concession gamble (Opus N7, Dammam No. 7) -> instantly spawns a **Rival Patron Bid** at lease expiry AND a **Nationalization Temptation** if the host's ruling ideology drifts.

This creates an organic Act I -> Act II -> Act III storyline in every campaign without writing railroaded focus trees.

### 2.2 Turn Sol's "Commercial Counteroffer" into the flagship peacetime playstyle for Democracies
In 1936-1938, democracies (UK, France, USA) should not be able to run offensive gunboat shakedowns on 0-WT neutrals. Sol's **Commercial Counteroffer** (a protector reserving a real contract to buy a squeezed minor's unsold output or replace cut-off imports if the minor defies the coercer) solves the "what does Britain do before 1939?" problem:
- **Playing economic spoiler:** Britain or the US watches Germany squeeze Romania or Japan squeeze Siam, and steps in with an actual factory/equipment commitment that stiffens the target's spine.
- **Patron overextension:** Because each Commercial Counteroffer reserves real CIVs or equipment tranches, a patron cannot backstop everyone at once. A clever coercer can trigger two crises in the same patron's sphere simultaneously (for example, Romania and Turkey) to force the patron to abandon one.

### 2.3 Generalize Sol's "90-Day Temporary Route Closure" into a universal Coercion Stalling Card
Sol proposed the historical 3-month Burma Road closure as a timed route suspension that creates a second decision at reopening. Make **"90-Day Provisional Suspension"** a standard target counterplay option in *any* Coercive Crisis (for both AI and human targets):
- Choosing it immediately prevents a war breaking point, pauses the contested delivery for 90 days (giving the coercer a partial win), and puts a **Reopening Clock** on the Situation card.
- Those 90 days become a playable scramble: the target hunts for a Patron Counteroffer or finishes an alternate corridor, while the coercer decides whether to keep fleets burning fuel on station until day 90. When day 90 hits, the target chooses *Reopen* (re-igniting the crisis with new leverage) or *Formalize Concession*.

### 2.4 Fuse Opus's `civilian_intel` readout with Band-Based Negotiation into a peacetime Intelligence loop
Opus proposed `civilian_intel`-sharpened coercion readouts AND negotiation term cards that reveal red lines and hidden wants round by round. Link them directly:
- At low `civilian_intel` (<30%), you enter talks blind, burn patience discovering red lines, and cannot tell whether a rival patron's promise is backed by a real Commercial Counteroffer or an empty bluff.
- At high `civilian_intel` (60%+), your agency exposes one hidden want before Round 1 (*"Lisbon's admiralty wants destroyer blueprints"*), reveals patron backing strength, and triggers the **Knife-Edge** war warning a full stage earlier.
- This gives La Resistance spy networks (`network_strength`, civilian infiltration) a concrete, rewarding peacetime job without adding a single new espionage subsystem.

### 2.5 Make Opus's Schachtian Clearing Balances a double-edged sword via Sol's bidirectional dependency
Opus modeled clearing balances as blocked credits redeemable for the major's arms, building target Dependency. Layer Sol's **bidirectional dependency** directly on top:
- While Germany is at peace with spare industrial capacity, clearing credits lock Balkan exporters into Berlin's arms ecosystem cheaply.
- Once Germany enters a major war and needs every rifle and tank for the front, unredeemed clearing credits flip from **leverage into liability**. If Berlin delays or defaults on clearing tranches, the minor's resentment spikes, its Dependency flips to grievance, and it can tear up the oil lease or jump to an Allied counteroffer. Your peacetime weapon becomes a wartime juggling act.

---

## 3. Change your mind

Six honest changes to my own Round 1 review after reading Opus and Sol:

1. **Adopt Opus's `scripted_diplomatic_actions` backbone instead of my custom negotiation/coercion GUI windows.** In Round 1 (§1.7), I kept custom scripted GUIs attached to `diplomacy_target_context` for negotiation and coercion actions, mentioning `scripted_diplomatic_actions` only as an MP fallback. Opus's analysis is clearly better: `send_scripted_gui`, `receive_scripted_gui`, `ai_desire`, and `ai_acceptance` eliminate four fragile GUIs, give human-as-target play and MP networking for free, and remove the need for a bespoke AI proposal scheduler. I keep my `parent_window_token = top_bar` alert badge and `dirty` rule, and move bilateral flows onto scripted diplomatic actions.
2. **Adopt Sol's "One Complete Story First" vertical slice and Opus's Situations spine over horizontal phasing.** In Round 1, I accepted the draft's horizontal phases (all coercion -> all contracts -> all market) and piled on big features (Strategic Reserves, capital ships, map mode). Both Opus and Sol rightly identified that horizontal phases hide whether the core loop is actually fun. Proving *one* complete Tungsten crisis (playable as both Portugal and a demanding major) right after Phase 0 beats building half the mod in the dark. Strategic Reserve Warehouses and the custom Map Mode should move to Phase 2/3 after the vertical slice proves fun.
3. **Drop day-1 upfront irreversible transfers (`transfer_ship`, lump-sum `add_cic`, instant `set_technology`) in favor of Sol's tranche settlement.** In Round 1 (§2.1, §3.7), I pitched upfront warship transfers and lump-sum CIC bonuses for mega-deals. Sol (§1.3) spotted an exploit I completely missed: if war or force majeure ends a contract penalty-free, any irreversible day-1 transfer becomes a farmable heist. Warships and full tech unlocks should unlock at a delivery milestone (or exceptional settlement with strict prerequisites), never on signature day.
4. **Replace my "Economic Hegemony Spirit" reward with Sol's narrative Campaign Milestones.** In Round 1 (§1.1), I suggested rewarding economic milestones with a bespoke hegemon national spirit. Sol (§1.4) stayed truer to the anti-goals ("no passive buffs disguised as content"): selectable, visible campaign milestones that close with a short chronicle of the bargains and crises that earned them, while letting the sandbox continue.
5. **Switch my Negotiation counter rounds to Opus's Band Cards + Seeded RNG.** Adding causal rejection text (my Round 1 §1.5) helps, but Opus (§P6) solved the deeper root cause: replacing numeric amounts with qualitative bands (Small / Fair / Large / Generous), card-based terms that reveal red lines and hidden wants, and seeding hidden negotiation variables at talk start eliminates both slider-minigame spreadsheets and save-scumming.
6. **Tighten my Resource Rights and R56 map handling based on Sol's catches.** My Round 1 (§2.3) assumed rights reconciliation was enough without accounting for `remove_resource_rights` wiping *all* rights held by a country in a state (`effects_documentation.md:6211-6218`), and I did not catch R56's `replace_path` on `history/states` and `map/strategicregions` (`descriptor.mod:14-15`). Adopting Sol's one-lease-per-(holder, state) rule and dynamic startup state resolution fixes both cleanly.

---

## 4. Your design

If I were the lead designer reshaping **Power Without War** today, here is the end-to-end architecture I would lock in.

### 4.1 The Core Loop
The game runs on a **Situation -> Action -> Counterplay -> Consequence** cadence across three acts:
- **Act I (1936-1938, Positioning & Quiet Leverage):** Historical opening Situations teach one lever per major/key neutral (Germany: Schacht's clearing agreements; UK: Iberian wolfram; USA: Mexican oil; Italy: coal lifeline; USSR: Baltic pressure; Japan: oil desperation clock; Portugal/Sweden/Romania: playing patrons). Players build Dependency, fund a Rail Corridor or Oil Concession, and learn to read `civilian_intel` cues.
- **Act II (1939-1942, Peak Scarcity & The Neutral Tightrope):** World War II spikes global scarcity across all **7 resources** (including **Coal / `energy_ratio`**). Auctions heat up, Preclusive Buying unlocks, navies enforce **Quarantines** and **Navicerts**, smugglers try to arbitrage blockades, and neutral players walk the razor's edge between getting rich and getting invaded.
- **Act III (1942-1945, Hegemony & Renewal at Gunpoint):** 5-year leases and war-won concessions expire into dramatic renewal crises; clearing balances come due; rich neutrals spend surplus CIVs on **Proxy Arming**, **Merchant Marine**, and **Strategic Reserves**; peaceful runs culminate in selectable **Economic Campaign Milestones** (Neutral Broker, Resource Hegemon, Shadow Arsenal).

### 4.2 The Five Load-Bearing Systems
1. **The Situations Board (Core Spine):**
   - Caps live player-facing crises at **2 to 4** at once ("alive but not noisy").
   - Seeded by dynamic historical flashpoints (condition-triggered, not railroaded dates) plus a systemic generator (desperate buyer + scarce seller + rival, or expiring lease, or nationalization).
   - Lives in **one Trade Desk GUI** (with a Monthly Market Report in words, Active Agreements ledger, Wishlist, and Per-Resource Market Stance: *Open / Brokered / Withheld*), backed by one **Country Dossier GUI**, one additive **`top_bar` alert strip**, and mandatory `dirty` updates.
2. **Unified Agreement Lifecycle (Mod-Owned Flows + Named-State Leases):**
   - **Vanilla trade + auto-import** stays untouched as the low-micro background market (gently nudged via `trade = yes` trade-only opinion modifiers).
   - **Bilateral Supply Contracts** use `country_resource_cost_<res>` (seller) + `country_resource_<res>` (buyer), `civilian_factory_use` + `add_offsite_building` (CIV flows), **tranched equipment / `add_equipment_subsidy` clearing credits**, and **escrowed convoys** checked weekly against `has_naval_control`.
   - **Named-State Leases** use `give_resource_rights`, strictly 1 mod lease per `(holder, state)`, skipping states with an existing vanilla right for that holder, reconciled periodically against focus-tree revocations (converting silent vanilla revocations into live Nationalization Situations).
   - **One shared state machine** for all deals: Active -> Suspended (90-day provisional closure or third-party Force Majeure, excluding same-faction/subject blockaders) -> Renewed / Completed / Defaulted / Nationalized (with real settlement: staged equipment/CIC repayment or completed host project, not mere factory-locking).
3. **Scripted Diplomatic Actions & Band-Based Negotiation:**
   - Six actions (`Propose Contract`, `Lease Rights`, `Issue Demand`, `Declare Quarantine`, `Demand Repayment`, `Join Our Embargo`) using `send_scripted_gui`, `receive_scripted_gui`, and `ai_desire`.
   - **Banded Valuation:** Precise CFE only for resources and CIVs; short rule-table bands (Trivial / Small / Fair / Large / Huge) for tech bonuses, licenses, equipment tranches, capped ideology drift (`0.01-0.03/day`), bases, and route closures.
   - **Negotiation (max 3 rounds):** Term cards in qualitative bands, seeded at talk start (anti-save-scum), revealing one red line or hidden want per round, sharpened upfront by `civilian_intel`.
4. **Coercive Crisis Engine:**
   - **Sustained single-crisis commitment:** One fleet/air wing/border corps per crisis, ramping over 30-60 days with upkeep.
   - **Channel + Fig Leaf:** Back-Channel vs. Public Ultimatum interacting with regime type (dictatorships fold quietly with a Fig Leaf; democracies rally against public threats).
   - **Target Counterplay + Patron Counteroffer:** Every demand has one deadline. Targets can fold, offer a partial state deal, invoke a 90-day Provisional Suspension, mobilize toward a telegraphed **Knife-Edge** breaking point, or call a patron who can reserve a real **Commercial Counteroffer**.
   - **Escalation Ladder:** Targeted Mod-Contract Cutoff -> Join Our Embargo (named partners + deadline, Credibility vs. Reliability tension) -> **Gunboat Quarantine** (mod-owned, `has_naval_control`, AI `naval_blockade` / `naval_dominance`) -> Casus Belli.
   - **Guardrails:** Democratic domestic limits against 0-WT offensive coercion, cumulative Coercive Infamy, 2-year "recently humiliated" anti-cycling timer, and R56-normalized opinion bounds (`[-100, +100]`).
5. **7-Resource Scarcity, AI Desperation, & Physical Investments:**
   - All **7 resources** (`oil`, `aluminium`, `rubber`, `tungsten`, `steel`, `chromium`, `coal`), with `energy_ratio` driving coal desperation.
   - Staggered daily evaluation (`pww_tick_bucket`, ~2-3 countries/day) restricted to ~15-20 Active Traders, filtering out lumpy temporary deficits (Sol's consumption/duration/fuel-runway check).
   - **AI Desperation Ladder:** Procure (contract via `ai_desire`) -> Substitute (`building_target` refineries, shift production) -> Rebalance/Invest (trade law or foreign mine/corridor) -> Coerce (spawn a Crisis Situation).
   - **Investments (Rail Corridors, Ports, Pipelines, Concessions with Oil Strike variance):** Investor locks `civilian_factory_use` during staged build; physical buildings spawn in host state upon consent/ownership check; corridors protect eligible contracts from sea interdiction.

### 4.3 First Playable Slice (Phase 0 + Phase 1 Vertical Slice)
Do **not** build all sixteen systems before playtesting. Prove the mod is thrilling with a tight, complete vertical slice:

**Phase 0 (Engine Spike, throwaway test mod, ~2-3 days):**
Verify the 8 load-bearing engine behaviors under vanilla + R56:
1. `country_resource_cost_<res>` + `country_resource_<res>` in dynamic modifiers and how v1.20 player auto-import reacts to them.
2. `civilian_factory_use` + `add_offsite_building` (including negative-level removal) vs. `cic_to_target_factor` in dynamic modifiers (`scope = TARGET`).
3. `scripted_diplomatic_actions` (`send_scripted_gui`, `receive_scripted_gui`, `ai_desire`) rendering cleanly with R56's `interface/countrydiplomacyview.gui`.
4. `add_equipment_subsidy` + `send_equipment` tranches vs. `create_purchase_contract` (specifically whether `civilian_factories = 0` is legal).
5. `give_resource_rights` / `remove_resource_rights` convoy exposure, occupation behavior, and safe 1-per-(holder, state) cleanup.
6. `ships_in_area` (does it count docked ships?), `has_naval_control`, `num_planes_stationed_in_regions`, and AI `naval_blockade` / `naval_dominance` movement.
7. `parent_window_token = top_bar` widget placement alongside R56 and common UI mods.
8. `add_named_threat` attribution (nice-to-have, non-blocking).

**Phase 1 Playable Slice ("The Iberian Wolfram Proof", 1936-1938, playable from 3 seats: Germany, UK, Portugal):**
- **Scope:** One complete, replayable Situation (*Iberian Wolfram*) dynamically resolving Portugal's tungsten state(s) for both vanilla and R56, backed by the 7-resource schema, one Trade Desk (Situations Board + Active Agreements + Monthly Market Report), one Country Dossier, and the `top_bar` alert strip.
- **Included loops:**
  - Seller-structured Auction (exclusive lease, split award, or short bridge contract) with bid cards and rival reactions.
  - One full Agreement Lifecycle (Supply Contract + Named-State Lease, quarterly equipment/subsidy tranches, escrowed convoys, 90-day Provisional Suspension, Nationalization + Repayment).
  - One full Coercive Crisis (Back-Channel vs. Public Ultimatum, Fig Leaf, sustained Naval Demonstration off Portugal, Gunboat Quarantine via `has_naval_control`, UK Commercial Counteroffer, `civilian_intel`-sharpened causal deltas, Knife-Edge warning).
- **Exit gate (how we know it works):** Play three 1936-1938 runs without firing a shot (as Portugal juggling Berlin and London, as Germany securing wolfram via clearing credits or coercion, and as the UK denying Germany via preclusive buying, counteroffers, or quarantine). If all three seats feel tense, legible, and fun, expand in Phase 2 (Oil/Coal Situations: Romania, Mexico, Italy, Sweden + Physical Investments + Economic Leverage Map Mode) and Phase 3 (Living World AI, Smuggling, Navicerts, Strategic Reserves, Campaign Milestones).

---

## 5. Disagreements

Where I think another reviewer is wrong, and the better alternative.

### 5.1 With Opus: Do not build in-kind payments on `create_purchase_contract` or seller deductions on negative `country_resource_<res>` (Opus P2, Engine Note 2)
- **Why it is wrong:**
  1. Checking vanilla v1.20 files shows **zero** usages of negative `country_resource_<res>`. Vanilla deducts country resources in dynamic modifiers using positive **`country_resource_cost_<res>`** (`common/dynamic_modifiers/TAOG_dynamic_modifiers.txt:95-96`, `common/decisions/INS.txt:2347`). Likewise, `documentation/effects_documentation.md:1168-1170` documents `add_dynamic_modifier`'s `scope =` parameter specifically for restricting a *state* modifier to one country, not as a country-scoped `targeted_modifier` substitute for `cic_to_target_factor`.
  2. `create_purchase_contract` (`effects_documentation.md:3220-3242`) also has **zero** vanilla script usages, and its structure has the *buyer* paying civilian factories to the *seller* for equipment (`civilian_factories = 2`). Using it for an in-kind resource payment (Germany sending rifles to Romania *in exchange for* oil, with Romania paying 0 CIVs) is untested and likely fails or stalls because vanilla market delivery speed scales with buyer CIVs.
- **Better alternative:** Use `country_resource_cost_<res>` (seller) + `country_resource_<res>` (buyer) and `civilian_factory_use` + `add_offsite_building` for CIV payments. For direct equipment barter, use **tranched `send_equipment`** (reliable, zero CIV distortion, clean cancellation on breach). For Schachtian clearing credits, use verified **`add_equipment_subsidy`** (`seller_tags = { ROOT }`) so the host genuinely buys your arms with your funded subsidy. Test `create_purchase_contract` in Phase 0 as an optional enhancement, never a core dependency.

### 5.2 With Opus: Hand-authored per-country strategic region lists will break under Road to 56 (Opus P8, N4)
- **Why it is wrong:** Opus checked `r56_defines.lua` (clean) and then proposed hand-authored per-country strategic region lists for Quarantine and Navicerts. However, checking R56's `descriptor.mod:14-15` and diffing `map/strategicregions/` proves R56 replaces both `history/states` (1,143 vs. 1,081) and `map/strategicregions` (298 vs. 304), shifting ID 279 from **Gulf of Bothnia** (vanilla) to **Rio Grande do Norte** (R56) and renumbering land regions 275+ (including Northern Norrland, Finland, and Jutland). A hardcoded region table built on vanilla IDs will silently check Brazil when blockading Sweden under R56.
- **Better alternative:** Resolve all land states, producing regions, and air-basing regions dynamically at `on_startup` via state triggers (owner, resources, coastal, adjacency, continent). Keep sea chokepoints to a small verified set below ID 275 (where vanilla and R56 match 100%) plus one explicit R56-aware mapping for Bothnia/Baltic.

### 5.3 With Opus: Cutting down to two GUIs should not mean cutting peacetime visibility on the map (Opus P3)
- **Why it is wrong:** Reducing six bespoke screens to two (Trade Desk + Dossier) plus `scripted_diplomatic_actions` is a huge architectural win. Still, if every interaction lives inside tables and diplomatic popups, the HoI4 map itself remains visually dead during peace. Watching your concessions, dependency web, and rivals' desperation shift directly on the map is what makes peacetime feel like grand strategy instead of an inbox manager.
- **Better alternative:** Keep Opus's lean 2-GUI + scripted-diplomatic-action interaction model, and pair it in Phase 2/3 with one additive **`scripted_map_modes`** layer ("Economic Leverage", `common/map_modes/`). It adds zero UI-mod conflict risk and turns the world map into the mod's primary scouting surface.

### 5.4 With Sol: Do not anchor non-committal contracts to "observed vanilla imports" (Sol §1.2)
- **Why it is wrong:** Sol suggests letting non-committal agreements ride on an observed vanilla import ("stop its side payments when verified delivery stops") if `create_import` cannot be locked. Verified in `documentation/dynamic_variables_documentation.md:777-790`, HoI4 exposes **no pairwise trade trigger or variable**, only country-wide `resource_imported@X` and `resource_exported@X`. The mod literally cannot verify whether Country A is still importing tungsten from Country B rather than Country C. Stopping side-payments only when total imports drop lets a buyer switch suppliers while still collecting side-payments, or breaks valid deals whenever a third party changes trade.
- **Better alternative:** Never tie mod contracts or side-payments to observing pairwise vanilla trade. Keep vanilla trade + auto-import strictly as the unmonitored open market, and run *all* signed mod contracts (both non-committal flows and fixed-term deals) on mod-owned `country_resource_cost_<res>` / `country_resource_<res>` flows with escrowed convoys.

### 5.5 With Sol: Leaving out v1.20 Coal/Energy and being too cautious on AI deficit action leaves a real hole (Sol overall, §2.3)
- **Why it is wrong:** Sol's review omits v1.20's **7th resource (`coal` / `energy_ratio`)**. Under `00_defines.lua:627-632`, `ENERGY_SCALE_PER_TRADE_FACTORY_EXPORT = 0.25` increases energy demand as a country accumulates export-trade factories, which directly hits the Neutral Broker and Trade Empire playstyles Sol highlights. In addition, while Sol is right to avoid "cargo cult imports" on brief lumpy deficits, treating AI resource shortages too passively risks leaving the world quiet and unreactive, undercutting the "alive" pillar.
- **Better alternative:** Put all **7 resources** (with `energy_ratio` driving coal desperation) into the core data model from Phase 1 Day 1 so the schema never has to be retrofitted. Combine Sol's smart desperation filter (deficit share of consumption + sustained duration + fuel runway) with Opus's concrete 4-step **AI Desperation Ladder** (Procure -> Substitute -> Rebalance -> Coerce) so desperate AIs reliably drive live Situations without wasting factories on transient dips.
