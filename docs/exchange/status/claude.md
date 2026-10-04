---
agent: claude
updated: 2026-10-04T10:48Z
state: waiting
current_task: Provisional slice overlay delivered (141db45), cap 12; client launches it; waiting on Codex review
branch: claude/milestone-b-client-shell
head_commit: d8c867a
waiting_on: Codex (review; whether to add a consumed-by blocker parameter)
---

## Now

- Block 1 delivered (HANDOFF to Codex):
  - Bridge verified: 234 of 234 client tests at `948b1bc`.
  - Human opening reaches first Stable at 30:29 and stays food-solvent through Dry.
  - `sim_bridge` v2 published (1010Z CONTRACT).
  - Fewer early job slots: 0 of 8 pass. The best result, L3 on the playable package, reaches Symbiotic at 83:59, but Enzyme upkeep and Carbonate then block it.
- One pre-existing failure in Codex's `a3f9cae`: an asset manifest test. Reported.

## Next

- Done: `141db45`, provisional slice overlay `candidate_playable_slice_v1` (L3 + Carbonate renewal capped at 12). Retest unchanged; client launches it; human opening reaches Stable at 25:55.

- Done: `b553643`, carbonate_workforce_v1. 8 bounded candidates: L3 + C meets every criterion except the Reef (Symbiotic at 106:29 and held, upkeep paid). Nothing promoted.

- Done since block 1: `dd7fda3`, a one-click Staff first / Normal priority inspector action (Codex 1015Z). Client tests 240 of 240.

- Raise-priority inspector action, if Codex assigns it to me.
- The workforce follow-up Rich chooses: bounded test, then report.

## Blocked on / waiting for

- Codex: v2 acknowledgement; HUD items; asset test.
- Rich via Codex: follow-up choice (a)–(d).

## Assumptions I'm making about the other agent's work

- Codex owns terrain, map, assets, placement, camera and HUD look. Edits to the shared files `main.gd`, `hud.gd` and `world_view.gd` are announced first.
- Map geometry and `HarvestAnchor` are presentation-only until Rich decides otherwise.

## Recently finished

- `67437ed`: merged the exchange histories. `70f9b7a`: client shell, bridge, ADR 0001. `16455ef`: sweep v4.
