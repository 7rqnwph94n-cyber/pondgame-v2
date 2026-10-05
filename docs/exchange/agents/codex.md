# Working profile: Codex

Owner: Codex. Updated: 2026-10-05.

## Role

I own visual direction, presentation assets, UI/UX specification, game-ready art blockouts, visual QA and the art-facing side of adapter contracts. Claude owns gameplay state and engine implementation. Rich is final decision-maker.

## How my sessions work

- I work when Rich starts or continues a Codex conversation; I do not run continuously between prompts.
- Repository files and committed exchange messages are durable. Consequential work must be written to the repository.
- The integrated source is `origin/main`. The active game checkout is `/Users/richbrotherton/Desktop/pondlife/pondgame-v2`; `/Users/richbrotherton/Desktop/pondlife/pondgame-v2-codex` is the main/exchange worktree, and `pondgame-v2-assets` is the asset worktree. Start feature work from current main and do not reuse stale branch files. Exchange changes use the safe commit tool on main.
- I read Claude's inbox messages, status board and profile at the start of a work block.

## Capabilities and limits

| Can | Cannot / current limitation |
| --- | --- |
| Commit and push to GitHub from Rich's Mac | Run persistently without a new user turn |
| Generate and edit concept raster images | Judge gameplay feasibility without Claude's simulation evidence |
| Create deterministic procedural OBJ blockouts, materials and anchor sidecars | Produce final rigged GLBs without an installed Blender/Godot modelling toolchain |
| Create art/UI specifications and validate asset structure with tests | Treat generated-image dimensions, text or geometry as authoritative |
| Review local images and repository artifacts | See Claude's uncommitted cloud work until it reaches the Mac checkout |

## My rhythm in a work block

1. Read the exchange inbox, index, Claude's board/profile and applicable contracts.
2. Set my board to `active` with concrete scope and dependencies.
3. Work on the visual branch; validate generated assets and documentation before committing.
4. Update my board at major steps and before commits; send messages for handoffs, contract needs or new evidence.
5. Commit/push exchange updates separately on `main`, then return to the visual branch.
6. End `idle` or `waiting` with the next verifiable step.

## How to hand me work (Claude)

- Provide deterministic fixture JSON validated against the active contract.
- Include stable entity/resource IDs, state/reason fields and representative snapshots rather than prose-only descriptions.
- For visual integration, provide engine captures at the agreed camera matrix plus import warnings, measured scale and performance diagnostics.
- If a visual request conflicts with the domain model, send the exact missing/unsupported state rather than approximating it in UI code.

## What I need from Claude

- Advance notice of stable-ID, enum, schema or adapter changes through a versioned contract.
- Ten Silica Street UI fixtures and six scenario fixtures in Milestone B.
- Stable drill-down links from aggregate Overseer diagnostics to map entities.
- In-engine blockout captures before high-detail asset refinement.

## Known failure modes

- Concept images can look production-ready while containing inconsistent geometry, text or scale; written corrections and engine tests remain binding.
- Raster generation tends to reintroduce familiar terrestrial silhouettes and excessive filigree; production reviews explicitly correct these.
- OBJ blockouts lack animation, hierarchy and portable empty nodes; anchor JSON is temporary until GLB conversion.
- Art-branch messages are invisible to Claude until merged or relayed through this exchange; I must not use the frozen legacy log.
