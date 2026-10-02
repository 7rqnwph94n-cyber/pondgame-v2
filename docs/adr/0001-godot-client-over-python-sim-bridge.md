# ADR 0001: The Godot client runs the Python simulation through a local bridge

- **Status:** accepted. Rich, 2026-10-02T18:11Z (exchange `2026-10-02T1811Z-rich-milestone-b-architecture-python-sim-plus-godot-4-3-view`).
- **Deciders:** Rich, on Claude's proposal.
- **Engine:** Godot 4.3, chosen by Rich.

## Context

Milestone B needs a client that loads the same definitions as the headless economy, advances the simulation, renders replaceable placeholder entities through the presentation adapter, has pause and speed controls, and shows why a process is stalled.

The rules are still changing quickly. Milestone A is not accepted: governor sweeps v2–v4 found no passing package. CLAUDE.md requires the domain to stay headless and independent of Godot nodes.

## Decision

The Python domain (`economy/`) remains the only rules authority.

1. The Godot client (`client/`) starts `python3 -m economy.bridge` as a local child process and talks to it over TCP on 127.0.0.1, using newline-delimited JSON.
2. The protocol is the `sim_bridge` contract (`docs/exchange/contracts/sim_bridge.json`). It is enforced by `tests/test_bridge.py`.
3. The client sends player commands (`command`) and time requests (`advance` N seconds). Pause and speed are client-side: they set how many fixed 1-second steps the client asks for per real second.
4. The bridge answers with the **player view** (`economy/player_view.py`). This is the same information the reference governor is restricted to, so the HUD, inspectors and balance instrument see one truth.
5. The stall inspector's reasoning (`economy/bridge.py: explain`) lives in Python, next to the rules it explains.
6. Presentation is data-driven and replaceable:
   - `client/presentation/asset_map.json` maps domain IDs to Codex's blockout assets;
   - `EntityView` implements the CLAUDE.md adapter surface;
   - OBJ blockouts are read at runtime from `assets/`, so Codex's asset folder stays untouched and no import step is needed;
   - a missing asset falls back to a category placeholder.
7. Layout is presentation-only and deterministic. The domain has districts, not coordinates. When spatial logistics arrive, positions become domain state and this changes.

## Consequences

**Positive**
- One source of truth, with no port to keep in sync while balance changes daily.
- Every balance change is immediately playable.
- Deterministic: the same commands and advances give the same views. This is tested.
- Headless sweeps, the governor and the client share code.

**Negative**
- Shipping needs either a bundled Python runtime or a port to GDScript/C# once the rules settle. That decision is Rich's, later.
- The process boundary adds latency. Measured locally in my workspace: 0.6 ms median for a 1-second `advance`, 6.4 ms for 32 seconds. Full views are re-sent each time (4–6 KB early in a game); deltas can come later if needed.
- Python 3.10+ is needed on the player's machine. The interpreter path is set in `client/settings.cfg` or with `POND_PYTHON`.

**Godot naming notes**
- `Node.set_owner()` and `Node3D.set_identity()` exist natively. The adapter therefore names those methods `set_owner_identity()` and `set_entity_identity()`; everything else matches CLAUDE.md.
- Under the dummy (headless) renderer, mesh commits print "Parameter m is null". This is harmless and does not appear with a real renderer.

## Alternatives considered

- **Port the rules to GDScript.** Ships natively, but means weeks of porting before anything is playable, with two drifting copies during balancing.
- **Port the rules to C#.** The same trade-off, and it needs the .NET build of Godot.
- **GDExtension or embedded Python.** Tighter integration, but heavy build tooling per platform. It may be revisited for shipping.

## Verification

From the repository root:

| Check | Command |
|---|---|
| Python tests, bridge included | `python3 -m unittest discover -s tests` |
| Client test setup (once) | `godot --headless --path client --import` |
| Client tests (launch the real bridge) | `godot --headless --path client -s res://tests/run_tests.gd` |
| Screenshot capture, also used for Codex's import review | `godot --path client -- --capture=out.png --capture-seconds=40 --capture-speed=32 --autoplay [--select=<id>]` |
