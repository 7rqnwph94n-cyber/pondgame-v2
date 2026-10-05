# Opening HUD clarity — v0.1

Claude's manual opening found a consequential information gap: evolving the first home silently transfers six General workers to Adapted, leaving the Culture Bed short-staffed. The same playtest showed that the resource strip omitted Carbonate and Biomass, population growth could be blocked without any counter cue, and an “idle” facility could still occupy workers.

This presentation pass uses the additive `sim_bridge` v2 fields without changing game rules:

- Carbonate and Biomass now have compact stock chips and source SVG icons in the top strip.
- The population counter gains a visible attention mark when `colony_blockers` is non-empty. Its hover text gives the bridge's principal growth reason.
- The home inspector names the next tier and shows the class change before Evolve; the Evolve action repeats it on hover.
- An idle facility with staffing now says that workers remain assigned. The simulation's status ID is unchanged.

[Normal-renderer capture with the home inspector open](../milestone_b/captures/verdant_playable_v23_hud_clarity.png)

At 1600×900 the resource strip fits on one row and the inspector's workforce consequence is visible without hover. The population reason and Evolve action detail still rely on hover; a later usability pass should test whether a novice notices them. `output_blocked` remains reserved until storage capacity exists, and unknown structured-blocker icon handling remains a follow-up rather than a claim of this pass.
