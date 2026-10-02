# Pondgame v2 — Claude/Codex project channel

This file is the durable, append-only communication channel between the project's programming and visual-design agents. It exists because conversational context is temporary and the repository must retain cross-disciplinary decisions.

Rich is the final decision-maker. `CLAUDE.md`, accepted design documents, data contracts and tests remain authoritative; this log records handoffs, requests, discoveries and the reasoning behind changes.

## Required protocol

- Read the latest entries before beginning work.
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
