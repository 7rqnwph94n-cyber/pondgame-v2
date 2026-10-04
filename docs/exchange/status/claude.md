---
agent: claude
updated: 2026-10-04T10:29Z
state: waiting
current_task: Carbonate+workforce v1 reported (b553643): L3+C meets all criteria except Reef; waiting on Rich via Codex
branch: claude/milestone-b-client-shell
head_commit: d8c867a
waiting_on: Rich via Codex (adopt L3+C provisionally / longer-horizon check / no change)
---

## Now

- Block 1 delivered (HANDOFF to Codex):
  - Bridge verified: 234 of 234 client tests at `948b1bc`.
  - Human opening reaches first Stable at 30:29 and stays food-solvent through Dry.
  - `sim_bridge` v2 published (1010Z CONTRACT).
  - Fewer early job slots: 0 of 8 pass. The best result, L3 on the playable package, reaches Symbiotic at 83:59, but Enzyme upkeep and Carbonate then block it.
- One pre-existing failure in Codex's `a3f9cae`: an asset manifest test. Reported.

## Next

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
