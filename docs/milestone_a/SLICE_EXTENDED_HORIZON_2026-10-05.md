# Provisional slice: extended horizon, 5 October 2026

Reproduce with `python3 tools/verify_slice_horizon.py`. Uses unchanged `candidate_playable_slice_v1` rules and `reference_governor_v3`; only the scenario run duration changes. Raw results and events are in `SLICE_EXTENDED_HORIZON_2026-10-05.json`.

| Horizon | Population | Stable / Symbiotic | Food emergency | Unpaid upkeep | Enzyme paid | Carbonate reserve | Reef stages |
|---|---:|---|---:|---:|---:|---:|---:|
| 120 min | 92 | 3 / 1 | 0 min | 0 min | 6 | 6.28 | 0 |
| 180 min | 100 | 3 / 1 | 0 min | 21.5 min | 25 | 3.28 | 0 |
| 240 min | 124 | 3 / 1 | 0 min | 54.7 min | 40 | 0.28 | 0 |

First Stable remains 21:39 and first Symbiotic 106:29 in every run. No Staple shortage or devolution; cumulative Gel shortage remains 3.0 residence-minutes. No Memory home or Reef stage at any horizon. Governor reports zero failed actions.

**First unpaid upkeep: 136:29**, after the grace period. It repeatedly suspends and restores maintenance service thereafter. Biomass and Fired Ceramic feature among the later bottlenecks; the surface Carbonate source is almost depleted by 240 minutes. The renewal cap limits standing stock, not total extraction over time.

Conclusion: the opening remains a viable provisional slice, but the 120-minute result does not establish long-game upkeep solvency. Waiting longer does not solve Reef progression under this governor. A future bounded upkeep/production diagnosis should precede any rule promotion. This is one deterministic governor trajectory, not a new human playtest or proof that other strategies cannot succeed. No economy values were changed.
