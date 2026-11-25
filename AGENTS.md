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

## Wave 2 lanes (each in its own git worktree; the lead merges)
- **situations**: `pww_sit_*` across common/scripted_effects, scripted_triggers, on_actions, events (`mod/events/pww_sit_*.txt`, namespace `pww_sit`), decisions, localisation. Situation records, seats, clock, noise cap, resolution, the Wolfram Question anchor and its AI seat behavior.
- **coercion**: `pww_coer_*` (same folder pattern, events namespace `pww_coer`, plus `common/opinion_modifiers/pww_coer_*`). Demands, channels, pressure sources, committed forces, resistance, target states and reasons, Cornered, fig leaves, routes to war, quarantine, embargo rungs, credibility, regional alarm, pretexts.
- **diplomacy**: `pww_diplo_*` (scripted_diplomatic_actions, scripted_guis, `mod/interface/pww_diplo_*.gui`, `mod/gfx/interface/pww_diplo_*`, localisation). The scripted diplomatic actions with sender and receiver GUIs, negotiation (term cards, bands, seeded, 3 rounds, red lines and wants), patron pledges (reserved agreements), seller-written auctions.
- Every lane converts its own lines from `docs/content/*.md` into its own `pww_<lane>_*_l_english.yml` (keep the suggested key names).
- on_actions blocks from different files merge in HoI4, so each lane hooks on_daily/on_monthly in its own `pww_<lane>_on_actions.txt` and staggers with core's `pww_bucket` / `global.pww_day_mod30`.

## Wave 2 interface contract (owners finalize names in their file headers and in this section)
- Inputs to scripted effects are passed in temp variables (no `$PARAM$`). Country refs as variables (`set_temp_variable = { pww_in_target = FROM }`).
- **situations provides** (full docs: headers of `mod/common/scripted_effects/pww_sit_core.txt`, `pww_sit_ai.txt`, `pww_sit_outcomes.txt`, `pww_sit_wolfram.txt`). Global flag `pww_sit_loaded`.
  - `pww_sit_open` in: `pww_in_template` (0 generic, 1 Wolfram, 2 Wolfram renewal), `pww_in_claimant`, `pww_in_holder`, `pww_in_patron`, optional `pww_in_no_patron` (1 = none), `pww_in_resource` (0..6), `pww_in_days`, `pww_in_parent` (template 2). out: `pww_out_sit_id` (-1), `pww_out_result`, `pww_out_fail`, `pww_out_queued` (1 = noise cap). Prize = holder's owned+controlled producing states (core arrays), stored as **plain numeric state ids**.
  - `pww_sit_resolve` in: `pww_in_sit_id`, `pww_in_outcome` (1 split, 2 lease to claimant, 3 lease to patron, 4 holder holds out (pledge fires), 5 war, 6 renewed, 7 outbid, 8 reverted). Applies once (live only). `pww_sit_cancel`. `pww_sit_seat_of_this` (country; out `pww_out_seat`).
  - Inbound hooks: `pww_sit_on_bid` (`pww_in_sit_id`, `pww_in_bidder`, `pww_in_bid_band` 1..4), `pww_sit_on_pledge` (`pww_in_sit_id`, `pww_in_ag` = reserved ledger agreement or -1), `pww_sit_on_target_state` (`pww_in_sit_id`, `pww_in_demand_id`, `pww_in_tstate` 0..4, `pww_in_public`), `pww_sit_on_hardened` (`pww_in_sit_id`).
  - Calls out (via `meta_effect`, guarded): `pww_coer_issue_demand` (type 1, `pww_in_res`, `pww_in_days`, `pww_in_term`, `pww_in_state`) under `pww_coer_loaded`. Under `pww_diplo_loaded` AI seats set intents (country flags `pww_sit_ai_wants_bid` / `pww_sit_ai_wants_pledge`, var `pww_sit_ai_sit`) and wait `global.pww_sit_c_diplo_grace` (21) days before acting directly.
  - Triggers: `pww_sit_is_live`, `pww_sit_is_valid`, `pww_sit_is_queued`, `pww_sit_this_has_seat`, `pww_sit_has_live` (temp `pww_in_sit_id`).
  - Records: global arrays `global.pww_sit_<field>^id` (template, status 0 queued/1 live/2 resolved/3 cancelled, claimant, holder, patron, has_patron, res, days_left, dev, phase, tstate, pledge, outcome, ...); prize entries `global.pww_sitp_{sit,state,lot,amt,ag,to}`. `global.pww_sit_live`. Outcome queue `global.pww_sitq_*`.
  - UI rows: country array `pww_my_situations` = LIVE ids only (one alert row each); dirty var `global.pww_sit_rev`; alert key by seat/phase/tstate/pledge in the core header; dev line loc `pww_sit_dev_<n>`. Noise cap `global.pww_sit_c_cap` (4) live situations per human seat holder; excess queues and goes live (full clock) when a slot frees.
  - Seat enum: 0 claimant, 1 holder, 2 patron. Events namespace `pww_sit` (human seats only).
- **coercion provides** (full docs: header of `mod/common/scripted_effects/pww_coer_core.txt`; ladder in `pww_coer_ladder.txt`, reputation in `pww_coer_rep.txt`). Global flag `pww_coer_loaded`. Every effect sets `pww_out_result` (1/0) and `pww_out_fail`.
  - `pww_coer_issue_demand` in: `pww_in_claimant`, `pww_in_target`, `pww_in_sit_id` (**-1 for none**; unset reads 0 = situation 0), `pww_in_demand_type` (0 output share, 1 named-state lease, 2 cutoff of a third party), `pww_in_channel` (0 quiet, 1 public); optional `pww_in_res`, `pww_in_share` (default 0.25), `pww_in_state`, `pww_in_third`, `pww_in_days` (default 120), `pww_in_term` (default 365). out: `pww_out_demand_id` (-1 refused).
  - `pww_coer_commit_force` in: `pww_in_demand_id`, `pww_in_force_type` (1 naval, 2 air, 3 army). One force per demand; one live commitment per force type per claimant. `pww_coer_release_force`.
  - `pww_coer_target_respond` in: `pww_in_demand_id`, `pww_in_response` 0 fold, 1 smaller lot, 2 90-day provisional (ledger timed clause), 3 own fig leaf (`pww_in_fig_leaf` 1..4), 4 call patron, 5 harden, 6 refuse, 7 stall (quiet only). `pww_coer_claimant_respond` in: `pww_in_demand_id`, `pww_in_response` 0 accept counter, 1 reject, 2 offer fig leaf (`pww_in_fig_leaf` 1 token purchase, 2 joint commission, 3 assurance, 4 temporary), 3 withdraw, 4 go public, 5 take less.
  - Ladder: `pww_coer_cutoff` (`pww_in_cut_mode` 0 supplies/1 purchases/2 both, `pww_in_res` -1 all), `pww_coer_embargo`, `pww_coer_lift_embargo`, `pww_coer_join_embargo_ask` / `_reply` / `pww_coer_punish_noncompliance` (`pww_in_third`, `pww_in_comply`), `pww_coer_declare_quarantine`, `pww_coer_lift_quarantine`. All take `pww_in_demand_id`. `pww_coer_grant_pretext` (`pww_in_claimant`, `pww_in_target`), `pww_coer_set_rival`.
  - **Fold creates the ledger agreement** (supply or lease, committal, the demand's term; token purchase = 1 civ; temporary = 180-day revert). Callers must not create it too. Demands with a valid situation id instead call `pww_sit_resolve` outcome 2 (the situation applies the lease) and report shifts via `pww_sit_on_target_state` / `pww_sit_on_hardened` (called through `meta_effect`).
  - Records: global arrays `global.pww_cd_<field>^id` (fields in `pww_coer_storage.txt`): `status` (0 live, 1 folded, 2 lapsed/refused, 3 withdrawn, 4 war route, 5 provisional, 6 void), `tstate` 0 Defiant .. 4 Ready, `prev`, `cause`/`cause_side`, reason slots `for0..3` / `hold0..3` (strongest first; ids listed in the core header, loc `pww_cause_for_*` / `pww_cause_against_*`), `warn` (Cornered line), `intel`, `route`. `global.pww_coer_live`, country array `pww_coer_dem_ids`. Event queue `global.pww_cq_*`.
  - GUI: `pww_coer_load_readout` (viewer scope, in `pww_in_demand_id`) fills `pww_coer_rd_*` + `pww_patron`/`pww_rival`; scripted loc `[pww_coer_loc_state]`, `[pww_coer_loc_for_0..3]`, `[pww_coer_loc_hold_0..3]`, `[pww_coer_loc_cornered]`, `[pww_coer_loc_intel]`, `[pww_coer_loc_shift]`, `[pww_coer_loc_cred_band]`, `[pww_coer_loc_alarm_band]` (FROM = target).
  - Country vars: `pww_credibility` (0..100, coercion writes), `pww_alarm@<claimant>` on observers (0..100), flags `pww_coer_quarantined`, `pww_coer_humiliated`, array `pww_coer_pretexts`. Trigger `pww_coer_target_quarantined` (diplomacy: a quarantined holder's pledged deal is undeliverable).
  - **Reads from diplomacy**: target country vars `pww_patron_pledge_strength` (0..100) and optional `pww_patron_pledge_patron` (country; else a major guarantor is shown as patron).
  - Map: `tools/pww_coer_gen.py` regenerates `pww_coer_map_data.txt` (per-state seas, land region, air regions, vanilla + R56, picked by state count), the readout scripted loc and the readout/reputation loc files. Ships in port count in the port's **land** region (`ships_in_area`), so approaches = adjacent seas + the coastal states' land regions.
- **diplomacy provides**: the scripted diplomatic actions; it calls ledger (`pww_ledger_create_agreement`), coercion (`pww_coer_issue_demand`, `pww_coer_target_respond`) and situations (`pww_sit_*`). Where a callee is not yet available in your worktree, call it anyway per this contract and note it; the lead integrates.

## Engine facts (verified in game, Phase 0: docs/engine/phase0-results.md)
- `on_startup` has NO scope and does not fire on save load. Wrap in `random_country`; make init idempotent with a lazy on_daily fallback.
- Scripted effects cannot take `$PARAM$` arguments in v1.20. Pass inputs via temp/global variables.
- Resource flows (`country_resource_cost_<res>` seller, `country_resource_<res>` buyer, variable-driven dynamic modifier) work and survive reload. Clamp seller cost to production. Buyer's received resource counts as production, so its export law re-exports part of it.
- Civ payment: `civilian_factory_use` (payer) + `add_offsite_building` (receiver). `cic_to_target_factor` does NOT work in a scoped dynamic modifier; `targeted_modifier` in a dynamic modifier fails to load.
- `send_embargo` works at 0 world tension (one-way, no PP). `break_embargo` only from the sender.
- Resource rights: output becomes receiver production; granting twice doubles; any owner/controller change destroys it. Delivery to USA silently failed (unexplained): verify delivery after granting.
- `has_naval_control` is always false in peacetime (needs patrol missions). Use `ships_in_area` (counts ships in port). AI naval strategies don't move fleets in peace.
- Ships in port count in the port's LAND strategic region for `ships_in_area`, not the adjacent sea. AI fleets return home in peace, so AI naval demonstrations only count docked ships. Use `any_home_area_neighbor_country` for real neighbors (`is_neighbor_of` counts colonies).
- Unset temp variables read 0: use -1 for "none" ids (e.g. `pww_in_sit_id = -1`).
- `send_equipment` works. `create_purchase_contract` needs 1..15 civs. `add_equipment_subsidy` effect unverified.
- Scripted GUI attachment to `trade_tab`, `top_bar`, `diplomacy_target_context` loads cleanly. Scripted diplomatic actions work AI to AI.
- No script trigger for sea regions adjacent to a state: use offline tables from `tools/map_tables.py` (vanilla and R56). POR tungsten states 112 and 181 in both maps.

## Testing
- Load test: `python tools/run_hoi4.py [--r56] [--days N]`. Scenario: `--test <dir>` (log `PWW_RESULT <t>.<check> PASS|FAIL|INFO`, end with `PWW_DONE <dirname>`). Exit 0 = clean.
- Tests live in `tests/<lane>/<name>/` (a mini mod with descriptor.mod). Never in a scratchpad.
- Isolation is via redirected USERPROFILE; the harness verifies the user's real files by sha256 after each run.
