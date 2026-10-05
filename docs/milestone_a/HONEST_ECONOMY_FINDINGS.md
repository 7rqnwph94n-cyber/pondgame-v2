# Milestone A: what the honest economy reveals

Date: 2026-10-02 · Author: Claude · Branch: `claude/milestone-a-honest-economy`
Reproduce: `python3 -m economy.run` and `python3 -m economy.run --overlay economy/data/experiments/probe_unblock_bootstrap.json`

> **Update 2026-10-02:** Rich's preferred resolutions to the decisions below have been simulated. See `CANDIDATE_RULES_V1_RESULTS.md`: they remove every deadlock here, but the Reef is still infeasible in 90 minutes.

## Verdict

**The Memory Reef cannot be completed under the documented slice economy.** This is not a timing shortfall. The doc-faithful definitions contain structural deadlocks: the reference city never leaves the Shelter tier, never produces Growth Nutrient, and the Great Work can never unlock.

To see what lies behind the deadlocks, a clearly labelled probe overlay (`economy/data/experiments/probe_unblock_bootstrap.json`) makes the smallest changes that clear every static deadlock. **It is not a balance proposal.** Even with the probe and a reactive, competent reference plan, the city reaches its first Stable at 41:09 (doc target 12–18), ends with 3 Stables and 44 population (doc target at minute 55: 12 residences, 90–105 population), and never begins the Memory Reef.

The legacy 84:48 result came from facilities and residences appearing at scripted times and from the aggregate "investment" event. None of those things is buildable under the rules once costs, staffing and evolution are honest.

## Finding 1: structural deadlocks in the documented rules (static proof)

`python3 -m economy.run --bootstrap-only` computes, without running time, what is reachable from the starting colony. It is generous: one-off costs may use finite stock or anything the neighbour sells. Two blocker cycles remain:

**A. First Stable / Adapted workers.**
- Shelter → Stable needs 2 Growth Nutrient plus Waste and Clean Flow service (§9.1).
- Growth Nutrient comes only from the Nutrient Washer (3 **Adapted**, §7.1) or the Channel Separator (Adapted, plus Filter Crown, which needs Stable).
- Waste service comes only from the Waste Digester: 3 **Adapted** (§13) and a cost of 2 Fired Ceramic (§14.3).
- Clean Flow comes from the Clean-Flow Node: 1 **Adapted** (§13).
- Adapted workers come only from Stable homes.

So the first Stable can never happen. §18.1 has the player running a Washer and holding 4 Nutrient before any Stable, which contradicts the §7/§13 staffing tables.

**B. Symbiotic / Artisan workers.**
- The Ceramic Kiln needs **Artisans** (§7.2), and Artisans come only from Symbiotic homes.
- Symbiotic needs Health; the Detox Clinic costs Fired Ceramic and Habitat Composite.
- Composite needs the Composite Workshop (Artisans, and Ceramic to build).

§18.3 runs a Kiln before the first Symbiotic.

**C. Memory Enclave / Coordinators.**
- The Memory Enclave needs Memory service.
- The Memory Circle provides it but needs 3 **Coordinators**.
- Coordinators come only from Memory Enclaves.

**D. Repair Enzyme / Silica loop** (appears once A–C are removed).
- The Silicate Pit and Carbonate Cutter cost Repair Enzyme, and the colony starts with none.
- Every Enzyme route needs Fired Ceramic first: the Digester build cost, or the Anoxic Pump build cost for the Emergency Enzyme Culture.
- Ceramic needs Prepared Silica beyond the starting 2, which needs the Pit.

**Probe changes used to get past A–D (for evidence only):**
- Nutrient Washer and Clean-Flow Node staffed by General.
- A cheap General-staffed `waste_collector` as a second Waste provider (§13 names a "Waste Collector/Digester").
- Kiln staffed by Adapted.
- Detox Clinic without Composite.
- Memory Circle staffed by Artisans.
- 2 starting Repair Enzyme.

## Finding 2: Carbonate is the dominant dynamic bottleneck

Top bottleneck in both runs. In the probe it accounts for 151 blocked entity-minutes: the Silicate Pit waited 46 minutes for Carbonate, the Mineral Washery 50, and a Shelter 20.

Budget evidence (one-off demand of the reference plan, computed from its commands):

| | Carbonate |
|---|---:|
| City buildings in the reference plan | 42 |
| Memory Reef stages | 30 |
| **Total one-off demand** | **72** |
| Starting stock | 6 |
| Neighbour's maximum sale for the whole scenario (§15.3, includes the opening 20-value purchase) | 30 |
| Fertile Exchange reward | 12 |
| **Maximum without a Carbonate Cutter** | **48** |

So the Cutter is mandatory, and it sits at the end of the longest chain in the slice:

Carbonate (Pit 2, Washery 3) → Raw Silicate at half rate without Mineral Jaw → Prepared Silica → Mineral Jaw research (4 Nutrient, 3 Silica, 1 Enzyme, 60 Nursery-work) → expression on a Stable (1 Nutrient, 1 Silica) → Cutter (2 Silica, 1 Enzyme) → 4 Adapted workers.

Every link competes for the same scarce Carbonate and Nutrient. §19.3 assumes the Cutter runs for 50 minutes; in the probe the first link (Pit) is not commissioned by minute 90.

## Finding 3: Growth Nutrient supply is far below demand, and seasonally absent

- A Dredge without Burrowing Limb yields 0.225 sediment/min in Bloom (0.5 × 0.75 × 0.60), nothing for the 17 minutes of High Water, then 0.405/min in Recession.
- Probe with two Dredges: 30 Growth Nutrient produced in 90 minutes. 12 were sold, because Nutrient is also the only early currency for Carbonate.
- One-off Nutrient demand in the reference plan is 26: 4 evolutions to Stable/Symbiotic, three researches and their expressions. Add 8 for the Fertile Exchange and about 0.25 per new organism. The doc's minute-55 target of 90–105 population needs 66–81 more organisms, which is 16–20 Nutrient.
- §18.1 expects 3–5 Nutrient by minute 12; the probe has 1.

Growth is also rate-capped at 1 organism/min (migration plus Nursery). Reaching the doc's 90–105 population takes at least 66–81 minutes of uninterrupted growth from minute 0.

## Finding 4: construction labour collapses as the city upgrades

- Only unassigned General/Adapted WP builds (§10.2). Every new General building takes its crew from the same pool, so builders vanish as industry opens. The opening 6-WP slack is gone once a Dredge and Washer are staffed.
- Evolving three Shelters converts their General workers to Adapted, who then fill General jobs at 0.85 efficiency. The probe records 993 Adapted WP-minutes worked below class and 37 WP-minutes of General vacancies.
- From minute 53 the city has about 0.5 WP of construction labour, so the Pit, Washery and Shelter crawl. Ranked bottleneck #2: `labour:construction`, 80 blocked entity-minutes.
- This is §20.2's intended "workforce composition" lesson, but its magnitude leaves no recovery route inside 90 minutes.

## Finding 5: trade caps bind early

Neighbour demand for Growth Nutrient (max 12) was exhausted, and Carbonate stock accrues at only 0.5/min. Ranked #3 and #4 in the probe. Trade can bypass one capability (§27) but cannot fund the Reef's bulk materials.

## Also surfaced (not yet enforced, reported as risks)

- **Maintenance upkeep:** §13 requires 1 Repair Enzyme per 10 maintenance weight per 8 minutes. The probe city would need 16.7 Enzyme over 90 minutes and produces none. Enforcing it from minute 0 (starting Enzyme 0) would switch off Maintenance service, which gates every residence evolution: a fifth deadlock.
- **Storage:** the General Store holds 40 units; the store exceeded that for 50 minutes (peak 114), mostly food, biomass and waste.
- **Partial deliveries:** an early-queued research project takes scarce goods one unit at a time and holds them while waiting for the rest. In one plan iteration this froze 4 Nutrient for 55 minutes and starved residence evolution. Either the UI must show reserved goods prominently, or research and evolution should reserve all-or-nothing (evolution already does).

## Source conflicts recorded (JSON v0.1 wins over the design doc, per CLAUDE.md)

- Starting Photosynthetic Field fertility: JSON 0.90 vs doc's 75-fertility patch.
- The doc's Washer/Washery sludge by-products are absent from the JSON recipes and not modelled.
- §18 build order vs §7/§13 staffing (Finding 1).
- Ambiguous text resolved conservatively: "1 Fibre" and "2 Fibre" costs read as Woven Fibre; Detox Sac occupies the Stable extraction slot.

## Provisional values the docs do not specify (need confirmation)

- Construction cost/work for Fibre Garden, Resin Grove and Pigment Bed (copied from Photosynthetic Field).
- Channel Separator (copied from the Washer).
- Emergency Enzyme Culture and Clean-Flow Node (2 Carbonate, 1 Biomass).
- Additional Nursery staffing.
- The diagnostic 4-WP nominal crew.

All are tagged `provisional` in `verdant_v0_2.json` and listed in every report header.

## Decisions needed from Rich

1. **First-Stable loop (A).** Pick one or more:
   - General-staffed Washer and Clean-Flow Node;
   - a General Waste Collector;
   - Waste removed from the Stable gate;
   - starting Nutrient plus one starting Stable.
2. **Kiln/Clinic loop (B).** Adapted Kiln, a Clinic without Composite, or Health moved to the Memory gate.
3. **Memory loop (C).** Artisan-staffed Memory Circle, or a scripted first Coordinator (an envoy, like trade), or no Memory service in the Enclave gate.
4. **Enzyme bootstrap (D).** Starting Enzyme, or Pit/Cutter costs without Enzyme.
5. **Carbonate economy.** The Reef plus city needs about 72; the non-Cutter ceiling is 48. Options:
   - a pre-Jaw Cutter at a penalty (like the Pit);
   - higher neighbour supply;
   - cheaper Carbonate costs;
   - a larger starting stock.
6. **Growth Nutrient economy.** Options:
   - soften the no-Burrowing Dredge penalty;
   - reduce Nutrient per organism or per evolution;
   - make High Water a slowdown rather than a closure.
7. **Construction labour.** Keep "only unassigned workers build" (strong pressure), or add a builder job / let idle crews build.
8. **Maintenance upkeep and the starting Enzyme** (before it is enforced).

Once Rich chooses, the chosen values move into `verdant_v0_2.json` with a chat entry, the characterisation tests are updated, and the reference plan is re-run. No balance value has been changed on Claude's own authority.
