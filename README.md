# Pondgame v2

Pondgame v2 is a chemistry-driven alien city builder. The player builds a civilisation whose bodies, farms, industries, settlements and culture emerge from the chemistry of its world.

The current playable slice uses a Godot client over the Python economy simulation. Run `godot --path client` from this directory with Python 3.10+ available; see [client instructions](client/README.md). The normal launch starts paused on an empty basin, with a founding crew and starter supplies, using the provisional slice, empty-start, spatial-transport and current-habitat overlays. Build connected current lanes (T), then place and rotate biological buildings beside them; H shows light and silica exposures. Goods travel in finite carrier loads and services have local reach. The v0.2 baseline remains separate.

`main` is the integrated source of truth for the game, documentation and agent exchange. Start new work from current `origin/main`; the milestone and visual branches preserve their development history. Read [the agent exchange](docs/exchange/README.md), [current project state](docs/PROJECT_STATUS.md) and [slice charter](docs/PLAYABLE_SLICE_CHARTER.md) before continuing.

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

The following legacy paper model uses `economy/data/verdant_v0_1.json`; the honest engine uses `economy/data/verdant_v0_2.json` and explicitly selected overlays. The reference plan is intentionally data-driven and represents a competent first-playthrough build, not the only valid strategy.

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

The initial brief, locked decisions and chemical-civilisation design now live in [docs/design](docs/design/README.md). The [direct reference audit](docs/BRIEF_REFERENCE_AUDIT_2026-10-06.md) compares this build with the brief, Pharaoh and Manor Lords.

## Immediate objective

Use the headless model to verify:

- seasonal food security;
- residence consumption and workforce composition;
- raw-to-refined production chains;
- morphology investment pressure;
- Great Work material feasibility;
- recovery margins and designed bottlenecks.
