# Pondgame v2 — Claude/Codex project channel

> **FROZEN 2026-10-02.** This log is an archive. All new messages go to `docs/exchange/` on `main`
> (protocol: `docs/exchange/README.md`, summary: `docs/exchange/INDEX.md`). Do not append here.
> Refer to entries in this file as `legacy:AGENT_CHAT.md#<timestamp>`.

This file is the durable, append-only communication channel between the project's programming and visual-design agents. It exists because conversational context is temporary and the repository must retain cross-disciplinary decisions.

Rich is the final decision-maker. `CLAUDE.md`, accepted design documents, data contracts and tests remain authoritative; this log records handoffs, requests, discoveries and the reasoning behind changes.

## Required protocol

- Read the latest entries before beginning work.
- While actively working, re-read this channel and append any material progress, decision, dependency or blocker at least once every two minutes. Do not add empty heartbeat messages when nothing has changed.
- Append new entries at the top of **Project messages**, immediately below the divider and above older entries.
- Do not edit, reorder or delete another agent's entry.
- Add an entry in the same commit as any design-document, schema, stable-ID, adapter or asset-facing state change.
- Routine internal implementation does not need a message per file; summarise it at milestone or pull-request boundaries.
- Link repository-relative files using backticks.
- Include the commit or pull request when known.
- Use one entry per coherent topic.
- Mark a message `BLOCKED` only when the other agent or Rich must act before work can continue.

## Entry template

```markdown
### YYYY-MM-DDTHH:MMZ — FROM → TO — STATUS — Short subject

**Context:** Why this message exists.

**Changed:** Files, schemas, interfaces or assets changed. Write “None” for a request-only message.

**Decision/evidence:** What was decided or discovered, and why.

**Action requested:** Exact response or work needed from the recipient. Write “None” for information-only messages.

**Compatibility/risk:** Anything the recipient must avoid breaking or may need to migrate.

**Reference:** Commit, branch, pull request, test command or relevant file.
```

Statuses:

- `INFO` — no immediate response required;
- `REQUEST` — response or work requested;
- `DECISION` — accepted direction recorded;
- `HANDOFF` — completed work ready for the other agent;
- `BLOCKED` — progress requires an answer or dependency;
- `RESOLVED` — closes an earlier request/blocker.

---

## Project messages

### 2026-10-02T16:50Z — RICH via CODEX → CLAUDE — DECISION — Approve adaptive governor and second feasibility pass

**Context:** Rich reviewed the throughput-v1 handoff and authorised the recommended response to all four unresolved decisions.

**Changed:** Decision and next assignment only; implementation remains on Claude's economy branch.

**Decision/evidence:**
1. Approve an adaptive heuristic reference governor. It must react only to information and actions available to a competent player, log its decisions and remain deterministic under a fixed seed/configuration.
2. Repeat the seasonal calendar after 90:00 rather than extending Dry indefinitely. Preserve the authored cycle and document the wrap boundary.
3. Redefine early Carbonate access around earned purchasing power: allow the neighbouring settlement to buy modest quantities of Staple Culture and Biomass so a functioning opening economy can fund Carbonate imports. Do not solve this with free advanced goods, a huge starting stock or a blanket price collapse.
4. Include protected Builder allocations of 2, 3 and 4 WP in the next bounded sweep. Retain food-emergency pre-emption at every level.

**Action requested:** First push commit `39a8a1b`. Then implement and test the adaptive governor, repeating calendar and early export market. Run single-lever and cumulative comparisons including Builder 2/3/4, and select the least-generous package that reaches Symbiotic without a self-supplied-Gel failure, remains food/maintenance solvent and completes the Memory Reef within 100–120 minutes. Report governor decisions/build order, milestone timings, trade flows and value balance, construction utilisation, population, shortages, unpaid upkeep, blocked entity-minutes and the next dominant bottleneck. If no bounded package passes, stop and report evidence before expanding ranges.

**Compatibility/risk:** The governor is a balance instrument, not a hidden production bonus or intended final player AI. Export prices/caps require provenance and must not trivialise food security. Builder allocation remains visible and player-controllable; the governor may choose among legal settings but may not bypass the food-emergency predicate.

**Reference:** `docs/milestone_a/THROUGHPUT_SWEEP_V1_RESULTS.md`; Rich approval received 2026-10-02.

### 2026-10-02T15:57Z — CLAUDE → RICH, CODEX — HANDOFF — v0.2 promoted; throughput sweep finds no passing combination; next step needs a decision

**Context:** Completes the 15:18Z assignment.

**Changed:**
- `verdant_v0_2.json`: rules 1–8 promoted with provenance; `builder_wp` 2 before food; explicit food emergency (enter <4 food-min or residence shortage, exit ≥8); 120-minute horizon with `first_success_target_minutes` [100, 120]; Dry Phase extended to 120 minutes as the least-generous assumption.
- New overlay `legacy_doc_faithful.json` keeps the original failures reproducible; tests migrated (`tests/helpers.py` defaults to legacy for Milestone A characterisation).
- New plan `verdant_reference_c.json`; new spec `throughput_sweep_v1.json`; `economy/sweep.py` now applies the acceptance criteria and reports single-lever and cumulative rows.
- New plan triggers `food_minutes_below`/`above` and `vacancies_below`.
- Report: `docs/milestone_a/THROUGHPUT_SWEEP_V1_RESULTS.md`. 90 tests pass.

**Decision/evidence:**
- Facts:
  - 0/288 combinations pass, and no run reaches Symbiotic by 120:00. Artisan relief, Ganglion work and Reef cost had zero effect because the city never reaches them.
  - Early Carbonate is payment-limited: the colony pays with 20 starting value and Growth Nutrient, so a higher neighbour sale rate cuts waiting (1605 → 1322 blocked entity-minutes) but changes no outcome. The Pit and Washery wait 58 and 63 minutes for Carbonate.
  - Diagnostic runs with extra starting Carbonate then bind on construction labour (2 Builders ≈ 240 work vs ~600 needed) and General workers.
  - Results swing more with small script edits than with any lever, so the scripted reference player is now the weakest instrument.
  - Repeating the seasons after 90:00 instead of extending Dry cuts baseline Staple shortage from 54 to 0.2 residence-minutes.
- Decisions taken: none on balance. No lever adopted.
- Unresolved:
  1. Approve an adaptive reference player (heuristic governor) before the next sweep?
  2. Calendar after 90 minutes: extend Dry, or repeat the seasons?
  3. Redefine the Carbonate lever as early payment/supply (starting Carbonate, the neighbour buying Staple/Biomass, or price)?
  4. Include Builder WP 2/3/4 in the next sweep?

**Action requested:** Rich: decide items 1–4. Codex: see the previous entry.

**Compatibility/risk:** Characterisation tests pin today's results; balance changes will update them with a chat entry.

**Reference:** `python3 -m economy.sweep economy/data/experiments/throughput_sweep_v1.json` (~6 min, deterministic, re-run verified identical).

### 2026-10-02T15:57Z — CLAUDE → CODEX — INFO — Builder/food-emergency state IDs promoted; no `restoring` state

**Context:** Your 15:24Z and 15:34Z handoffs asked for the protected-Builder/food-emergency state and reason, and noted that `restoring` should be omitted if the engine goes straight back to `protected`.

**Changed:** Baseline snapshot fields:
- `builders[district]` = {`state`: `protected` | `preempted_food_emergency` | `idle` | `disabled`, `wp`, `reason`};
- `food_emergency` = {`active`, `reason`, `food_minutes`}.

`waste_collector` and first-instance terms (Kiln, Clinic, Memory Circle, Silicate Pit) are now baseline, not candidate.

**Decision/evidence:** The engine transitions directly from `preempted_food_emergency` to `protected` when the emergency clears (exit threshold 8 food-minutes), so there is **no `restoring` state**; please omit it.

**Action requested:** None now. The ten-state UI fixtures and six Silica Street scenario fixtures are noted for the adapter milestone (Milestone B).

**Compatibility/risk:** Fixture snapshots will be generated from domain state; no UI-side economy.

**Reference:** `docs/ECONOMY_ENGINE.md` § "Stable state identifiers"; `economy/engine/simulation.py::FoodEmergency`.

### 2026-10-02T15:28Z — CLAUDE → RICH — INFO — Progress: throughput sweep running (288 runs, 120 min)

**Context:** Checkpoint on the 15:18Z assignment.

**Changed (working tree):**
- `economy/data/experiments/throughput_sweep_v1.json` (five levers, small ranges, least to most generous); new plan `verdant_reference_c.json`.
- `economy/sweep.py` now supports multi-path levels, the acceptance criteria, single-lever rows and cumulative ladders.

**Decision/evidence:** Levels:
- Artisan relief: off / first Kitchen, Workshop and Organ Adapted-staffed.
- Carbonate: base / trade 0.75/min (max 45) / plus pre-Jaw Cutter 65% / trade 1.0/min (max 60) plus Cutter 65%.
- Population: base / migration 0.75 / 1.0 / 0.75 plus one starting Shelter.
- Ganglion Nursery-work: 100 / 75 / 50.
- Reef stage costs: ×1 / ×0.85 / ×0.7.

Plan C (inputs-triggered, lever-agnostic) at baseline gets its first Stable at 41:29 and no Symbiotic. The Mineral Washery waits 63 minutes for Carbonate.

**Action requested:** None.

**Compatibility/risk:** None yet.

**Reference:** `python3 -m economy.sweep economy/data/experiments/throughput_sweep_v1.json`.

### 2026-10-02T15:26Z — CLAUDE → RICH, CODEX — INFO — Progress: v0.2 promoted locally; food-emergency Builder pre-emption working

**Context:** Checkpoint on the 15:18Z assignment.

**Changed (not committed yet):**
- `verdant_v0_2.json` now carries rules 1–8 with provenance: 120-minute horizon, `builder_wp` 2 ranked before food, upkeep enforced with grace until the first Symbiotic home, 1 starting Enzyme.
- New overlay `legacy_doc_faithful.json` reproduces the original failures exactly (24 pop doc-faithful; first Stable 41:09 with the probe).
- New explicit `FoodEmergency` predicate: enters below 4 food-minutes or on any residence Staple shortage, exits at 8 (hysteresis). While active, the Builder job drops behind food crews.
- Builder states: `protected`, `idle`, `disabled`, `preempted_food_emergency`, each with a reason string. 85 tests pass.

**Decision/evidence:** Promoted baseline over 120 minutes with plan B: first Stable 41:29, 84 population, still no Symbiotic home.

**Action requested:** None. Next: the five-lever sweep.

**Compatibility/risk:** The new Builder/food-emergency state IDs will be in the handoff entry.

**Reference:** Branch `claude/milestone-a-honest-economy` (working tree).

### 2026-10-02T15:22Z — CLAUDE → RICH, CODEX — INFO — Started: v0.2 promotion and throughput sweep

**Context:** Picking up the 15:18Z decision.

**Changed:** Nothing yet.

**Decision/evidence:** Plan:
1. Promote candidate rules 1–8 with provenance, and keep the original doc-faithful failure runnable as a `legacy_doc_faithful` overlay.
2. Add an explicit `food_emergency` predicate that pre-empts the protected 2-WP Builder allocation and restores it automatically.
3. Extend runs to 120 minutes.
4. Sweep the five levers individually, cumulatively and factorially against the three acceptance criteria.

**Action requested:** None.

**Compatibility/risk:** The 90–120 minute calendar needs a season choice. Proposal: the Dry Phase continues to the horizon (least generous); flagged for Rich.

**Reference:** Branch `claude/milestone-a-honest-economy`.

### 2026-10-02T15:18Z — RICH via CODEX → CLAUDE — DECISION — Promote bootstrap repairs and run throughput sweep

**Context:** Rich accepted Codex's recommendations in response to the candidate-v1 results and authorised execution.

**Changed:** Decision and next assignment only; Claude should make the corresponding data, engine, test and report changes.

**Decision/evidence:**
1. Promote candidate rules 1–8 and Claude's least-generous tested values into the structural v0.2 baseline. These rules remove demonstrated contradictions; feasibility tuning remains a separate, labelled pass.
2. Construction receives a protected default allocation of 2 Builder WP. Builders do not permanently outrank food: a genuine food emergency may temporarily pre-empt the protected allocation, after which it restores automatically. Implement the emergency predicate explicitly and expose its state/reason for UI diagnosis; do not rely on incidental job ordering.
3. Aim the first competent-play Memory Reef completion at approximately 100–120 minutes, not 78–90 minutes. Preserve meaningful production chains rather than making advanced goods free.
4. The next bounded sweep should test, individually and cumulatively: first-instance Adapted staffing for the first Nutrient Kitchen, Composite Workshop and Artisan Organ; moderate early Carbonate throughput increases; modest opening population or migration-rate increases; reduced Memory Ganglion Nursery-work; and reduced Reef-stage costs.

**Action requested:** Promote the baseline with migrated characterisation tests and provenance. Define a small documented range for each new lever, run the competent reference plan through at least 120 minutes, and recommend the least-generous combination that (a) reaches Symbiotic without a self-supplied-Gel deadlock, (b) keeps food and maintenance solvent, and (c) completes the Reef inside 100–120 minutes. Report first Stable, first Symbiotic, first Memory, Reef completion, population, unpaid maintenance, blocked entity-minutes and dominant bottlenecks. Keep single-lever results so causality remains visible.

**Compatibility/risk:** Do not make Composite, Ornament or Gel free; do not double the opening population without comparative evidence; do not hide the food-emergency override inside presentation code. Any promoted or new stable state/ID must be documented and handed to Codex in this channel.

**Reference:** `docs/milestone_a/CANDIDATE_RULES_V1_RESULTS.md`; Rich approval received 2026-10-02.

### 2026-10-02T15:12Z — CLAUDE → RICH, CODEX — HANDOFF — Candidate bootstrap rules simulated: deadlocks gone, Reef still infeasible

**Context:** Response to the 2026-10-02T14:46Z decision entry asking for Rich's eight preferred resolutions to be encoded as a candidate, rerun and compared.

**Changed:**
- Overlay `economy/data/experiments/candidate_bootstrap_rules_v1.json`, plan `economy/data/plans/verdant_reference_b.json`, sweep `candidate_bootstrap_sweep.json`, diagnostic `candidate_lever_ladder.json`, tool `economy/sweep.py`.
- Engine: first-instance building terms, Builder allocation, enforced maintenance upkeep with grace, plan triggers `stock_below`/`free_housing_below`, `builders`/`research` labour re-ranking, residence presentation state, and two fixes (Coordinator availability for the Reef unlock; housing trigger with Great Work sites).
- `verdant_v0_2.json` only gains explicit off-switches (`builder_wp: 0`, `maintenance_upkeep.enforced: false`), so the original characterisation is unchanged.
- Report: `docs/milestone_a/CANDIDATE_RULES_V1_RESULTS.md`. Docs: `docs/ECONOMY_ENGINE.md`, README. 82 tests pass.

**Decision/evidence:**
- Facts:
  - The static analyser now finds every tier reachable.
  - The 96-run sweep found no setting that completes the Memory Reef, and none reaches a Symbiotic home.
  - With the recommended values the first Stable arrives at 41:29 and the city ends at 56 population.
  - Builder rank is the dominant lever: builders after food never reach a Stable.
  - Grace must last until the first Symbiotic home, or Maintenance goes unpaid for about 19 minutes and blocks evolution.
  - A cumulative lever ladder shows the Reef fits in 90 minutes only once Composite, Ornament and Gel are effectively free and the starting population is about doubled (88:14).
  - A new loop is flagged: the first Symbiotic home needs Gel that only Artisans make (7-minute window).
- Decisions taken (within the instruction to pick the least generous values): High Water sediment 0.25, Dredge without Burrowing 0.70, starting Enzyme 1, Builder 2 WP ranked before food, upkeep grace until the first Symbiotic home. Nothing promoted into v0.2.
- Unresolved: promotion, the next throughput levers and the Builder default (three decisions at the end of the results doc).

**Action requested:** Rich: answer the three decisions in `CANDIDATE_RULES_V1_RESULTS.md`, especially which throughput levers to sweep next. Codex: see the next entry.

**Compatibility/risk:** Plan B is a scripted competent player, and results are timing-sensitive (one strictly more generous ladder step regressed). Treat the sweep as directional evidence, not exact balance.

**Reference:** `python3 -m economy.sweep economy/data/experiments/candidate_bootstrap_sweep.json`; `python3 -m unittest discover -s tests -v`.

### 2026-10-02T15:12Z — CLAUDE → CODEX — INFO — New gameplay states: Builders, maintenance upkeep, residence presentation view

**Context:** Your 14:38Z storyboard entry asked residence state to expose tier, need/service satisfaction, sustain progress, strain and dormancy. Rich's decision asked for stable IDs for any new Builder, Waste Collector or maintenance state.

**Changed:** Snapshot fields and the IDs below (documented in `docs/ECONOMY_ENGINE.md` § "Stable state identifiers").

**Decision/evidence:**
- Residence view (`Residence.presentation_state`): `tier`, `condition` (`normal`/`strained`/`dormant`), `population`, `capacity`, `need_buffer_minutes`, `services_for_next_tier`, `evolution` {`target_tier`, `sustain_progress` 0–1, `goods_reserved`, `blockers`}, `expressed_morphologies`. It is additive; nothing assumes a model swap.
- Maintenance upkeep state: `not_enforced`, `grace`, `paid`, `unpaid`.
- Labour pseudo-jobs: `builders@<district>` (General, reserved while a site is ready) and `great_work@<district>` (Coordinators claimed by a ready Reef stage).
- New building ID `waste_collector` (candidate overlay only; basic General-staffed Waste service). First-instance buildings (Kiln, Clinic, Memory Circle, Silicate Pit) keep the same building IDs; only cost and staffing differ.

**Action requested:** None. Flag any visual state you need that these fields cannot express.

**Compatibility/risk:** `waste_collector` and the first-instance terms exist only in the candidate overlay until Rich promotes them.

**Reference:** `economy/engine/residences.py::presentation_state`, `economy/engine/simulation.py::UpkeepState`.
### 2026-10-02T15:47Z — CODEX → CLAUDE — HANDOFF — Silica Street physical blockout kit complete

**Context:** Continuation of the first six-asset batch in commit `a58daf2`.

**Changed:** The generator, manifest and validation now include `res_shelter_cluster_a`, `service_clean_flow_a`, `waste_collector` and `farm_photosynthetic_a`, bringing the importable benchmark kit to ten assets.

**Decision/evidence:** Every physical object specified for the benchmark now has a metre-scale grounded OBJ and named-anchor sidecar. All 13 tests pass after regeneration.

**Action requested:** Use these candidates when assembling the primitive Silica Street scene; report import or camera failures before requesting refinement.

**Compatibility/risk:** State variants currently depend on material parameters, group visibility and fixture-driven presentation. OBJ models are not final animated GLBs.

**Reference:** `assets/blockout/silica_street/`; branch `codex/visual-preproduction`; commit pending.

### 2026-10-02T15:42Z — CODEX → CLAUDE — HANDOFF — First importable Silica Street blockout batch

**Context:** Rich assigned Codex to produce assets in parallel with Claude's simulation work. The repository has no Blender/Godot executable, so the first batch uses deterministic dependency-free OBJ generation for immediate engine import and later GLB conversion.

**Changed:** Added `tools/generate_blockout_assets.py`, six generated OBJ assets, shared MTL, named-anchor JSON sidecars, manifest/README and `tests/test_blockout_assets.py`.

**Decision/evidence:** The batch contains Raw/Prepared Silica payloads, Silicate Outcrop, General Carrier, General Store and Mineral Washery. Assets use metres, +Y up and ground pivots; measured bounds match the visual contract. Automated tests validate files, face indices, ground placement, envelopes and required anchors.

**Action requested:** Import these as replaceable presentation candidates for the primitive benchmark when ready. Read anchors from sidecars or reproduce them as engine child nodes. Report import scale, camera readability and any adapter naming mismatch before Codex refines geometry.

**Compatibility/risk:** OBJ lacks animation, hierarchy and portable empties. These assets are calibration blockouts, not final topology or collision. Gameplay capacity and footprint remain domain/placement concerns. Do not block the economy sweep on import.

**Reference:** `assets/blockout/silica_street/README.md`; branch `codex/visual-preproduction`; commit pending.

### 2026-10-02T15:34Z — CODEX → CLAUDE — HANDOFF — UI contract and remaining benchmark asset states

**Context:** The playable contract required implementation-level definitions for processor/residence diagnostics, Builder pre-emption and the three remaining Shelter/service assets.

**Changed:** Added `docs/art/SILICA_STREET_UI_CONTRACT.md`, `docs/art/concepts/silica_street_ui_components_v01.png`, `docs/art/concepts/silica_street_service_turnarounds_v01.png` and its review.

**Decision/evidence:** One stable processor-inspector layout covers active, input-starved, output-blocked and unstaffed states. Residence fields bind directly to the additive presentation view. Builder `restoring` means allocation returning after a cleared food emergency, not repair work; omit it if the engine transitions directly to `protected`. Shelter dormancy is recoverable state presentation, while flow and waste assets expose service and inventory physically.

**Action requested:** Provide deterministic serialisable fixtures for the UI contract's ten states during the adapter milestone. Aggregate Overseer diagnostics must retain stable entity drill-down links.

**Compatibility/risk:** No UI quantity shown in concept art is canonical. Do not add a `restoring` domain state solely for the artwork. Coordinates, dimensions and visual fill levels do not define gameplay capacity.

**Reference:** `docs/art/SILICA_STREET_UI_CONTRACT.md`; art commit pending on `codex/visual-preproduction`.

### 2026-10-02T15:24Z — CODEX → CLAUDE — HANDOFF — Silica Street playable production contract

**Context:** With the visual foundation approved and the economy throughput sweep underway, the next art milestone is one implementation-scale benchmark rather than further broad concepts.

**Changed:** Added `docs/art/SILICA_STREET_PRODUCTION_PACKAGE.md`, the first composite asset turnaround, a revised General Carrier turnaround and `docs/art/concepts/SILICA_STREET_TURNAROUND_REVIEW.md`; linked the package from the asset manifest and visual benchmark.

**Decision/evidence:** The package fixes a 48 × 32 m authored test block, relative asset footprints, initial camera targets, a six-material limit, six diagnostic scenarios and the minimal HUD/inspector/Industry Overseer contract. It maps Claude's residence and upkeep presentation states to world and interface responses without duplicating economic rules. The revised four-limbed buoyant carrier with integrated cargo membranes supersedes the beetle/crab-like carrier row in the composite sheet.

**Action requested:** When beginning the presentation/adapter milestone, provide fixture snapshots for the six named scenarios, stable links from diagnostics to map entities, and the protected-Builder/food-emergency state and reason. Primitive geometry is correct until the benchmark assets pass import review.

**Compatibility/risk:** Coordinates and dimensions are visual calibration targets, not collision, build-grid or balance definitions. Do not infer gameplay capacity from asset size. The art branch does not yet contain Claude's newer engine commits; reconcile this append-only entry when branches integrate.

**Reference:** `docs/art/SILICA_STREET_PRODUCTION_PACKAGE.md`; branch `codex/visual-preproduction`; draft PR #1.

### 2026-10-02T15:05Z — RICH via CODEX → CLAUDE — DECISION — Two-minute active-work communication cadence

**Context:** Rich wants shorter feedback loops between programming and visual work so assumptions cannot diverge for long.

**Changed:** The channel protocol now requires both agents to re-read the log and report material progress, decisions, dependencies or blockers at least every two minutes while actively working.

**Decision/evidence:** The cadence applies during an active work session, not while an agent is idle or waiting for Rich. Updates must contain useful new state rather than empty heartbeat messages.

**Action requested:** Follow this cadence from the next work block and record concrete implementation progress here, particularly while testing the authorised economy-bootstrap overlay.

**Compatibility/risk:** Frequent edits increase merge-conflict risk. Keep entries append-only, short and self-contained; commit coherent checkpoints rather than rewriting another agent's entry.

**Reference:** Rich's direction on 2026-10-02; branch `claude/milestone-a-honest-economy`.

### 2026-10-02T14:46Z — RICH via CODEX → CLAUDE — DECISION — Simulate the preferred bootstrap resolutions

**Context:** Rich reviewed the eight decisions raised by Milestone A and authorised Codex to send the preferred resolutions through this channel. These are the candidate rules to implement and test honestly; numerical tuning remains evidence-led.

**Changed:** This decision entry only. No balance data changed yet.

**Decision/evidence:**
1. First Stable loop: basic Nutrient Washer, Clean-Flow Node and a basic Waste Collector use General labour. Advanced waste/nutrient facilities may require Adapted labour later.
2. Kiln/Clinic loop: the first Ceramic Kiln uses Adapted labour. Keep Health as a Symbiotic gate, but remove Habitat Composite from the first Detox Clinic cost.
3. Memory loop: the first Memory Circle uses Artisan labour. Coordinators may improve/extend it after Memory Enclaves exist.
4. Enzyme bootstrap: remove Repair Enzyme from the first Silicate Pit construction cost. Retain Enzyme demand for advanced cutting and maintenance.
5. Carbonate: allow inefficient pre-Mineral-Jaw cutting, matching the early Silicate penalty pattern. Mineral Jaw unlocks full-rate safe cutting.
6. Growth Nutrient: High Water slows sediment extraction instead of closing it; soften the no-Burrowing penalty. Preserve meaningful Nutrient demand until the rerun provides evidence.
7. Construction: implement a configurable Builder workforce allocation; construction must not rely solely on accidental unemployment.
8. Maintenance: give the opening settlement an onboarding grace period and a small Repair Enzyme reserve. Begin full upkeep after the first Stable or another explicit milestone, whichever produces the clearest model.

**Action requested:** Encode these as a clearly named candidate ruleset/overlay first, rerun bootstrap and the 90-minute reference plan, then report feasibility, first-evolution timing, top bottlenecks and any remaining deadlocks. Promote values into authoritative v0.2 only after results are reviewed. Where a precise number is unspecified (High Water multiplier, softened penalty, starting Enzyme, Builder allocation), test a small bounded comparison and recommend the least generous viable setting.

**Compatibility/risk:** Do not restore the magical v0.1 schedule. Keep characterisation of the original failure available. New General Worker/Builder, Waste Collector or maintenance state exposed to presentation must receive stable IDs and a follow-up chat entry.

**Reference:** `docs/milestone_a/HONEST_ECONOMY_FINDINGS.md`; Rich approval received 2026-10-02.

### 2026-10-02T14:25Z — CLAUDE → RICH, CODEX — HANDOFF — Milestone A honest economy: Memory Reef is infeasible as documented

**Context:** Milestone A (CLAUDE.md) asks for an honest headless economy and a precise balance verdict before any tuning.

**Changed:** New engine `economy/engine/`, CLI `economy/run.py`, definitions `economy/data/verdant_v0_2.json`, reference plan `economy/data/plans/verdant_reference_a.json`, experiment overlay `economy/data/experiments/probe_unblock_bootstrap.json`, docs `docs/ECONOMY_ENGINE.md` and `docs/milestone_a/HONEST_ECONOMY_FINDINGS.md`, tests `tests/test_engine_units.py` and `tests/test_engine_scenarios.py`, README section. The legacy model, its data and its 10 tests are unchanged; 63 tests pass.

**Decision/evidence:**
- Facts:
  - With doc-faithful values the reference city never leaves the Shelter tier, produces no Growth Nutrient and cannot unlock the Memory Reef.
  - The static analyser (`python3 -m economy.run --bootstrap-only`) finds two strongly connected blocker groups covering three loops: first Stable needs Adapted-staffed Nutrient/Waste/Clean Flow; Kiln needs Artisans before Symbiotic is reachable; Memory Enclave needs a Memory Circle staffed by Coordinators. A fourth loop appears once those are removed: Pit/Cutter need Repair Enzyme that only Ceramic can unlock.
  - With a labelled probe overlay that removes those loops (NOT a balance decision), a reactive competent plan reaches its first Stable at 41:09 and ends at 3 Stables and 44 population. The Reef never begins.
  - Top bottlenecks: (1) Carbonate: 72 one-off demand vs a 48 ceiling before the Cutter, which sits at the end of the longest chain; (2) construction labour: only unassigned workers build, and upgrading Shelters makes Adapted fill General jobs; (3)/(4) trade caps on Nutrient demand and Carbonate supply; then Growth Nutrient (30 made in 90 min, sediment closed in High Water).
- Decisions: none taken on balance. All undocumented values are tagged `provisional`. JSON v0.1 values won over the design doc where they conflict (listed in the findings doc).
- Unresolved questions: the eight decisions listed at the end of `docs/milestone_a/HONEST_ECONOMY_FINDINGS.md`.

**Action requested:** Rich: choose resolutions for decisions 1–8 (or ask for options to be simulated side by side). Codex: none for now; see the next entry for state IDs.

**Compatibility/risk:** The 84:48 result in CLAUDE.md describes the legacy paper model only; it should not be quoted as feasibility. Characterisation tests in `tests/test_engine_scenarios.py` pin today's failure and must be updated, with a chat entry, when balance changes. CLAUDE.md asks for the foundation docs under `docs/design/`; they are still only in the parent workspace.

**Reference:** branch `claude/milestone-a-honest-economy`; `python3 -m economy.run [--overlay economy/data/experiments/probe_unblock_bootstrap.json]`; `python3 -m unittest discover -s tests -v`.

### 2026-10-02T14:25Z — CLAUDE → CODEX — INFO — New data schema and gameplay state IDs for the future adapter

**Context:** CLAUDE.md requires a chat entry for schema/stable-ID changes and asset-facing states.

**Changed:** `economy/data/verdant_v0_2.json` (schema_version 2) adds `buildings` (cost, work, jobs, recipes, patch, services, morphology gates, `source` provenance), `services`, `patches`, `workforce`, `residence_rules`, `population`, `morphologies`, `trade`, `construction_rules` and `starting_state`. Every resource and recipe ID from v0.1 is unchanged. Added recipe `ceramic_kiln_biofuel` (§7.4 substitute). Experiment-only building `waste_collector` exists only in the probe overlay.

**Decision/evidence:** Gameplay state strings the adapter can rely on (Milestone B will map them to `set_action`/`set_condition_state`/`set_construction_progress`):
- facility status: `running`, `idle`, `no_input`, `no_workforce`, `environment`, `patch_depleted`, `morphology_missing`, `paused`;
- construction site: `awaiting_materials`, `awaiting_labour`, `in_progress`, `complete`, `cancelled`;
- residence: `normal`, `strained`, `dormant`; tiers `shelter`, `stable`, `symbiotic`, `memory`.

**Action requested:** None. Flag any state you expect to need visually that is missing.

**Compatibility/risk:** No presentation adapter exists yet (Milestone B). Building IDs may still be renamed or retired once Rich resolves the balance decisions; any such change will get its own entry.

**Reference:** `docs/ECONOMY_ENGINE.md` § "Stable state identifiers".
**Action requested:** Follow this cadence from the next work block and record concrete implementation progress here.

**Compatibility/risk:** Frequent edits increase merge-conflict risk. Keep entries append-only, short and self-contained; commit coherent checkpoints rather than rewriting another agent's entry.

**Reference:** Rich's direction on 2026-10-02.

### 2026-10-02T14:55Z — CODEX → CLAUDE — HANDOFF — Material chains, service states and Overseer UI

**Context:** Rich asked Codex to continue the approved artistic path while Claude resolves the honest-economy bootstrap. The remaining presentation gaps were resource transformation, visible neighbourhood condition and Pharaoh-like economic diagnosis.

**Changed:** Added three concept boards and `docs/art/concepts/VERDANT_MATERIAL_SERVICE_UI.md`; linked the system reference from the art bible.

**Decision/evidence:** Every resource family reads source → carried payload → dedicated storage → processed intermediate → use. District shortage, strain, dormancy and recovery appear physically in the persistent world. Ten departmental Overseer views connect aggregate stocks and throughput back to map entities; the Industry view requires stock, rate, workforce, bottleneck and seasonal forecast, while the residence inspector exposes service coverage and upgrade readiness.

**Action requested:** In Milestone B or the presentation-adapter pass, expose the implementation-facing diagnostics listed in `VERDANT_MATERIAL_SERVICE_UI.md`, using stable entity/resource IDs so ledgers and map selection can cross-locate. Domain logic remains authoritative; do not calculate a second economy in UI code.

**Compatibility/risk:** All depicted counts, recipes, building footprints and rates are illustrative. This handoff adds no mechanics to Milestone A and does not supersede accepted balance data. Concepts are art/interface targets, not sprite sheets or final geometry.

**Reference:** `docs/art/concepts/VERDANT_MATERIAL_SERVICE_UI.md`; branch `codex/visual-preproduction`; draft PR #1.

### 2026-10-02T14:42Z — RICH via CODEX → CLAUDE — DECISION — Verdant concepts approved as visual foundation

**Context:** Rich reviewed the benchmark, era progression, residence evolution, branching morphology and map-development spreads.

**Changed:** `docs/art/ART_BIBLE.md` now records the concept family as the approved foundation for Verdant art style and design direction.

**Decision/evidence:** Use the concept images under `docs/art/concepts/` as the project's authoritative Verdant visual target. Written production corrections remain binding so generated painterly clutter, human architectural cues and excessive emission are not reproduced literally.

**Action requested:** Future presentation architecture and placeholders must remain replaceable by this visual system and expose the states described in `CLAUDE.md` and the art documents.

**Compatibility/risk:** Approval does not turn concept-image dimensions into gameplay footprints or expand vertical-slice content. Numerical balance and simulation remain independent.

**Reference:** `docs/art/ART_BIBLE.md`, `docs/art/concepts/`; Rich's approval on 2026-10-02.

### 2026-10-02T14:38Z — CODEX → CLAUDE — HANDOFF — Residence, morphology and map-evolution storyboards

**Context:** Rich requested three spreads to make the game's visual progression explicit: Pharaoh-like housing evolution, one ancestor branching through environmental/player choices, and empty-map-to-mature-district timelines.

**Changed:** Added three concept boards and `docs/art/concepts/VERDANT_EVOLUTION_STORYBOARDS.md`; linked the system reference from the art bible.

**Decision/evidence:** Residence evolution is additive and service-driven. Morphology retains common ancestry while changing economic capability. Mature maps retain visible original geography, resource history and district logic.

**Action requested:** Milestone A residence state should expose tier, need/service satisfaction, sustain progress, strain and dormancy without assuming a full model swap. Morphology IDs should remain stable and separate from payload/action state. Map systems must preserve patch identity through depletion or seasonal access changes.

**Compatibility/risk:** The images do not define tier counts beyond the art exploration, numerical effects, footprints or final morphology availability. Do not add a fifth residence tier to the vertical slice solely because the art spread explores it.

**Reference:** `docs/art/concepts/VERDANT_EVOLUTION_STORYBOARDS.md`; branch `codex/visual-preproduction`.

### 2026-10-02T14:24Z — CODEX → CLAUDE — INFO — Same-species visual progression established

**Context:** Rich approved the initial Verdant concept and requested three further boards to ensure both agents share the same artistic destination across resources, morphologies and development thresholds.

**Changed:** Added Early Settlement, Mature Industry and Memory/Planetary concept boards plus `docs/art/concepts/VERDANT_ERA_PROGRESSION.md`. Linked the progression reference from the art bible.

**Decision/evidence:** The same Verdant lineage escalates through economic organisation, material complexity and visible morphology rather than switching to metal/human technology. These concepts do not enlarge the current vertical-slice implementation scope.

**Action requested:** None for Milestone A. Preserve stable resource, workforce and morphology IDs so later presentation mapping can express this progression without rewriting the domain model.

**Compatibility/risk:** Treat boards as visual targets only. Do not infer footprints, recipes, collision, unit counts or new gameplay eras from them.

**Reference:** `docs/art/concepts/VERDANT_ERA_PROGRESSION.md`; branch `codex/visual-preproduction`.

### 2026-10-02T14:12Z — CODEX → CLAUDE — INFO — First Verdant benchmark concept retained

**Context:** The visual benchmark now has a directional concept showing the Silicate extraction, transport, storage and washing story alongside residence and agriculture.

**Changed:** Added `docs/art/concepts/verdant_benchmark_concept_v01.png` and its production review. Linked the concept from the vertical-slice asset manifest.

**Decision/evidence:** The concept successfully establishes material hierarchy and functional process visibility. It is explicitly not a geometry or collision blueprint. The review records required reductions in clutter/emission and calls for a more alien carrier silhouette.

**Action requested:** None during Milestone A. For Milestone B, use the concept only to validate that placeholder/presentation adapters can express payload, recipe progress, output and seasonal state.

**Compatibility/risk:** Do not infer collision, capacity, path width or building footprint from the image. Final scale remains a Godot benchmark decision.

**Reference:** `docs/art/concepts/VERDANT_BENCHMARK_CONCEPT_V01_REVIEW.md`; branch `codex/visual-preproduction`.

### 2026-10-02T14:00Z — CODEX → CLAUDE — HANDOFF — Verdant visual pre-production contracts ready

**Context:** Rich approved beginning the visual track while Milestone A strengthens the headless economy. The v2 art direction now translates the former Pondlife look into the chemistry-driven economy and limits bulk production behind one benchmark.

**Changed:** Added `docs/art/ART_BIBLE.md`, `docs/art/ASSET_REUSE_AUDIT.md`, `docs/art/VERTICAL_SLICE_ASSET_MANIFEST.md` and `docs/art/VISUAL_BENCHMARK.md` on branch `codex/visual-preproduction`.

**Decision/evidence:** Preserve the living-glass/coral/shell/mineral visual thesis and Verdant palette, but derive new forms from economic functions. Reuse legacy environment/material work selectively; do not reinstate the old generic three-resource or 11-role × 3-faction roster. The first art gate is a nine-asset Silicate extraction/processing benchmark, not a broad content batch.

**Action requested:** During Milestone A, preserve the adapter semantics in `CLAUDE.md`. When preparing Milestone B, review `docs/art/VISUAL_BENCHMARK.md` and flag any presentation state that the proposed adapter cannot express cleanly. Do not encode final visual bounds as collision or balance.

**Compatibility/risk:** The docs introduce no gameplay schema changes. Visual IDs are presentation identifiers and must map to gameplay definitions rather than replace them. Canonical asset paths are intentionally unset until benchmark acceptance.

**Reference:** Branch `codex/visual-preproduction`; validation: `git diff --check`; art documents under `docs/art/`.

### 2026-10-02T13:46Z — CODEX → CLAUDE — HANDOFF — Begin Milestone A: honest headless economy

**Context:** Rich has approved starting programming in this repository. The existing simulator proves the paper recipe arithmetic but currently uses magical time-based facility/residence `set` events. It does not yet prove that the city can afford construction or staff its economy.

**Changed:** Added root `CLAUDE.md` with project memory, technical boundaries, art-integration contract, collaboration rules and the complete Milestone A assignment. Added this project channel.

**Decision/evidence:** Preserve the deterministic, data-driven headless model and strengthen it before creating the Godot client. The current reference completes the Memory Reef at 84:48 with ten passing tests, but that time is not sacred once construction and workforce become honest.

**Action requested:** Implement Milestone A from `CLAUDE.md` on a focused branch. Report genuine infeasibility rather than weakening rules to preserve 84:48. Add a new entry here for any schema or adapter-facing change and at the review handoff.

**Compatibility/risk:** Do not couple the domain model to Godot. Do not encode visual dimensions as gameplay collision or balance. Do not rename resource IDs without documenting migration impact.

**Reference:** `CLAUDE.md`, `economy/data/verdant_v0_1.json`, `economy/model.py`, `tests/test_economy.py`; baseline command: `python3 -m unittest discover -s tests -v`.

### 2026-10-02T13:40Z — CODEX → CLAUDE — INFO — Art direction that remains valid

**Context:** The project has pivoted from the old three-resource prototype to a chemistry-driven city builder, but Rich wants to preserve and extend its successful visual identity.

**Changed:** None in this repository yet.

**Decision/evidence:** Retain the miniature living-glass/coral/shell/mineral thesis, Verdant teal/green/amber material language, rotating-camera readability, clustered environmental composition and staged organic construction. Treat the old fixed building/faction roster as reference rather than a requirement.

**Action requested:** Keep presentation replaceable and use the adapter described in `CLAUDE.md`. Do not create final silhouettes in programmer art.

**Compatibility/risk:** The revised asset manifest and chemistry-specific art bible are still pending. Placeholder scenes must tolerate later replacement without gameplay changes.

**Reference:** `CLAUDE.md` section “Code/art integration contract”.
