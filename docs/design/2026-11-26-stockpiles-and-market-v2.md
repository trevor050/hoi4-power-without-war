# Stockpiles and Market v2: Design Addendum

Status: approved by the designer, 2026-11-26. Extends the v2 design doc.

## Problem

HoI4 is structurally oversupplied: most export surplus never finds a buyer at the vanilla rate (8 units per civilian factory). An unsold unit is worth zero because resources cannot be stored, so a rational seller dumps surplus at any price above zero and mod deal prices collapse. A hard price floor would hide this; the designer rejected that. Fix the cause: make resources storable, so an unsold unit has a value that rises with world tension and falls as storage fills.

## Stockpiles (lane: stockpiles, prefix `pww_stock_`)

- Covers aluminium, rubber, tungsten, steel, chromium, coal. **Oil is excluded**: vanilla already converts spare oil into the fuel stockpile.
- Units: HoI4 resources are a daily flow. A reserve is stored in unit-days. Display it as days or months of the country's consumption of that resource.
- **Fill (automatic):** on the country's staggered tick, unsold leftover = the positive part of the resource balance (production minus domestic use minus exports; read `resource@X`, adding back the current intake so the reading is stable). Take a fraction of it into the reserve via a variable-driven `country_resource_cost_<res>` dynamic modifier while capacity remains. Exports and mod agreements take priority: never take so much that the balance goes negative.
- **Draw (automatic):** when the balance is negative and the reserve is non-empty, add `country_resource_<res>` to cover the shortfall, capped per day (for example 25% of the shortfall, or a throughput tied to capacity), draining the reserve. Fill and draw never run together for one resource.
- **Capacity:** small base for every country (for example 30 days of its own consumption, minimum a few hundred unit-days); **Strategic Depots** decision adds capacity, locking civilian factories via `civilian_factory_use` for a construction period. AI builds depots by priority (world tension, being a major, desperation, imports exposed to sea routes).
- **Decay:** about 2% of the stock per month.
- **War:** on capitulation, the occupier seizes a share. Quarantine and blockade do not touch stored stock (a reserve is blockade insurance).
- **Exposed data (interface contract):** country vars `pww_stock_<res>` (unit-days), `pww_stock_cap_<res>`, `pww_stock_fill_<res>` (0..100), `pww_stock_days_<res>` (days of consumption covered), `pww_stock_in_<res>` / `pww_stock_out_<res>` (current daily intake/draw); triggers `pww_stock_full_<res>`, `pww_stock_has_<res>`; scripted effect `pww_stock_value_<res>` writing temp `pww_stock_unit_value` (the per-unit reserve value in civilian-factory equivalents for THIS country, see below).
- **Reserve value of one unit** (used by valuation): `market_value x f(tension, fill)`. Roughly 40% of market at zero world tension, rising toward 120% near war, scaled down as fill approaches 100% (a full warehouse values extra units near zero). Countries at war value reserves highest.

## Delivered cost and trade relationships (lane: logistics, prefixes `pww_logi_`, `pww_rel_`)

- **Delivered cost** of a resource flow from seller to buyer, in civilian-factory equivalents per unit: zero-ish over land within range (connected by land, `any_home_area_neighbor_country` chains or capital distance), a sea cost scaled by distance and convoy need otherwise, plus raiding risk where verified signals exist (`convoy_threat`). Effect `pww_logi_delivered_cost` (temps in: seller, buyer, resource; out: `pww_logi_cost_per_unit`). Never hardcode state or region IDs.
- **Trade relationship** per ordered pair: `pww_rel_bond` 0..100, built by honored mod agreements over time (value x months), damaged by defaults, cutoffs and switching away from a long-time supplier. Effects to read and update it; ledger lifecycle hooks feed it. Bond gates locked (fixed) contracts and raises the cost of poaching.

## Cartels (lane: cartels, prefix `pww_cartel_`)

- A Situation template on the existing framework: producers of a glutted resource (historical anchor: the International Rubber Regulation Agreement, 1934, Britain/Malaya, Netherlands/Dutch East Indies, French Indochina, Siam; also tin-like behavior for tungsten) agree export quotas to hold prices.
- A quota forces a member's over-quota surplus into its stockpile instead of being dumped. Cheating = selling over quota through mod deals; detection by members over time, with reputation and expulsion. The player can join, cheat, organize, or break a cartel from outside (outbidding a member, poaching).
- Uses `pww_stock_*` (contract above), situations (`pww_sit_*`), ledger, and the relationship lane.

## Later lanes (after the current market-floor work lands)

- **Valuation v2:** seller walk-away for unsold units = reserve value; buyers value units beyond their deficit at their own reserve value while storage has room; delivered cost added to every comparison; bond and tension in acceptance; poaching offers against mod contracts; locked contracts gated by bond.
- **UI:** reserves on the Trade Desk (one compact row per resource, days stored, fill) and in the Dossier (words), a trade deals view of mod contracts between any two countries, and a poach entry point.
