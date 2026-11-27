# Production Capacity: Supply That Answers Demand

Status: direction approved by the designer, 2026-11-26. Replaces the "world price index" idea in
2026-11-26-market-dynamics.md as the fix for the glut. The AI-contracts lane of that document stands.

## Problem

Vanilla resources cost nothing to produce and never change with demand. The world produces about
twice what it uses, every year from 1936 to 1940 (all-AI baseline, R56: unsold rubber 630 a day in
1936 and 1,400 in 1940; chromium never finds a real buyer). Vanilla survives this only because its
trade price is fixed at 8 units per civilian factory. Our negotiated prices let sellers compete, and
with free supply and no outlet, competition drives prices toward zero: exporters lose the income
vanilla guaranteed them and well-connected buyers get a windfall. A price floor would hide this. The
cause is supply that never responds.

## Historical model

- **Market economies** (democracies, most non-aligned states, colonies). Output followed sales. In
  the slump, mines closed and plantations took "tapping holidays"; US steel ran near a fifth of
  capacity in 1932. Restarting idle capacity took months; new capacity took years (rubber trees
  mature in six to seven years, mines in one to three). Producers also organized: rubber (IRRA
  1934), tin (1931), copper (1935), steel (International Steel Cartel), oil (the 1928 As-Is
  agreement), aluminium. Gluts were met by cutting supply, not by selling at any price.
- **Planned economies** (the Soviet Union and other communist states). Output followed the plan,
  not prices: Soviet steel roughly quadrupled from 1928 to 1937 while world prices collapsed. Foreign
  trade was a state monopoly that exported (grain, timber, oil, manganese) to earn currency for
  machinery, at whatever price that took; the West accused it of dumping in 1930 and 1931. Exports
  then shrank as the plan absorbed output at home and autarky deepened.
- **Command economies** (fascist states). Private firms, state direction. Germany's Four-Year Plan
  (1936) kept strategic production running regardless of cost and invested in uneconomic domestic
  supply (synthetic oil and rubber, low-grade ore at Salzgitter); Italy turned to autarky after the
  1935 sanctions; Japan developed Manchuria. Output tracked state goals, not the market, and grew
  where the state was short.

## Mechanism (lane: capacity, prefix `pww_cap_`)

Per country and resource, an output factor `pww_cap_<res>` (1.0 = vanilla), applied through the
country modifier `local_resources_<res>_factor` (vanilla drives it from variables in dynamic
modifiers, e.g. Japan's industry coal factor). Evaluated monthly on the country's staggered tick.

Signals, per resource, after the stockpile intake:
- **spare** = unsold output (positive balance) beyond a working margin of 15% of output.
- **sold out** = no spare and either buyers turned away (open-market pool exhausted, refused
  contracts for lack of supply) or the country itself is short.

Behavior by economic system (ruling ideology; subjects follow their own government):

| | Spare persists | Sold out |
|---|---|---|
| Market | idle 2% of base a month, down to 50% | reopen idle 4% a month to 100%, then invest 1% a month to 130% |
| Planned | no idling; the state exports the surplus, eager to sell for factories | invest 1% a month to 130% where the country itself is short |
| Command | no idling of resources the state uses for war production; idle others as market | invest 1.5% a month to 130% where the country itself is short |

All rates and the margin are starting values for measurement, not tuned. Changes of the factor are
gradual and visible in the vanilla resource view (extraction falls or rises), and in the Dossier
words ("mines idle", "expanding").

## Interactions

- **Prices.** Idling removes spare output, so fewer rival sellers can serve each order and the
  competition share rises toward market on its own. No floor.
- **Cartels.** A member's withheld quota becomes idle capacity over time, as under the IRRA, instead
  of a held pool. Cartels form more readily for glutted resources with concentrated producers.
- **Stockpiles.** Storage fills first; output idles only once nothing more can be stored.
- **Leases and resource rights.** The factor applies to the owner's extraction; a lease holder
  receives the leased state's output as before.
- **War.** Belligerents' own shortages count as sold out, so mobilization reopens idle capacity at
  4% a month: a country that let its mines idle in 1937 cannot double output in 1939.

## Measured targets (1936 to 1940 all-AI run, compared with the vanilla-price baseline)

- World unsold share of output falls from about 50% (1936) to 15 to 25% by 1938.
- Median contract price factor 0.8 to 1.1 in peace; no rival-count bucket below 0.7.
- Every exporter's factories earned from resource sales within 20% of the vanilla baseline.
- Belligerent demand in 1939 to 1940 outruns reopening: open pools for contested resources shrink and
  contract prices rise above 1.2.
- Vanilla AI imports never fail for lack of a pool that capacity removed (the margin guarantees it).

## Engine facts to verify first
- `local_resources_<res>_factor` in a mod dynamic modifier, variable-driven, on any country, changes
  extraction live and survives reload.
- The export pool follows the reduced output (pool = export share x (output - costs)).
