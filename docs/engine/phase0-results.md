# Phase 0 engine results (HoI4 v1.20.0.0.8873)

All evidence comes from real game runs through `tools/run_hoi4.py` on 2026-11-25 (vanilla unless
marked R56), using the throwaway test mods in `tests/engine/`. Numbers are read in game via
dynamic variables (`resource_produced@X`, `resource@X`, `resource_exported@X`,
`resource_imported@X`, `modifier@X`, `num_of_*_factories`, `num_equipment@X`) and logged to
`game.log`. Run logs: `.hoi4-userdir/runs/` (local, gitignored).

## Verdicts

| # | Question | Verdict |
|---|---|---|
| 1 | Seller `country_resource_cost_<res>` + buyer `country_resource_<res>` (variable-driven dynamic modifiers) | **Works**, with two caveats (buyer export leak, no clamp) |
| 7 | `send_embargo` against a target with 0 generated tension | **Works** (no PP cost, one-way); `break_embargo` needs ROOT = sender |
| 5 | `give_resource_rights` / `remove_resource_rights` | **Partial**: works for some receivers, silently delivers nothing to USA; rights are destroyed by any controller or owner change |
| 2 | `civilian_factory_use` + `add_offsite_building` vs `cic_to_target_factor` | A **works**; dynamic modifier with `scope =` **does not**; idea `targeted_modifier` **works** (fixed tag); `targeted_modifier` in a dynamic modifier **fails to load** |
| 9 | Dynamic discovery of POR tungsten states and adjacent sea regions | States, amounts, land region, coastal: **works in script** (vanilla and R56). Sea regions: **no script path**; offline tables via `tools/map_tables.py` |
| 3 | Scripted diplomatic actions, AI to AI | **Works** (loads clean; ITA sent, HUN accepted within a day; vanilla and R56) |
| 4 | `send_equipment` tranches, `add_equipment_subsidy`, `create_purchase_contract` with 0 civs | `send_equipment` **works** (clamped to stock); subsidy **loads, effect unmeasured**; contract with 0 civs **does not work** (range is (0,15]); 1 civ failed for a buyer with no free civs |
| 6 | `ships_in_area` in port, peacetime `has_naval_control`, planes, AI naval strategies | `ships_in_area` and `num_planes_stationed_in_regions` **work** (ships in port count); `has_naval_control` is **always false in peacetime**; `naval_dominance`/`naval_blockade` **did not move fleets** in 27 peacetime days |
| 8 | Scripted GUI attachment (`trade_tab`, `top_bar`, `diplomacy_target_context`) | **Works** (no load errors; all three visible in screenshots) |

Cross-cutting engine facts found on the way (these affect every lane):
- **`on_startup` has no scope.** Calling a scripted effect directly in it errors with
  `Invalid Scope ... provided: None`. Wrap it in a country scope (vanilla uses `TAG = { }` blocks).
  This currently breaks `pww_core_init` and `pww_ledger_init` (`pww_core_on_actions.txt:18`,
  `pww_ledger_on_actions.txt:18`).
- **`on_startup` does not fire when a save is loaded** (verified by a reload). Init must be
  idempotent and guarded by a global flag, and anything that must run after a load (for example
  `force_update_dynamic_modifier`) needs another trigger, such as the first `on_daily` pulse.
- **Scripted effects take no parameters.** `my_effect = { LABEL = x }` with `$LABEL$` in the body
  fails to parse (`Invalid effect 'LABEL'`). Use variables or separate effects.
- `meta_trigger` with `"[?global.var|0]"` substitution works and lets literal-only triggers
  (`region = N`, `ships_in_area area = N`, `has_naval_control = N`, `has_resources_amount amount > N`)
  take computed values. Loops of 300 to 400 iterations of this ran without noticeable cost.
- Loc in `log`: `[THIS.GetID]` prints a state id. `[?var|0]` on a variable holding a **state
  scope** prints garbage (`-10737`); use `GetID`/`GetName`.
- Dynamic modifiers and their variables persist through save and reload; the save stores the
  modifier with its last evaluated value (`value={ 89.5 }`).

---

## 1. Resource flows via variable-driven dynamic modifiers (priority 1)

**Question.** Does a seller-side `country_resource_cost_tungsten` plus a buyer-side
`country_resource_tungsten`, both driven by variables, move tungsten? How do they interact with
production, the seller's exportable pool, export laws, player auto-import, save and reload?

**Method.** `tests/engine/t1_resource_flows`. Seller POR (player), buyer GER (AI). Day 3: both
modifiers added, variable = 0.5 x POR production (89.5), `force_update_dynamic_modifier`.
Snapshots on days 2 to 38. Day 15: POR trade law changed to free trade. Day 33: flow set to 0.
Day 36: flow set to 2 x production (358). Monthly autosave, then a second session with
`-continuelastsave`.

**Evidence.**

| day | POR produced / surplus / exported | GER produced / surplus / exported | note |
|---|---|---|---|
| 2 | 179 / 90 / 89 | 5 / 0 / 1 | baseline; POR export_focus, GER limited_exports |
| 4 to 14 | 90 / 45 / 45 | 95 / 67 / 24 | flow 89.5 applied within a day |
| 16 to 32 | 90 / 18 / 72 | 95 / 67 / 24 | POR on free trade |
| 35 | 179 / 36 / 143 | 5 / 0 / 1 | flow 0: fully reverted within 2 days |
| 38 | -179 / -179 / 0 | 363 / 268 / 91 | flow 358 (2 x production): seller goes negative |

Reload session (loaded the 1 Feb autosave, day 31): `t1.persist PASS` with cost 89.5 and gain 89.5,
and POR produced 90 / GER produced 95 on the first snapshot after load.

**Verdict: works.**
- The seller cost is subtracted from **`resource_produced`** (179 to 90), so the export law then
  applies to the reduced production: the cost **does remove supply from the exportable pool**
  (export_focus exported 89 to 45; free trade 143 to 72).
- The buyer gain is added to **`resource_produced`** and is therefore **subject to the buyer's
  export law**: GER exported 24 of its +90 (limited_exports, 25%). Part of every delivery leaks
  back into vanilla trade.
- No clamping: a cost above production drives production and surplus negative (shortage penalties).
- `modifier@country_resource_cost_tungsten` reads the live value.
- Persists through save and reload.
- Player auto-import: **not exercised.** The Trade tab shows an "Automatic Importing" toggle that
  is off by default (see `img/t8_trade_tab.png`); it needs a UI click per player.

**Recommended implementation.** Keep the design's single per-country dynamic modifier carrying
`country_resource_cost_<res>` (seller) and `country_resource_<res>` (buyer). Clamp the seller
amount in script to at most `resource_produced@<res>` (measured before the agreement's own cost,
so track the mod's own committed cost per resource) and treat the clamp as a shortfall. To
compensate the buyer export leak, either gross up the buyer amount by `1 / (1 - export share of
its trade law)`, or accept the leak and state it in the UI. Call `force_update_dynamic_modifier`
after every variable change.

## 7. `send_embargo` below the world-tension threshold (priority 2)

**Question.** Does `send_embargo` apply against a target that generated no world tension
(the diplomatic action needs 30)?

**Method.** `tests/engine/t7_embargo`. Day 3: `FRA = { send_embargo = YUG }` and
`USA = { send_embargo = SWI }`. Checks with `is_embargoed_by` / `is_embargoing` on days 4 to 22.
Day 21: `break_embargo` run once from FRA's own `on_daily` (ROOT = FRA) and once as
`USA = { break_embargo = SWI }` from GER's `on_daily` (ROOT = GER).

**Evidence.** World tension 0 throughout. Day 4 onwards: YUG `is_embargoed_by` FRA = yes,
FRA `is_embargoing` YUG = yes, SWI embargoed by USA = yes (`t7.applies PASS`). YUG
`is_embargoing` FRA stayed no. FRA political power kept rising (0.39, 0.79, 1.97 ...): no 100 PP
`EMBARGO_COST` charged. Day 22: FRA/YUG cleared; USA/SWI still present (ROOT was GER).

**Verdict: works.** It bypasses the threshold, costs nothing, and is one-directional.
`break_embargo` works only when ROOT is the sender ("breaks an existing embargo from ROOT").

**Recommended implementation.** Use `send_embargo` for leak and quarantine embargoes; charge any
PP cost in script. To lift one, run `break_embargo` in an effect where ROOT is the sender (for
example from the sender's own `on_daily` branch, or `country_event` to the sender). Track the
embargo in the ledger, since only the sender/target triggers exist.

## 5. Resource rights (priority 3)

**Question.** Who gets the output, do deliveries use convoys, what happens on occupation and owner
change, and does removal clean up?

**Method.** `tests/engine/t5_resource_rights` and `t5b_rights_filter`. Host TUR (chromium).
States picked dynamically: Ankara/Kayseri (inland), Antalya, Bursa, Izmir (coastal). Grants to GER
(land route), USA (overseas, ~600 convoys) and HAI (overseas, 4 to 5 convoys). Duplicate grant then
a single removal, controller change (to SOV), owner change (to BUL/GRE and back), removal.
Per-state delivery read with `has_resources_amount = { delivered = yes }` via `meta_trigger`.

**Evidence.**
- GER (Ankara, unfiltered): GER produced 5 to 20 (+15); Ankara delivered to TUR 17 to 0.
  GER (Kayseri, `resources = { chromium }`): 5 to 36. The output is **receiver production**
  (so the receiver's export law applies: GER exported 25%).
- HAI (Bursa, base 50): HAI produced 3 to 54 with 4 to 5 convoys, convoy count unchanged.
- USA (Antalya filtered in one run, Izmir unfiltered in another): USA produced stayed 1 in both;
  its `imported` 8 is normal AI trade covering a pre-existing deficit. TUR still lost the state's
  output (300 to 178/191). **The output vanished.**
- Duplicate grant: GER produced 20 to 34, so **duplicates stack**. One `remove_resource_rights`
  cleared both (`t5.dup_single_remove PASS`).
- Controller change to SOV: `has_resources_rights` false at once, the controller gets the output.
  After control returned to TUR, the right was **still gone**. Owner change (BUL/GRE): same.
- Removal: `HOLDER = { remove_resource_rights = <state var> }` clears it (accepts a variable),
  and the output returns to the host within 2 days (`t5.cleanup PASS`).
- `has_resources_rights` without `resources = {}` checks all of the state's resources, so a
  chromium-only right on a multi-resource state reads false. Pass `resources = { <res> }`.

**Verdict: partial.** Rights deliver as receiver production without visible convoy use (HAI), but
delivery to USA failed silently in two runs (cause not found: candidates are a USA idea/law or
route reachability). Any controller or owner change destroys the right permanently.

**Recommended implementation.** One lease per (holder, state): always check
`has_resources_rights = { receiver = X resources = { <res> } }` before granting (duplicates stack
output). After granting, verify delivery a few days later (receiver `resource_produced@<res>`
delta vs the state's delivered amount) and treat zero as a failed delivery (revert, refund, or
fall back to a supply agreement through dynamic modifiers). Reconciliation must expect rights to
vanish on **any** controller change, not just ownership: on `on_state_control_changed` or the
periodic check, re-grant when control returns, rather than classifying it as nationalization.
**Open item:** find why USA receives nothing (test other overseas majors, and USA after
removing its starting ideas).

## 2. Factory flows (priority 4)

**Question.** Payer `civilian_factory_use` + receiver `add_offsite_building` (with removal), vs
`cic_to_target_factor` in a dynamic modifier with `scope =`, or via an idea `targeted_modifier`.

**Method.** `tests/engine/t2_factories`. Payer ITA, receiver HUN. A: `civilian_factory_use = 3`
(variable) + `add_offsite_building = { type = industrial_complex level = 3 }`, removed with
`level = -3`. B: dynamic modifier `cic_to_target_factor = 0.1` added with `scope = HUN`. C: idea
with `targeted_modifier = { tag = HUN cic_to_target_factor = 0.1 }`. D: `targeted_modifier`
block inside a dynamic modifier.

**Evidence.**
- A: ITA `modifier@civilian_factory_use` 0 to 3, ITA factories for projects 11 to 0; HUN
  civilian factories 10 to 13, total 17 to 20. After removal HUN back to 10.
- B: no change on either side (ITA 21 civs / 56 factories, HUN 10 / 17).
- C: ITA civs 21 to 19 (factories 56 to 54, controlled stays 56); HUN civs 10 to 12 (17 to 19).
- D: load error `invalid modifier: targeted_modifier` in `dynamic_modifiers`.
- Caveat: ITA's `civilian_factory_use` read 5 after our removal (a vanilla ITA source added 5;
  ITA was a noisy pick). Our own add and remove behaved as expected.

**Verdict.** A works and is variable-driven on the payer side. B does not work. C works but its
target tag is fixed in the idea. D does not load.

**Recommended implementation.** Use A for factory flows: payer `civilian_factory_use` in the
per-country dynamic modifier, receiver `add_offsite_building` with an integer level (track the
level granted per agreement and remove it with a negative level). Use C only for a fixed pair
(an idea per target tag) if a percentage transfer is wanted.

## 9. Dynamic discovery (priority 5)

**Question.** Can script find POR's tungsten states and the strategic regions around them, in
vanilla and with R56?

**Method.** `tests/engine/t9_discovery`, run in vanilla and with `--r56`.
`every_owned_state` + `has_resources_amount`, a `meta_trigger` scan of `region = 1..400`,
`is_coastal`, a state count fingerprint. Offline: `tools/map_tables.py`.

**Evidence.**

| | vanilla | R56 |
|---|---|---|
| state count (fingerprint) | 1081 | 1143 |
| tungsten states | 112 Lisbon (55), 181 Guarda (123) | 112 Lisbon (87), 181 Guarda (195) |
| land region (both) | 209 | 209 |
| coastal | Lisbon yes, Guarda no | same |
| sea approaches (offline) | Lisbon: 47 Spanish Coast | same |

Amounts in game include modifiers (file values 32/95 vanilla, 50/150 R56). `random_scope_in_array`
over a state array works. Island states (Madeira, Azores) report a sea region as their region.

**Verdict.** States, amounts, land region and coastal flag: **works in script** under both.
Adjacent sea regions: **no trigger exists**; `tools/map_tables.py` computes them from the map
files for either variant.

**Recommended implementation.** Resolve producing states at startup in script (as designed). For
sea approaches, generate a table per map variant with `tools/map_tables.py` into a generated
scripted effect, and pick the variant at runtime by the state-count fingerprint (1081 vanilla,
1143 R56; unknown count means unsupported map, so disable sea-presence features).

## 3. Scripted diplomatic actions

**Method.** `tests/engine/t3_diplo_actions`: minimal action with `ai_desire` 1000 for ITA to HUN,
`ai_acceptance` base 100.

**Evidence.** No load errors. Vanilla and R56: ITA sent on 2 Jan 02:00, HUN accepted at 03:00
(`t3.accepted PASS`). Sender and receiver GUIs and the player-facing button were not inspected
visually.

**Verdict: works** for AI to AI. **Recommended:** usable for Offers and Demands. The AI acted
within a day of `ai_desire` turning positive, so gate repeat sends with `allowed`/flags.

## 4. Equipment

**Method.** `tests/engine/t4_equipment`: ENG to IRQ `send_equipment` 500 infantry equipment on
days 3 and 5, an over-ask of 1,000,000 on day 7, then `add_equipment_subsidy` (cic 100,
`seller_tags = { ENG }`) and `create_purchase_contract`.

**Evidence.** IRQ stockpile + in-army infantry equipment 847 to 1862 by day 6 (both tranches
arrived within 1 to 3 days). Over-ask drained ENG's stockpile to 0. `create_purchase_contract`
with `civilian_factories = 0`: error `should be in range (0,15]`. With 1: `Can not make the
contract` (IRQ had 0 free civilian factories). The subsidy produced no error; its effect was not
measured (no contract formed).

**Verdict.** `send_equipment` works for tranches (sends what exists; check stock first).
Contracts need 1 to 15 civilian factories, and the buyer probably needs them free: **not usable
as a free transfer.** Subsidy: unverified.

## 6. Presence detection

**Method.** `tests/engine/t6_naval_presence`: scanned regions 1..310 with `ships_in_area`,
`has_naval_control`, `num_planes_stationed_in_regions` for ENG, ITA, FRA on day 2 (all fleets in
port), then `add_ai_strategy` naval_dominance (ITA) / naval_blockade (FRA) on region 47, rescans
on days 15 and 30.

**Evidence.** Day 2: ENG ships counted in 14 regions (for example 49 in region 16, 41 in 18),
so ships in port count. `has_naval_control` = 0 in every region for all three (the in-game tooltip
says control counts only ships on patrol missions, minimum 375; `img/t6_naval_control_tooltip.png`).
Planes found in the expected home regions. Neither ITA nor FRA had any ship in region 47 by day 30,
though their fleets moved between home regions.

**Verdict.** `ships_in_area` (typed and untyped) and `num_planes_stationed_in_regions` work in
peace. `has_naval_control` is useless in peace unless ships run missions. AI naval strategies did
not produce a peacetime deployment.

**Recommended implementation.** Measure committed squadrons with `ships_in_area` (counting
port-based ships in the region, or require the player's own count above a threshold). Do not
use `has_naval_control` for peacetime pressure. For AI coercers, do not rely on AI strategies
to move fleets; either accept "committed in port" or teleport/spawn a token force in script.

## 8. Scripted GUI attachment

**Method.** `tests/engine/t8_scripted_gui`: three buttons with `parent_window_token = trade_tab`,
`parent_window_token = top_bar`, and `context_type = diplomacy_target_context` (no parent token),
each with a `dirty` variable. Game left running and driven with clicks.

**Evidence.** No error.log lines. Screenshots: `img/t8_top_bar.png` (button in the top bar),
`img/t8_trade_tab.png` (button inside the Trade tab), `img/t8_diplo_target.png` (button shown
once a foreign country is selected; without a parent token it anchors to the main window).

**Verdict: works.** For the diplomacy surface, add
`parent_window_token = selected_country_view_diplomacy` to anchor inside the diplomacy panel
(not tested).

## Not verified / open

- Player auto-import interaction with buyer flows (needs the Trade tab toggle).
- Why USA receives nothing from resource rights.
- `add_equipment_subsidy` effect; a successful `create_purchase_contract`.
- Scripted diplomatic action GUIs as seen by a player, and under R56's diplomacy view (R56 load
  and AI path verified).
- `diplomacy_target_context` with `selected_country_view_diplomacy` placement.
