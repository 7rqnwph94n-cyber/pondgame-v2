---
id: 2026-10-07T1542Z-codex-ten-architecture-massings-ready-for-review-not-default-adopt
from: codex
to: [claude, rich]
status: HANDOFF
subject: Ten architecture massings ready for review not default adoption
refs: []
closes: []
respond_by: 
tags: [architecture, art, review]
branch: codex/visual-preproduction
commit: ea646a4
---

## Context

Rich asked Codex to get going with six housing tiers and the Store/Washery/Kiln/Digester benchmark. Infrastructure allowance and Claude design request were published earlier today.

## Changed

Published ea646a4 on codex/visual-preproduction: ten bespoke Blender massing candidates, editable source, Y-up OBJ/MTL exports, visual cargo/utility anchors, separate Godot review scene, authored OBJ normal support and regressions. Production plan and review findings are in docs/art/. No playable asset mappings were changed in this commit. The earlier broad draft mapping was withdrawn locally and preserved in the draft archive rather than adopted.

## Decision/evidence

Ten runtime imports have zero mesh/normal errors. Normal Metal/Forward+ screenshots are docs/art/renders/architecture_v03/godot_housing.png and godot_industry.png. Export tests pass, Python regression 186/186, client 316/316 against retained original asset mapping. Six housing silhouettes range 0.81–4.23m, with shared court, terraces and archive fan rather than a shared segmented disc foundation.

Internal review: these are not finished production art. Rib repetition, enclosed habitation, stored goods, filtering anatomy and neighbour/rotation readability still require refinement. No six-stage gameplay support, utility transport semantics or Rich visual acceptance is claimed.

## Action requested

Consume the design request from 1530Z; do not integrate these massings into default playable settings yet. If needed, review assets on the art branch and respond with the bounded progression/infrastructure proposal. Codex next refines tiers 1–3, then 4–6, then the four facilities. This handoff does not close pending domain requests.

## Compatibility/risk

Authored normal loader changes are additive and separately regression-tested. Visual anchors remain nonauthoritative until a versioned domain agreement. Store intentionally has cargo ports without mandatory clean-flow/waste sockets. Kiln retains delivered fuel; no external power graph.

## Reference

ea646a4; docs/art/ARCHITECTURE_PRODUCTION_PLAN.md; docs/art/ARCHITECTURE_BENCHMARK_REVIEW.md; assets/architecture_v03/manifest.json. Review: godot --path client -s res://tests/architecture_review.gd -- housing (or industry/verify).
