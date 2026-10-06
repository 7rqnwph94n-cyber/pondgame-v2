# Empty founding start — 2026-10-06

Rich: “MAP MUST BE EMPTY AT START OF PLAY WITH A REASONABLE BUDGET TO START.”

The client now starts paused with zero facilities, residences and sites. Natural basin terrain/resources remain. No authored roads, crossing or carriers appear at start. Carriers can later walk a dry local route between completed player buildings; this remains visual movement.

## Budget

| Stock | Starting amount |
|---|---:|
| Carbonate | 30 |
| Prepared Silica | 16 |
| Biomass | 24 |
| Raw Silicate | 8 |
| Staple food | 40 |
| Growth Nutrient | 16 |
| Repair Enzyme | 4 |
| Trade credit | 50 |

Construction costs are paid in materials. Credit is for trade, not a hidden construction subsidy. The founding package is about 66.7 minutes of food for 24 founders at shelter-level consumption.

A tested opening builds three Shelters, one Photosynthetic Field, Culture Bed, First Nursery, General Store, Maintenance Organ, Survey Organ, Clean Flow Node and Waste Collector. These cost 19 Carbonate, 9 Biomass and 3 Prepared Silica, leaving 11 / 15 / 13 respectively before production/consumption. All eleven finish by ten simulated minutes, with 24 housed people, no remaining founders and eight operating facilities. The same explicit opening runs 90 minutes with no food emergency; its 90-minute food reserve is about 121.7 minutes. A separate run requests evolution at ten minutes and reaches the first Stable home within forty minutes with no food emergency. These are scripted acceptance examples, not promises for every build order or a claim about later-game balance.

## Founders and accounting

24 founders wait off-map; they replace the former three prebuilt occupied shelters. They provide the same 18 General work points before landing, consume real Staple food, and cannot work when their provisions run out. Built shelters receive them up to capacity. Workforce transfers instead of duplicating, and the remaining food buffer transfers to the last home. Normal migration waits until they are housed. Population in the existing bridge field continues to count housed residents, so it starts at zero. No bridge schema or protocol change.

First Nursery is buildable here for 2 Carbonate, 2 Biomass, 1 Prepared Silica and 10 work. The new starting overlay composes after the unchanged provisional slice overlay. Baseline definitions, previous acceptance evidence and the old populated benchmark remain intact. Autoplay selects a founding governor that queues the opening facilities through normal commands before the existing v3 build order.

## Verification

`python3 -m unittest tests.test_empty_start -v` covers the exact empty view/budget, first construction and founder transfer, finite food/workforce, funded opening through 90 minutes, first Stable, paid Autoplay bootstrap and unchanged earlier slice. Client checks cover empty/paused startup, no crossing/route and hidden starting carriers, alongside existing controls tests.
