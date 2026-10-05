# Honest headless economy engine (Milestone A)

Status: implemented on `claude/milestone-a-honest-economy`, awaiting review.
Owner: Claude. Consumers: Rich (balance), Codex (presentation adapter, later).

The legacy paper model (`economy/model.py`, `economy/simulate.py`, `verdant_v0_1.json`) is untouched and still proves the recipe arithmetic. The engine described here replaces its magical `set` events with buildable, staffed, evolving city state.

## Run it

```bash
python3 -m economy.run                                    # promoted v0.2 baseline (120 min) + reference plan A
python3 -m economy.run --plan economy/data/plans/verdant_reference_c.json   # current reference plan
python3 -m economy.run --overlay economy/data/experiments/legacy_doc_faithful.json   # original Milestone A failure
python3 -m economy.run --overlay economy/data/experiments/probe_unblock_bootstrap.json
python3 -m economy.run --bootstrap-only                   # static reachability/deadlock analysis
python3 -m economy.run --json reports/honest_run.json     # full report incl. minute snapshots (gitignored)
python3 -m economy.sweep economy/data/experiments/throughput_sweep_v1.json         # five-lever sweep with acceptance criteria (~6 min)
python3 -m economy.sweep economy/data/experiments/candidate_bootstrap_sweep.json   # bounded comparison (~1 min, parallel)
python3 -m economy.sweep economy/data/experiments/candidate_lever_ladder.json      # cumulative diagnostic levers
python3 -m unittest discover -s tests -v
```

Python 3.10+ standard library only. A full 90-minute run takes about one second.

## Files

| Path | Purpose |
|---|---|
| `economy/data/verdant_v0_2.json` | Schema-2 definitions. Rich's bootstrap rules 1–8 were promoted on 2026-10-02 (provenance in each `source`); the horizon is 120 minutes. Recipes, seasons, residence needs and Great Work stages are copied unchanged from v0.1; everything else comes from the slice economy doc with a `source` on each building. |
| `economy/data/plans/verdant_reference_a.json` | The reference city expressed only as player commands (doc-faithful rules and the probe). |
| `economy/data/plans/verdant_reference_b.json` | The same city adapted to the candidate bootstrap rules (record of candidate v1). |
| `economy/data/plans/verdant_reference_c.json` | Current 120-minute reference plan: lever-agnostic triggers (inputs, food-minutes, housing, vacancies). |
| `economy/data/experiments/*.json` | Overlays deep-merged onto the definitions. Experiments are not balance decisions. |
| `economy/engine/` | Domain packages (below). No Godot or rendering imports. |
| `economy/run.py` | CLI and text report. |
| `economy/sweep.py` | Bounded parameter comparisons and cumulative lever ladders. |

## Domain boundaries

| CLAUDE.md domain | Module |
|---|---|
| environment, patches, seasons | `environment.py` |
| inventories, reservations, goods | `inventory.py` (whole units only; every holder owns its own counts) |
| recipes and production | `production.py` |
| construction and maintenance upkeep | `construction.py`, `simulation.py::UpkeepState` |
| population, residences, needs, workforce | `residences.py`, `workforce.py`, population growth in `simulation.py` |
| services (abstract booleans this milestone) | `simulation.py::_allocate_workforce` |
| morphology and caste capability | `morphology.py` |
| trade | `trade.py` |
| missions/Great Works | `simulation.py` (stage sites) and `construction.py` |
| commands | `commands.py` |
| diagnostics | `diagnostics.py`, `bootstrap.py` |

## Fixed step order (1 s per step, deterministic)

1. Environment: seasonal deposits (phosphate +30 at High Water) and patch renewal.
2. Commands whose time has come, plus pending retries.
3. Maintenance upkeep (when enforced): pay or suspend the Maintenance service.
4. Workforce allocation per district (jobs by category priority, then commission order; player override with `set_labour_priority`).
   - Construction labour is the Builder job (when `builder_wp` > 0 and a site is ready for work) plus unassigned General and Adapted WP.
   - While a Great Work stage is ready for Coordinator work, every Coordinator is claimed for it ahead of all other jobs.
   - Services are on when a provider building is staffed at 25% or more.
5. Residences: refill need buffers (one whole unit when below 3 minutes of need), consume, emit waste, run Strain → Dormancy → Devolution, and advance evolution.
6. Material delivery to construction sites and research projects in priority order (partial delivery allowed), then labour.
7. Production: a cycle reserves its full input batch at start; progress per second = staffing × season × fertility × adaptation; outputs at completion.
8. Trade caravan arrivals.
9. Population growth (migration 0.5/min plus staffed Nursery 0.5/min, 0.25 Growth Nutrient per organism, reserve policy).
10. Food-reserve tracking for the Great Work unlock, then diagnostics.

## Rules implemented

- **Construction:** materials must be fully delivered before work starts; 1 WP gives 1 work unit per minute; the building is commissioned only when both are complete. Cancelling refunds 90% of delivered goods (rounded down). Demolishing salvages 60% of durable cost goods. Starting buildings cannot be demolished.
- **Workforce:** jobs come from building definitions. Higher classes fill lower jobs at 0.85 / 0.65 / 0.50 efficiency; lower classes never fill higher jobs. Below 25% staffing a building stops; above that it slows proportionally. Unemployment, vacancies and below-class working are reported each minute.
- **Residences:** evolution is a request. It needs the next tier's service gates, a normal state, non-empty need buffers and (Memory) an expressed Memory Ganglion. The one-time goods are reserved at timer start, released if conditions fail, and consumed when the sustain timer completes. Population above a devolved tier's capacity emigrates over 3 minutes. The Shelter tier never devolves.
- **Morphology:** research reserves its goods, then needs Nursery work (4 General WP of research jobs). Expressing a morphology costs the per-residence goods and pauses that residence's workforce for 90 s. A capability exists in a district when a residence of an allowed tier expresses it.
- **Trade:** barter at doc values. Partner stock accrues at its per-minute rate up to the scenario maximum. Goods leave at departure; purchases and contract rewards arrive after the round trip (+30 s in Dry). Fertile Exchange applies its −15% Carbonate price.
- **Great Work:** `begin_great_work` checks every §16.1 unlock condition and names each failure. Coordinators covering lower-class jobs count as available, because they can be recalled. Stages open one at a time as construction sites that also need Coordinator work.
- **First-instance terms:** a building may define `first_instance.cost` / `first_instance.jobs`. They replace the defaults for the first site of that building placed in the settlement, and that facility keeps them for life. Cancelling that first site releases the terms.
- **Food emergency:** `construction_rules.food_emergency` (`FoodEmergency` in `simulation.py`). Food minutes = food held in stores and residence buffers ÷ consumption per minute. It enters below `enter_below_minutes` or on any residence shortage, and exits at `exit_above_minutes` with no shortage. While active, the Builder job ranks after food crews (state `preempted_food_emergency`, with a reason), and it restores automatically.
- **Builders:** `construction_rules.builder_wp` reserves that many WP of `builder_class` (higher classes substitute) at the `construction` rank in `workforce.job_priority`, only while a site has its materials and needs physical work. Player policy: `set_policy builder_wp`; rank override: `set_labour_priority target=builders`.
- **Maintenance upkeep** (`maintenance_upkeep`, off in v0.2):
  - charges `enzyme_per_weight_per_minute` × maintenance weight, from the end of the grace period (`grace_until_tier`, `grace_until_building` or `grace_max_seconds`, whichever comes first);
  - pays whole Repair Enzyme units from the store;
  - an unpaid unit suspends the Maintenance service, which blocks evolution, until Enzyme arrives.

## Plan/command contract

Each plan entry is `{"at": seconds, "do": <command>, ...}` with optional fields:

- `retry: true`: retry every step until the end; `retry_until: seconds`: retry until that time.
- `when`: conditions that must all hold before the first attempt. Keys: `built` (id or list), `tier` `[residence, tier]`, `researched`, `contract` `[id, statuses]`, `stock` `{resource: min}`, `stock_below` `{resource: max}`, `free_housing_below` `n`, `food_minutes_below` / `food_minutes_above` `n`, `vacancies_below` `{class: wp}`.
- `priority`: material/labour priority for sites and research (lower first, default 50).
- `label`: free text shown in reports.

Commands: `construct`, `cancel`, `demolish`, `evolve`, `research`, `express`, `set_recipe`, `pause`, `resume`, `set_labour_priority` (facility id, `builders` or `research`), `set_policy` (`growth_nutrient_reserve`, `builder_wp`), `trade`, `deliver_contract`, `decline_contract`, `begin_great_work`.

Failures return machine-readable reasons such as `unknown_building:x`, `morphology_not_researched:x`, `tier_cannot_express:x`, `slot_occupied:x`, `insufficient_goods:x`, `insufficient_value:...`, `partner_stock_insufficient:x`, `partner_demand_exhausted:x`, `trade_not_open:...`, `needs_residence:memory`, `needs_coordinator_wp:a/b`, `needs_contract_resolved:x=status`, `needs_food_reserve:a/b`, `cycle_in_progress`, `protected_building:x`.

## Stable state identifiers (presentation-facing)

These strings are part of the contract for a future adapter and are listed in `docs/AGENT_CHAT.md`:

- facility status: `running`, `idle`, `no_input`, `no_workforce`, `environment`, `patch_depleted`, `morphology_missing`, `paused`;
- construction site state: `awaiting_materials`, `awaiting_labour`, `in_progress`, `complete`, `cancelled`;
- residence state: `normal`, `strained`, `dormant`;
- residence presentation view (`Residence.presentation_state`, in every snapshot): `tier`, `condition`, `population`, `capacity`, `need_buffer_minutes`, `services_for_next_tier`, `evolution` {`target_tier`, `sustain_progress` 0–1, `goods_reserved`, `blockers`}, `expressed_morphologies`;
- maintenance upkeep: `not_enforced`, `grace`, `paid`, `unpaid` (snapshot `maintenance_upkeep`);
- labour pseudo-jobs: `builders@<district>`, `great_work@<district>` (snapshot `builders_wp`);
- Builder allocation (snapshot `builders`): `protected`, `preempted_food_emergency`, `idle`, `disabled`, plus `wp` and `reason`;
- food emergency (snapshot `food_emergency`): `active`, `reason`, `food_minutes`.

## Diagnostics

The report (`--json`) contains:

- `snapshots`: every minute, with store, total custody of every unit wherever it is held, workforce supply/employed/demand/vacancies/unassigned/below-class per class, residences, services, facility status with detail, active sites and their missing goods, and patch reserves;
- `commands.failed` / `commands.delayed` with reasons and time waited per reason;
- `lost_production`: output units lost by cause per building type, plus trade value by cause;
- `construction`, `residences`, `research`: per-entity timelines and wait breakdowns;
- `great_work_critical_path`: unlock blockers, or per stage opened/materials-complete/last material/completed and material vs labour waits;
- `bottlenecks`: ranked root-cause keys (see the `diagnostics.py` docstring). The unit is blocked entity-minutes. A site crawling below a nominal 4-WP crew is weighted by its shortfall;
- `bootstrap`: the static analysis from `bootstrap.py`, including `self_supplied_needs` (a tier whose recurring need only its own class can produce, with the Strain + Dormancy grace before devolution);
- `maintenance_upkeep`: state, grace end, Enzyme paid and minutes unpaid;
- `risks_not_enforced`: quantities the rules do not yet enforce (maintenance enzyme demand, store capacity overflow, idle construction labour).

## Not modelled yet (deliberate Milestone A abstractions)

- Spatial logistics, carriers, distance, store capacity (overflow is reported only), and Flow Channels.
- Habitat Quality and placement modifiers; service gates are booleans.
- Disrepair (unpaid upkeep only suspends the service); Detox/Memory service upkeep.
- Morphology reveal conditions; Silicate Pit injury chance; Dredge's extra worker penalty.
- Fertilisation, Recovered Fertiliser use, sludge, contamination, waste decay and the 3-unit residence waste limit.
- Emergency food and other §21 anti-spiral rules; rival claims; the trade-opening 6-unit surplus rule.
- One district only; reachability is district membership.
