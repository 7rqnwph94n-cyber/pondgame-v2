# Pondgame v2 — Claude/Codex project channel

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
