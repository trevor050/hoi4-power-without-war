# Integration to-do (lead decisions)

Collected from wave 2 lane reports. The integration pass owns these.

1. **War ownership: coercion.** Design 7.8: wars happen only through Cornered and never fire on refusal. Coercion grants war goals and AI war strategies; it never scripts a declaration. Situations outcome 5 ("crisis to war") must stop declaring war itself. It becomes a resolution that fires when war actually breaks out between the claimant and the holder (detect via `has_war_with` on the weekly situation tick or `on_war_relation_added`).
   - **Done.** `pww_sit_apply_outcome` outcome 5 only records; `pww_sit_resolve` refuses 5 unless claimant and holder are at war; the daily `pww_sit_tick_live` resolves 5 when war breaks out. The AI war route runs only without coercion (fallback model) and grants a war goal plus AI strategies, never a declaration.
2. **Fold creates the agreement once.** Coercion's fold creates the ledger agreement, or calls `pww_sit_resolve` outcome 2 when the demand belongs to a situation. Diplomacy's receiver GUI must call `pww_coer_target_respond` and never create the agreement itself.
   - **Done (verified).** Diplomacy's accept and receiver moves call `pww_coer_target_respond`; `pww_diplo_demand_fulfil` creates an agreement only when coercion is absent. Situation demands fold through `pww_sit_resolve` outcome 2 (wolfram_full).
3. **Patron pledge fields.** Diplomacy sets `pww_patron_pledge_patron` on the holder alongside `pww_patron_pledge_strength`, and reads `pww_coer_target_quarantined` so a pledged deal to a quarantined target is suspended rather than delivered.
   - **Done.** Fields were set; added: a fired pledge to a quarantined holder is suspended at once via new `pww_coer_quarantine_hold_ag` (resumes when the quarantine lapses), pledge strength counts a quarter while `pww_coer_quarantined`, recomputed on coercion queue kind 11. Situations' fallback pledge now goes through new `pww_diplo_make_pledge_direct`, so every pledge feeds `pww_patron_pledge_strength`.
4. **"No situation" id is -1.** Every caller of `pww_coer_issue_demand` and `pww_sit_*` sets `pww_in_sit_id = -1` explicitly when there is no situation.
   - **Done.** All mod callers already passed -1 (`pww_diplo_find_shared_sit` defaults -1). `pww_diplo_auction_open` now validates its situation id (-1 unless it names a situation the holder holds).
5. **State scopes vs ids.** Core's producing-state arrays hold scopes; convert with `[THIS.GetID]` before handing states to the ledger.
   - **Done.** Situations and diplomacy already converted; `pww_coer_pick_largest_state` now returns a numeric id via `[THIS.GetID]`. Rule recorded in AGENTS.md.
6. **Cutoff and Reliability.** Coercion's targeted cutoff suspends agreements (cause 15) with no Reliability cost. Keep it: a cutoff is a declared political act, not a breach. Revisit after playtests.
   - **Kept** as decided (cause 15, no Reliability cost).
7. **Civilian intel baseline.** Countries without an agency sit at 40 civilian intel, so the second and third reasons only appear at 50+. Acceptable: building an agency is the intended way to see more.
   - **Kept** as decided.
8. **Test the coercion escalation path from the Wolfram situation** (claimant AI escalating with Germany's desperation at 40+ and 90+), which no run has reached yet.
   - **Done.** `tests/integration/wolfram_full` (desperation floored at 90) reaches demand, committed force, weekly readout, holder responses and a real-lane resolution.
9. **`[X.GetCapitalName]` is not a loc function** and renders empty ("double weight in ."). Replace it everywhere (content-derived loc in all lanes) with `[X.Capital.GetCapitalVictoryPointName]`, the vanilla pattern.
   - **Done.** `tools/pww_coer_gen.py` rewrites it like the diplomacy generator; regenerated readouts/reputation yml and fixed `pww_coer_l_english.yml`. No `GetCapitalName` left under `mod/`.
10. **Diplomatic action titles truncate** in the vanilla actions list ("Propose Commercial...", "Request Embargo Co..."). Shorten titles to fit (for example "Propose Trade Deal", "Lease Mines", "Demand (Quiet)", "Demand (Public)", "Pledge Support", "Quarantine", "Demand Settlement", "Join Our Embargo").
   - **Done.** Titles: Propose Trade Deal, Lease Mines, Demand (Quiet), Demand (Public), Pledge Support, Quarantine, Demand Settlement, Join Our Embargo, Submit Bid (`tools/pww_diplo_gen_loc.py`, regenerated). Long `pww_act_*_title` window headers unchanged.
11. **Tests are not composable in one session.** Run scenario tests one per session (the diplomacy propose test hands GER Portugal's tungsten before the auction runs). Add a `tools/run_all_tests.py` that runs every test folder in its own session and prints a table.
   - **Done.** `tools/run_all_tests.py` (one session per test, two-session reload tests, `--r56`/`--both`/`--engine`/`--soak`/`--only`, waits for other agents' games and retries a held lock).

## Added during integration (lead, after the UI lane landed)

12. **Patron reason with no patron** ("leans on its guarantee from ."). **Done.** A situation demand with no pledge patron or major guarantor now records the situation's patron seat (`pww_coer_eval_patron`); when a demand still has no known patron, `pww_coer_load_readout` clears `pww_patron` and drops every patron-naming line (for 23/24, hold 1/2/34, Cornered 2/17, intel 6/7).
13. **Desk row "Claimant: Portugal is Defiant".** **Done.** New keys `pww_seat_line_claimant/holder/patron` ("You are the claimant." ...), defined texts `pww_ui_sl_s0..3_seatline`; `pww_ui_s0..3_line2` now read "You are the claimant. Portugal is Defiant." Tooltips keep "Our seat: Claimant".
14. **Harness stale game.log.** **Done.** `tools/run_hoi4.py` deletes or rotates `game.log` before launch and ignores lines stamped before the launch.
15. **Unanswered popups conceded.** **Done.** Found by the human-holder e2e: an ignored `pww_coer.1` timed out after 13 days into "fold". The engine takes the first option on timeout, so the no-change option is now first (and the only weighted one) in `pww_coer.1/.2/.7`; `pww_sit.10/.11` weight hold/reclaim.
16. **Diplomacy grace and AI pledges.** **Done.** The situations grace now runs from when an intent is raised (30 days), diplomacy runs a seat's tick within a week of a fresh intent, the situations' direct pledge goes through `pww_diplo_make_pledge_direct`, and the ledger no longer checks seller capacity when a reserved agreement is created (it is rechecked when it fires). Before this the UK pledge never reached `pww_patron_pledge_strength`.
