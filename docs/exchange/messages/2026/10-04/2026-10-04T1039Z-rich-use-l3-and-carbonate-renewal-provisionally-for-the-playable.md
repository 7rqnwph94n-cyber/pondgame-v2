---
id: 2026-10-04T1039Z-rich-use-l3-and-carbonate-renewal-provisionally-for-the-playable
from: rich
to: [claude, codex]
status: DECISION
subject: Use L3 and Carbonate renewal provisionally for the playable slice
refs: [2026-10-04T1029Z-claude-carbonate-workforce-v1-l3-carbonate-renewal-meets-every-crit]
closes: []
respond_by: 
tags: [economy, playable, decision]
branch: 
commit: 
relayed_by: codex
---

## Context

Codex presented Rich three choices after Claude's L3 + C result: (1) cap renewal and test longer (recommended); (2) use the two-lever package provisionally for the playable slice; (3) keep the current economy unchanged. The candidate reached Symbiotic at 106:29 and maintained food and upkeep solvency through 120:00, but did not open the Reef. Surface Carbonate renewal in the experiment is currently uncapped.

## Changed

Rich chose provisional use for the playable slice. The long-game v0.2 baseline is not being rewritten by this decision.

## Decision/evidence

Rich's reply, verbatim: “2”

Codex interpretation, separately labelled: make the L3 + slow Carbonate-renewal package the **provisional default playable-slice overlay**, not a final economy rule or a claim that the Memory Reef is reachable. Before exposing it in the Godot client, add a finite cap to the renewable surface Carbonate reserve and verify that this safety constraint preserves the slice result. If it does not, do not silently loosen the cap or switch the client; return the evidence to Codex/Rich.

## Action requested

Claude: own the economy/config integration. Prepare a named overlay combining the existing `candidate_playable_v1` package with L3 early job slots and C = 0.2/min surface Carbonate renewal. Add an optional finite reserve cap (with tests and a documented physically grounded value), leaving the v0.2 baseline and existing experiments intact. Re-run the 120-minute criteria on the capped candidate; verify the human opening without Autoplay and the Godot bridge/client tests. Only if those pass, point `client/settings.cfg` at the provisional slice overlay and update `client/README.md` so removal/selection is obvious. Make the launch state and remaining Reef limitation explicit. Announce any shared-file edits before touching them; do not edit HUD look or map presentation. Handoff the exact capped value, metrics and commits to Codex through the exchange.

## Compatibility/risk

The cap may change the previously observed 106:29 Symbiotic and upkeep result. The action is conditional on the re-test; Rich did not authorise an uncapped renewable source as a permanent economy law or a broad redesign. No Memory Reef target is declared met.

## Reference

Rich's reply on 2026-10-04; `b553643`; `docs/milestone_a/CARBONATE_WORKFORCE_V1_RESULTS.md`; `docs/PLAYABLE_SLICE_CHARTER.md`.
