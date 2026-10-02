---
id: 2026-10-02T1746Z-rich-test-all-four-design-changes-in-governor-sweep-v3
from: rich
to: [claude, codex]
status: DECISION
subject: Test all four design changes in governor sweep v3
refs: [2026-10-02T1741Z-claude-governor-sweep-v2-no-bounded-package-passes-design-decision]
closes: [2026-10-02T1741Z-claude-governor-sweep-v2-no-bounded-package-passes-design-decision]
respond_by: 
tags: [economy, balance]
branch: 
commit: 
relayed_by: claude
---

## Context

Answer to the 1741Z REQUEST: governor sweep v2 found no passing package. Rich answered in the Claude conversation, in a multiple-choice prompt with multi-select.

## Changed

Nothing yet.

## Decision/evidence

Rich selected all four options to test in the next sweep, verbatim labels:

- "Ease Carbonate bootstrap (Recommended)"
- "Earlier Mineral Jaw (Recommended)"
- "Less Adapted demand"
- "Longer horizon"

The question as asked: "Which design changes should I test in the next sweep? Each is a rule change, so I need your call. I'd test each one alone and then in combination, with the same pass criteria."

## Action requested

Claude: build governor sweep v3 with these four levers, each bounded and listed least to most generous, plus the Builder WP lever. Report the least-generous passing package, or the evidence if none passes. Selecting a package for promotion remains Rich's decision.

## Compatibility/risk

These are rule candidates, tested as overlays in the sweep only. Nothing is promoted to the baseline until Rich approves it.

## Reference

2026-10-02T1741Z-claude-governor-sweep-v2-no-bounded-package-passes-design-decision
