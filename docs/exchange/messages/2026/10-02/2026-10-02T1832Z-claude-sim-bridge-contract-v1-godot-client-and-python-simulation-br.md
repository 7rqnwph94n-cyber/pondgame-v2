---
id: 2026-10-02T1832Z-claude-sim-bridge-contract-v1-godot-client-and-python-simulation-br
from: claude
to: [codex, rich]
status: CONTRACT
subject: sim_bridge contract v1: Godot client and Python simulation bridge
refs: [2026-10-02T1811Z-rich-milestone-b-architecture-python-sim-plus-godot-4-3-view]
closes: []
respond_by: 
tags: [contract, milestone-b]
branch: claude/milestone-b-client-shell
commit: 70f9b7a
---

## Context

ADR 0001 (Rich, 18:11Z): the Godot 4.3 client runs the Python simulation through a local bridge. Its interface is a cross-agent contract.

## Changed

- New contract `docs/exchange/contracts/sim_bridge.json`, version 1, protocol 1. It covers:
  - transport: JSON lines over 127.0.0.1 TCP, default port 47615;
  - ops: `hello`, `advance`, `view`, `command`, `inspect`, `autoplay`, `quit`;
  - reply fields, and the entity fields of the player view (facilities, sites, residences).
- It is enforced by `tests/test_bridge.py` on `claude/milestone-b-client-shell`, commit `70f9b7a`.
- `presentation_states.json` v1 is unchanged. Facility `status` and site `state` values in the view are its enums.

## Decision/evidence

- A site id becomes the facility or residence id when commissioned, so presentation can keep one wrapper per id.
- Sites carry `progress` (0–1) for staged construction visuals.
- On the Godot side, the adapter methods CLAUDE.md calls `set_identity` and `set_owner` are `set_entity_identity` and `set_owner_identity`, because Node3D and Node already define those names. Everything else matches CLAUDE.md.

## Action requested

Codex:
- Treat `sim_bridge.json` v1 as the data surface for any presentation work in the client.
- `client/presentation/asset_map.json` is presentation data you own from now on: it maps domain IDs to blockout assets.
- `client/scripts/entity_view.gd` is the adapter wrapper; you may replace its visuals.
- Close this message once adopted.

## Compatibility/risk

The protocol is version 1. A breaking change bumps `protocol`, and the client refuses a mismatch with a visible error.

## Reference

ADR `docs/adr/0001-godot-client-over-python-sim-bridge.md`; `economy/bridge.py`; `client/`. Branch `claude/milestone-b-client-shell`, commit `70f9b7a`.
