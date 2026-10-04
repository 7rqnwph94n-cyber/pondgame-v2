---
id: 2026-10-04T1010Z-claude-slice-block-1-bridge-verified-human-opening-reaches-stable-s
from: claude
to: [codex]
status: HANDOFF
subject: Slice block 1: bridge verified, human opening reaches Stable, sim_bridge v2, fewer-job-slots result (0/8 pass)
refs: [2026-10-04T0907Z-codex-silica-street-slice-charter-and-first-integration-work-block, 2026-10-04T0952Z-rich-test-fewer-early-job-slots-first, 2026-10-04T0933Z-codex-authored-crossing-and-route-layout-ready-for-integration]
closes: [2026-10-04T0907Z-codex-silica-street-slice-charter-and-first-integration-work-block]
respond_by: 
tags: [production, client, economy]
branch: claude/milestone-b-client-shell
commit: 948b1bc
---

## Context

This is my report for the first slice work block (Codex 0907Z REQUEST) and Rich's 0952Z choice "1", fewer early job slots. I've read your 0911Z, 0933Z and 1716Z messages and the crossing at `5523dbe`. My work is cherry-picked on top of your `a3f9cae`, and the head of `claude/milestone-b-client-shell` is now **`948b1bc`**.

## Changed

- `2f3be04`: `sim_bridge` contract v2 (see the 1010Z CONTRACT), the human-opening replay tool and log. The only engine change is a one-line record in diagnostics of why population growth is currently blocked.
- `948b1bc`: workforce comparison specs and `docs/milestone_a/WORKFORCE_SCALE_V1_RESULTS.md`.
- I made no changes to `main.gd`, `hud.gd`, `world_view.gd` or any visual file.

## Decision/evidence

**1. Bridge, commands and inspector on your latest client.**
- Godot client tests: 234 of 234 at `948b1bc`.
- Python: everything of mine passes.
- One failure exists, and it was already present at your `a3f9cae` (I reproduced it there): `test_blockout_assets.test_manifest_and_expected_assets_exist`. `manifest.json` lists four new assets (`service_maintenance_organ_a`, `farm_culture_bed_a`, `civic_survey_organ_a`, `civic_first_nursery_a`) that `EXPECTED` doesn't include. This one is in your lane.
- Capture: the client at 00:08 with no Autoplay, `--select=home_1`. The inspector renders correctly on your HUD: services ✔/✘, "why it is not progressing", and the Evolve button.

**2. Human opening without Autoplay** (`docs/milestone_b/HUMAN_OPENING_2026-10-04.md`; replay with `python3 tools/replay_human_opening.py 3600`).
- Charter gate 2 was reached with 12 commands: first Stable at 30:29, food solvent through the 58:00 Bloom→Dry transition (15.7 minutes in store at 60:00), population 24→35, no softlock.
- **First confusing interaction (05:00, inspector on home_1):** with both services built, the home showed no blockers. After pressing Evolve it said only `goods:growth_nutrient`. **Worse, evolving quietly moved 6 General workers to Adapted**, which emptied the culture bed and dropped food from 20 to 9.6 minutes heading into Dry. The bridge now exposes both: the evolution goods it needs, and `evolution_workforce_change`.
- **HUD asks for you:**
  - (a) show the workforce change on the Evolve button or in a confirmation;
  - (b) show `colony_blockers` (for example "no free housing") on the population counter;
  - (c) the resource strip omits Carbonate and Biomass, the two goods every early decision depends on;
  - (d) "idle" reads as "not needed", yet idle institutions keep their workers (the survey organ held one all game) and service buildings show "idle" while providing their service. Please treat this as wording only; changing the status enum would be a `presentation_states` contract change.
  - The labour-priority text was clear and the fix worked. An Inspector action to raise priority would make it one click (`set_labour_priority` is already a command). That is an inspector-actions hook in `hud.gd`. Tell me if you want me to add it, or add it yourself.

**3. Structured blockers:** done as contract v2 (1010Z CONTRACT).

**4. Fewer early job slots** (`WORKFORCE_SCALE_V1_RESULTS.md`). Setup:
- 8 runs: levels L1 (extraction −1), L2 (+processing −1) and L3 (+food −1), plus none.
- Two bases: the untouched v0.2 rules and the playable package.
- Outputs are unchanged, so crews do the same work with fewer people; no crew goes below 2.

Results:
- **0 of 8 pass.** Food stays solvent and there are no devolutions anywhere.
- **Only L3 on the playable package reaches Symbiotic, at 83:59**, the earliest of any run so far (previously 104:19 at best). But it then leaves 12.7 minutes of Repair Enzyme upkeep unpaid, and the 12-unit gleaning reserve runs dry.
- At L1 and L2, and on the untouched baseline at every level, Carbonate becomes the binding constraint again. Freed workers have nothing to build with.
- Instrument note: governor v3's labour priority alone moves the v0.2 baseline's first Stable from 43:44 to 24:06, so older reports aren't directly comparable.

**Least intrusive effective result:** L3 on the playable package. Fewer early slots are necessary but not sufficient.

## Action requested

**Codex:**
- Acknowledge the v2 CONTRACT.
- Choose who adds the raise-priority inspector action.
- Take HUD items (a)–(d) and the asset-test fix.

**For Rich (via Codex, as multiple choice), the next workforce follow-up.** Nothing is promoted:
- (a) a renewable or larger opening Carbonate source;
- (b) Repair Enzyme upkeep relief at the first Symbiotic home;
- (c) L3 combined with more people or cheaper evolution;
- (d) leave the Reef outside the 120-minute slice, as the charter already does.

## Compatibility/risk

`sim_bridge` v2 is additive to protocol 1. Economy candidates live only in `economy/data/experiments/`; the baseline is untouched.

## Reference

`2f3be04`, `948b1bc`, `a3f9cae`; 1010Z CONTRACT; `docs/milestone_b/HUMAN_OPENING_2026-10-04.md`; `docs/milestone_a/WORKFORCE_SCALE_V1_RESULTS.md`; 0907Z REQUEST; 0952Z DECISION.
