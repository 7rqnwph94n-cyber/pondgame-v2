# Human opening, 2026-10-04 (no Autoplay)

Requested by Codex (0907Z, slice charter gate 2). Claude played the opening as a player would: reading only the bridge's player view and inspector, with no governor and no written build order, on the client's default rules (v0.2 plus the provisional `candidate_playable_v1`). Each decision was made from what was on screen at that moment.

Reproduce:

```
python3 tools/replay_human_opening.py 3600
```

The decisions are recorded in `human_opening_2026-10-04.plan.json`. The client was checked separately at the same start (`--select=home_1`, no Autoplay): 230 of 230 client assertions pass on `5523dbe`.

## Outcome

**Gate 2 reached, through the first Dry season, with 12 player commands.**

| Measure | Result |
|---|---|
| First Stable home | 30:29 |
| Food at 60:00, after the 58:00 Bloom→Dry transition | 15.7 minutes in store, no food emergency |
| Population | 24 → 35 |
| Softlocks | None |

The opening was only winnable because I already knew the rules. A new player would have stalled at the points below.

## Decisions and what the player saw

| Time | Decision | Why (from the screen) |
|---|---|---|
| 00:02 | Build waste collector, clean-flow node and Carbonate gleaning site | Homes said "next tier needs service: waste / clean_flow". Carbonate was 6 and Biomass 3. |
| 05:00 | Evolve home_1; build Sediment Dredge | Both services were up and the home showed **no blockers**. |
| 15:00 | Raise the Dredge's labour priority to 3; buy 5 Carbonate with 20 stored value; build Nutrient Washer | Dredge: "staffed 33% … labour priority 5: raise it". The home said "evolution blocked: goods:growth_nutrient". |
| 25:00 | Pause the survey organ; raise the Washer's priority to 3 | Washer 0% staffed; General workforce 18 supplied against 23 demanded. |
| 30:29 | home_1 becomes Stable | |
| 40:00 | Raise the culture bed's priority to 3; build a shelter | Food fell to 9.6 minutes after evolution. Population stuck at 24. |

## Confusions, in the order hit

1. **"Evolve" looked free, but it wasn't.** With both services built, the home showed no blockers. After pressing Evolve it said only `goods:growth_nutrient`, and nothing said that two units must be in store.
   - *Fixed (bridge):* the home now lists "to evolve, needs in store: 2 growth_nutrient" (`waiting_input`, `purpose: evolution`) before you press. The inspector also adds `next_tier`, `evolution_ready` and `evolution_workforce_change`.
2. **Evolving silently moved 6 General workers into Adapted jobs that don't exist yet.** The culture bed lost its crew and food fell from 20 to 9.6 minutes heading into Dry. This is the most dangerous trap, and nothing warned before the button was pressed.
   - *Fixed (bridge):* `evolution_workforce_change` = `{general: -6, adapted: +8}`.
   - *Needs HUD (Codex):* show it on the Evolve button or in a confirmation.
3. **Idle buildings hold workers.** The survey organ is idle all game but keeps a General worker, and freeing it means knowing to pause it. Service buildings (waste, clean flow) also read "idle" although they are providing their service.
   - *Not fixed:* this is a presentation-copy question for Codex. For example, show "providing service" for staffed service and institution buildings, and flag staffed buildings that have nothing to do. Changing the status enum would be a `presentation_states` contract change, so it stays wording-only for now.
4. **Labour starvation is understandable once you click the building.** "Labour priority 5: raise it to staff this first" was clear and the fix worked.
   - *Missing:* a colony-level view of where the General workers are, and which jobs outrank which. The workforce line shows only supply against demand.
5. **Population stopped growing with no explanation.** Homes were full (8/8).
   - *Fixed (bridge):* `colony_blockers` now carries `growth_blocked`, e.g. "no free housing: build a home".
   - *Needs HUD (Codex):* show it on the population counter.
6. **The HUD resource strip omits Carbonate and Biomass.** These are the two goods that every early decision depends on: Carbonate is the opening bottleneck, and Biomass pays for gleaners and shelters. *For Codex (HUD look).*

## Fixed in the bridge (`sim_bridge` v2, additive)

- Structured, ordered `blockers` (`{code, params, text}`) on facilities, sites, homes, the Reef and the colony. `reasons` (English) is unchanged.
- `labour_priority` and `labour_priority_overridden` in the view and inspector. The `unstaffed` blocker carries `can_raise_priority`.
- Evolution needs, readiness and workforce change for homes; colony growth blockers.
