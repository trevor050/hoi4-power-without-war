# Power Without War (HoI4 mod): agent notes

HoI4 v1.20 mod: trade empire + coercion short of war. Design: `docs/design/2026-11-25-power-without-war-design.md` (v2, approved). Council reviews: `docs/design/council/`.

## Layout
- `mod/`: the mod root (has `descriptor.mod`). Everything the game loads lives here.
- `tools/`: test harness (headless game runs). `tests/engine/`: Phase 0 engine test mods. `docs/engine/`: engine findings.
- Game install: `C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV` (script docs in `documentation\`). Road to 56: `...\workshop\content\394360\820260968`.
- Real user dir (DO NOT modify): `C:\Users\Trevor\Documents\Paradox Interactive\Hearts of Iron IV`. Tests use an isolated `-userdir=`.

## Hard rules
- Prefix every key, file, variable, flag, effect, trigger, modifier, loc key with `pww_`. Files: `pww_<lane>_<topic>.txt`.
- Additive only. Never overwrite a vanilla file path. No `replace_path`.
- Never hardcode state or strategic region IDs. Resolve at startup (owner, resources, coastal, adjacency). Road to 56 renumbers states and regions.
- Opinion inputs normalized to +-100 (R56 doubles range to +-200).
- No randomness in scripted GUI triggers/properties. Seed randomness in effects.
- Every scripted GUI uses a `dirty` variable.
- Localisation: `mod/localisation/english/pww_*_l_english.yml`, UTF-8 **with BOM**, header `l_english:`. No em dashes in player text.
- Do not `git commit`. The lead commits after review.
- Stay inside your lane's owned files. Need something from another lane: use its documented interface, or note the request in your report.

## Resource index (fixed)
0 oil, 1 aluminium, 2 rubber, 3 tungsten, 4 steel, 5 chromium, 6 coal.
Per-resource country variables use the resource name suffix: `pww_desp_oil`, `pww_desp_coal`, etc.

## Lane ownership (wave 1)
- **harness**: `tools/`, `tests/engine/`, `docs/engine/`.
- **core**: `mod/common/scripted_effects/pww_core_*`, `mod/common/scripted_triggers/pww_core_*`, `mod/common/script_values/pww_core_*`, `mod/common/on_actions/pww_core_*`, `mod/localisation/english/pww_core_*`.
- **ledger**: `mod/common/scripted_effects/pww_ledger_*`, `mod/common/scripted_triggers/pww_ledger_*`, `mod/common/script_values/pww_ledger_*`, `mod/common/dynamic_modifiers/pww_ledger_*`, `mod/common/on_actions/pww_ledger_*`, `mod/localisation/english/pww_ledger_*`.

## Cross-lane interfaces (contract; owners document final signatures in their files' headers)
**core provides** (full docs: header of `mod/common/scripted_effects/pww_core_effects.txt`)
- On startup: `pww_core_init` (idempotent; also run lazily from on_daily). Sets global flag + var `pww_initialized`, `global.pww_res_<res>` index vars, `global.pww_opinion_scale` (1 or 2), assigns each country `pww_bucket` 0..29, resolves map data.
- Daily staggered tick: on_daily runs `pww_core_country_tick` for countries whose `pww_bucket` equals `global.pww_day_mod30`; it refreshes map + desperation, then calls `pww_ledger_country_tick` (country scope). Core defines NO stub: ledger must define it.
- Monthly global hook: `pww_ledger_monthly_tick` (arbitrary country scope, >= 28 days apart, after active traders are recomputed). Ledger must define it.
- Country vars: `pww_desp_<res>` (0..100), `pww_desp_max`, `pww_desp_max_res` (index), flag `pww_is_active_trader` (+ `global.pww_active_traders` array, ~18).
- Map resolution: country arrays `pww_producing_states_<res>`, `pww_coastal_states` (owned states).
- Utility (HoI4 has no script_values folder; helpers are effects on temp vars): `pww_core_norm_opinion` (temp in `pww_opinion_target`, out `pww_norm_opinion`, +-100), `pww_core_norm_value`, `pww_core_value_to_band` (temp `pww_band_value` -> `pww_band` 0..4, loc `pww_core_band_N`).
- Triggers: `pww_core_is_initialized`, `pww_core_is_active_trader`, `pww_core_is_desperate_any`, `pww_core_has_deficit_<res>`, `pww_core_produces_<res>`. Debug: global flag `pww_core_debug` logs `PWW_CORE` lines to game.log.

**ledger provides**
- Agreements stored in global parallel arrays keyed by agreement id (see ledger header).
- Effects: `pww_ledger_create_agreement`, `pww_ledger_set_status`, `pww_ledger_recompute_flows` (per country), `pww_ledger_country_tick`, `pww_ledger_monthly_tick`.
- One dynamic modifier per country carrying all agreement flows (variable-driven).
- Status enum: 0 draft, 1 active, 2 suspended, 3 completed, 4 terminated, 5 defaulted, 6 nationalized, 7 reserved.

## Engine facts (verified in game, Phase 0: docs/engine/phase0-results.md)
- `on_startup` has NO scope and does not fire on save load. Wrap in `random_country`; make init idempotent with a lazy on_daily fallback.
- Scripted effects cannot take `$PARAM$` arguments in v1.20. Pass inputs via temp/global variables.
- Resource flows (`country_resource_cost_<res>` seller, `country_resource_<res>` buyer, variable-driven dynamic modifier) work and survive reload. Clamp seller cost to production. Buyer's received resource counts as production, so its export law re-exports part of it.
- Civ payment: `civilian_factory_use` (payer) + `add_offsite_building` (receiver). `cic_to_target_factor` does NOT work in a scoped dynamic modifier; `targeted_modifier` in a dynamic modifier fails to load.
- `send_embargo` works at 0 world tension (one-way, no PP). `break_embargo` only from the sender.
- Resource rights: output becomes receiver production; granting twice doubles; any owner/controller change destroys it. Delivery to USA silently failed (unexplained): verify delivery after granting.
- `has_naval_control` is always false in peacetime (needs patrol missions). Use `ships_in_area` (counts ships in port). AI naval strategies don't move fleets in peace.
- `send_equipment` works. `create_purchase_contract` needs 1..15 civs. `add_equipment_subsidy` effect unverified.
- Scripted GUI attachment to `trade_tab`, `top_bar`, `diplomacy_target_context` loads cleanly. Scripted diplomatic actions work AI to AI.
- No script trigger for sea regions adjacent to a state: use offline tables from `tools/map_tables.py` (vanilla and R56). POR tungsten states 112 and 181 in both maps.

## Testing
- Load test: `python tools/run_hoi4.py [--r56] [--days N]`. Scenario: `--test <dir>` (log `PWW_RESULT <t>.<check> PASS|FAIL|INFO`, end with `PWW_DONE <dirname>`). Exit 0 = clean.
- Tests live in `tests/<lane>/<name>/` (a mini mod with descriptor.mod). Never in a scratchpad.
- Isolation is via redirected USERPROFILE; the harness verifies the user's real files by sha256 after each run.
