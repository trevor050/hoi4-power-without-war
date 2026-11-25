# Integration to-do (lead decisions)

Collected from wave 2 lane reports. The integration pass owns these.

1. **War ownership: coercion.** Design 7.8: wars happen only through Cornered and never fire on refusal. Coercion grants war goals and AI war strategies; it never scripts a declaration. Situations outcome 5 ("crisis to war") must stop declaring war itself. It becomes a resolution that fires when war actually breaks out between the claimant and the holder (detect via `has_war_with` on the weekly situation tick or `on_war_relation_added`).
2. **Fold creates the agreement once.** Coercion's fold creates the ledger agreement, or calls `pww_sit_resolve` outcome 2 when the demand belongs to a situation. Diplomacy's receiver GUI must call `pww_coer_target_respond` and never create the agreement itself.
3. **Patron pledge fields.** Diplomacy sets `pww_patron_pledge_patron` on the holder alongside `pww_patron_pledge_strength`, and reads `pww_coer_target_quarantined` so a pledged deal to a quarantined target is suspended rather than delivered.
4. **"No situation" id is -1.** Every caller of `pww_coer_issue_demand` and `pww_sit_*` sets `pww_in_sit_id = -1` explicitly when there is no situation.
5. **State scopes vs ids.** Core's producing-state arrays hold scopes; convert with `[THIS.GetID]` before handing states to the ledger.
6. **Cutoff and Reliability.** Coercion's targeted cutoff suspends agreements (cause 15) with no Reliability cost. Keep it: a cutoff is a declared political act, not a breach. Revisit after playtests.
7. **Civilian intel baseline.** Countries without an agency sit at 40 civilian intel, so the second and third reasons only appear at 50+. Acceptable: building an agency is the intended way to see more.
8. **Test the coercion escalation path from the Wolfram situation** (claimant AI escalating with Germany's desperation at 40+ and 90+), which no run has reached yet.
9. **`[X.GetCapitalName]` is not a loc function** and renders empty ("double weight in ."). Replace it everywhere (content-derived loc in all lanes) with `[X.Capital.GetCapitalVictoryPointName]`, the vanilla pattern.
10. **Diplomatic action titles truncate** in the vanilla actions list ("Propose Commercial...", "Request Embargo Co..."). Shorten titles to fit (for example "Propose Trade Deal", "Lease Mines", "Demand (Quiet)", "Demand (Public)", "Pledge Support", "Quarantine", "Demand Settlement", "Join Our Embargo").
11. **Tests are not composable in one session.** Run scenario tests one per session (the diplomacy propose test hands GER Portugal's tungsten before the auction runs). Add a `tools/run_all_tests.py` that runs every test folder in its own session and prints a table.
