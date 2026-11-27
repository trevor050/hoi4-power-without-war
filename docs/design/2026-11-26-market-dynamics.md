# Market Dynamics: One Market for Everyone

Status: direction approved by the designer, 2026-11-26. Engine levers probed the same day (see Probes).

## Target

Resources follow the arc of the late 1930s:

- **1936 to 1937, the glut.** Demand is low, warehouses are full, sellers take what they can get. A country willing to spare civilian factories (better spent growing its economy most of the time) can buy resources very cheaply and store them for later. That is a real trade-off, not a free lunch.
- **1938 to 1939, rearmament.** Imports rise, reserves are being filled, sellers get choosy. Prices climb past the old market rate. Supply moves into contracts.
- **War.** For contested resources the open market is close to empty: most output is locked in contracts, and what is left costs well above market. You cannot simply import your way out of a shortage.

Constraint: everything above must hold for AI countries as well as the player. The player gets no price the AI does not also get. No price floors or caps that exist only to force an outcome; every price movement has an in-world cause.

## Why the current model fails

The all-AI survey (59 deals, 400 days) shows the cheapest deals all come from sellers whose storage is 99% full: their walk-away price falls to about 0.005 of market, so only competition between sellers holds the price up. The price formula counts rival sellers but not rival buyers, so nothing raises prices when demand grows. The AI rarely uses mod deals, so the discount is a player-only buff worth 15 to 25 factories to a large importer by 1939.

## Mechanisms

### 1. World price index (new, prefix `pww_mkt_`)
Monthly, per resource r:
- **Free supply** S_r: output nobody buys (positive balances) plus open-market export capacity not yet sold or contracted.
- **Demand** D_r: open-market imports, unmet shortfalls, and reserve building (countries filling storage, weighted by world tension).
- **Tightness** T_r = D_r / S_r, and a smooth **price factor** p_r = f(T_r): about 0.5 in a deep glut, 1.0 when balanced, 2.0 to 2.5 when demand is several times supply. p_r moves gradually (monthly smoothing) so prices trend instead of jumping.
- Published in the monthly market report (prices visible in civilian-factory terms, per the design's visibility pillar).

### 2. The open market follows the index
Vanilla trade is the spot market. Its rate (8 units per civilian factory) is scaled by p_r through a per-country or per-pair trade-rate modifier, so glut imports are cheap and scarce imports are dear for every country, AI included. Exact lever depends on probe results (section 6). Fallback if no lever works: the open market keeps the vanilla rate and scarcity shows as an emptying export pool (mechanism 4) and contract premiums.

### 3. The AI uses the contract market
On its staggered tick, every AI country that imports or lacks a resource looks for a contract when either:
- a seller would sell below the open-market price (it saves factories), or
- supply security is worth paying for: world tension, its own desperation, or reserves it wants to fill.

AI sellers with unsold output approach importers the same way. Signed contracts replace vanilla imports (auto-import trims itself once the balance is covered). The player competes with these AI buyers and sellers for the same supply.

### 4. Contracts lock supply
Contracted volume leaves the open market: the seller can no longer offer it to vanilla trade. As AIs sign contracts through rearmament, the open-market pool for contested resources shrinks toward zero. (Lever: a contract's resource cost reducing the export pool, or a per-seller export reduction; section 6.)

### 5. Prices count both sides
Contract pricing uses p_r times the market rate as its reference. The seller's share of the surplus depends on rival sellers able to serve this buyer and rival buyers competing for this seller's output. Glut: many sellers, few buyers, the buyer captures most of the surplus. Scarcity: many buyers, the seller captures it, and desperate buyers' valuation lifts prices above market.

### 6. Sellers get choosy when supply is tight
When T_r exceeds 1, sellers rank buyers by trade bond, faction and ideology, and term (locked contracts preferred), refuse weak offers, and put scarce lots up for bids (existing auction action). Storage value rises with tension, so a seller with room would rather keep output than sell cheap.

## Measured targets
A 1936 to 1940 all-AI run, logged quarterly per resource (p_r, T_r, open pool, contract share of trade) and per major (factories spent on imports, vanilla and contracts):

| Period | Glut resources (steel, coal, aluminium) | Contested resources (rubber, tungsten, chromium, oil) |
|---|---|---|
| 1936 | p 0.5 to 0.8; glut contracts 0.3 to 0.6 | p 0.7 to 1.0 |
| 1938 | p near 1.0 | p 1.1 to 1.5; contracts over 30% of trade |
| 1940 | p 1.0 to 1.3 | p 1.5 to 2.5 for belligerents; open pool near zero |

Economy guard: worldwide factories spent on imports, 1936 to 1940, within 30% of the vanilla baseline. Symmetry guard: a scripted player buying optimally saves no more factories per unit imported than AI countries of similar size.

## Probes (2026-11-26, tests/probes/trade_rate_probe)
- P1, open-market price: **works, buyer side.** `resource_trade_cost_bonus_per_factory` on the importing country changes units bought per factory from every seller (+8: 16 units per factory). It is variable-driven and updates live. Integer values, so the importer's rate moves in steps of 8 + n units per factory: 16 (0.5 of market), 12 (0.67), 10 (0.8), 8 (1.0), 7 (1.14), 6 (1.33), 5 (1.6), 4 (2.0). On the exporter it has no effect on buyers.
- P2, pair rate: **does not work.** `trade_cost_for_target_factor` from a dynamic modifier with a target scope changed nothing in either direction.
- P3, contracts lock supply: **works, partially.** A seller's `country_resource_cost_<res>` shrinks its open-market pool at the next daily tick by its export share times the cost (pool = export share x (output - costs)).
- P4, export share: **works.** A negative `min_export` on a seller shrinks its pool, across all resources.
- Baseline (pending): a 1936 to 1940 all-AI run with the current mod, to measure how much demand rises on its own.

Consequence for mechanism 2: the open-market rate is set per importing country, not per resource. Each importer's rate is the import-weighted average of the price index over what it buys, so a country importing scarce rubber pays more per factory than one importing glutted steel. Per-resource differences beyond that live in contracts.

## Build order
1. Probes and baseline.
2. Market index lane (mechanisms 1, 2, 4) and the measurement harness.
3. Diplomacy lane: AI contract seeking, two-sided pricing, choosy sellers (mechanisms 3, 5, 6).
4. Soak, compare to targets, tune.
