# Repair Enzyme upkeep diagnosis — 5 October 2026

Reproduce: `python3 tools/diagnose_slice_upkeep.py`. Raw snapshots, digester states, legal commands, commissioning times and kiln governor decisions are in the matching JSON file. The tool asserts that its reference summary exactly matches every common metric in the existing 240-minute extended-horizon result and that first unpaid upkeep is second 8189 (136:29).

## Primary cause: insufficient installed capacity

The existing Waste Digester is commissioned at 69:19 and runs for 10,241 seconds through 240:00, with only its initial one-second staffing transition recorded as `no_workforce`. It is fully staffed, has ample Organic Waste, and is not paused. Its recipe makes one Repair Enzyme every 240 seconds: **0.25 per minute**.

Maintenance grace ends at 106:30, one step after first Symbiotic. Maintenance weight is 40, requiring **0.50 Enzyme/minute**. Seven stored Enzyme units delay failure, but production supplies only half the ongoing requirement. At first failure, 136:29, Organic Waste stock is 67 and the digester remains running at full staffing. By 240:00 maintenance weight is 46.5 and demand is 0.58125/minute; Waste stock has risen to 159.

This is a capacity shortfall in this governor trajectory, not a digester labour/input stall. No other current production recipe consumes Enzyme at the final checkpoint. Earlier construction/evolution can draw from reserves, but cannot explain the continuing production-versus-upkeep deficit.

## Legal player-action comparison

All four runs use the unchanged provisional overlay and reference governor through 240 minutes. The interventions occur at 120:00 using `Simulation.issue(source='player')`; construction pays normal costs, uses normal labour and adds normal upkeep weight. No resources are injected and no rates/costs are altered.

| Action at 120:00 | First unpaid | Unpaid minutes by 240 | Additional digesters commissioned | Enzyme stock at 240 |
|---|---|---:|---|---:|
| None (reference) | 136:29 | 54.7 | — | 0 |
| Staff existing digester first (priority 3) | 136:29 | 54.7 | — | 0 |
| Order one extra digester | 136:29 | 36.0 | 191:47 | 0 |
| Order two extra digesters | 136:29 | 30.0 | 191:47, 198:43 | 7 |

Every command was accepted. All runs retain first Stable 21:39 and Symbiotic 106:29, zero Staple shortage, zero food emergencies and zero devolutions; Gel shortage remains 3.0 residence-minutes. None reaches Memory or a Reef stage. Two extra digesters recover maintenance late (last restoration 199:48) but do not prevent the earlier outage. Ordering extra capacity changes construction competition and the later trajectory, so these are bounded comparisons rather than an isolated rate experiment.

## Why extra capacity arrives late

At 120:00 and at the first failure, Fired Ceramic and Biomass stores are empty. The Ceramic Kiln uses `ceramic_kiln_biofuel`: two Prepared Silica plus three Biomass per cycle, producing two Fired Ceramic. Prepared Silica is available (14 at 120:00, 22 at first failure); Biomass is the missing ingredient. The governor pauses the kiln after a 60-second input stall to release its crew, resuming only when inputs are available. Its logged resumes around 185:30 and 197:10 precede commissioning the extra digesters. Normal construction also competes for that scarce Ceramic.

Thus there are two linked constraints: too little Enzyme capacity, and Biomass/Ceramic supply delaying construction of more capacity. Staffing the existing digester is not a remedy. Reducing upkeep or gifting Enzyme would conceal the unresolved construction chain.

## Recommended next bounded test

Before changing baseline balance, test an explicit governor strategy that plans sufficient Enzyme capacity before Symbiotic and reserves the Biomass/Ceramic needed to build it. Compare an earlier extra-digester order plus temporary consumer management with the current control, preserving food solvency and normal costs. Only propose a narrow rule change if legal scheduling cannot achieve this without breaking the opening.

This report is evidence from deterministic simulated trajectories, not a fresh human playtest or proof that all player strategies fail. Gameplay rules, launch defaults and bridge contracts remain unchanged.
