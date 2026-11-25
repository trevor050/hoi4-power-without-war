# Monthly Market Report: Vocabulary, Cause Hints, and Samples

Player-facing localisation bible for the Trade Desk's Monthly Market Report (section 6, 7.1, 9).
Designed for the 30-second monthly glance: terse commodity-wire style, no numbers, no em dashes.

Resource index (matches `AGENTS.md`):
`0 oil`, `1 aluminium`, `2 rubber`, `3 tungsten`, `4 steel`, `5 chromium`, `6 coal`.

---

## 1. Resource Names (Report Headers)

| Index | Loc Key | Text |
|---|---|---|
| 0 | `pww_mkt_res_oil` | `Oil` |
| 1 | `pww_mkt_res_aluminium` | `Aluminium` |
| 2 | `pww_mkt_res_rubber` | `Rubber` |
| 3 | `pww_mkt_res_tungsten` | `Tungsten` |
| 4 | `pww_mkt_res_steel` | `Steel` |
| 5 | `pww_mkt_res_chromium` | `Chromium` |
| 6 | `pww_mkt_res_coal` | `Coal` |

---

## 2. Scarcity Words by Band

Seven bands from oversupply to crisis. Color codes used sparingly so frantic/scarce lines pop on a quick scan.

| Band | Loc Key | Generic Word | Notes |
|---|---|---|---|
| 0 | `pww_mkt_band_glut` | `glut` | Heavy global surplus, buyers' market |
| 1 | `pww_mkt_band_slack` | `slack` | Ample supply, soft demand |
| 2 | `pww_mkt_band_steady` | `steady` | Normal peacetime balance |
| 3 | `pww_mkt_band_firm` | `firm` | Rising orders, little spare margin |
| 4 | `pww_mkt_band_tight` | `§Ytight§!` | Noticeable pinch, premiums forming |
| 5 | `pww_mkt_band_scarce` | `§Oscarce§!` | Real shortages, buyers competing |
| 6 | `pww_mkt_band_frantic` | `§Rfrantic§!` | Acute scramble, war-footing bidding |

### Per-Resource Flavor Variants (optional swap-ins for variety)

| Resource | Slack / Steady | Tight / Scarce | Frantic |
|---|---|---|---|
| Oil | `pww_mkt_oil_easy`: `plentiful` | `pww_mkt_oil_tight`: `§Yshort§!` | `pww_mkt_oil_frantic`: `§Rrationed§!` |
| Aluminium | `pww_mkt_alu_easy`: `ample` | `pww_mkt_alu_tight`: `§Ystretched§!` | `pww_mkt_alu_frantic`: `§Rstarved§!` |
| Rubber | `pww_mkt_rub_easy`: `easy` | `pww_mkt_rub_tight`: `§Ypinched§!` | `pww_mkt_rub_frantic`: `§Rcut off§!` |
| Tungsten | `pww_mkt_tun_easy`: `quiet` | `pww_mkt_tun_tight`: `§Ycontested§!` | `pww_mkt_tun_frantic`: `§Rfrantic§!` |
| Steel | `pww_mkt_stl_easy`: `steady` | `pww_mkt_stl_tight`: `§Yheavy§!` | `pww_mkt_stl_frantic`: `§Rstrained§!` |
| Chromium | `pww_mkt_chr_easy`: `thin` | `pww_mkt_chr_tight`: `§Yscarce§!` | `pww_mkt_chr_frantic`: `§Rcornered§!` |
| Coal | `pww_mkt_col_easy`: `abundant` | `pww_mkt_col_tight`: `§Yshort§!` | `pww_mkt_col_frantic`: `§Rcritical§!` |

### Line Assembly Templates

| Loc Key | Template |
|---|---|
| `pww_mkt_line_plain` | `[pww_mkt_res]: [pww_mkt_band].` |
| `pww_mkt_line_cause` | `[pww_mkt_res]: [pww_mkt_band], [pww_mkt_cause].` |
| `pww_mkt_line_two_causes` | `[pww_mkt_res]: [pww_mkt_band], [pww_mkt_cause_1]; [pww_mkt_cause_2].` |

---

## 3. Cause Hints

Short 2 to 5 word phrases appended after a comma when a concrete driver explains the band.

### Dynamic Country & Situation Drivers
| Loc Key | Text |
|---|---|
| `pww_mkt_cause_buyer_surge` | `[pww_top_buyer.GetAdjective] buying` |
| `pww_mkt_cause_rival_bidding` | `[pww_buyer_a.GetAdjective] and [pww_buyer_b.GetAdjective] bidding` |
| `pww_mkt_cause_held_withhold` | `[pww_holder.GetAdjective] withholding` |
| `pww_mkt_cause_quarantine` | `quarantine off [pww_target.GetName]` |
| `pww_mkt_cause_embargo` | `embargo against [pww_target.GetName]` |
| `pww_mkt_cause_nationalized` | `concession seized in [pww_host.GetName]` |
| `pww_mkt_cause_lease_expiry` | `[pww_host.GetAdjective] leases up for renewal` |
| `pww_mkt_cause_big_strike` | `new strike in [pww_host.GetName]` |

### Resource-Specific & Regional Drivers
| Loc Key | Resource | Text |
|---|---|---|
| `pww_mkt_cause_oil_fleet` | Oil | `naval exercises heavy` |
| `pww_mkt_cause_oil_caribbean` | Oil | `Caribbean tankers backed up` |
| `pww_mkt_cause_oil_ploesti` | Oil | `Romanian output contested` |
| `pww_mkt_cause_oil_pacific` | Oil | `Pacific tankers diverted` |
| `pww_mkt_cause_oil_mex` | Oil | `Mexican crude in dispute` |
| `pww_mkt_cause_alu_air` | Aluminium | `airframe orders surging` |
| `pww_mkt_cause_alu_bauxite` | Aluminium | `Balkan bauxite tight` |
| `pww_mkt_cause_rub_pacific` | Rubber | `Pacific shipping tight` |
| `pww_mkt_cause_rub_malaya` | Rubber | `Malayan lanes raided` |
| `pww_mkt_cause_rub_stockpile` | Rubber | `colonial stockpiling` |
| `pww_mkt_cause_tun_china` | Tungsten | `Chinese supply cut` |
| `pww_mkt_cause_tun_iberia` | Tungsten | `Iberian mines contested` |
| `pww_mkt_cause_tun_shells` | Tungsten | `ordnance demand spiking` |
| `pww_mkt_cause_stl_narvik` | Steel | `Northern ore routes watched` |
| `pww_mkt_cause_stl_rearm` | Steel | `European rearmament` |
| `pww_mkt_cause_stl_yards` | Steel | `shipyard orders full` |
| `pww_mkt_cause_chr_balkan` | Chromium | `Anatolian shipments sought` |
| `pww_mkt_cause_chr_armor` | Chromium | `heavy armor programs` |
| `pww_mkt_cause_col_winter` | Coal | `winter power demand` |
| `pww_mkt_cause_col_med` | Coal | `Mediterranean colliers halted` |
| `pww_mkt_cause_col_rail` | Coal | `continental rail congested` |
| `pww_mkt_cause_col_exports` | Coal | `export mills drawing hard` |
| `pww_mkt_cause_shipping_general` | Any | `convoy losses mounting` |
| `pww_mkt_cause_quiet_season` | Any | `quiet trading` |

---

## 4. Twenty Sample Full Monthly Reports

Each sample shows the compact 7-line block rendered in the Trade Desk.

### Sample 1: February 1936 (Early Peace)
```
Oil: slack, quiet trading.
Aluminium: steady.
Rubber: steady.
Tungsten: quiet.
Steel: firm, European rearmament.
Chromium: steady.
Coal: abundant.
```

### Sample 2: October 1936 (Rearmament Picking Up)
```
Oil: steady.
Aluminium: firm, airframe orders surging.
Rubber: steady.
Tungsten: firm, German buying.
Steel: firm, shipyard orders full.
Chromium: steady.
Coal: steady.
```

### Sample 3: August 1937 (China War Cuts Tungsten)
```
Oil: steady.
Aluminium: firm, airframe orders surging.
Rubber: firm, Pacific shipping tight.
Tungsten: scarce, Chinese supply cut.
Steel: firm, European rearmament.
Chromium: firm, heavy armor programs.
Coal: steady.
```

### Sample 4: January 1938 (The Wolfram Question Opens)
```
Oil: firm, naval exercises heavy.
Aluminium: tight, Balkan bauxite tight.
Rubber: firm, Japanese buying.
Tungsten: frantic, German and British bidding; Iberian mines contested.
Steel: firm, European rearmament.
Chromium: firm, Anatolian shipments sought.
Coal: tight, winter power demand.
```

### Sample 5: April 1938 (Mexican Expropriation)
```
Oil: tight, concession seized in Mexico; Mexican crude in dispute.
Aluminium: tight, airframe orders surging.
Rubber: steady.
Tungsten: scarce, Iberian mines contested.
Steel: firm, shipyard orders full.
Chromium: firm.
Coal: steady.
```

### Sample 6: November 1938 (Post-Munich Scramble)
```
Oil: firm, Romanian output contested.
Aluminium: scarce, German buying; airframe orders surging.
Rubber: firm, colonial stockpiling.
Tungsten: tight, Portuguese leases up for renewal.
Steel: tight, European rearmament.
Chromium: tight, Turkish withholding.
Coal: tight, export mills drawing hard.
```

### Sample 7: May 1939 (Pre-War Stockpiling)
```
Oil: tight, German and Italian buying.
Aluminium: scarce, airframe orders surging.
Rubber: tight, colonial stockpiling.
Tungsten: tight, ordnance demand spiking.
Steel: tight, Northern ore routes watched.
Chromium: tight, heavy armor programs.
Coal: firm, continental rail congested.
```

### Sample 8: September 1939 (War in Europe)
```
Oil: scarce, convoy losses mounting; Romanian output contested.
Aluminium: scarce, airframe orders surging.
Rubber: tight, Pacific shipping tight.
Tungsten: frantic, Iberian mines contested.
Steel: scarce, Northern ore routes watched.
Chromium: scarce, Anatolian shipments sought.
Coal: tight, export mills drawing hard.
```

### Sample 9: March 1940 (Italian Coal Crisis)
```
Oil: scarce, Mediterranean lanes strained.
Aluminium: scarce, airframe orders surging.
Rubber: tight, convoy losses mounting.
Tungsten: scarce, German and British bidding.
Steel: scarce, Northern ore routes watched.
Chromium: tight, heavy armor programs.
Coal: frantic, Mediterranean colliers halted; Italian buying.
```

### Sample 10: July 1940 (Fall of France / Blockade Tightens)
```
Oil: scarce, Romanian output contested.
Aluminium: tight, continental supply realigning.
Rubber: scarce, Atlantic shipping cut.
Tungsten: frantic, Iberian mines contested; Spanish re-exports watched.
Steel: tight, European rearmament.
Chromium: scarce, Anatolian shipments sought.
Coal: tight, continental rail congested.
```

### Sample 11: January 1941 (Atlantic Convoy Pinch)
```
Oil: scarce, convoy losses mounting.
Aluminium: scarce, British buying.
Rubber: scarce, convoy losses mounting.
Tungsten: scarce, Portuguese withholding.
Steel: tight, shipyard orders full.
Chromium: scarce, heavy armor programs.
Coal: tight, winter power demand.
```

### Sample 12: August 1941 (US Oil Embargo on Japan)
```
Oil: frantic, embargo against Japan; Pacific tankers diverted.
Aluminium: scarce, airframe orders surging.
Rubber: scarce, Pacific shipping tight.
Tungsten: tight, Iberian mines contested.
Steel: scarce, American buying.
Chromium: tight, Anatolian shipments sought.
Coal: firm.
```

### Sample 13: February 1942 (Pacific War / Rubber Cut Off)
```
Oil: frantic, Pacific tankers diverted; convoy losses mounting.
Aluminium: frantic, airframe orders surging.
Rubber: frantic, Malayan lanes raided; Pacific shipping tight.
Tungsten: scarce, ordnance demand spiking.
Steel: scarce, shipyard orders full.
Chromium: scarce, heavy armor programs.
Coal: tight, export mills drawing hard.
```

### Sample 14: October 1942 (Peak Neutral Tightrope)
```
Oil: scarce, Romanian output contested.
Aluminium: scarce, Balkan bauxite tight.
Rubber: frantic, Malayan lanes raided.
Tungsten: frantic, German and British bidding; Portuguese leases up for renewal.
Steel: scarce, Northern ore routes watched.
Chromium: frantic, Turkish withholding; Anatolian shipments sought.
Coal: scarce, continental rail congested.
```

### Sample 15: June 1943 (Quarantine in the Atlantic)
```
Oil: tight, Caribbean tankers backed up.
Aluminium: scarce, airframe orders surging.
Rubber: scarce, colonial stockpiling.
Tungsten: frantic, quarantine off Portugal.
Steel: tight, shipyard orders full.
Chromium: scarce, Anatolian shipments sought.
Coal: tight, export mills drawing hard.
```

### Sample 16: December 1943 (Winter Energy Crunch)
```
Oil: scarce, Romanian output contested.
Aluminium: tight, airframe orders surging.
Rubber: scarce, Pacific shipping tight.
Tungsten: tight, ordnance demand spiking.
Steel: scarce, European rearmament.
Chromium: scarce, heavy armor programs.
Coal: frantic, winter power demand; continental rail congested.
```

### Sample 17: May 1944 (Big Oil Strike in the Gulf)
```
Oil: firm, new strike in Saudi Arabia.
Aluminium: tight, airframe orders surging.
Rubber: scarce, Pacific shipping tight.
Tungsten: tight, Iberian mines contested.
Steel: tight, shipyard orders full.
Chromium: tight, Anatolian shipments sought.
Coal: tight, export mills drawing hard.
```

### Sample 18: November 1944 (Late-War Exhaustion)
```
Oil: frantic, Romanian output contested; naval exercises heavy.
Aluminium: tight, airframe orders surging.
Rubber: tight, colonial stockpiling.
Tungsten: firm, quiet trading.
Steel: tight, continental rail congested.
Chromium: firm, Anatolian shipments sought.
Coal: scarce, winter power demand.
```

### Sample 19: Peaceful Trade Empire (Ahistorical 1940, Monopoly Holder)
```
Oil: tight, American withholding.
Aluminium: firm, airframe orders surging.
Rubber: scarce, Dutch withholding.
Tungsten: frantic, Portuguese withholding.
Steel: steady.
Chromium: tight, Turkish withholding.
Coal: steady.
```

### Sample 20: Post-Crisis Cool-Down (Ahistorical 1941, Treaties Settled)
```
Oil: slack, new strike in Iraq.
Aluminium: steady.
Rubber: firm, Pacific shipping tight.
Tungsten: steady, quiet trading.
Steel: firm, shipyard orders full.
Chromium: steady.
Coal: steady.
```
