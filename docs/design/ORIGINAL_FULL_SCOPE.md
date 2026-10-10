# Pond Life — Full Scope Design Document

Synthesizes the Era Design Document and Cross-Era Systems doc, extrapolates into the systems needed for a real production scope, and closes with a cut-list for optimizing toward a buildable MVP.

---

## 1. Vision & Pillars

**One-line pitch:** A peaceful-leaning city builder where you evolve a civilization from a single microbe in a rock pool to a spacefaring species, across a connected world of rock pool, pond, lake, river, and sea.

**Design pillars** (every system should serve at least one; cut anything that serves none):
1. **Scale is the spectacle.** The camera/zoom mechanic and the water-body hierarchy exist to keep delivering "this world is bigger than you thought" moments, culminating in the rocket launch.
2. **Consequence without cruelty.** Choices matter (forks, seasons, rivals) but the game never produces a permanently unwinnable state.
3. **Biology as the tech tree.** Every mechanical system should be explainable in evolutionary/biological terms first, mechanical-game-term second.
4. **Peaceful competition.** Rivals exist for comparison and soft pressure, not combat. Tension comes from environment and time, not war.

---

## 2. World & Map Structure (expanded)

**Hybrid map**, as decided: five distinct, fully-built zones (rock pool, pond, lake, river, sea) connected by traversable stream corridors. Confirmed decisions carried forward: soft-push migration (resource ceilings + seasonal pressure, never a hard wall), single-player first with AI rivals from day one, multiplayer as a planned second phase.

**New scope consideration — zone sizing and reuse.** Five fully unique zones is a lot of content. Recommend defining each zone by a **biome kit** (a palette of terrain tiles, resource nodes, hazard types, and ambient creatures) rather than fully bespoke art per zone — lets you reuse a build pipeline five times instead of building five unrelated environments from scratch. The *distinctiveness* between zones should come from resource type, hazard type, and scale (per the era doc's resource table), not from needing five entirely separate art styles.

**Camera/scale mechanic — needs a concrete implementation plan.** Two viable approaches:
- **Discrete zoom tiers** (individual unit view → colony view → territory/empire view), each with different interactable elements and different UI overlays. Cheaper to build, easier to balance, closer to how AoE already handles zoom-dependent detail.
- **Continuous zoom with LOD (level-of-detail) swapping.** More immersive, matches the "wow" framing better, significantly more expensive technically (asset swapping, performance budgeting at every zoom level).
- **Recommendation:** discrete tiers for MVP (3 tiers: Organism / Colony / Territory), with continuous zoom as a post-launch polish target if the discrete version proves the concept works.

---

## 3. Full Era Progression (reference + scope notes)

The ten-era structure (Microbial Genesis → Colonial Awakening → Tidepool Tribal → Settlement Era → Pond Industrial Age → Lake Information Age → River Engineering Age → Oceanic Age → Surface Breach → Spacefaring) stands as designed in the Era Document. Scope-relevant additions:

**Unit/building count discipline.** Ten eras each introducing new units, buildings, and resource types is a large content surface. Recommend a **shared-chassis approach**: define a small number of unit *roles* (Gatherer, Builder, Defender, Scout, Specialist) that persist across all ten eras, re-skinned and re-statted per era, rather than inventing wholly new unit types per era. This is standard practice in AoE-likes (villager → equivalent roles across ages) and keeps art/animation/balancing scope linear rather than exponential.

**Fork count discipline.** The era doc sketched one major + one minor fork per era as *examples*. For a real build, recommend capping at **1 major fork + 1–2 minor forks per era** (matches what's already sketched) — more than that risks overwhelming the trajectory UI and diluting the weight of "major" choices. Total scope: ~10 major forks, ~15–20 minor forks across the whole game.

**Era pacing target.** Worth deciding early (design question, not yet answered): rough target playtime per era for a "normal" playthrough. Suggest prototyping Eras 1–4 first (the rock pool/pond portion) since they're cheapest to build and validate the core loop before committing art/systems budget to lake/river/sea.

---

## 4. Core Gameplay Systems (expanded from Cross-Era doc)

The four systems already designed — Evolutionary Trajectory UI, Rival AI Behavior, Seasonal/Environmental Calendar, Symbiosis — stand as specified. Additional systems a full scope needs that haven't been designed yet:

**Economy & resource sinks.** Every resource-gathering game needs somewhere for resources to *go*, or the economy stagnates once storage caps out. Needs a pass on: build costs, upkeep costs (do buildings/partners require ongoing resource spend, or one-time cost only?), and a "prestige"/optional-sink layer for late-game players who've maxed core progression (cosmetic trait variants, optional mega-structures, etc.).

**Onboarding/tutorial.** A ten-era evolutionary game with fork-based consequence needs careful first-hour design — the player must understand *forks have weight* before the first major fork (Era 1's autotroph/heterotroph choice) or it'll be made blind. Recommend a soft-gated Era 1 that can't be skipped quickly, with the trajectory UI introduced explicitly the first time a major fork is offered.

**Win/loss and pacing framing.** Confirmed: no permanent unwinnable states. Still needs: what does "winning" mean — is launching the first rocket an ending, or does play continue post-launch (multiple launches, expanding further)? Worth deciding since it affects whether Era 10 needs post-completion content.

**Accessibility considerations.** A biology-heavy tech tree and a small-scale visual world (per the "pond looks huge" framing) both raise colorblind-mode and readability questions worth flagging now rather than retrofitting later — icon/shape coding for resource types alongside color, scalable UI for the trajectory tree.

---

## 5. Art & Audio Direction (new — not yet discussed, flagged as a gap)

This hasn't come up yet in our conversation and is a real scope item:

**Visual arc.** The design already implies one: organic/biofilm aesthetics in early eras, increasingly geometric/industrial by Era 10 (explicitly called out in the era doc as a deliberate contrast for the space-age visual payoff). This should be a formal art-direction pillar, not just an emergent implication.

**Scale-communication in art.** Since "the pond is huge" is a core pillar, art direction needs consistent devices for selling scale — water droplet physics/refraction at the surface, light shafts through water at larger zoom tiers, silhouette-only rendering for very large threats (herons, etc.) to keep them threatening without needing full character art budget.

**Audio.** Underwater ambient sound design, muffled/filtered audio as a scale-and-immersion device, and a clear audio "event" language for the seasonal calendar (distinct stings for drought onset, freeze onset, predator incursion) so players get non-visual warning too.

---

## 6. Multiplayer Roadmap (phase 2 — scoping now to avoid painting into a corner)

Not building this now, but single-player systems should be designed to not preclude it later:

- **Territory model already supports this** — separate water-body "zones" per rival colony maps cleanly onto "a zone per player" in multiplayer, without needing a redesign.
- **Trajectory UI's ghosted-rival-silhouette feature** was explicitly designed as a stepping stone toward showing real player data in multiplayer — worth keeping that data structure generalized (colony ID–keyed) from the start rather than single-player-specific.
- **Diplomacy system (Era 6 fork)** — open-trade vs closed stance — was designed against AI, but the same mechanic should function against human players with minimal rework if built generally.
- **Recommendation:** don't design multiplayer-specific systems yet, but do a lightweight architecture review before Alpha to confirm the single-player systems (rival AI, trajectory data, diplomacy) are built in a way that doesn't require a rewrite later.

---

## 7. Technical & Platform Considerations (new — flagged as a gap)

Not yet discussed and needed for real scoping:

- **Target platform(s)** — PC, mobile, or both? This materially affects the camera/zoom mechanic decision (continuous zoom is much harder to make performant on mobile), UI density (trajectory tree needs more screen real estate than a phone comfortably offers), and control scheme (a city-builder with unit micromanagement at "Organism" zoom tier is a very different input problem on touch vs mouse).
- **Engine/tooling** — worth deciding early since the biome-kit content strategy (section 2) and shared-unit-chassis strategy (section 3) both assume a data-driven, reusable-asset pipeline — which points toward an engine with strong support for that (e.g. Godot or Unity) rather than a fully bespoke engine.
- **Save/simulation scope** — a ten-era, multi-zone, always-persistent-rival-AI game needs a save system that can serialize a lot of simulated state (rival colonies continuing to evolve, environmental calendar state, symbiosis partner health). Worth flagging as a technical risk to scope early rather than discover late.

---

## 8. Production Scope & Phasing

**Recommended phase structure, given everything above:**

**MVP (prove the core loop):**
- Eras 1–4 only (rock pool through pond settlement).
- Single water body plus one stream crossing (rock pool → pond), not the full five-zone hierarchy.
- One rival colony, using the personality-axis system but without the full diplomatic/trade depth (Era 6+ systems).
- Seasonal calendar Layer 1 only (predictable cycle); skip Layer 2 (unpredictable events) initially.
- Symbiosis: 2–3 partner types, slot system working, but skip the tradeable/diplomatic symbiosis extension (that's an Era 6 feature anyway).
- Trajectory UI: build it early even in MVP — it's core to validating whether the fork-consequence system is fun, which is a central bet of the whole game.
- 3-tier discrete zoom, not continuous.

**Alpha (validate full progression):**
- All ten eras, all five zones, full fork set.
- Full seasonal calendar (both layers).
- Full symbiosis depth across eras.
- Multiple rival colonies.

**Beta (polish and balance):**
- Art/audio direction fully realized (organic → geometric visual arc, full audio event language).
- Accessibility pass.
- Onboarding/tutorial built and tested.
- Economy balancing pass (resource sinks, upkeep tuning).

**1.0 and beyond:**
- Multiplayer architecture review and buildout.
- Post-launch content: additional forks, additional partner species, possibly additional water bodies beyond the sea (estuary? open ocean? — worth brainstorming later, not now).

---

## 9. Risk Register (new — worth tracking explicitly)

| Risk | Why it matters | Mitigation already implied by design |
|---|---|---|
| Content scope explosion (10 eras × 5 zones × unique units/art) | Biggest single risk to shipping at all | Biome-kit + shared-unit-chassis strategy (sections 2–3) |
| Fork system feels arbitrary instead of meaningful | Central to the game's identity — if this doesn't land, little else matters | MVP explicitly prioritizes proving this early with the trajectory UI |
| Rival AI feels either too passive (boring) or too punishing (breaks "peaceful" framing) | Core tension source | Personality-axis + decision-quality-not-resource-cheat scaling (Cross-Era doc) |
| Camera/scale mechanic underdelivers on the "wow" pillar | This is the game's central hook per the original pitch | Discrete tiers first to prove the concept cheaply before investing in continuous zoom |
| Platform decision made too late, forces rework | Affects UI density, zoom implementation, controls | Flagged now (section 7) as a needed early decision |

---

## 10. Open Design Questions (consolidated from this doc and prior discussion)

- Target platform(s)?
- Engine choice?
- Win/loss framing — does the game end at first launch, or continue?
- Rough target playtime per era?
- Do buildings/partners have ongoing upkeep cost, or one-time build cost only?
- Post-sea water bodies (estuary, open ocean) — in scope eventually, or is the sea the deliberate final water body?

---

## Suggested Next Step

Given the MVP phasing above, the next concrete design task would be **fully specifying Eras 1–4** at implementation detail (exact resource numbers, exact building list, exact fork options and their numeric effects) — everything before this point has been structural/conceptual, and MVP scoping needs one vertical slice specified in enough detail to actually prototype.
