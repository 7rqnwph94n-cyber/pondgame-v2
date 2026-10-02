# Pondgame v2 — Claude programming brief and persistent memory

## Read this first

You are the principal gameplay and systems programmer for Pondgame v2. Treat this file as standing project memory. Read it at the beginning of every session, then follow the start-of-session steps in "Collaboration protocol" (the exchange in `docs/exchange/`) before changing code or design data.

The repository is shared with:

- **Rich:** project owner, creative director and final decision-maker.
- **Claude:** gameplay engineering, simulation, Godot architecture, tooling, UI behaviour, saves, automated tests and integration.
- **Codex:** art direction, visual design, asset briefs, asset production where practical, materials, environments, presentation scenes, visual QA and overall look.

Do not assume chat history is available. Repository documents, data and tests are the durable source of truth.

---

## Project identity

**One-line pitch:** Build an alien civilisation whose bodies, farms, industries, settlements and culture emerge from the chemistry of its world.

**Genre:** Evolutionary city-builder, production-chain simulation and territory strategy game.

**Primary design reference:** *Pharaoh*.

Supporting references:

- *Anno* for production chains, workforce classes, fertility and regional trade;
- *Age of Empires* for readable gathering, territory pressure and age-scale commitments;
- *Spore* for visible morphology and civilisational transformation.

This is not an RTS with pond graphics and it is not a generic three-resource economy. Geography, chemistry, fertility, logistics, services, housing evolution and Great Works must form one connected city-building system.

---

## Core design pillars

1. **Chemistry is destiny, but not a script.** Atmosphere, solvent, geology, climate and energy gradients define the opportunity space without imposing one build order.
2. **The settlement is a living production organism.** Goods are physically produced, stored, moved, consumed and transformed.
3. **Biology is the technology tree.** Morphologies unlock economic verbs and introduce dependencies.
4. **Place matters.** Local chemistry, fertility, flow, light, temperature and hazards determine useful settlement layouts.
5. **Prosperity creates complexity.** Advanced homes create specialist labour while demanding more goods and services.
6. **Consequence without cruelty.** Failure progresses through strain, dormancy, devolution and migration with visible recovery routes.
7. **Peaceful competition with real pressure.** Rivals compete through territory, trade, prestige, environmental policy and Great Works more than extermination.
8. **Scale is the spectacle.** The civilisation grows from one niche toward planetary agency.

---

## Current scope: Verdant Basin vertical slice

Do not implement the full game yet. The first playable target is one 60–90 minute scenario containing:

- one oxygenated water-world basin;
- four predictable seasonal phases: Bloom, High Water, Recession and Dry Phase;
- eight environmentally distinct raw resources;
- ten principal processed goods;
- physical local inventories and logistics;
- four residence tiers and four workforce classes;
- six economically grounded morphologies;
- crop-specific fertility;
- one neighbouring settlement and trade relationship;
- one staged Great Work, the Memory Reef;
- readable failure, diagnostics and recovery;
- no multiplayer, space stage, arbitrary chemistry generator or combat campaign.

The existing balance source is `economy/data/verdant_v0_1.json`. The executable reference model is in `economy/model.py`; run it with:

```bash
python3 -m economy.simulate
python3 -m unittest discover -s tests -v
```

Current verified reference result:

- Memory Reef completion: 84:48;
- all three stages complete;
- no negative inventory;
- no unpaid planned investment;
- no recurring unmet demand;
- all ten tests passing.

These results prove internal arithmetic only. They do not yet prove construction affordability, workforce scheduling, spatial logistics or fun.

---

## Source-of-truth hierarchy

When sources disagree, use this order and record the conflict in `docs/exchange/`:

1. Rich's latest explicit decision.
2. Automated tests and accepted data contracts.
3. `CLAUDE.md` and accepted architecture/design records in this repository.
4. `economy/data/verdant_v0_1.json` for current balance values.
5. The foundational design documents in the parent workspace:
   - `../design/PONDLIFE_CHEMICAL_CIVILISATION_GDD.md`
   - `../design/VERDANT_VERTICAL_SLICE_ECONOMY.md`
6. Old Pondlife prototype documents and code, which are references rather than requirements.

If working from a checkout that does not contain the parent workspace, ask for the two foundation documents to be copied into `docs/design/`. Do not silently reconstruct them from memory.

---

## Technical direction

### General

- PC first.
- Godot remains the intended client engine, but do not bury simulation rules in scene scripts.
- Keep the headless economy runnable without Godot or rendering.
- Use data-driven definitions with stable IDs.
- Make simulations deterministic under a recorded seed.
- Prefer explicit state machines and small systems over one large entity script.
- Save stable identifiers and versioned data, not array positions or transient node paths.
- Build observability alongside mechanics: every stalled process must explain why.

### Required boundaries

Keep these domains separate:

1. environmental fields, patches and seasons;
2. inventories, reservations and goods;
3. recipes and production;
4. construction and maintenance;
5. population, residences, needs and workforce;
6. logistics and dispatch;
7. services and habitat quality;
8. morphology and caste capability;
9. trade and rivals;
10. missions, Great Works and scoring;
11. presentation and rendering.

The headless domain layer must not depend on Godot nodes. Godot adapters may translate domain state into scenes and input commands.

### Goods

- Goods use discrete cargo units.
- Goods are held in local inventories; a global total is a report, not magical shared storage.
- Production reserves full input batches at cycle start.
- Outputs appear at cycle completion.
- Construction and trade must reserve goods explicitly.
- By-products and waste use the same inventory model as useful goods.

### Simulation clock

- Domain time is fixed-step and independent of render frame rate.
- Pause and speed multipliers control how many fixed steps are processed.
- No gameplay logic should depend on wall-clock time.

### Testing

- Every new system needs unit tests.
- Cross-system milestones need scenario tests.
- Regressions discovered during integration receive a test before or with the fix.
- Tests must assert player-visible outcomes, not only internal implementation details.
- Keep the reference economy test; add alternative plans later so balance is not overfit to one script.

---

## Code/art integration contract

Claude owns gameplay state; Codex owns presentation assets and visual direction. Neither side should create a second authority for the other's data.

### Gameplay owns

- simulation and numerical state;
- entity identity and lifecycle;
- inventories, recipes and production progress;
- navigation, collision and selection;
- environmental values and patch state;
- construction, damage, health and condition;
- save/load;
- input and UI behaviour.

### Presentation owns

- meshes, textures, materials and animations;
- visual-effect scenes;
- environment assemblies;
- icons and portraits;
- presentation wrappers and visual QA;
- art manifests containing visual metadata only.

### Adapter surface

Create a presentation adapter that can accept, at minimum:

```text
set_identity(entity_id, definition_id, culture_id)
set_action(action_id)
set_payload(resource_id, amount, capacity)
set_recipe_state(input_state, progress, output_state)
set_construction_progress(progress)
set_condition_state(state_id)
set_patch_state(grade, remaining, contamination)
set_season(season_id, transition_progress)
set_owner(owner_id, display_colour)
play_feedback(event_id, payload)
```

Exact language-level signatures may evolve, but semantic changes require a `CONTRACT` message in `docs/exchange/`, an updated contract file and tests. Unsupported presentation actions fall back safely to idle/default visuals.

Presentation assets must never determine gameplay collision, capacity, recipes or balance implicitly. Those values belong to gameplay data.

---

## Art direction Claude must preserve

The visual thesis is a miniature civilisation grown from living glass, coral, shell and mineral within a substantial underwater landscape.

For the Verdant slice:

- rounded buds, branching lobes and opening cups;
- deep teal shells, leaf green growth, amber organs and pale mint accents;
- glossy opaque shells with selective translucent membranes;
- restrained emission used for focal organs and activity;
- quiet playable clearings surrounded by clustered ledges, roots and ecological landmarks;
- geometry and contact shadows establish volume; fog, bloom and caustics support rather than replace them;
- buildings visibly expose inputs, transformation and outputs where practical;
- construction grows through staged parts rather than whole-object scale animation;
- high camera angles, full rotation and distant zoom must remain readable;
- functional silhouette is more important than surface detail.

Reuse from the original prototype is encouraged only after audit. Environment pieces, material language, residence forms and symbionts are likely candidates. The former 14-building and three-faction rosters are not automatic requirements.

Do not create final programmer art that hard-codes the eventual silhouette. Use replaceable presentation scenes and stable anchors.

---

## Collaboration protocol

The exchange between Claude, Codex and Rich lives in `docs/exchange/` on `main`. `docs/exchange/README.md` is authoritative; `docs/AGENT_CHAT.md` is a frozen archive.

### At the start of every session

1. `git switch main && git pull`, then `python3 tools/exchange.py inbox --agent claude`.
2. Read this file completely, `docs/exchange/INDEX.md`, every new message addressed to you, and Codex's board (`docs/exchange/status/codex.md`) and profile (`docs/exchange/agents/codex.md`).
3. Run the relevant tests before changing behaviour.
4. Update `docs/exchange/status/claude.md` (state `active`, plan for this block).

### During and after work

- Keep `status/claude.md` current: at every major step, at least about every 15 minutes of active work, after long jobs, before each commit, and at the end of the block.
- Send event-based messages with `python3 tools/exchange.py new` for: decisions (Rich's decisions recorded verbatim as `from: rich`), blockers, contract/schema/stable-ID/adapter changes (`CONTRACT`), handoffs, and evidence that changes someone's plan. No empty heartbeats.
- Cross-agent interfaces are defined in `docs/exchange/contracts/*.json` and enforced by tests. Never define an interface only in prose.
- Exchange changes are separate `exchange:` commits on `main`; never edit `docs/exchange/` on a feature branch; never edit another agent's message, board or profile.
- Rich resolves creative disagreements. Do not silently choose on Rich's behalf when the choice materially changes the game.

---

## Git workflow

- Pull before beginning work.
- Use focused branches for substantial work: `claude/<description>` or `codex/<description>`.
- Keep commits narrow and descriptive.
- Do not commit generated caches, local reports or imported engine caches.
- Do not rewrite or force-push another agent's branch.
- Open a pull request for review before merging substantial architecture, schema or art-pipeline work.
- Small documentation handoffs may go directly to `main` when Rich has requested them.
- Preserve user and other-agent changes in a dirty worktree.

---

## Claude's first programming assignment

Do not start by creating gameplay scenes. Strengthen the domain model so the numbers represent a buildable city rather than an externally scripted spreadsheet.

### Milestone A — Honest headless economy

Implement:

1. **Construction economy**
   - building definitions and material costs;
   - construction work;
   - material reservation and delivery state;
   - commissioning a building only after cost and work are complete;
   - cancellation and recoverable salvage.

2. **Workforce allocation**
   - jobs by workforce class;
   - reachability abstracted initially as district membership;
   - under-staffing productivity;
   - higher-tier substitution penalties;
   - explicit unemployment and vacancies.

3. **Residence evolution**
   - recurring need buffers;
   - service gates as abstract booleans for this milestone;
   - one-time evolution reservations;
   - sustain timers;
   - strain, dormancy and devolution;
   - workforce-class conversion.

4. **Reference-plan commands**
   - replace magical `set` events with requests such as construct, evolve, trade and begin project;
   - commands may fail with a structured reason;
   - the reference plan must achieve its result through normal rules.

5. **Diagnostics**
   - minute-by-minute inventory and workforce;
   - failed command reasons;
   - lost production by missing input, workforce or environmental access;
   - Great Work critical-path report.

### Acceptance criteria

- No building appears without paying its construction cost and completing work.
- No production occurs without the correct workforce.
- No residence changes tier through an external state overwrite.
- The reference plan either completes the Memory Reef within 90 minutes or produces a precise, evidence-backed balance failure.
- Simulation is deterministic.
- Current tests remain meaningful and new behaviour has coverage.
- The output identifies at least the top three bottlenecks.
- Any schema/interface changes are documented in `docs/exchange/` (messages, and contracts where relevant).

Do not adjust costs merely to make the old 84:48 result pass. First report what the honest model reveals. Balance changes require explanation and a chat entry.

### Milestone B — only after A is accepted

Prepare an architecture decision record for the Godot client and create the smallest possible client shell that:

- loads the same definitions;
- advances the headless simulation;
- renders replaceable placeholder entities through the presentation adapter;
- provides pause and speed control;
- exposes one inspector showing why a process is stalled.

Do not create final terrain, broad UI, navigation or content during this milestone.

---

## Definition of done for programming work

A task is done when:

- behaviour is implemented through the intended domain boundary;
- relevant automated tests pass;
- diagnostics make failure understandable;
- authoritative docs/data match behaviour;
- `docs/exchange/` contains any required cross-agent handoff, contract update and a current status board;
- no generated or unrelated files are committed;
- the branch is ready for review with a concise explanation of trade-offs and remaining risks.
