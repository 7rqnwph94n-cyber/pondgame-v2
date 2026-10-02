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
