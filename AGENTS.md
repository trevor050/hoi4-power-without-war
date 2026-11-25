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
**core provides**
- On startup: `pww_core_init` (sets `global.pww_initialized`, assigns each country `pww_bucket` 0..29, resolves map data).
- Daily staggered tick: on_daily runs countries whose `pww_bucket` equals `global.pww_day_mod30`, firing scripted effect hook `pww_on_country_tick` (other lanes append via their own scripted effect called from core's list: core calls `pww_ledger_country_tick` if defined; see core header).
- Monthly global hook: core calls `pww_ledger_monthly_tick`.
- Country vars: `pww_desp_<res>` (0..100 desperation), `pww_is_active_trader` flag.
- Map resolution: country array `pww_producing_states_<res>` (state scopes producing that resource), `pww_coastal_states`.
- Utility: `pww_norm_opinion` script value (opinion normalized to +-100).

**ledger provides**
- Agreements stored in global parallel arrays keyed by agreement id (see ledger header).
- Effects: `pww_ledger_create_agreement`, `pww_ledger_set_status`, `pww_ledger_recompute_flows` (per country), `pww_ledger_country_tick`, `pww_ledger_monthly_tick`.
- One dynamic modifier per country carrying all agreement flows (variable-driven).
- Status enum: 0 draft, 1 active, 2 suspended, 3 completed, 4 terminated, 5 defaulted, 6 nationalized, 7 reserved.

## Testing
See `tools/README.md` (harness lane) once it exists. Run the game headless against the mod; check `error.log` for `pww` lines and the `game.log` test output. Only one game instance at a time: the harness uses a lock file.
