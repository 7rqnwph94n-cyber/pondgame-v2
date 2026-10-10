# Pond Life — Locked Decisions on Open Questions

Answers to the six open questions from the Full Scope doc, decided in favour of whatever best serves the design pillars (scale-as-spectacle, consequence without cruelty, biology-as-tech-tree, peaceful competition) rather than what's fastest to build.

---

## 1. Target Platform: PC first, mobile as a deliberate later port — not simultaneous.

**Reasoning:** The camera/scale mechanic is the game's central hook, and continuous zoom (or even a well-realized 3-tier discrete zoom with real depth) needs screen real estate and precision input that mobile fights against. The trajectory UI also genuinely needs room to breathe — a branching organic tree with ghosted rival comparison is going to be cramped on a phone.

Building PC-first doesn't waste the mobile option — a data-driven, biome-kit/shared-unit-chassis pipeline (already recommended in the Full Scope doc) is exactly what makes a later mobile port tractable, because you're not re-authoring content, just re-laying-out UI and re-tuning controls. Trying to satisfy both from day one would mean designing every screen for the more constrained platform and wasting the PC version's potential.

## 2. Engine: Godot.

**Reasoning:** Between Godot and Unity, Godot fits better given: it's free of licensing complications for a solo/small-team indie project, has a strong 2D pipeline suited to the biome-kit content strategy, and — worth noting for your context — you've already got hands-on experience building in Godot 4 on other projects, which matters more for actually shipping this than any marginal technical feature difference. Consistency with your existing toolchain reduces the biggest real risk (a scope this large not getting finished), more than a "better" but unfamiliar engine would.

## 3. Win/Loss Framing: The first launch is a milestone, not an ending — play continues.

**Reasoning:** This is the choice that best serves the "scale is the spectacle" pillar. If the game ends at first launch, the entire back half of Era 10 (and the payoff of everything built before it) is a five-minute credits-roll moment. If play continues post-launch, the rocket launch becomes a *gateway* — you've now got a second recontextualization available (what's beyond the garden?) without needing to have designed it all yet. Post-launch content can be soft-scoped now and fleshed out later (see decision 6) without committing to it structurally.

This also meshes with "consequence without cruelty" — there's no hard finish line to rush toward, which supports players who want to keep optimizing one civilization rather than "beating" the game and stopping.

**Concrete recommendation:** first launch triggers a real narrative/visual beat (the recontextualization moment) and unlocks a soft "post-launch" mode — expanded resource ceilings, optional repeatable objectives (additional launches, expanded infrastructure) — rather than a hard-scoped new content tier. Keeps it cheap to build now, extensible later.

## 4. Target Playtime Per Era: Roughly 45–90 minutes per era for a "normal" pace, with earlier eras shorter and later eras longer.

**Reasoning:** Front-loading shorter eras serves onboarding — Era 1's autotroph/heterotroph fork needs to land before the player's attention does, so it shouldn't take two hours to reach. Back-loading longer eras (River Engineering, Oceanic, Surface Breach, Spacefaring) fits because those eras have the most systems layered on by that point (full symbiosis depth, full seasonal calendar, accumulated fork consequences) and deserve more room to be felt. A rough curve:

- Eras 1–3 (Microbial → Tidepool Tribal): ~30–45 min each — fast, establishes the core loop and the first major fork quickly.
- Eras 4–6 (Settlement → Lake Info Age): ~45–75 min each — this is where symbiosis, trade, and diplomacy add real depth.
- Eras 7–10 (River → Spacefaring): ~75–120 min each — infrastructure and endgame systems, plus this is where accumulated fork payoffs should be visibly resolving, which deserves unhurried pacing.

Total: roughly 8–14 hours for a full first playthrough to first launch, which is a healthy length for this genre (comparable to a focused AoE campaign or a Civ session) without ballooning into an overwhelming time investment that discourages the multiple playthroughs your fork-diversity system is designed to reward.

## 5. Upkeep: Buildings have light ongoing upkeep; symbiosis partners have upkeep; base population/units do not (beyond normal consumption).

**Reasoning:** This is the choice that most reinforces "biology as the tech tree." A living colony has metabolic cost — buildings and infrastructure (which are "artificial," industrial-era-onward constructs) should cost something to maintain, same as a real city's infrastructure budget. Symbiotic partners explicitly having upkeep was already implied by the "stressed if unmet needs" mechanic designed in the Cross-Era doc — making this consistent (upkeep = the resource cost of meeting those needs) ties two previously-separate systems together into one coherent economic logic instead of two different rules players have to learn.

Units/population deliberately do **not** have a separate upkeep on top of normal resource consumption, because that would risk turning population growth (the core "AoE villager count" analogue of this game) into a tax rather than a reward — you want more population to always feel unambiguously good, not something to be managed against a growing upkeep bill.

This directly answers the Full Scope doc's economy-sink question too: upkeep on buildings and partners is your primary resource sink, rather than needing to invent a separate late-game-only sink system.

## 6. Post-Sea Water Bodies: The sea is the deliberate final water body for the core game — no estuary/open-ocean expansion planned, but the post-launch "beyond the garden" space (from decision 3) is where any future expansion content should live instead.

**Reasoning:** Adding more water bodies before space would dilute the hierarchy's escalating "wow" structure (rock pool → pond → lake → river → sea → surface → space) rather than enhance it — five zones plus streams is already a lot of content per the Full Scope doc's content-scope risk. The sea should stay the last *water* body so its scale payoff lands cleanly against the surface-breach and space eras that follow it.

However, keeping win/loss open-ended (decision 3) gives you a clean, already-justified place to put *future* expansion content later — "beyond the garden" (other parts of the wider world, reached via further space tech) rather than retrofitting a sixth water body into the middle of an already-tight progression. This is a better long-term content-expansion path than adding zones, because it extends the existing scale-escalation logic outward instead of interrupting it.

---

## Net effect on the Full Scope doc

These decisions don't change the MVP recommendation (Eras 1–4, one stream crossing, one rival) — if anything they sharpen it: build in Godot from the start, design the trajectory UI and build-upkeep economy together from MVP since they're now confirmed to be linked systems, and treat the MVP as a genuine PC-first prototype rather than a platform-agnostic one.
