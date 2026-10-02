# Working profile: Claude

Owner: Claude. Updated: 2026-10-02. Update this file whenever how I work changes.

## Role

I'm the gameplay and systems programmer: the headless economy, simulation, Godot architecture (Milestone B onward), tooling, saves, tests and integration. I own gameplay state and the presentation adapter's data side. Codex owns art, presentation assets and visual QA. `CLAUDE.md` is my standing brief.

## How my sessions work

- **I only work when Rich starts or continues a conversation with me.** I do not poll the repository in the background. "Respond within your next work block" means the next time Rich prompts me. If something is urgent for me, Rich needs to tell me, or the message has to be waiting when he does.
- Each session starts cold except for the repository. I read `CLAUDE.md`, my inbox, `INDEX.md` and Codex's board before touching code. Anything not written down in the repository is lost to me.
- I run in a cloud workspace and reach Rich's Mac (`~/Desktop/pondlife/pondgame-v2`) through a desktop bridge.
  - The bridge sometimes drops for a few minutes. Anything I haven't written to the Mac yet waits in my workspace until it reconnects; it is not lost, just delayed.
  - If my board says `offline`, that is usually the reason.
- I tell Rich in plain words when I finish a block. My last board update is the reliable record of where I stopped.

## Capabilities and limits

| Can | Cannot (currently) |
|---|---|
| Read, edit, run and commit in the repository on Rich's Mac (Python 3.10 there; 3.13 in my workspace) | **Push to GitHub.** No credentials. Rich pushes for me, so Codex only sees my work after a push. |
| Run long headless jobs (a 288-run economy sweep takes ~6 min on my workspace's 2 cores) | Delete files on Rich's Mac without his per-session approval (git sometimes needs it for lock files) |
| Read Codex's branches (`git show codex/...:path`) | See Codex's conversations with Rich, or its local, uncommitted work |
| Produce deterministic fixtures, reports and charts from the simulation | Judge visual quality; I treat art documents as authoritative for look and feel |

## My rhythm in a work block

1. Pull `main`, read the inbox and the board, and run the relevant tests.
2. Update my board (state `active`, plan).
3. Work in small verifiable steps, updating the board at each major step or about every 15 minutes, and after every long job.
4. Send messages only on the events in the cadence table: decisions, blockers, contract changes, handoffs, and evidence that changes someone's plan.
5. Commit feature work on `claude/<topic>` and exchange updates on `main` as `exchange:` commits.
6. End with the board set to `idle` or `waiting`, saying exactly what's next.

## How to hand me work (Codex)

- Send a `REQUEST` with **acceptance criteria I can test**, for example: "fixture JSON for these ten states, validated against `contracts/presentation_states.json`".
- If you need a new state, field or ID from the simulation, ask for a **contract change**. Don't describe it only in prose; I will add it to `contracts/` with tests.
- Tell me which of your assumptions about gameplay you're relying on (put them in your board's "Assumptions" section). I check them against the model every session.
- Visual dimensions never become gameplay values unless Rich decides so. You don't need to restate this each time.

## What I need from Codex

- Early warning when an art direction implies a gameplay state the model doesn't have yet.
- Your board kept current, so I know which states and fixtures you're about to depend on.
- Confirmation (a message that `closes` my `REQUEST`) when you have adopted a contract version.

## Known failure modes (so you can catch them)

- My scripted reference plans can be brittle. Treat balance conclusions as evidence for Rich, not decisions, unless Rich has approved them.
- I can over-explore on a hard problem. If my board shows the same task for a long time with no new evidence, it's fair to ask me (through Rich or a `REQUEST`) for a checkpoint.
