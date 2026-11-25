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

## Lanes (file prefixes; each lane documents its interface in its file headers)
- **harness**: `tools/run_hoi4.py`, `tools/map_tables.py`, `tests/engine/`, `docs/engine/`.
- **core** `pww_core_*`, **ledger** `pww_ledger_*`, **situations** `pww_sit_*` (events ns `pww_sit`), **coercion** `pww_coer_*` (events ns `pww_coer`, opinion modifiers, generator `tools/pww_coer_gen.py`), **diplomacy** `pww_diplo_*` (scripted diplomatic actions, loc generator `tools/pww_diplo_gen_loc.py`), **UI** `mod/interface/*`, `mod/gfx/`, `mod/common/scripted_guis/*`, `pww_ui_*`, `tests/ui/`.
- Each lane hooks on_daily/on_monthly in its own `pww_<lane>_on_actions.txt` (on_actions blocks merge) and staggers with core's `pww_bucket` / `global.pww_day_mod30`.
- Cross-lane calls go through `meta_effect = { text = { <effect> = [Y] } Y = "yes" }` under the callee's `pww_<lane>_loaded` global flag, so each lane loads alone.
- Generated loc: edit the generators, not the yml (`pww_coer_readouts/_reputation` from `docs/content/*.md`; `pww_diplo_*` yml). Content bible keys keep their names.

## Core and ledger interfaces
**core provides** (full docs: header of `mod/common/scripted_effects/pww_core_effects.txt`)
- On startup: `pww_core_init` (idempotent; also run lazily from on_daily). Sets global flag + var `pww_initialized`, `global.pww_res_<res>` index vars, `global.pww_opinion_scale` (1 or 2), assigns each country `pww_bucket` 0..29, resolves map data.
- Daily staggered tick: on_daily runs `pww_core_country_tick` for countries whose `pww_bucket` equals `global.pww_day_mod30`; it refreshes map + desperation, then calls `pww_ledger_country_tick` (country scope). Core defines NO stub: ledger must define it.
- Monthly global hook: `pww_ledger_monthly_tick` (arbitrary country scope, >= 28 days apart, after active traders are recomputed). Ledger must define it.
- Country vars: `pww_desp_<res>` (0..100), `pww_desp_max`, `pww_desp_max_res` (index), flag `pww_is_active_trader` (+ `global.pww_active_traders` array, ~18). Test hook: country var `pww_desp_floor_<res>` floors the recomputed desperation.
- Map resolution: country arrays `pww_producing_states_<res>`, `pww_coastal_states` (owned states).
- Utility (HoI4 has no script_values folder; helpers are effects on temp vars): `pww_core_norm_opinion` (temp in `pww_opinion_target`, out `pww_norm_opinion`, +-100), `pww_core_norm_value`, `pww_core_value_to_band` (temp `pww_band_value` -> `pww_band` 0..4, loc `pww_core_band_N`).
- Triggers: `pww_core_is_initialized`, `pww_core_is_active_trader`, `pww_core_is_desperate_any`, `pww_core_has_deficit_<res>`, `pww_core_produces_<res>`. Debug: global flag `pww_core_debug` logs `PWW_CORE` lines to game.log.

**ledger provides**
- Agreements stored in global parallel arrays keyed by agreement id (see ledger header).
- Effects: `pww_ledger_create_agreement`, `pww_ledger_set_status`, `pww_ledger_recompute_flows` (per country), `pww_ledger_country_tick`, `pww_ledger_monthly_tick`.
- One dynamic modifier per country carrying all agreement flows (variable-driven).
- Status enum: 0 draft, 1 active, 2 suspended, 3 completed, 4 terminated, 5 defaulted, 6 nationalized, 7 reserved.

## Interface contract (owners keep names in their file headers and here)
- Inputs to scripted effects are passed in temp variables (no `$PARAM$`). Country refs as variables (`set_temp_variable = { pww_in_target = FROM }`). "No situation" is `pww_in_sit_id = -1`, set explicitly (unset reads 0 = situation 0).
- State refs handed to the ledger, `meta_effect` text or other lanes are plain numeric ids. Core's `pww_producing_states_<res>` / `pww_coastal_states` hold state scopes: convert with `meta_effect = { text = { set_temp_variable = { x = [ID] } } ID = "[THIS.GetID]" }` in state scope.
- **situations provides** (full docs: headers of `mod/common/scripted_effects/pww_sit_core.txt`, `pww_sit_ai.txt`, `pww_sit_outcomes.txt`, `pww_sit_wolfram.txt`). Global flag `pww_sit_loaded`.
  - `pww_sit_open` in: `pww_in_template` (0 generic, 1 Wolfram, 2 Wolfram renewal), `pww_in_claimant`, `pww_in_holder`, `pww_in_patron`, optional `pww_in_no_patron` (1 = none), `pww_in_resource` (0..6), `pww_in_days`, `pww_in_parent` (template 2). out: `pww_out_sit_id` (-1), `pww_out_result`, `pww_out_fail`, `pww_out_queued` (1 = noise cap). Prize = holder's owned+controlled producing states (core arrays), stored as **plain numeric state ids**.
  - `pww_sit_resolve` in: `pww_in_sit_id`, `pww_in_outcome` (1 split, 2 lease to claimant, 3 lease to patron, 4 holder holds out (pledge fires), 5 war, 6 renewed, 7 outbid, 8 reverted). Applies once (live only). Outcome 5 only records a war that exists (refused otherwise; the daily tick resolves it when claimant and holder go to war). The mod never scripts a declaration: wars come from coercion's Cornered routes (war goal + AI strategies). `pww_sit_cancel`. `pww_sit_seat_of_this` (country; out `pww_out_seat`).
  - Inbound hooks: `pww_sit_on_bid` (`pww_in_sit_id`, `pww_in_bidder`, `pww_in_bid_band` 1..4), `pww_sit_on_pledge` (`pww_in_sit_id`, `pww_in_ag` = reserved ledger agreement or -1), `pww_sit_on_target_state` (`pww_in_sit_id`, `pww_in_demand_id`, `pww_in_tstate` 0..4, `pww_in_public`), `pww_sit_on_hardened` (`pww_in_sit_id`).
  - Calls out (via `meta_effect`, guarded): `pww_coer_issue_demand` (type 1, `pww_in_res`, `pww_in_days`, `pww_in_term`, `pww_in_state`) under `pww_coer_loaded`. Under `pww_diplo_loaded` AI seats set intents (country flags `pww_sit_ai_wants_bid` / `pww_sit_ai_wants_pledge`, var `pww_sit_ai_sit`) and wait `global.pww_sit_c_diplo_grace` (30) days counted from when the intent was raised (`pww_sit_ai_bid_day` / `_pledge_day`); diplomacy runs a seat's country tick within a week of a fresh intent. A direct AI pledge then still goes through `pww_diplo_make_pledge_direct`.
  - Triggers: `pww_sit_is_live`, `pww_sit_is_valid`, `pww_sit_is_queued`, `pww_sit_this_has_seat`, `pww_sit_has_live` (temp `pww_in_sit_id`).
  - Records: global arrays `global.pww_sit_<field>^id` (template, status 0 queued/1 live/2 resolved/3 cancelled, claimant, holder, patron, has_patron, res, days_left, dev, phase, tstate, pledge, outcome, ...); prize entries `global.pww_sitp_{sit,state,lot,amt,ag,to}`. `global.pww_sit_live`. Outcome queue `global.pww_sitq_*`.
  - UI rows: country array `pww_my_situations` = LIVE ids only (one alert row each); dirty var `global.pww_sit_rev`; alert key by seat/phase/tstate/pledge in the core header; dev line loc `pww_sit_dev_<n>`. Noise cap `global.pww_sit_c_cap` (4) live situations per human seat holder; excess queues and goes live (full clock) when a slot frees.
  - Seat enum: 0 claimant, 1 holder, 2 patron. Events namespace `pww_sit` (human seats only).
- **coercion provides** (full docs: header of `mod/common/scripted_effects/pww_coer_core.txt`; ladder in `pww_coer_ladder.txt`, reputation in `pww_coer_rep.txt`). Global flag `pww_coer_loaded`. Every effect sets `pww_out_result` (1/0) and `pww_out_fail`.
  - `pww_coer_issue_demand` in: `pww_in_claimant`, `pww_in_target`, `pww_in_sit_id` (**-1 for none**; unset reads 0 = situation 0), `pww_in_demand_type` (0 output share, 1 named-state lease, 2 cutoff of a third party), `pww_in_channel` (0 quiet, 1 public); optional `pww_in_res`, `pww_in_share` (default 0.25), `pww_in_state`, `pww_in_third`, `pww_in_days` (default 120), `pww_in_term` (default 365). out: `pww_out_demand_id` (-1 refused).
  - `pww_coer_commit_force` in: `pww_in_demand_id`, `pww_in_force_type` (1 naval, 2 air, 3 army). One force per demand; one live commitment per force type per claimant. `pww_coer_release_force`.
  - `pww_coer_target_respond` in: `pww_in_demand_id`, `pww_in_response` 0 fold, 1 smaller lot, 2 90-day provisional (ledger timed clause), 3 own fig leaf (`pww_in_fig_leaf` 1..4), 4 call patron, 5 harden, 6 refuse, 7 stall (quiet only). `pww_coer_claimant_respond` in: `pww_in_demand_id`, `pww_in_response` 0 accept counter, 1 reject, 2 offer fig leaf (`pww_in_fig_leaf` 1 token purchase, 2 joint commission, 3 assurance, 4 temporary), 3 withdraw, 4 go public, 5 take less.
  - Ladder: `pww_coer_cutoff` (`pww_in_cut_mode` 0 supplies/1 purchases/2 both, `pww_in_res` -1 all), `pww_coer_embargo`, `pww_coer_lift_embargo`, `pww_coer_join_embargo_ask` / `_reply` / `pww_coer_punish_noncompliance` (`pww_in_third`, `pww_in_comply`), `pww_coer_declare_quarantine`, `pww_coer_lift_quarantine`. All take `pww_in_demand_id`. `pww_coer_quarantine_hold_ag` (`pww_in_ag`, `pww_in_target`): suspends an agreement that turned active while a quarantine holds, under the holding demand. `pww_coer_grant_pretext` (`pww_in_claimant`, `pww_in_target`), `pww_coer_set_rival`.
  - AI claimant: commits a force after 14 days, releases it if it registers 0 raw after 28 days (flag `pww_coer_ai_force_idle`, 120 days), climbs cutoff/embargo when stuck without a lever or when desperate (`pww_desp_max` >= 70) and still Defiant/Strained after 6 weeks.
  - **Fold creates the ledger agreement** (supply or lease, committal, the demand's term; token purchase = 1 civ; temporary = 180-day revert). Callers must not create it too. Demands with a valid situation id instead call `pww_sit_resolve` outcome 2 (the situation applies the lease) and report shifts via `pww_sit_on_target_state` / `pww_sit_on_hardened` (called through `meta_effect`).
  - Records: global arrays `global.pww_cd_<field>^id` (fields in `pww_coer_storage.txt`): `status` (0 live, 1 folded, 2 lapsed/refused, 3 withdrawn, 4 war route, 5 provisional, 6 void), `tstate` 0 Defiant .. 4 Ready, `prev`, `cause`/`cause_side`, reason slots `for0..3` / `hold0..3` (strongest first; ids listed in the core header, loc `pww_cause_for_*` / `pww_cause_against_*`), `warn` (Cornered line), `intel`, `route`. `global.pww_coer_live`, country array `pww_coer_dem_ids`. Event queue `global.pww_cq_*`.
  - GUI: `pww_coer_load_readout` (viewer scope, in `pww_in_demand_id`) fills `pww_coer_rd_*` + `pww_patron`/`pww_rival`; scripted loc `[pww_coer_loc_state]`, `[pww_coer_loc_for_0..3]`, `[pww_coer_loc_hold_0..3]`, `[pww_coer_loc_cornered]`, `[pww_coer_loc_intel]`, `[pww_coer_loc_shift]`, `[pww_coer_loc_cred_band]`, `[pww_coer_loc_alarm_band]` (FROM = target).
  - Country vars: `pww_credibility` (0..100, coercion writes), `pww_alarm@<claimant>` on observers (0..100), flags `pww_coer_quarantined`, `pww_coer_humiliated`, array `pww_coer_pretexts`. Trigger `pww_coer_target_quarantined` (diplomacy: a quarantined holder's pledged deal is undeliverable).
  - **Reads from diplomacy**: target country vars `pww_patron_pledge_strength` (0..100) and optional `pww_patron_pledge_patron` (country; else a major guarantor is shown as patron).
  - Map: `tools/pww_coer_gen.py` regenerates `pww_coer_map_data.txt` (per-state seas, land region, air regions, vanilla + R56, picked by state count), the readout scripted loc and the readout/reputation loc files. Ships in port count in the port's **land** region (`ships_in_area`), so approaches = adjacent seas + the coastal states' land regions.
- **diplomacy provides** (full docs: headers of `mod/common/scripted_effects/pww_diplo_core.txt` (storage, enums, queue), `pww_diplo_talks.txt`, `pww_diplo_pledges.txt`, `pww_diplo_auctions.txt`, `pww_diplo_pressure.txt`, `pww_diplo_ticks.txt`). Global flag `pww_diplo_loaded`. Calls out only through `meta_effect` under `pww_coer_loaded` / `pww_sit_loaded`, so the lane loads alone.
  - Actions (`common/scripted_diplomatic_actions/pww_diplo_actions.txt`): `pww_diplo_propose_agreement`, `pww_diplo_lease_rights`, `pww_diplo_demand_quiet`, `pww_diplo_demand_public`, `pww_diplo_pledge_support`, `pww_diplo_quarantine` (visible with coercion only), `pww_diplo_demand_settlement`, `pww_diplo_join_embargo`, `pww_diplo_submit_bid`. Loc keys are `<KEY upper>_TITLE` / `<KEY upper>_ACTION_DESC`; titles must stay <= ~18 chars (the vanilla actions list truncates).
  - Negotiation: talks `global.pww_dt_<field>^id` (sender, target, act, status 0 open/1 signed/2 broken off/3 expired/4 superseded, round, patience, redline 0..7, want 0..8, rl_seen, want_seen, reserve, seed, ag, sit, line). Draft on the sender `pww_do_*`. Hidden values derive from `global.pww_diplo_salt` + both core buckets + talk id (stable across reload; verified). 3 counters; repeats get the same answer.
  - Pledges: `pww_patron_pledge_strength` (holder, 0..100) and `pww_patron_pledge_patron` (holder; cleared when none). Records `global.pww_dpl_<field>` (patron, holder, claimant or 0 = anyone, cond, ag, status 0 live/1 fired/2 lapsed/3 withdrawn/4 failed). Pledges fire from coercion's queue (kind 3 val 2, kind 7 val 5/6) or `pww_diplo_on_demand_refused` (`pww_in_claimant`, `pww_in_target`; out `pww_out_fired`). `pww_diplo_withdraw_pledge` (`pww_in_pledge_id`). `pww_diplo_make_pledge_direct` (patron scope; `pww_in_target`, `pww_in_claimant`, `pww_in_resource`; out `pww_out_ag`, `pww_out_pledge_id`). Situations may fire the reserved agreement itself; the sweep follows the ledger status. Quarantined holder: strength x0.25, a fired pledge is held suspended (`pww_diplo_pledge_quarantine_hold`).
  - Auctions (UI lane): `pww_diplo_auction_open` (`pww_in_holder`, `pww_in_resource`, `pww_in_sit_id`, `pww_in_days`; out `pww_out_auction_id`), `pww_diplo_auction_add_lot` (`pww_in_auction_id`, `pww_in_lot_kind` 0 lease/1 split half/2 exclusive/3 bridge, `pww_in_state` numeric id, `pww_in_group`, `pww_in_amount_band`, `pww_in_term_days`), `pww_diplo_auction_write_default_lots`, `pww_diplo_auction_bid` (`pww_in_lot_id`, `pww_in_bidder`, `pww_in_pay`, `pww_in_price`, `pww_in_sweet`, `pww_in_fig`; once per lot), `pww_diplo_auction_award`, `pww_diplo_auction_close`. Records `global.pww_dau_*`, `global.pww_dlot_*` (status 0 open/1 awarded/2 void; `winner` valid only when awarded), `global.pww_dbid_*`, exclusivity `global.pww_dex_*`; live lists `global.pww_dau_live`, `global.pww_dlot_live`, `global.pww_dbid_live`; holder flag `pww_diplo_auction_open`. AI holders auto-open an auction when two senders seek the same resource.
  - Demands: with coercion loaded, the action issues/presses through `pww_coer_issue_demand` / `pww_coer_claimant_respond` (2 fig leaf, 4 go public, 5 take less) and a human target's popup move goes to `pww_coer_target_respond`; coercion's fold creates the agreement. Without coercion a local fallback record (`global.pww_ddm_*`) folds into a ledger agreement itself. Target array `pww_dd_pressers` (claimants with live demands).
  - Event queue `global.pww_dq_{seq,kind,a,b,ref,ag,sit,x,day}` (kinds in the core header). Situation hooks called: `pww_sit_on_bid` (offer or bid to a situation holder), `pww_sit_on_pledge` (pledge inside a shared situation); AI intents `pww_sit_ai_wants_bid` / `_pledge` are consumed on the tick.

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
- v1.20 logs `Unexpected token: context_type` once per `context_type = diplomatic_action` block in scripted GUIs: false positive (the GUIs work; the harness ignores it).
- An AI sends a scripted diplomatic action only when the target's `ai_acceptance`, read on the draft as it stands BEFORE `reset_send_effect`, is positive: prepare AI drafts on the tick.
- `[X.GetCapitalName]` is not a loc function (renders empty): use `[X.Capital.GetCapitalVictoryPointName]`.
- AI fleets stay in home ports in peacetime, so an AI naval demonstration far from home registers 0 (Germany vs Portugal).
- `global.date` value = hours since -5000 / 100000 (1 day = 0.00024): `global.date + days*0.00024` renders with `GetDateStringNoHourLong`.
- In `diplomacy_target_context` scripted GUIs THIS/FROM = the target, ROOT = the player; `[ROOT.scripted_loc]` flips FROM to the viewer.
- Children of `trade_tab` placed outside its bounds still render and take clicks.
- Vanilla `tiled_selection_bold` sprite is a magenta placeholder: do not use it.
- Unanswered player events time out to the FIRST option: list the no-change option first (pww_coer.1, .2, .7; pww_sit.10, .11) and weight it in ai_chance.
- No script trigger for sea regions adjacent to a state: use offline tables from `tools/map_tables.py` (vanilla and R56). POR tungsten states 112 and 181 in both maps.

## Testing
- Load test: `python tools/run_hoi4.py [--r56] [--days N]`. Scenario: `--test <dir>` (log `PWW_RESULT <t>.<check> PASS|FAIL|INFO`, end with `PWW_DONE <dirname>`). Exit 0 = clean.
- Full suite: `python tools/run_all_tests.py [--r56|--both] [--only NAME] [--engine] [--soak]`. One game session per test (tests are not composable: one test's setup changes the world another reads); prints a table. Add new tests to its `TESTS` list.
- Tests live in `tests/<lane>/<name>/` (a mini mod). Never in a scratchpad. Integration: `tests/integration/wolfram_full` (all AI with `--tag HAI`; human holder with `--tag POR`: the driver answers POR's popups through the event-option effects), `tests/integration/soak` (`--days 730`; same folder with `--no-pww` is the tick-time baseline; `tests/integration/soak_report.py <run> [<baseline>]`).
- Prefix every temp variable, tests included: a bare temp like `bad` read 10782 under R56 (name collision).
- Force a desperate claimant with core's `pww_desp_floor_<res>` country var, not by setting `pww_desp_<res>` (core's tick overwrites it).
- Isolation is via redirected USERPROFILE; the harness verifies the user's real files by sha256 after each run.
- Hazard: another agent's `--leave-running` game holds no lock but shares `.hoi4-userdir`. The harness rotates `game.log` at launch and ignores lines stamped before launch; `run_all_tests.py` also waits until no `hoi4.exe` runs.
- UI: desk/dossier rows are UI-lane loc (`pww_ui_*`) built from situation/coercion keys (`pww_seat_line_*`, readout scripted loc). The readout hides patron-naming reasons when the demand has no known patron.
