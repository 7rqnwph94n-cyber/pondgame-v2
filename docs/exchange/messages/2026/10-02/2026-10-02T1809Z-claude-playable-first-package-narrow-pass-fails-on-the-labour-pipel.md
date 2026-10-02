---
id: 2026-10-02T1809Z-claude-playable-first-package-narrow-pass-fails-on-the-labour-pipel
from: claude
to: [rich, codex]
status: HANDOFF
subject: Playable-first package: narrow pass fails on the labour pipeline; moving to Milestone B
refs: [2026-10-02T1742Z-rich-prioritise-playable-silica-street-after-targeted-structural, 2026-10-02T1802Z-claude-governor-sweep-v3-carbonate-fixed-labour-pipeline-now-binds]
closes: [2026-10-02T1802Z-claude-governor-sweep-v3-carbonate-fixed-labour-pipeline-now-binds]
respond_by: 
tags: [economy, milestone-b]
branch: claude/milestone-a-honest-economy
commit: 16455ef
---

## Context

Rich's 17:42Z playable-first decision (relayed by Codex) asked for one narrow acceptance pass on four targeted repairs, then Milestone B. My sweep v3 (all four design changes, per Rich's 17:46Z answer to me) had already run. Both are now done.

## Changed

- `candidate_playable_v1.json` contains the four repairs and is marked CANDIDATE, not promoted:
  1. finite surface-Carbonate gleaning by 2 General workers;
  2. Mineral Jaw research without Repair Enzyme;
  3. the first Washery staffed by General workers (later ones stay Adapted);
  4. Builders at 3 WP.
- Reference governor v3: skips buildings the rules don't define, and gives the Dredge and Nutrient Washer a player-visible labour priority of 3.
- Sweep v4 (9 runs: gleaning rate × reserve only) and `docs/milestone_a/GOVERNOR_SWEEP_V4_RESULTS.md`, commit `16455ef`. 122 tests pass on the Mac.

## Decision/evidence

**The narrow package fails: 0 of 9 runs, and no run reaches Symbiotic.**

What it achieves:
- first Stable at 24:29 (baseline 43:44);
- population 88–103;
- food and maintenance solvent, with no devolution.

Without the labour priority the package froze population at 24: the new General jobs starved the Dredge, so no Growth Nutrient was made and no migrants came. That trap matters for onboarding.

The remaining blocker, the same as in sweep v3, is labour supply against job count:
- only 3 Shelter→Stable evolutions in 120 minutes;
- General and Adapted vacancies at the same time;
- Symbiotic gates (Distribution, Clinic) only around 95–100 minutes.

Carbonate is solved by either route: gleaning, or the Carbonate-only first Cutter.

## Action requested

**Rich:** no blocking decision. Following 17:42Z item 6, I am moving to Milestone B now and will build the playable Silica Street slice on the honest economy plus this provisional package. When you're ready, choose a population or job-scale fix to make the Reef reachable, for example:
- faster migration or larger homes;
- fewer early job slots;
- cheaper evolution;
- a later Reef target.

**Codex:**
- New candidate stable IDs: patch `surface_carbonate`, building `carbonate_gleaning_site`, recipe `carbonate_gleaning`. These are not contract-bound until promotion.
- A placeholder is fine; please don't commission final art for it yet.
- I will send a CONTRACT message before the Milestone B adapter depends on them.

## Compatibility/risk

`presentation_states.json` v1 is unchanged; it does not enumerate building IDs. The package is provisional, so balance values may change.

## Reference

`docs/milestone_a/GOVERNOR_SWEEP_V3_RESULTS.md` (`0119aec`) and `GOVERNOR_SWEEP_V4_RESULTS.md` (`16455ef`) on `claude/milestone-a-honest-economy`. Decisions: `2026-10-02T1742Z-rich-prioritise-playable-silica-street-after-targeted-structural`, `2026-10-02T1746Z-rich-test-all-four-design-changes-in-governor-sweep-v3`.
