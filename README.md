# Pondgame v2

Pondgame v2 is a chemistry-driven alien city builder. The player builds a civilisation whose bodies, farms, industries, settlements and culture emerge from the chemistry of its world.

The project is starting with a headless economic model. No game-client architecture will be chosen until the first 90-minute Verdant Basin economy can be simulated, inspected and balanced.

## Run the economy model

Requires Python 3.11+ and no third-party packages.

```bash
python3 -m economy.simulate
python3 -m unittest discover -s tests -v
```

Generate a machine-readable report:

```bash
python3 -m economy.simulate --json reports/reference_run.json
```

The source of truth for balance values is `economy/data/verdant_v0_1.json`. The reference plan is intentionally data-driven and represents a competent first-playthrough build, not the only valid strategy.

## Honest economy engine (Milestone A)

`economy/engine/` replaces the reference plan's scripted `set` events with real rules. Buildings are paid for and built, jobs are staffed by workforce class, residences evolve and decline through needs and services, and the plan issues player commands that can fail with reasons.

```bash
python3 -m economy.run                      # doc-faithful definitions
python3 -m economy.run --overlay economy/data/experiments/probe_unblock_bootstrap.json
python3 -m economy.run --bootstrap-only     # static deadlock analysis
python3 -m economy.sweep economy/data/experiments/candidate_bootstrap_sweep.json   # bounded rule comparison
```

- Architecture and contracts: `docs/ECONOMY_ENGINE.md`
- Current balance evidence: `docs/milestone_a/HONEST_ECONOMY_FINDINGS.md`, then `CANDIDATE_RULES_V1_RESULTS.md`, then `THROUGHPUT_SWEEP_V1_RESULTS.md` (all in `docs/milestone_a/`)
- Definitions: `economy/data/verdant_v0_2.json`; reference plan: `economy/data/plans/verdant_reference_a.json`

The legacy paper model above is kept unchanged as an arithmetic check.

## Design documents

The current foundation documents are being maintained in the design workspace and will move into this repository with the next documentation pass:

- `PONDLIFE_CHEMICAL_CIVILISATION_GDD.md`
- `VERDANT_VERTICAL_SLICE_ECONOMY.md`

## Immediate objective

Use the headless model to verify:

- seasonal food security;
- residence consumption and workforce composition;
- raw-to-refined production chains;
- morphology investment pressure;
- Great Work material feasibility;
- recovery margins and designed bottlenecks.
