# Council Review, Round 1: Power Without War

Reviewer: `neon`
Date: 2026-11-25
Target document: `docs/design/2026-11-25-power-without-war-design.md`
Game version verified: Hearts of Iron IV v1.20 ("Operation Postern")

The core concept is strong. The two halves of the fantasy (building a trade empire and wielding coercive power short of war) reinforce each other cleanly, and the six pillars protect the mod from turning into either a spreadsheet clicker or a passive buff tree. The main risks in the current draft are structural: fighting hardcoded vanilla systems where cleaner v1.20 hooks already exist, leaving the peaceful trade-empire run without a late-game climax or capital sink, hitting a wall on vanilla's 15% World Tension blockade gate, and missing v1.20's seventh resource (coal and energy). Every issue below comes with a concrete reshape that keeps the pillars intact and makes the peacetime game sharper.

---

## 1. Problems and fixes

Ranked from highest to lowest impact on player fun.

### 1.1 The peaceful "trade empire" run has no late-game climax and no peacetime capital sink (Sections 1, 3, 6.4, 6.9)

**Problem:** Goal 1 promises that a peaceful or neutral playthrough can be "won economically." Right now, wealth converts into civilian factories, technology, equipment, and political power. In HoI4, civilian factories exist primarily to construct military factories. Without a war or a non-combat sink for surplus factories, a trade-empire playthrough peaks in 1939 and drifts into aimless number-watching by 1941 while Germany and the USSR fight the real game. Worse, v1.20's energy system (`common/defines/00_defines.lua:627-632`) increases energy cost per factory with total factory count and counts exported-trade factories (`ENERGY_SCALE_PER_TRADE_FACTORY_EXPORT = 0.25`), which actively penalizes piling up surplus civilian factories with nothing to spend them on.

**Why it matters for fun:** The opening 3 years of building a trade empire will feel great, and then the moment World War II erupts (which should be the *most* exciting chapter for a neutral profiteer or economic hegemon), the player runs out of meaningful things to spend their dominance on.

**Fix:** Give the non-war playthrough a real Act II and Act III:
1. **The Neutral Tightrope (wartime survival loop):** Once a major war starts, holding scarce resources or rights leases becomes dangerous as well as lucrative. Both sides press for exclusivity, slap Statutory Lists on you, threaten invasion or blockade if you feed their enemy, and bid aggressively in auctions. Staying rich, indispensable, and uninvaded while balancing rival blocs (historical Sweden, Switzerland, Turkey, Portugal) becomes the late-game thriller.
2. **Peacetime Capital Sinks that compound leverage:** Add non-war sinks for civilian factories and equipment:
   - **Proxy Arming / Patronage:** Use `add_equipment_subsidy` and `send_equipment` to prop up a weak concession host so a rival does not annex your oil fields.
   - **Strategic Reserve Warehouses:** Divert surplus production in cheap pre-war years into capped physical reserves, then dump them in 1941-1943 auctions at peak scarcity.
   - **Merchant Marine Expansion:** Invest civilian factories into convoy fleets and escorts to survive wartime raiding and unlock long-range sea contracts.
3. **Economic Hegemony Milestones (non-war win arcs):** Add a small set of trackable, high-bar economic capstone goals (for example: control over 40% of global extraction of a strategic resource through rights; force a major power into a resource-driven strategic collapse or peace concession; maintain profitable neutrality while financing a winning faction; hold concessions across 5+ nations). Reaching them grants tangible diplomatic status (faction-leader respect, non-aggression guarantees, bespoke hegemon spirit) and a clean "Economic Victory" milestone rather than an endless sandbox.

### 1.2 Steering vanilla `create_import` for contracts fights the engine and breaks variable pricing (Sections 4, 6.3, 6.4)

**Problem:** Sections 6.3 and 6.4 assume contracts and above-market payments sit on top of vanilla trade via `create_import`, `extra_trade_to_target_factor`, and `trade_cost_for_target_factor`. Verified game files show why this will fight the engine constantly:
- `create_import` has zero usages anywhere in vanilla `common/` or `events/`.
- v1.20 introduced player auto-import defines (`AUTO_IMPORT_DEFICIT_TOLERANCE`, `AUTO_IMPORT_TARGET_MARGIN`, `AUTO_IMPORT_MIN_CONVOY_EFFICIENCY` in `00_defines.lua:2337-2345`) alongside AI trade cancellation (`MIN_DELIVERED_TRADE_FRACTION = 0.8` in `00_defines.lua:2415`).
- Vanilla `common/resources/00_resources.txt` hardcodes `cic = 0.125` (8 units per civilian factory) globally, and `trade_cost_for_target_factor` (as used in `common/ideas/australia.txt:618` and `common/ideas/china_warlord.txt:949`) discounts buyer cost rather than cleanly letting a seller charge a 1.5x or 2x scarcity premium.

**Why it matters for fun:** Nothing destroys trust in a trade mod faster than spending 3 rounds negotiating a 5-year tungsten-for-cruisers contract only to watch HoI4's auto-trade or export-law math silently cancel or flatten it a month later.

**Fix:** Split the two layers cleanly:
- **Keep Default Market (6.3) on vanilla trade:** Let HoI4's native trade engine and auto-import handle background open-market flow, gently steered by `extra_trade_to_target_factor`, `trade_opinion_factor`, and targeted opinion modifiers. Low micro, zero engine combat.
- **Build Contracts (6.4) on v1.20's verified Dynamic Resource + CIC layer:** Verified in `common/dynamic_modifiers/TAOG_dynamic_modifiers.txt:95-96` and `common/dynamic_modifiers/wuw_dynamic_modifiers.txt:915`, both `country_resource_<res>` (adds resource to buyer) and `country_resource_cost_<res>` (subtracts resource from seller) accept script variables inside dynamic modifiers. Pair a single aggregated contract dynamic modifier per country with `civilian_factory_use` / `add_offsite_building` (or `cic_to_target_factor` via `targeted_modifier`, verified in `common/decisions/SWI.txt:3326,3671`, and `add_cic` / `add_equipment_subsidy` for lump-sum or arms-credit deals). This sidesteps Engine Unknowns 1 and 2 entirely, guarantees true 1-to-5-year lock-in, supports arbitrary scarcity pricing and in-kind payments, naturally punishes a seller whose extraction falls short (`country_resource_cost_<res>` pushes them into deficit), and suspends cleanly on Force Majeure.

### 1.3 Vanilla naval blockade and embargo thresholds lock out peacetime coercion targets (Sections 4, 6.12, 6.14)

**Problem:** The centerpiece fantasy of Section 6.12 is squeezing weak resource states (Venezuela, Mexico, Romania, Portugal, Sweden, Persia, Bolivia) with naval pressure, embargoes, and blockades. Verified in `common/defines/00_defines.lua:272, 283`:
- `EMBARGO_THREAT_THRESHOLD = 30` (target must have generated 30% World Tension).
- `NAVAL_BLOCKADE_THREAT_THRESHOLD = 15` (target must have generated 15% World Tension).
- `documentation/modifiers_documentation.md` has `embargo_threshold_factor` and `embargo_cost_factor`, and **no** blockade threshold modifier. `documentation/effects_documentation.md` has **no** script effect to start a naval blockade.

Peaceful resource exporters generate 0% World Tension from 1936 through 1945. Even after Mexico expropriates British and American oil fields (Section 6.11: "eased blockade conditions against the host"), Mexico still sits at 0% generated World Tension, so the vanilla naval blockade action cannot legally target it.

**Why it matters for fun:** If gunboat diplomacy cannot actually blockade or quarantine a peaceful oil exporter, the flagship coercion ladder stalls right before its most dramatic rung.

**Fix:** Separate **Peacetime Gunboat Quarantine** (mod-driven) from **Formal Naval Blockade** (vanilla diplomatic action):
1. Build **Gunboat Quarantine** directly in the Coercion system using verified v1.20 triggers: `has_naval_control = <REGION_ID>` (`documentation/triggers_documentation.md:4434`) and `ships_in_area`. Once the coercer declares a Quarantine (paying PP, World Tension, and third-party opinion) and physically parks a fleet holding naval control or required tonnage in the sea region(s) bordering the target's ports, the quarantine immediately activates: it suspends the target's overseas mod-contracts (Force Majeure), applies a trade/export choke modifier (or fires `send_embargo` plus third-party avoidance weighting), and drives rapid coercion pressure.
2. For AI coercers, drive actual fleet movement to the target's coastal sea zone with `add_ai_strategy = { type = naval_dominance id = <region_id> value = 99 }` (`common/ai_strategy/_documentation.md:673-682`).
3. Reserve vanilla's formal Naval Blockade for high-tension majors (or lower `NAVAL_BLOCKADE_THREAT_THRESHOLD` modestly in the late-loading defines file for wars/escalations). Historically, 1930s peacetime blockades were framed as "quarantines" and "patrols" specifically because formal blockades were acts of war, so this makes the mod both more functional and more authentic.

### 1.4 "Monopoly via rights lease" clashes with HoI4's country-wide export laws and all-or-nothing state rights (Sections 6.4, 6.10)

**Problem:** Section 6.4 proposes that leasing resource rights from producers makes you the world's seller through the normal market. Two HoI4 mechanics break that loop:
- **Country-wide `min_export`:** Export law applies uniformly to every resource you hold. If you are on Limited Exports (25%) or Closed Economy (0%), leasing 100% of Portugal's tungsten locks 75% to 100% of it off the market unless you switch to Free Trade (80%), which exposes all of your own steel, oil, and coal. Conversely, if you are on Free Trade, you cannot withhold tungsten to drive up scarcity while continuing to export steel; buyers just grab your tungsten off the vanilla market at the flat 8:1 CIV rate.
- **State-level granularity:** `give_resource_rights` (`documentation/effects_documentation.md`) grants all output of the listed resource(s) in a given state, not a percentage like "70% of oil" (Section 6.12).

**Why it matters for fun:** Cornering a market is only fun if you can actually *act like a monopolist*: ration supply, starve a rival, and force majors into your auction room.

**Fix:**
1. **Per-resource Market Stance in the Trade Desk:** Give players with export surpluses or rights leases a simple 3-state qualitative stance per resource (no sliders): *Open Market* (flows into vanilla trade normally), *Brokered / Rationed* (pulls half the exportable surplus off the vanilla open market via `country_resource_cost_<res>` and reserves it strictly for bilateral contracts and auctions), and *Withheld / Strategic Reserve* (pulls surplus off the vanilla market to spike global scarcity and drive up buyer Desperation, at a small political/opinion cost with desperate majors).
2. **Cleanly distinguish State Concessions from Output Quotas:** Use `give_resource_rights` for full state concessions (visible on the map, high prestige, high nationalization risk, contested state-by-state like Ploesti vs. secondary fields), and use bilateral contracts (`country_resource_cost_<res>` to `country_resource_<res>`) for flexible tonnage/percentage demands ("70% of oil for 3 years").

### 1.5 Hidden math + fuzzy feedback risks feeling arbitrary at negotiation walkouts and war breaking points (Sections 2, 6.6, 6.12)

**Problem:** Pillars 3 and 4 ("Fuzzy feedback" and "Hard but fair") will collide if the player cannot diagnose *why* an envoy stormed out on counter-round 2 or *why* a target suddenly chose Finland-style war over folding. Right now, "their envoy looks irritated" tells the player mood, not cause, and hidden breaking points can feel like unfair RNG when a coercion campaign unexpectedly explodes into war.

**Why it matters for fun:** Brinkmanship is exhilarating only when the player can read the room, feel the ice cracking, and make a deliberate gamble.

**Fix:** Keep all math hidden, but make **causal attribution** and **cliff-edge tells** crystal clear:
- **Negotiation Red Lines:** Every counter-rejection gives a one-line qualitative diagnosis tied to the dominant hidden blocker (for example: *"They balked at the political clause, not the price"*, *"They doubt you will honor a five-year term"*, or *"They believe Berlin will outbid you"*). The 3 counter rounds become a rewarding reading-the-room minigame instead of trial-and-error.
- **Coercion Attribution + Knife-Edge State:** In the Coercion View, display two concise qualitative lists: **Pressure working for you** (e.g., *Cruisers off Maracaibo*, *Heavy export dependency*) and **Why they are holding out** (e.g., *Expecting British protection*, *Public ultimatum rallied parliament*). Insert a distinct **"Cornered / On a Knife-Edge"** warning state right before the war breaking point (*"Reserves are mobilizing; another public demand may trigger war"*), forcing a juicy decision: push anyway, switch to a quiet face-saving offer, or cash out for a smaller concession.

### 1.6 Coal and energy (v1.20's 7th resource) are missing from the design (Sections 4, 6, 9)

**Problem:** Section 9 assumes 6 resources ("60+ countries and 6 resources"). Verified in `common/resources/00_resources.txt:38-42` and `common/defines/00_defines.lua:627-632, 3600-3608`, HoI4 v1.20 ships with **7 resources** (`oil`, `aluminium`, `rubber`, `tungsten`, `steel`, `chromium`, `coal`), with coal fueling industrial energy (`energy_ratio` in `documentation/dynamic_variables_documentation.md`).

**Why it matters for fun:** Leaving coal out creates both a mechanical bug (export-rich minors suddenly brown out from `ENERGY_SCALE_PER_TRADE_FACTORY_EXPORT = 0.25` with no contract tool to secure coal) and a huge missed historical opportunity. Coal was the quintessential peacetime coercion lever of 1936-1941: Britain's coal cutoff of Italy and Germany's coal-for-iron-ore barter with Sweden are textbook examples of power without war.

**Fix:** Make `coal` a first-class 7th resource across valuation, dossiers, contracts, and auctions, and feed `energy_ratio` directly into coal Desperation (any industrializing state dropping below 0.85 `energy_ratio` becomes acutely desperate for coal). Highlight **Energy Cutoff** as a premier quiet coercion tool against coal-poor powers like Italy, Sweden, Switzerland, and Argentina.

### 1.7 Splitting coercion across scripted GUIs and Decisions creates workflow friction and UI-mod conflict risk (Sections 5, 7, 8)

**Problem:** Section 7 puts the Country Dossier and Coercion View in scripted GUIs, puts coercive moves and investments in the Decisions tab, and notes that top-bar alerts might require overwriting vanilla's `topbar.gui`. In a playset running Road to 56 and ~80 UI mods, overwriting `topbar.gui` guarantees conflicts, and forcing players to inspect a country in a custom window only to hunt through a crowded R56 Decisions tab to click "Issue Ultimatum" breaks flow.

**Why it matters for fun:** The mod's best moments happen when the player scans the map, right-clicks a target, reads their leverage, and pulls the trigger in one seamless screen.

**Fix:** Unify interactive controls in additive scripted GUIs and reserve Decisions strictly for **active timed missions/trackers**:
- Attach a compact **Trade Desk + Alert Strip** directly via `parent_window_token = top_bar` (`common/scripted_guis/_documentation.md:30`), achieving zero edits to `topbar.gui` or `alerts.gui`.
- Attach a **"Trade & Leverage" entry button** directly to every country's diplomacy panel via `context_type = diplomacy_target_context` (`parent_window_token = selected_country_view_diplomacy`, verified in `common/scripted_guis/_documentation.md:14,29`) so right-clicking any nation opens its unified Dossier, Targeted Deal, Investment, and Coercion actions in one click.
- Use the Decisions tab *only* for running countdown timers with map highlights (e.g., *"Rail Corridor under construction: 114 days"*, *"Ultimatum expires in 12 days"*, *"Nationalization repayment active"*), where vanilla decision missions shine.

### 1.8 Quiet vs. Loud coercion needs distinct player actions, not just hidden math (Section 6.12)

**Problem:** Section 6.12 has an inspired idea: dictatorships resist public humiliation while conceding quietly, whereas democracies accept economic deals readily but harden when pressure becomes visible. However, almost every listed pressure source (naval/air demonstrations, border troops, embargoes, blockades, blacklists) is loud and public. Without a real quiet toolkit, the regime nuance feels like an invisible dice modifier rather than a tactical choice.

**Why it matters for fun:** Choosing *how* to squeeze a country (quiet stranglehold vs. public gunboats) should be one of the signature strategic decisions in the mod.

**Fix:** Give every coercive campaign an explicit **Channel / Posture choice**:
- **Back-Channel Squeeze (Quiet):** Powered by Dependency, targeted single-resource cutoffs, credit/subsidy withdrawal, envoy leverage, and intelligence `network_strength` (`documentation/triggers_documentation.md`). Adds minimal World Tension, sidesteps democratic rally-around-the-flag penalties, and lets proud dictatorships save face. Builds pressure more slowly and caps out at moderate demands (output quotas, preferential contracts, closing a third-party route, expelling rival agents).
- **Public Ultimatum (Loud):** Powered by naval/air/border demonstrations, public embargoes, Quarantines, and open threats. Builds pressure rapidly and unlocks maximal demands (state resource rights, military access, naval/air bases, friendly ministers), at the cost of World Tension, democratic hardening, patron intervention risk, and higher war-breaking-point danger.

### 1.9 Air and naval demonstrations are vulnerable to instant-teleport micro cheese (Sections 4, 6.12)

**Problem:** Section 6.12 frames air demonstrations as planes flying over unowned territory at peace. Verified in `documentation/triggers_documentation.md`, HoI4 cannot fly peacetime combat missions over neutral countries; the real trigger is `num_planes_stationed_in_regions` (planes based at airfields in specified regions). Furthermore, if naval, air, and border demonstrations apply instant pressure on day 1, optimal play degenerates into teleporting one fleet and 500 fighters around the globe for 24 hours per minor ("the flying circus").

**Why it matters for fun:** Instant unit-shuffling exploits violate both "low micro by default" and "hard but fair," turning tense diplomatic crises into tedious click-farming.

**Fix:** Make military demonstrations **sustained crises**:
- Measure presence via `ships_in_area` (with carrier strength weighted via `num_ships_with_type@carrier`), `num_planes_stationed_in_regions` in adjacent/target regions, and `divisions_in_border_state` / `num_divisions_in_states`.
- Pressure from demonstrations **ramps over 30 to 60 days** while an active Demonstration Posture is maintained (costing a modest PP/command power upkeep and keeping the units committed). Pulling forces out early decays the ramp.
- This eliminates teleport cheese, mirrors real 1930s crises (weeks of standoff), and gives targets and rival majors time to notice and respond.

---

## 2. Things not considered

### 2.1 Tech and obsolete-equipment dumping exploits in contracts
**Gap:** Allowing instant `set_technology` or arbitrary `send_equipment` in exchange for 5-year resource contracts lets a player trade 1918 rifles for Ploesti oil, or lets a resource-rich minor like Venezuela or Sweden leapfrog into 1943 techs by 1938 via `set_technology`.
**Handling:** Separate **blueprints & licenses** (`add_tech_bonus` + `create_production_license`) for standard contracts from **full tech transfer** (`set_technology`), which is restricted strictly to non-ahead-of-time techs where the receiver already owns the prerequisite, limited to mega-deals/rights leases, and gated by a per-country cooldown. For equipment, discount CFE sharply for obsolete tech years and only let AIs accept equipment archetypes matching their active division/air templates or shortages.

### 2.2 1936 major-power "free concession farming" on unprotected minors
**Gap:** In January 1936, the UK, USA, or France can outgun Venezuela, Persia, Siam, Cuba, and Liberia ten-to-one. Without guardrails, a human major can park the Home Fleet off every neutral exporter in 1936 and seize half the world's resources before 1937.
**Handling:** Three interlocking checks:
1. **Democratic Domestic Constraint:** Democracies pay steep PP/war-support penalties and cannot launch *offensive* Loud Coercion against a 0-WT target without a casus (such as nationalization, contract default, or target aggression). They excel at quiet economic deals, investments, and defensive retaliation.
2. **Sphere-of-Influence / Patron Reflex:** Squeezing a minor alerts regional majors (USA for the Americas, UK/USSR for the Middle East, Germany/USSR for Northern/Eastern Europe), who can step in with a guarantee or counter-fleet.
3. **Cumulative Coercive Infamy:** Each successful coerced concession raises an "Economic Predator" alarm that lowers major guarantee thresholds and stiffens target resistance worldwide for 2-3 years.

### 2.3 Vanilla and Road to 56 focus trees silently revoking resource rights
**Gap:** Vanilla and R56 have dozens of scripted focuses and events calling `give_resource_rights` / `remove_resource_rights` (Mexico PEMEX, Persia, Iraq, Romania, China, Afghanistan, Dutch East Indies, verified across `common/decisions/*.txt`). If a focus revokes a player's hard-won concession, mod variables will desync and the Nationalization ladder will not fire.
**Handling:** Run a lightweight periodic **Rights Reconciliation Check** comparing tracked mod concessions against live `has_resources_rights`. If a tracked right vanishes without mod expiry or war, automatically interpret it as an **external nationalization** and fire the mod's Nationalization response (Demand Repayment, embargo, quarantine, war justification). This turns a compatibility hazard into seamless emergent gameplay.

### 2.4 Integration with Arms Against Tyranny's International Market
**Gap:** Section 4 mentions AAT's International Market and then leaves it separate. In v1.20, players can already sell weapons for CIC, and script hooks exist for `give_market_access`, `add_relation_rule_override = { can_access_market = no }`, `add_cic`, and `add_equipment_subsidy`. Keeping raw-resource contracts isolated from the International Market creates awkward splits (for example, imposing a secondary blacklist while still granting full weapon market access).
**Handling:** Weave AAT hooks directly in: include Market Access as a bargaining chip and Blacklist penalty (`can_access_market = no`), use `add_cic` for clean one-off Nationalization repayments and lump-sum contract bonuses, and use `add_equipment_subsidy` (locked to `seller_tags = { ROOT }`) for historical clearing-agreement arms credits.

### 2.5 Road to 56 doubles opinion bounds and triples AI fuel buffers
**Gap:** Verified in `workshop/content/394360/820260968/common/defines/r56_defines.lua:11-14, 293-295`, Road to 56 sets `MAX_OPINION_VALUE = 200`, `MIN_OPINION_VALUE = -200` (vanilla is `[-100, +100]`), and raises `WANTED_MAX_FUEL_BUFFER_IN_DAYS_*` to `365`. Any mod formula assuming `[-100, +100]` opinion will behave twice as aggressively under R56, and `DIPLOMATIC_ACTION_NAVAL_BLOCKADE_OPINION_SCALING = -2` will swing by +400 instead of +200.
**Handling:** Clamp or normalize opinion inputs inside the mod's scoring scripts to `[-100, +100]` (detecting R56 or dividing by 2 when opinion bounds exceed 100), and calibrate blockade defines assuming R56's `-200` floor so AI majors do not blockade every ideological rival on sight.

### 2.6 Mid-contract wars, transit occupation, civil wars, and Governments-in-Exile
**Gap:** What happens when a transit country hosting your Rail Corridor or Pipeline gets occupied, when a Concession state is conquered by a third party, when a partner splits in a civil war (Spain 1936), or when a partner capitulates into a Government-in-Exile (still `exists = yes`, zero controlled states)?
**Handling:** Hook `on_state_control_changed`, `on_capitulation`, `on_declare_war`, `on_government_change`, and `on_civil_war_end` (`common/on_actions/00_on_actions.txt`):
- Transit state occupied by a hostile or embargoing power triggers Force Majeure on the route and unlocks a "Demand Transit Reopening" move against the occupier.
- Concession state conquered by a third party fires a **Concession Fate** choice for the conqueror: *Honor Foreign Rights* (keeps peace/goodwill with investor) or *Seize Assets* (triggers Nationalization escalation against the conqueror, mirroring Japan seizing Dutch/British oil fields).
- Capitulation/exile immediately suspends active contracts via Force Majeure so exiled tags cannot bleed offsite factories or phantom resources.

### 2.7 Implementing "Close a Supply Route to Your Enemy" (Burma Road / Haiphong)
**Gap:** Section 6.12 lists closing a supply route to an enemy as a demand type, which is great flavor, but vanilla has no single "close transit route" effect.
**Handling:** Bundle real v1.20 effects on the pressured nation B against target C: `send_embargo = C`, `add_relation_rule_override = { target = C can_access_market = no can_send_volunteer = no }`, suspension of mod-tracked contracts and transit corridors between B and C (Force Majeure for C, plus grievance against the coercer), and cancellation of military access (`diplomatic_relation = { country = C relation = military_access active = no }`).

### 2.8 Performance: Scripted GUI per-tick re-evaluation and monthly lag spikes
**Gap:** Section 9 focuses on periodic scoring passes, which is sensible, but two common HoI4 performance traps remain unaddressed:
1. Scripted GUIs without a `dirty` variable re-evaluate every trigger and `dynamic_lists` array **every game tick** (`common/scripted_guis/_documentation.md:102-105`), which tanks FPS when a Trade Desk or Dossier is open.
2. Running a single `on_monthly` pass across 70+ countries x 7 resources x potential partners creates a noticeable stutter on the 1st of every month.
**Handling:** Require `dirty = <var>` on every scripted GUI (bumped only on data updates or clicks). Assign each country a static `pww_tick_bucket` (0 to 29) on `on_startup` and process ~2 to 3 countries per day on `on_daily`, restricting full bilateral AI-to-AI evaluation to the ~15 to 20 "Active Traders" (majors, top exporters, high-desperation industrializers) and using `common/collections/` where appropriate.

### 2.9 Why vanilla AI tolerates deficits (and how to fix it without bankrupting AI construction)
**Gap:** Goal 5 targets AI countries running at -200 steel. In `00_defines.lua:2414`, `TRADEABLE_FACTORIES_FRACTION` is already `0.8` (80% of CIVs), and `MIN_FACTORIES_TO_WANT_TO_IMPORT` is already `0` for everything except coal (`10`). Vanilla AI sits in huge deficits primarily because (a) wartime sea-lane loss and Closed Economy laws exhaust open-market supply, (b) low convoy efficiency triggers `convoy_efficiency_to_cancel_trades`, and (c) the AI cannot strike bilateral in-kind deals or develop foreign mines.
**Handling:** Do not just push `TRADEABLE_FACTORIES_FRACTION` higher (which starves AI repairs and construction). Instead, make high-Desperation AIs take three constructive actions: send **in-kind offers** (equipment, licenses, `add_equipment_subsidy`) when CIV-starved; fund **resource concessions/infrastructure** on friendly neighbors; and initiate **coercion campaigns** against reachable neutral exporters when open-market supply dries up.

### 2.10 Multiplayer desync safety and Human-as-Target coercion
**Gap:** Sections 6.5 through 6.8 mostly assume `human = seller/coercer, AI = counterparty`. Even in single-player, an AI major should be able to coerce a human minor (for example, Germany pressuring a player Sweden or Romania), and in multiplayer two humans may bid against each other or coerce each other.
**Handling:** Never place `random` or state-mutating logic in scripted GUI triggers/visibility blocks (prevents MP desyncs). Route player-targeted ultimatums, contracts, and auctions through the same unified Trade Desk Inbox + Alert Strip (or `common/scripted_diplomatic_actions/`, which handles MP networking and send/receive GUIs natively). Receiving a terrifying German ultimatum as a neutral player minor, then choosing whether to stall, play the Allies against Berlin, or harden like Switzerland, will be one of the best moments in the entire mod.

---

## 3. New ideas

1. **The "Economic Leverage" Custom Map Mode:** Give peacetime players a real strategic gameboard on the map itself. Toggle one map mode button to see global Desperation heat, your Dependency web, pulsing borders on states with foreign Concessions, and clickable icons on active Rail/Pipeline projects.
   *How to build:* Define an additive `scripted_map_modes` entry (`common/map_modes/`) using country colors for leverage/desperation and state borders (`highlighted = 1.0`) for concessions, paired with `state_mapicon` / `country_mapicon` scripted GUIs bound to `map_mode`.

2. **Preemptive "Shadow Buying" and Wartime Smuggling (The Wolfram War):** Let wealthy powers sign **Preemptive Denial** contracts that buy a neutral's surplus purely to lock it away from an enemy, even when the buyer already has a surplus. In response, let embargoed/blockaded powers hire a neutral land neighbor as a **Smuggling Middleman** at a steep markup, which gives the blockader an intel-gated reason to slap Secondary Sanctions on the middleman.
   *How to build:* Add a denial contract mode using `country_resource_cost_<res>` on the seller without requiring buyer deficit (adding heavy escalation weight on the denied rival), and allow embargoed AIs/players to propose high-markup transit contracts to neutral neighbors detectable when civilian intel (`CIVILIAN_MIN_INTEL_FOR_TRADE_ROUTES`) or `network_strength` crosses a threshold.

3. **Schachtian Clearing Agreements (Locked Arms Credits):** Instead of paying a minor in untied civilian factories, let industrial majors pay for oil, tungsten, or chromium in **Locked Equipment Subsidies** redeemable exclusively from the major's own arms market. The minor gets a modern army, the major's factories boom, and the minor's Dependency climbs fast because their armed forces now rely on the major's equipment ecosystem.
   *How to build:* Expose v1.20's `add_equipment_subsidy = { cic = X equipment_type = ... seller_tags = { ROOT } }` as a first-class contract payment option that ticks up the hidden `pww_dependency@ROOT` variable.

4. **Coercive "Crisis Table" and Rival Patron Intervention:** Turn loud ultimatums from a 1v1 meter into a live diplomatic crisis. When a coercer pushes a target to *Wavering* or issues a Loud Ultimatum, regional majors get a 21-day Crisis Alert with three choices: *Stay Out* (target feels abandoned and folds faster), *Diplomatic Warning* (stiffens target spine), or *Patron Backing* (deploys a counter-fleet or issues a guarantee, forcing the coercer to either back down for a Credibility hit or escalate toward war). Playing spoiler against a rival's shakedown becomes a fun non-war game on its own.
   *How to build:* On entering `Wavering` or `Loud Ultimatum`, filter regional majors by distance/faction/sphere and fire a targeted alert/event writing a temporary `pww_patron_backing` variable into target resistance plus optional `add_ai_strategy` (`naval_dominance` / `protect`).

5. **Dynamic Historical Flashpoints (6-8 Systemic Anchors):** Without adding railroaded popup spam, seed a handful of dynamic, condition-driven crises that showcase the mod's systems early: 1937 Bolivia vs. Standard Oil (first nationalization test), 1938 Mexico PEMEX, 1938 Gulf/Saudi Oil Concessions (early multi-major auction), 1939-1940 Anglo-German Coal-and-Ore Squeeze on Italy and Sweden, the 1940-1942 Iberian Wolfram Auction, and the 1940 Burma Road Closure crisis.
   *How to build:* Trigger via lightweight systemic checks (for example, major at war + tungsten deficit activates the Iberian Wolfram Auction) that open directly inside the existing Auction, Nationalization, and Coercion screens rather than bespoke event chains.

6. **Strategic Reserve Warehouses and Wartime Speculation:** Let peacetime merchants buy or divert cheap 1936-1938 oil, rubber, tungsten, and chromium into capped national stockpiles, then release them as high-value bursts during 1941-1943 auctions when desperate majors are offering naval blueprints and warships.
   *How to build:* Track capped per-resource reserve variables (`pww_reserve_<res>`) filled slowly via a Trade Desk `country_resource_cost_<res>` stance and discharged during contracts/auctions via temporary `add_resource = { type = X amount = Y days = 180 }` bursts.

7. **Capital Ships and Neutrality Guarantees as High-Tier Contract Currency:** Historically, resource-rich neutrals (Brazil, Argentina, Chile, Turkey, Sweden) traded raw materials for foreign-built cruisers/battleships and ironclad non-aggression pledges. Letting a desperate major with a surplus navy offer an actual warship (`transfer_ship`) or a binding Non-Aggression Pact for a 5-year monopoly lease makes mega-deals unforgettable.
   *How to build:* Add `transfer_ship` (`documentation/effects_documentation.md`) for wishlist-matching naval mega-deals and `diplomatic_relation = { relation = non_aggression_pact / guarantee active = yes }` as top-tier contract terms valued in hidden CFE.

---

## 4. Engine notes

All claims below were checked against the local HoI4 v1.20 installation (`C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV`) and Road to 56 (`workshop\content\394360\820260968`). Items requiring live in-game verification in Phase 0 are marked explicitly.

- **Seven resources, including `coal` and energy scaling (verified):**
  - `common/resources/00_resources.txt:38-42` defines `coal` (`icon_frame = 7`, `cic = 0.125`, `convoys = 0.1`).
  - `common/defines/00_defines.lua:627-632` defines `RESOURCE_TO_ENERGY_COEFFICIENT = 9.0`, `BASE_COUNTRY_ENERGY_PRODUCTION = 10.0`, `ENERGY_SCALING_COST_BY_FACTORY_COUNT = 0.0225`, and `ENERGY_SCALE_PER_TRADE_FACTORY_EXPORT = 0.25`.
  - `common/defines/00_defines.lua:3600-3608` lists 7 entries in `MIN_FACTORIES_TO_WANT_TO_IMPORT` (`0` for the original six, `10` for `coal`).
  - `documentation/dynamic_variables_documentation.md` confirms `energy_ratio` (`0..1`), and `documentation/modifiers_documentation.md` confirms `country_resource_coal`, `country_resource_cost_coal`, and `energy_scale_per_trade_factory_export_factor`.

- **Resolves Engine Unknowns 1 & 2 (Contracts and Variable Pricing):**
  - `documentation/modifiers_documentation.md` confirms `country_resource_<Resource>` and `country_resource_cost_<Resource>` for all 7 resources.
  - `common/dynamic_modifiers/TAOG_dynamic_modifiers.txt:95-96` and `common/dynamic_modifiers/wuw_dynamic_modifiers.txt:915` prove both keys accept script variables inside dynamic modifiers.
  - `common/decisions/SWI.txt:3326,3671` and `common/ideas/china_warlord.txt:946-1039` prove `cic_to_target_factor` and `mic_to_target_factor` work inside `targeted_modifier` blocks (including timed decisions).
  - `documentation/effects_documentation.md` confirms `add_cic`, `add_equipment_subsidy` (with `seller_tags`), `add_offsite_building`, `transfer_ship`, `create_production_license`, `steal_random_tech_bonus`, `give_market_access`, and `add_relation_rule_override` (`can_access_market`, `can_send_volunteer`, `can_not_declare_war`).
  - `create_import` appears in `documentation/effects_documentation.md` with zero vanilla usages, while `common/defines/00_defines.lua:2337-2345` confirms v1.20's `AUTO_IMPORT_*` system and `00_defines.lua:2415` confirms `MIN_DELIVERED_TRADE_FRACTION = 0.8`. **Guess to verify in Phase 0:** `create_import` is likely overridden by player auto-import or AI trade re-evaluation; building contracts on dynamic modifiers (`country_resource_<res>` / `country_resource_cost_<res>`) + `civilian_factory_use` / `add_offsite_building` / `add_cic` avoids this dependency completely.

- **Resolves Engine Unknown 3 (Foreign Construction Cost):**
  - `documentation/modifiers_documentation.md:2202` confirms `civilian_factory_use` as a country/war_production modifier.
  - `documentation/effects_documentation.md` confirms `build_railway` (`start_state`, `target_state`, `level`, `controller_priority`) and `add_building_construction` (state scope).
  - **Guess to verify in Phase 0:** Calling `add_building_construction` with `instant_build = no` on a foreign state likely places it in the *host's* construction queue rather than charging the investor. The clean, verified pattern is locking `civilian_factory_use = N` on the *investor* via a timed decision/modifier for 180 days, then spawning the completed building (`instant_build = yes`) or `build_railway` / `add_resource` in the host state on completion.

- **Resolves Engine Unknown 5 (Air, Naval, and Border Presence):**
  - `documentation/triggers_documentation.md` confirms `num_planes_stationed_in_regions = { value < 100 regions = { 18 47 } }` (checks aircraft **based at airfields** in those strategic regions, not planes flying peacetime missions over unowned territory), `ships_in_area`, `ships_in_state_ports`, `has_naval_control = <REGION_ID>` (line 4434), `has_enemy_naval_control = <REGION_ID>` (line 3846), `divisions_in_border_state`, `num_divisions_in_states`, `naval_strength_comparison`, and `network_strength`.
  - `documentation/dynamic_variables_documentation.md` confirms `num_ships_with_type@carrier`, `num_deployed_planes_with_type@<type>`, `convoy_threat`, and `fuel_ratio`.

- **Naval Blockade Constraints & AI Fleet Direction:**
  - `common/defines/00_defines.lua:272, 281-283` confirms `EMBARGO_THREAT_THRESHOLD = 30` and `NAVAL_BLOCKADE_THREAT_THRESHOLD = 15`.
  - `documentation/modifiers_documentation.md` confirms `embargo_threshold_factor` exists, while no equivalent blockade threshold modifier exists, and `documentation/effects_documentation.md` confirms no script effect starts a vanilla naval blockade.
  - `common/ai_strategy/_documentation.md:673-703` confirms both `type = naval_dominance` (`id = <region_id>`, `value = 0..100`) and `type = naval_blockade` (`target_country = TAG`, `id = <region_id>`, `value = 0..100`).

- **Additive UI, Alerts, Map Modes, and Performance:**
  - `common/scripted_guis/_documentation.md:10-37, 102-105` confirms `parent_window_token = top_bar`, `context_type = diplomacy_target_context` (`parent_window_token = selected_country_view_diplomacy`), and `dirty = <var>` (critical for avoiding per-tick UI re-evaluation).
  - `common/alerts.txt` is a closed engine alert table, so custom top-bar alerts should be rendered as a `parent_window_token = top_bar` scripted GUI strip rather than editing `topbar.gui` or `alerts.gui`.
  - `common/map_modes/documentation.md` confirms additive `scripted_map_modes`.
  - `common/scripted_diplomatic_actions/scripted_diplomatic_actions.txt` confirms custom diplomatic actions with `send_scripted_gui`, `receive_scripted_gui`, `ai_acceptance`, and `ai_desire`.

- **Road to 56 Compatibility Check:**
  - `workshop/content/394360/820260968/common/defines/r56_defines.lua:11-14, 293-295` doubles opinion range to `[-200, +200]` and sets AI fuel buffers to `365` days. R56 does not override `NTrade` or `DIPLOMATIC_ACTION_NAVAL_BLOCKADE_*` defines.

- **Still requires live Phase 0 verification (Unknowns 4 & 6):**
  - **Unknown 4 (resource rights & convoys):** Neither `effects_documentation.md` nor `triggers_documentation.md` specifies whether `give_resource_rights` consumes convoys or breaks under naval blockade (also note `triggers_documentation.md` explicitly warns `has_resources_rights` returns false if the state has 0 resources). **Guess:** In past HoI4 versions, resource rights bypassed standard trade-convoy raiding; if still true in v1.20, Phase 1 should explicitly check `has_enemy_naval_control` on the sea lane and suspend overseas concession deliveries during blockades/quarantines so naval power still matters.
  - **Unknown 6 (vanilla trade routing & railways):** `00_defines.lua:2332` sets `BASE_LAND_TRADE_RANGE = 1000`, and `00_defines.lua:14` sets `TRADE_ROUTE_RECALCULATE_FREQUENCY_DAYS = 45`. **Guess:** Vanilla trade routing checks land connectivity and distance rather than railway level; Rail Corridors and Pipelines should deliver their main payoff through the mod's own logistics discount, sea-to-land contract conversion, and dual-use supply benefits.

---

## 5. Your top 5

The five changes to make first, in order:

1. **Decouple Contracts from vanilla `create_import` by building them on v1.20's Dynamic Resource + CIC layer (`country_resource_<res>`, `country_resource_cost_<res>`, `civilian_factory_use`, `add_cic`, `add_equipment_subsidy`).** This immediately eliminates the two scariest engine unknowns (Unknowns 1 and 2), makes scarcity pricing and in-kind deals rock-solid, unlocks per-resource monopoly rationing, and keeps default background trade effortlessly low-micro on vanilla's auto-trade engine.
2. **Replace the 15%-WT vanilla blockade dependency with a mod-driven "Gunboat Quarantine" powered by `has_naval_control` / `ships_in_area` and sustained demonstration posture.** This unblocks peacetime coercion against 0-WT oil and metal exporters, integrates cleanly with AI `naval_dominance` strategies, and prevents instant fleet/air-teleport cheese.
3. **Add `coal` (and `energy_ratio`) as the 7th resource across the whole design.** It fixes a concrete v1.20 mechanical gap (export-factory energy scaling) and unlocks one of the richest historical coercion levers of the 1930s (coal-for-ore and energy strangulation).
4. **Make the peaceful trade-empire run sing in 1939-1945 with the Neutral Tightrope loop, Per-Resource Market Stances, Strategic Reserves, and Economic Hegemony milestones.** Without late-game stakes and capital sinks, half the mod's pitch runs out of gas the moment WWII begins; with them, playing Sweden, Turkey, Brazil, or a mercantile UK/USA stays gripping through 1945.
5. **Unify the UI into zero-conflict additive scripted GUIs (`parent_window_token = top_bar`, `diplomacy_target_context`, mandatory `dirty` flags) plus an "Economic Leverage" custom map mode, with qualitative causal tells and a Crisis Table for rival patrons.** This keeps 80-mod/R56 compatibility intact, removes the awkward split between custom windows and the Decisions tab, makes hidden math feel fair and thrilling at the brink of war, and turns the HoI4 map itself into a peacetime strategy board.
