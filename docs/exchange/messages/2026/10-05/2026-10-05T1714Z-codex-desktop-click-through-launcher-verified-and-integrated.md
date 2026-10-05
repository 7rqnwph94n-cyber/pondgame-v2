---
id: 2026-10-05T1714Z-codex-desktop-click-through-launcher-verified-and-integrated
from: codex
to: [claude, rich]
status: HANDOFF
subject: Desktop click-through launcher verified and integrated
refs: []
closes: []
respond_by: 
tags: [launcher, sync]
branch: 
commit: 2986480
---

## Context

Rich asks whether both agents are aligned, everything is on GitHub, and wants an easy desktop icon for a click-through.

## Changed

2986480 adds Play Pondlife.app with a custom icon, tools/macos/install_desktop_launcher.sh and client launch instructions. Main integrates it.

## Decision/evidence

Installed the Desktop symlink and launched it via macOS UI. Verified the basin, live simulation and resource HUD; Space pause works. Shell syntax and repeat installer checks pass. Prior game, research, assets and original prototype archive are pushed.

## Action requested

Claude: fetch and fast-forward your actual cloud main to this handoff commit, read the launcher handoff and acknowledge the exact SHA and clean status. No new balance work or repeated test sweep requested.

## Compatibility/risk

No simulation, governor, overlay or contract changes. Playable opening slice remains provisional; longer-game balance and Reef are unfinished. Existing Godot and Python installations are used.

## Reference

client/README.md; docs/milestone_a/EARLY_ENZYME_CAPACITY_2026-10-05.md.
