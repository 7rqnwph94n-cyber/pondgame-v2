# Verdant Basin vertical-slice economy

## Paper balance specification — v0.1

**Date:** 2 October 2026  
**Parent design:** `PONDLIFE_CHEMICAL_CIVILISATION_GDD.md`  
**Scenario length:** 60–90 minutes on a first successful playthrough  
**Simulation speed:** 1× real time, with pause, 2× and 4× controls  
**Purpose:** Provide exact starting values for a playable economy prototype. These are tuning hypotheses, not final balance.

---

## 1. What this economy must prove

The slice succeeds if a new player can:

1. read the basin's chemical geography;
2. establish a food surplus before the first seasonal transition;
3. discover that fertility depends on phosphate rather than biomass alone;
4. separate residential, farming and dirty industrial districts;
5. diagnose and repair a logistics bottleneck;
6. evolve residences by supplying goods and services;
7. create at least two specialist castes through morphology;
8. trade with a chemically complementary neighbour;
9. choose between local extraction, imports and substitute production;
10. convert a functioning city economy into the Memory Reef great work.

The economy should feel generous at subsistence level and demanding at the level of refinement. Basic survival must recover quickly; advanced prosperity must require planning.

---

## 2. Units and simulation conventions

### 2.1 Time

- One **game minute** equals one real minute at 1× speed.
- Recipe cycle times are expressed in seconds.
- Rates in the UI are normalised to units per game minute.
- Buildings check for inputs at the beginning of a cycle and place outputs at the end.
- Interrupted cycles retain progress unless the building is demolished or physically disconnected.

### 2.2 Goods

- One **unit** is one standard cargo bundle.
- One carrier can normally move **2 units** per trip.
- Goods remain discrete internally; the UI may display one decimal place for average rates.
- A recipe never consumes fractional cargo bundles in storage. Fractions shown in rate tables are averages across full batches.

### 2.3 Population and workforce

- Population is counted as individual organisms.
- Workforce is counted in **workforce points** (WP), representing organisms available for sustained work.
- Approximately 75% of a residence's population becomes workforce; the rest represents juveniles, caretakers and non-working dependants.
- Workforce is assigned automatically within a connected district.
- Each residence tier supplies one workforce class. Upgrading a residence converts its workforce class, so the player must retain a mixture of housing tiers.
- Unfilled jobs reduce building productivity proportionally rather than shutting the building off until staffing falls below 25%.

### 2.4 Energy

The slice does not use a global electricity-like resource. Metabolic energy is embodied in food goods and workforce. Heat-demanding buildings consume **anoxic organics** directly as fuel until later energy infrastructure exists.

### 2.5 Distance

One map tile is the standard spatial unit.

- Local district: up to 24 tiles from a logistics node.
- Comfortable walking/hauling distance: up to 18 tiles.
- Long local route: 19–36 tiles.
- Remote route: over 36 tiles; normally requires a Flow Channel or satellite store.

---

## 3. Scenario map and initial state

### 3.1 Starting colony

The player begins with:

| Asset | Quantity | Contents/state |
|---|---:|---|
| First Nursery | 1 | Active; provides Broodcare and caste conversion |
| Shelter Cluster | 3 | 24/24 population; 18 General WP total |
| General Store | 1 | 40-unit capacity; 2 local carriers |
| Maintenance Organ | 1 | Covers all starting buildings |
| Survey Organ | 1 | Reveals broad chemistry within 22 tiles |
| Photosynthetic Field | 1 | On a 75-fertility patch |
| Culture Bed | 1 | Producing Staple Culture |
| Staple Culture | 8 | About 13 minutes of opening food reserve |
| Photosynthetic Biomass | 4 | Four Culture Bed cycles |
| Carbonate | 6 | Early construction reserve |
| Prepared Silica | 2 | Early specialist-building reserve |
| Stored value | 20 | Barter credit used only after trade opens |

Starting workforce use:

| Employer | General WP |
|---|---:|
| Photosynthetic Field | 3 |
| Culture Bed | 3 |
| General Store/carriers | 2 |
| Maintenance Organ | 2 |
| Survey Organ | 1 |
| First Nursery | 1 |
| Unassigned/building reserve | 6 |

The player therefore has room to open one or two industries immediately without first building more housing.

### 3.2 Resource geography

| Patch | Distance from start | Grade | Reserve/renewal | Strategic purpose |
|---|---:|---:|---|---|
| Sunlit shelf | 5–16 tiles | 55–90 fertility | Renewable | Opening biomass and later fibre/resin crops |
| Phosphate sediment | 20 tiles | 0.8 | 150 reserve; +30 at High Water | First limiting nutrient |
| Suspended-nutrient channel | 14 tiles | 0.7 | Renewable; seasonal | Alternative nutrient source and Filter Crown proof |
| Silicate outcrop | 28 tiles | 0.75 | 130 reserve | Ceramic and composite economy |
| Carbonate reef | 34 tiles | 0.65 | 110 reserve | Bulk project material; rival also claims it |
| Anoxic basin | 24 tiles | 0.9 | 80 reserve; slow seep renewal | Fuel and Repair Enzyme input; hazardous |
| Pigment shallows | 18 tiles | 0.6 | Renewable when cultivated | Luxury and export good |
| Clean-flow spring | 12 tiles | N/A | Renewable service field | Advanced residence anchor |

The neighbouring colony begins closer to the carbonate reef. The player can obtain carbonate locally, trade for it, or reduce use through a costly ceramic substitution.

---

## 4. Seasonal calendar

The full calendar is visible from the beginning. Forecast accuracy is exact in the slice so players learn planning before uncertainty is introduced.

| Phase | Time | Farm output | Filter output | Sediment access | Anoxic risk | Logistics |
|---|---:|---:|---:|---:|---:|---|
| Bloom | 0–18 min | ×1.25 | ×0.80 | ×0.75 | Low | Normal |
| High Water | 18–35 min | ×1.00 | ×1.50 | Closed | Medium | Low ground slowed 15% |
| Recession | 35–58 min | ×1.10 | ×1.00 | ×1.35 | Medium | Normal |
| Dry Phase | 58–90 min | ×0.65 | ×0.55 | ×1.10 | High | Flow Channels −20% |

At the start of High Water, phosphate beds receive **30 units** of new reserve. This is visible as sediment deposition but cannot be dredged until Recession.

At the start of the Dry Phase:

- residences hold a three-minute internal need buffer;
- exposed farms lose productivity gradually over two minutes rather than instantly;
- the player receives warnings at 8, 4 and 1 minute before transition;
- clean-flow service radius contracts by 20%;
- the anoxic basin's unadapted-worker penalty increases from 25% to 60%.

---

## 5. Fertility and farming

### 5.1 Output formula

```text
Actual output rate = base rate
                   × fertility factor
                   × seasonal factor
                   × staffing factor
                   × logistics/output-block factor
                   × health factor
```

Fertility factor is `displayed fertility / 100`, clamped from 0.25 to 1.25.

### 5.2 Crop-specific fertility

| Crop | Bulk need | Limiting factor | Best terrain | Pollution sensitivity |
|---|---|---|---|---:|
| Photosynthetic Biomass | light, CO₂, clean water | phosphate | sunlit shelf | Medium |
| Fibre Fronds | light, flow | fixed nitrogen | shelf edge/channel | Low |
| Resin Colony | biomass feed, warmth | trace mineral | sheltered shelf | High |
| Pigment Culture | light variation, mineral salts | clean flow | shallow margin | Very high |

The chemistry lens shows fertility separately for the selected crop.

### 5.3 Farm buildings

| Building | Output | Base cycle | Batch | Base rate | General WP | Field modules |
|---|---|---:|---:|---:|---:|---:|
| Photosynthetic Field | Photosynthetic Biomass | 60 s | 1 | 1.00/min | 3 | 8–16 |
| Fibre Garden | Raw Fibre | 100 s | 1 | 0.60/min | 3 | 6–12 |
| Resin Grove | Raw Resin | 150 s | 1 | 0.40/min | 3 | 6–10 |
| Pigment Bed | Raw Pigment | 240 s | 1 | 0.25/min | 2 | 4–8 |

Base rate assumes 100 fertility before seasonal modifiers. A starting Photosynthetic Field at 75 fertility during Bloom produces `1.00 × 0.75 × 1.25 = 0.94` Biomass per minute.

### 5.4 Fertilisation

- One Growth Nutrient applied to a farm adds **+20 crop-specific fertility** for 8 minutes.
- Fertility cannot exceed 125.
- Farms request fertiliser automatically only when the player enables a target-fertility policy.
- Fertilising staple crops competes directly with residence evolution and reproduction for Growth Nutrient.

---

## 6. Raw-resource extraction

| Building | Input condition | Output | Cycle | Batch | Base rate | Workforce | Renewal |
|---|---|---|---:|---:|---:|---|---|
| Sediment Dredge | Accessible phosphate bed | Phosphate Sediment | 120 s | 1 | 0.50/min | 3 General | Seasonal deposit |
| Filter Crown | Flow ≥ 0.5 | Suspended Nutrient | 100 s | 1 | 0.60/min | 3 Adapted | Renewable |
| Silicate Pit | Silicate outcrop | Raw Silicate | 120 s | 1 | 0.50/min | 4 Adapted | Finite |
| Carbonate Cutter | Carbonate reef | Carbonate | 100 s | 1 | 0.60/min | 4 Adapted | Finite |
| Anoxic Pump | Anoxic basin | Anoxic Organics | 170 s | 1 | 0.35/min | 3 Adapted | 0.08/min seep |

### 6.1 Extraction adaptation penalties

- Sediment Dredge without Burrowing Limb: −40% output and +1 General WP.
- Filter Crown cannot operate without Filter Crown morphology in its workforce district.
- Silicate Pit without Mineral Jaw: −50% output and 10% worker injury/stress chance per cycle.
- Carbonate Cutter cannot operate without Mineral Jaw.
- Anoxic Pump without Detox Sac: −25% output before Dry Phase, −60% during Dry Phase, plus health-service demand.

These penalties make morphologies economically legible without hard-locking every early experiment.

---

## 7. Production recipes

Rates assume full staffing, immediate input access and unblocked output.

### 7.1 Food and fertility

| Building/recipe | Inputs | Outputs | Cycle | Rate | Workforce |
|---|---|---|---:|---:|---|
| Culture Bed | 1 Biomass | 1 Staple Culture | 60 s | 1.00 Staple/min | 3 General |
| Nutrient Washer | 1 Phosphate Sediment | 1 Growth Nutrient + 1 Sludge every second cycle | 120 s | 0.50 Nutrient/min | 3 Adapted |
| Channel Separator | 1 Suspended Nutrient | 1 Growth Nutrient | 150 s | 0.40 Nutrient/min | 2 Adapted |
| Nutrient Kitchen | 2 Staple + 1 Growth Nutrient | 4 Balanced Nutrient Gel | 180 s | 1.33 Gel/min | 4 Artisan |

The Channel Separator provides a renewable alternative to finite/seasonal phosphate, but its output falls in the Dry Phase.

### 7.2 Mineral and construction

| Building/recipe | Inputs | Outputs | Cycle | Rate | Workforce |
|---|---|---|---:|---:|---|
| Mineral Washery | 1 Raw Silicate | 1 Prepared Silica + 1 Sludge every second cycle | 120 s | 0.50 Silica/min | 3 Adapted |
| Ceramic Kiln | 2 Prepared Silica + 1 Anoxic Organics | 2 Fired Ceramic | 240 s | 0.50 Ceramic/min | 4 Artisan |
| Retting Pool | 1 Raw Fibre | 1 Woven Fibre | 100 s | 0.60 Fibre/min | 3 Adapted |
| Resin Curing Organ | 1 Raw Resin | 1 Cured Resin | 150 s | 0.40 Resin/min | 3 Adapted |
| Composite Workshop | 2 Woven Fibre + 2 Cured Resin + 1 Prepared Silica | 4 Habitat Composite | 480 s | 0.50 Composite/min | 5 Artisan |

Composite Workshop batches are intentionally large and slow. A missing ingredient is highly visible, while a completed batch materially advances construction.

### 7.3 Health, maintenance and luxury

| Building/recipe | Inputs | Outputs | Cycle | Rate | Workforce |
|---|---|---|---:|---:|---|
| Waste Digester | 2 Organic Waste | 1 Repair Enzyme + 1 Recovered Fertiliser | 240 s | 0.25 each/min | 3 Adapted |
| Emergency Enzyme Culture | 2 Staple + 1 Anoxic Organics | 1 Repair Enzyme | 180 s | 0.33/min | 3 Adapted |
| Artisan Organ | 1 Raw Pigment + 1 Cured Resin | 1 Pigment Ornament | 240 s | 0.25/min | 4 Artisan |

Recovered Fertiliser substitutes one-for-one for Growth Nutrient when applied to a farm but cannot be used for residence evolution or morphology.

### 7.4 Substitute recipes

| Problem | Substitute | Cost |
|---|---|---|
| Carbonate shortage | 2 Fired Ceramic → 1 Project Masonry | doubles mineral-processing demand |
| Resin shortage | 2 Repair Enzyme + 1 Woven Fibre → 1 Cured Sealant | competes with maintenance and produces only one substitute Resin |
| Phosphate inaccessible | 1 Suspended Nutrient → Channel Separator | seasonally weak in Dry Phase |
| Anoxic Organics unavailable | 3 Biomass → 1 Kiln Fuel Culture | consumes food feedstock and adds 60 s to kiln cycle |

Substitutes protect solvability but are deliberately less efficient than territorial access or trade.

---

## 8. Waste and by-products

### 8.1 Waste generation

| Source | Waste output |
|---|---:|
| Shelter Cluster | 0.05 Organic Waste/min |
| Stable Habitat | 0.08 Organic Waste/min |
| Symbiotic Neighbourhood | 0.12 Organic Waste/min |
| Memory Enclave | 0.15 Organic Waste/min |
| Culture Bed | 1 Organic Waste every 5 cycles |
| Nutrient Kitchen | 1 Organic Waste every 2 cycles |
| Nutrient/Mineral Washer | Sludge as specified in recipe |
| Ceramic Kiln | 1 Heat/Turbidity pressure per cycle; not a stored good |

### 8.2 Waste handling

- Residences hold 3 units of local waste before losing Habitat Quality.
- Waste service moves Organic Waste to a Waste Digester or dump basin.
- Untreated Organic Waste decays after 10 minutes, adding contamination in a 6-tile radius.
- Sludge can be stored indefinitely but lowers desirability within 5 tiles.
- Five Sludge can be consumed by a Landform Project to improve 4 sediment tiles by +10 fertility.

### 8.3 Circular-economy payoff

A city of two Stable Habitats and two advanced residences generates approximately 0.4–0.5 Organic Waste per minute. Together with workshop waste, this supports one Waste Digester intermittently, producing enough Repair Enzyme for routine maintenance but not instantly funding the Memory Reef. The player may supplement it with Emergency Enzyme Culture.

---

## 9. Residence economy

### 9.1 Residence stages

| Stage | Capacity | Workforce supplied | Required recurring goods | Services | One-time evolution goods |
|---|---:|---|---|---|---|
| Shelter Cluster | 8 pop | 6 General WP | 0.20 Staple/min | Maintenance | — |
| Stable Habitat | 12 pop | 8 Adapted WP | 0.24 Staple/min | Maintenance, Waste, Clean Flow | 2 Growth Nutrient |
| Symbiotic Neighbourhood | 16 pop | 10 Artisan WP | 0.12 Staple + 0.18 Gel/min | Maintenance, Waste, Clean Flow, Health, Distribution | 2 Growth Nutrient, 2 Woven Fibre, 1 Repair Enzyme |
| Memory Enclave | 20 pop | 12 Coordinator WP | 0.10 Staple + 0.22 Gel + 0.05 Ornament/min | All prior services, Memory | 3 Habitat Composite, 2 Ornament, 2 Repair Enzyme |

### 9.2 Evolution sustain times

| Transition | Conditions must hold for |
|---|---:|
| Shelter → Stable | 90 seconds |
| Stable → Symbiotic | 150 seconds |
| Symbiotic → Memory | 240 seconds |

Evolution consumes the one-time goods only when the sustain timer completes. Goods are reserved during the timer and released if conditions fail.

### 9.3 Habitat Quality thresholds

| Stage sought | Minimum quality |
|---|---:|
| Stable Habitat | 45 |
| Symbiotic Neighbourhood | 65 |
| Memory Enclave | 82 |

Quality contributions:

| Condition | Quality |
|---|---:|
| Clean Flow | +15 |
| Maintenance | +10 |
| Waste service | +10 |
| Health/Detox service | +10 |
| Distribution | +10 |
| Memory service | +12 |
| Cultivated garden within 8 tiles | +8 |
| Another maintained residence within 6 tiles | +4, max +8 |
| Pigment ornament district supply | +8 |
| Processor within 7 tiles | −8 each, max −24 |
| Kiln, pump or pit within 10 tiles | −12 each, max −24 |
| Local contamination | −5 to −30 |
| Uncollected waste | −12 |
| Building in disrepair nearby | −8 each, max −16 |

### 9.4 Need buffers and decline

- Residences store 3 minutes of each recurring good internally.
- When a need empties, the residence becomes **Strained** for 3 minutes.
- Strained residences keep population and workforce but lose their tier bonus.
- Continued shortage causes **Dormancy** for 4 minutes, reducing supplied workforce by 50%.
- Continued shortage then devolves one stage; excess population emigrates gradually over 3 minutes.
- Resupply clears Strain after 60 seconds and Dormancy after 120 seconds.

### 9.5 Population growth

- Empty residence capacity fills through migration at 0.5 population/min when basic needs are supplied.
- The First Nursery adds 0.5 population/min across the settlement.
- Each new organism consumes 0.25 Growth Nutrient at the moment of spawning, accumulated internally so only whole cargo units move.
- Population growth pauses before it consumes the last 4 units of settlement Growth Nutrient unless the player disables the reserve policy.

---

## 10. Workforce and employment

### 10.1 Workforce classes

| Class | Supplied by | Typical work |
|---|---|---|
| General | Shelter Cluster | basic farming, carrying, construction, simple culture |
| Adapted | Stable Habitat | extraction, filtering, washing, curing, health |
| Artisan | Symbiotic Neighbourhood | multi-input production, kiln, advanced goods |
| Coordinator | Memory Enclave | administration, trade, research, Great Works |

Higher classes can fill lower-class jobs at these efficiencies:

| Worker used below class | Effective WP |
|---|---:|
| One tier below | 0.85 |
| Two tiers below | 0.65 |
| Three tiers below | 0.50 |

Lower classes cannot fill higher-class jobs.

### 10.2 Construction labour

- Unassigned General or Adapted WP becomes construction labour automatically.
- One WP contributes one construction-work unit per minute.
- A normal building requires 8–30 construction-work units.
- Great Works require Coordinator work in addition to physical construction.
- Construction priority can be set per site.

### 10.3 Unemployment and vacancies

- Up to 20% unemployment has no penalty and acts as a construction/logistics buffer.
- Above 35% sustained unemployment, residences lose 5 Habitat Quality from lack of purpose.
- Vacant buildings show missing workforce by class and identify reachable residences.

### 10.4 Recommended city mix at minute 55

| Residence | Count | Workforce |
|---|---:|---:|
| Shelter Cluster | 4 | 24 General WP |
| Stable Habitat | 4 | 32 Adapted WP |
| Symbiotic Neighbourhood | 3 | 30 Artisan WP |
| Memory Enclave | 1 | 12 Coordinator WP |

This supports a population capacity of 120 and 98 WP. A typical actual population of 90–105 fills roughly 75–88 WP proportionally.

The player does not need this exact mix; it is the balance reference used to price industry.

---

## 11. Morphology economy

Morphologies apply to a workforce caste, not instantly to the entire population.

### 11.1 Discovery, investment and conversion

| Morphology | Reveal condition | Research/institution cost | Conversion cost per residence | Result |
|---|---|---|---|---|
| Burrowing Limb | Dredge 6 Sediment or attempt Silicate Pit | 4 Growth Nutrient, 2 Silica, 40 Nursery-work | 1 Growth Nutrient per Stable Habitat | Dredging penalty removed; tunnels later |
| Filter Crown | Survey nutrient channel and filter 4 units manually | 3 Growth Nutrient, 2 Fibre, 40 Nursery-work | 1 Growth Nutrient per Stable Habitat | Filter Crown extraction enabled |
| Mineral Jaw | Extract 4 Raw Silicate | 4 Growth Nutrient, 3 Silica, 1 Repair Enzyme, 60 Nursery-work | 1 Nutrient + 1 Silica per Stable Habitat | Full-rate pits; Carbonate Cutter enabled |
| Detox Sac | Work 5 minutes in anoxic influence | 3 Growth Nutrient, 2 Repair Enzyme, 60 Nursery-work | 1 Nutrient + 1 Enzyme per Stable Habitat | Removes anoxic labour penalty |
| Vascular Carrier | Complete 40 deliveries | 4 Growth Nutrient, 2 Fibre, 2 Resin, 80 Nursery-work | 1 Nutrient + 1 Fibre per Shelter/Stable Habitat | Carrier capacity 3; Flow Channel enabled |
| Memory Ganglion | Maintain 2 Symbiotic homes for 5 minutes | 6 Growth Nutrient, 2 Gel, 2 Ornament, 100 Nursery-work | 2 Nutrient + 1 Gel per Symbiotic home | Memory Enclave and Coordinator class enabled |

One Nursery-work unit is produced by one assigned Nursery WP per minute. The First Nursery supports up to 4 WP assigned to adaptation work after its normal staffing is filled.

### 11.2 Active caste limit

- A Stable Habitat can express one extraction morphology plus Vascular Carrier.
- A Symbiotic Neighbourhood can express one artisan specialisation plus inherited carrier/tolerance traits.
- Converting a residence pauses its workforce contribution for 90 seconds.
- Reversing a caste is allowed at half the material cost and the same time.

### 11.3 Expected first-playthrough choices

The player should comfortably afford three of the first five morphologies before the Memory Ganglion commitment. They may:

- specialise in local Silicate and Carbonate with Burrowing Limb + Mineral Jaw;
- pursue Filter Crown for renewable nutrient security;
- choose Detox Sac for fuel and enzyme independence;
- favour Vascular Carrier to support a more spread-out city;
- use trade to bypass one unchosen adaptation.

---

## 12. Logistics model

### 12.1 Carrier performance

Default carrier:

- capacity: 2 units;
- movement speed: 4 tiles/second;
- loading/unloading: 3 seconds at each end;
- decision delay: no more than 1 second;
- one carrier requires 1 General WP;
- returns with a backhaul when a valid task exists.

Vascular Carrier:

- capacity: 3 units;
- movement speed: 4.5 tiles/second;
- loading/unloading: 2 seconds;
- same workforce cost.

### 12.2 Practical throughput

| One-way route | Default carrier throughput | Vascular carrier throughput |
|---|---:|---:|
| 8 tiles | ~6.0 units/min | ~9.5 units/min |
| 18 tiles | ~3.7 units/min | ~6.1 units/min |
| 30 tiles | ~2.5 units/min | ~4.2 units/min |
| 45 tiles | ~1.8 units/min | ~3.0 units/min |

These rates include return travel and handling but not congestion.

### 12.3 Logistics buildings

| Building | Capacity | Included carriers | Range/function | Workforce |
|---|---:|---:|---|---:|
| General Store | 40 | 2 | All stable bulk goods | 2 General |
| Living-Goods Store | 24 | 2 | Food, cultures, enzymes; halves decay | 2 General |
| Hazard Store | 20 | 1 | Organics, volatile reactants, contaminated goods | 1 Adapted |
| Distribution Node | 12 local buffer | 1 | Serves residence needs within 14 tiles | 1 General |
| Transfer Node | 30 | 2 | Route-to-route handoff | 2 General |
| Trade Landing | 40 trade-only | 2 route crews | Imports/exports | 3 Coordinator |

### 12.4 Flow Channel

- Cost: 1 Prepared Silica + 1 Woven Fibre per 6-tile segment.
- Construction: 4 work units per segment.
- Goods moving between attached logistics nodes gain +50% speed.
- During Dry Phase the bonus falls to +20% unless supplied with one Repair Enzyme per 12 segments every 10 minutes.
- Flow Channels add +5 Habitat Quality as a Clean Flow source when fed by the spring, but lose the bonus if contaminated upstream.

### 12.5 Dispatch rules

Default priorities:

1. prevent residence need from emptying;
2. supply health and maintenance;
3. supply active construction;
4. supply production inputs;
5. move output from blocked buildings;
6. fill strategic reserves;
7. export surplus.

The player can change priorities but the opening economy works without manual routing.

### 12.6 Bottleneck reporting

Every building records lost production during the last five minutes under:

- no input;
- output full;
- no workforce;
- environmental condition;
- no carrier pickup;
- paused by policy;
- damaged/contaminated.

The Industry Overseer ranks the largest losses by potential output value.

---

## 13. Services

| Service building | Coverage | Workforce | Ongoing input | Effect |
|---|---:|---:|---|---|
| Maintenance Organ | 16 tiles | 2 General | 1 Repair Enzyme per 10 maintained buildings per 8 min | Prevents disrepair |
| Waste Collector/Digester | 14 tiles | 3 Adapted | none beyond recipe | Removes and processes waste |
| Clean-Flow Node | 14 tiles downstream | 1 Adapted | clean source connection | Residence need and farm health |
| Detox Clinic | 14 tiles | 3 Adapted | 1 Repair Enzyme per 20 pop per 10 min | Health and anoxic recovery |
| Distribution Node | 14 tiles | 1 General | stocked goods | Delivers residence goods |
| Memory Circle | 16 tiles | 3 Coordinator | 1 Pigment Ornament per 20 pop per 12 min | Memory service and research |

### 13.1 Maintenance demand

Buildings have maintenance weights:

- simple farm/path/store: 0.5;
- residence/basic workshop: 1.0;
- advanced workshop/service: 1.5;
- kiln, pump or specialised infrastructure: 2.0;
- Great Work stage: 3.0 while under construction.

The “10 maintained buildings” recipe means 10 maintenance weight, not necessarily ten physical structures.

### 13.2 Service reliability

A residence must receive a service visit or network pulse at least once every 90 seconds. Service coverage overlays show theoretical reach and current reliability separately.

---

## 14. Construction costs

### 14.1 Basic buildings

| Building | Goods | Work units |
|---|---|---:|
| Shelter Cluster | 2 Carbonate, 1 Biomass | 8 |
| General Store | 3 Carbonate, 1 Prepared Silica | 12 |
| Living-Goods Store | 2 Carbonate, 1 Woven Fibre | 12 |
| Maintenance Organ | 2 Carbonate, 1 Biomass | 10 |
| Distribution Node | 1 Carbonate, 1 Fibre | 8 |
| Photosynthetic Field | 1 Biomass | 6 |
| Culture Bed | 1 Carbonate, 1 Biomass | 8 |
| Sediment Dredge | 2 Carbonate | 10 |
| Survey Organ | 1 Carbonate, 1 Silica | 10 |

### 14.2 Extraction and processing

| Building | Goods | Work units |
|---|---|---:|
| Filter Crown | 2 Woven Fibre, 1 Cured Resin | 12 |
| Silicate Pit | 2 Carbonate, 1 Repair Enzyme | 14 |
| Carbonate Cutter | 2 Prepared Silica, 1 Repair Enzyme | 14 |
| Anoxic Pump | 2 Ceramic, 2 Cured Resin | 18 |
| Nutrient/Mineral Washer | 3 Carbonate, 1 Prepared Silica | 14 |
| Nutrient Kitchen | 2 Ceramic, 1 Woven Fibre | 16 |
| Ceramic Kiln | 4 Carbonate, 2 Prepared Silica | 20 |
| Retting Pool | 2 Carbonate | 10 |
| Resin Curing Organ | 2 Carbonate, 1 Woven Fibre | 12 |
| Composite Workshop | 4 Ceramic, 2 Woven Fibre, 2 Cured Resin | 24 |
| Artisan Organ | 2 Ceramic, 1 Composite | 20 |

### 14.3 Services and advanced buildings

| Building | Goods | Work units |
|---|---|---:|
| Waste Digester | 3 Carbonate, 2 Ceramic | 18 |
| Detox Clinic | 2 Ceramic, 1 Composite, 1 Enzyme | 20 |
| Memory Circle | 2 Ceramic, 2 Composite, 2 Ornament | 24 |
| Trade Landing | 5 Carbonate, 3 Ceramic, 2 Composite | 30 |
| Additional Nursery | 4 Composite, 2 Enzyme | 30 |

Construction costs are intentionally dominated by simple materials; advanced goods gate only advanced functions.

---

## 15. Trade economy

### 15.1 Trade opening

Trade becomes available after:

- the neighbouring colony is surveyed;
- the player produces any 6-unit surplus above reserve;
- one Coordinator is available temporarily through a scripted envoy, or a Trade Landing is built later for permanent routes.

The first barter can therefore occur before Memory Ganglion.

### 15.2 Unit values

Stored value is a convenience unit for comparing barter, not modern money.

| Good | Base value |
|---|---:|
| Biomass | 1 |
| Staple Culture | 2 |
| Phosphate Sediment | 3 |
| Growth Nutrient | 6 |
| Suspended Nutrient | 3 |
| Raw Silicate | 3 |
| Prepared Silica | 5 |
| Carbonate | 4 |
| Raw/Woven Fibre | 2 / 4 |
| Raw/Cured Resin | 3 / 6 |
| Anoxic Organics | 5 |
| Fired Ceramic | 8 |
| Balanced Gel | 5 |
| Habitat Composite | 12 |
| Repair Enzyme | 9 |
| Pigment Ornament | 14 |

### 15.3 Neighbour profile

The neighbour has:

- Carbonate sell capacity: 0.50/min, maximum 30 per scenario.
- Pigment Ornament demand: up to 8 units at 18 value each.
- Growth Nutrient demand: up to 12 units at 8 value each.
- Prepared Silica demand: up to 10 units at 6 value each.
- Cured Resin sell capacity: 0.20/min, maximum 8.

Prices move no more than ±25% from base in the slice.

### 15.4 Contracts

#### Fertile Exchange

Deliver 8 Growth Nutrient before minute 55. Reward: 12 Carbonate immediately and Carbonate price −15% thereafter.

#### Colour of Memory

Deliver 6 Pigment Ornaments. Reward: 90 stored value, +10 relationship and one free Memory Circle service specialist.

#### Dry-Season Relief

If the neighbour suffers shortage during Dry Phase, send 12 Staple Culture. Reward: emergency imports ignore route delay for the rest of the scenario.

The player cannot complete every contract effortlessly while building the Memory Reef. Contracts are strategic opportunities, not a checklist.

### 15.5 Route timing

- Barter caravan round trip: 4 minutes.
- Trade Landing route: 2.5 minutes.
- Dry Phase route: +30 seconds without route investment.
- Goods leave inventory at departure and arrive physically at return.

---

## 16. Memory Reef great work

### 16.1 Unlock

The project unlocks when the player has:

- one Memory Enclave;
- an active Memory Circle;
- 8 Coordinator WP available settlement-wide;
- completed or declined the neighbour's first contract;
- maintained positive food reserve for 5 consecutive minutes.

### 16.2 Stages and costs

| Stage | Material cost | Labour | Function during construction |
|---|---|---|---|
| I — Foundation Bed | 12 Carbonate, 6 Fired Ceramic | 30 physical work | Creates project store and visible footprint |
| II — Living Lattice | 12 Carbonate, 8 Fired Ceramic, 10 Composite | 45 physical + 20 Coordinator work | Begins recording city history |
| III — Archive Crown | 6 Carbonate, 10 Fired Ceramic, 14 Composite, 8 Repair Enzyme, 6 Ornament | 40 physical + 40 Coordinator work | Completes scenario objective |

Total:

- 30 Carbonate;
- 24 Fired Ceramic;
- 24 Habitat Composite;
- 8 Repair Enzyme;
- 6 Pigment Ornament;
- 115 physical construction-work units;
- 60 Coordinator-work units.

### 16.3 Delivery and construction

- Each stage accepts deliveries only after the prior stage completes.
- Materials remain visible in the project yard.
- Physical and Coordinator labour can occur simultaneously once materials arrive.
- The player may pause the project and reclaim undelivered reservations.
- Demolishing an incomplete stage returns 75% of delivered durable materials and no biological consumables.

### 16.4 Completion effects

- permanent +10 settlement Memory/identity rating;
- all residences recover from Strain twice as quickly;
- reveals the region beyond the basin as the campaign continuation;
- scenario victory remains optional until the player chooses to conclude.

---

## 17. Supply targets and reserve policy

### 17.1 Default automatic reserves

| Good | Opening/mid-game reserve | Great Work reserve |
|---|---:|---:|
| Staple Culture | 12 / 20 | 24 |
| Growth Nutrient | 4 / 8 | 8 after morphology commitments |
| Balanced Gel | 0 / 8 | 12 |
| Carbonate | 6 / 12 | 30 project allocation |
| Prepared Silica | 2 / 8 | 8 |
| Fired Ceramic | 0 / 8 | 24 project allocation |
| Woven Fibre | 0 / 8 | 8 |
| Cured Resin | 0 / 6 | 6 |
| Habitat Composite | 0 / 8 | 24 project allocation |
| Repair Enzyme | 0 / 6 | 8 project allocation + 4 maintenance |
| Pigment Ornament | 0 / 4 | 6 project allocation + service stock |

### 17.2 Food safety

The Provisions Overseer reports:

- current minutes of food remaining;
- projected minutes at the next seasonal phase;
- five-minute production average;
- consumption at full residence occupancy;
- food committed to recipes or trade.

Warnings occur at 10, 5 and 2 minutes of projected food.

### 17.3 Expected food balance

At the reference minute-55 population mix, approximate recurring consumption at full occupancy is:

```text
4 Shelter × 0.20 Staple = 0.80 Staple/min
4 Stable × 0.24 Staple  = 0.96 Staple/min
3 Symbiotic × 0.12      = 0.36 Staple/min
1 Memory × 0.10         = 0.10 Staple/min
Total                    = 2.22 Staple/min

3 Symbiotic × 0.18 Gel  = 0.54 Gel/min
1 Memory × 0.22 Gel      = 0.22 Gel/min
Total                    = 0.76 Gel/min
```

This requires roughly three Culture Beds and three strong Photosynthetic Fields in normal seasons. During Dry Phase the player needs fertilised farms, a fourth field, imports or a reserve. One Nutrient Kitchen easily covers Gel consumption if supplied.

---

## 18. Reference production plan

This is a solvability proof, not the intended single build order.

### 18.1 Minutes 0–12: secure the opening

Suggested actions:

- survey phosphate and clean flow;
- build a fourth Shelter Cluster;
- build a Sediment Dredge and Nutrient Washer;
- add a second Photosynthetic Field before Bloom ends;
- accumulate 4 Growth Nutrient;
- maintain at least 10 Staple Culture.

Expected state near minute 12:

- population 30–34;
- 24–26 General WP available;
- food production 1.7–2.0 Staple/min;
- food consumption 0.8–1.0/min;
- 3–5 Growth Nutrient produced;
- Burrowing Limb revealed.

### 18.2 Minutes 12–25: create the first district

Suggested actions:

- establish Waste service and Clean Flow;
- evolve two Shelters into Stable Habitats;
- invest in Burrowing Limb or Filter Crown;
- open Silicate extraction or renewable filtering;
- create specialised storage/distribution;
- experience the High Water closure of the sediment bed.

Expected state near minute 25:

- 2 Shelter + 2 Stable residences, with additional construction possible;
- 12 General and 16 Adapted WP at full occupancy;
- a temporary Growth Nutrient bottleneck caused by High Water;
- either Filter Crown online or nutrient reserves carrying the city;
- first logistics warning caused by the distant Silicate route.

### 18.3 Minutes 25–42: become an industrial settlement

Suggested actions:

- mine and wash Silicate;
- establish Fibre Garden/Retting and Resin Grove/Curing;
- build one Ceramic Kiln;
- build Nutrient Kitchen;
- evolve the first Symbiotic Neighbourhood;
- contact and trade with the neighbour.

Expected state near minute 42:

- 55–70 population;
- at least 12 Artisan WP;
- Ceramic output 0.5/min;
- Fibre 0.6/min and Resin 0.4/min;
- Balanced Gel surplus above 0.4/min;
- one trade shipment complete;
- Mineral Jaw, Detox Sac or Vascular Carrier competing for investment.

### 18.4 Minutes 42–60: integrate the economy

Suggested actions:

- build Composite Workshop and Waste Digester;
- add a second Kiln or import material if project timing requires it;
- establish Pigment production;
- evolve two or three Symbiotic Neighbourhoods;
- invest in Memory Ganglion;
- start storing Dry Phase food;
- complete a trade contract or secure Carbonate locally.

Expected state near minute 60:

- 80–100 population;
- 20+ Artisan WP;
- first Memory Enclave in progress;
- 20+ Staple reserve;
- 8+ Ceramic and 8+ Composite reserved;
- Dry Phase begins and exposes any underbuilt food/logistics network.

### 18.5 Minutes 60–90: endure and build the Memory Reef

Suggested actions:

- protect staple production through fertilisation, imports or reserves;
- keep the anoxic supply chain safe with Detox Sac or accept reduced fuel output;
- build Memory Circle and unlock the Great Work;
- operate two Kilns and one or two Composite Workshops as inputs allow;
- choose whether to import Carbonate or divert Ceramic to substitution;
- deliver Great Work materials in stages;
- preserve enough Repair Enzyme for maintenance and project costs.

Expected first-success completion: minute 78–88.

---

## 19. Great Work feasibility check

Assume serious project production begins at minute 42 and runs until minute 84: 42 production minutes.

### 19.1 Fired Ceramic

- One Kiln at 0.50/min for 42 min = 21 Ceramic.
- A second Kiln built at minute 60 and running 24 min = 12 Ceramic.
- Gross = 33 Ceramic.
- Allow 9 Ceramic for buildings/services.
- Net project supply = 24 Ceramic.

This exactly meets the project requirement and makes fuel, Silica or logistics interruptions meaningful. Imports or earlier construction provide recovery.

### 19.2 Habitat Composite

- First Workshop at 0.50/min from minute 44 to 84 = 20 Composite.
- Second Workshop or mastery bonus from minute 68 to 84 adds at least 8.
- Allow 4 Composite for Memory Circle/Trade Landing/residence evolution beyond project prerequisites.
- Net project supply = 24 Composite.

If the player runs only one Workshop, they must start earlier, import Resin/Composite or reduce non-project spending.

### 19.3 Carbonate

- One adapted Cutter at 0.60/min for 50 min = 30 Carbonate before seasonal/staffing losses.
- The Fertile Exchange contract grants 12 Carbonate.
- Existing construction also consumes Carbonate.

The player therefore needs some combination of early cutting, trade and Ceramic substitution. This is intended to be the scenario's territorial/economic decision.

### 19.4 Repair Enzyme

- Waste Digester intermittent average target: 0.15–0.20/min.
- 40 active minutes yields 6–8 Enzyme.
- Emergency Culture or trade covers maintenance and project overlap.

The enzyme requirement tests whether the player built a circular economy rather than treating waste as a cosmetic penalty.

### 19.5 Pigment Ornament

- Artisan Organ at 0.25/min needs 24 active minutes for 6 project Ornament.
- Memory service and residence evolution consume additional Ornament.
- Pigment chain should begin no later than minute 55 unless the player earns the free service specialist contract reward.

### 19.6 Labour

- 10 unassigned physical WP completes 115 work in 11.5 minutes once staged materials arrive.
- 6 Coordinator WP completes 60 work in 10 minutes.
- Material delivery, not raw labour, should be the normal limiting factor.

---

## 20. Designed bottlenecks

### 20.1 First bottleneck: Growth Nutrient

The player needs it for:

- population growth;
- residence evolution;
- morphology;
- farm fertilisation;
- trade contract.

High Water temporarily closes the easiest source, teaching reserves and alternative filtering.

### 20.2 Second bottleneck: workforce composition

Upgrading every Shelter removes General WP, starving farms, carriers and construction. The player learns to maintain mixed housing rather than maximising tier.

### 20.3 Third bottleneck: distance and transport

Silicate and Carbonate occur beyond comfortable haul range. Additional carriers help initially; a Transfer Node or Vascular Carrier becomes the durable solution.

### 20.4 Fourth bottleneck: Resin

Resin is slow, fertility-sensitive and required for Composite, Ornament and advanced construction. The player may farm more, import, improve fertility or use an expensive substitute.

### 20.5 Fifth bottleneck: Dry Phase food

The late project competes with the need to protect food supply. The correct lesson is not “build more everything” but forecast, reserve and diversify.

### 20.6 Sixth bottleneck: Carbonate policy

The Great Work and city construction compete for a contested bulk material. Local extraction, neighbour relationship and mineral substitution are all valid.

---

## 21. Recovery and anti-spiral rules

### 21.1 Emergency food

- The First Nursery can convert 2 Biomass into 1 Staple every 90 seconds without workforce.
- This is inefficient but cannot be disabled by labour collapse.
- It activates automatically below 2 minutes of food unless the player opts out.

### 21.2 Minimum workforce

- One Shelter Cluster can never devolve or be abandoned.
- The First Nursery and starting Store each retain one emergency operator without consuming WP.
- If all General WP disappears, one higher-tier residence can re-express 4 General WP after a 90-second delay at no material cost.

### 21.3 Material recovery

- Normal buildings return 60% of durable construction goods when demolished.
- Cancelled construction returns all undelivered and 90% of delivered materials.
- Morphology conversion can be reversed at half material cost.

### 21.4 Trade relief

If projected food falls below two minutes and the neighbour relationship is non-hostile, one emergency shipment of 8 Staple is offered on credit. Repayment is a later optional obligation rather than instant failure.

### 21.5 Project protection

Memory Reef materials already incorporated into a completed stage are never consumed by maintenance or trade automation. The project cannot cause an accidental total-resource drain.

---

## 22. Difficulty levers

Do not change recipe relationships between difficulties; change pressure around them.

| Lever | Gentle | Standard | Demanding |
|---|---:|---:|---:|
| Starting Staple reserve | 12 | 8 | 6 |
| Farm seasonal penalty in Dry | ×0.80 | ×0.65 | ×0.55 |
| Residence internal buffer | 5 min | 3 min | 2 min |
| Trade price spread | ±10% | ±25% | ±35% |
| Deposit reserves | +25% | baseline | −15% |
| Service lapse grace | 4 min | 3 min | 2 min |
| Rival Carbonate claim | delayed | baseline | earlier/stronger |
| Forecast accuracy | exact | exact | ±10% after first cycle |

Great Work costs remain constant so the scenario retains a shared economic target.

---

## 23. UI requirements derived from the economy

### 23.1 Top-level HUD

Show only:

- population/capacity;
- four workforce classes with employed/available values;
- Staple minutes remaining;
- current season and next transition;
- active urgent warning count;
- selected pinned resources, maximum six.

Do not place every good permanently across the top of the screen.

### 23.2 Resource ledger

Each good shows:

- current stock;
- reserved stock;
- five-minute production and consumption;
- projected next-season balance;
- principal producers and consumers;
- import/export policy;
- storage locations.

### 23.3 Production-chain view

Selecting a finished good displays its upstream graph, current rates and weakest link. The graph uses functional family icons alongside alien names.

### 23.4 Residence inspection

Show:

- current and next stage;
- population and workforce class;
- internal need buffers in minutes;
- service reliability;
- Habitat Quality contributors;
- reserved evolution goods;
- exact decline timer if strained.

### 23.5 Seasonal forecast

For each phase, show expected changes to:

- crop yields;
- patch accessibility;
- filtering;
- hazards;
- transport;
- settlement food balance.

---

## 24. Instrumentation and balance telemetry

Record per minute:

- stock and net flow of every good;
- actual versus potential building output;
- lost production by cause;
- carrier utilisation and average trip distance;
- workforce demand/supply by class;
- residence needs, quality and evolution state;
- farm fertility and seasonal multiplier;
- patch reserves;
- trade volumes and prices;
- morphology timing;
- Great Work delivery and labour progress;
- warnings raised and time-to-resolution.

Key playtest markers:

| Marker | Target window |
|---|---:|
| First new building | 1–3 min |
| First detected limiting nutrient | 4–7 min |
| Stable food surplus | 6–10 min |
| First residence evolution | 12–18 min |
| First seasonal transition | 18 min fixed |
| First morphology | 15–23 min |
| First real logistics bottleneck | 20–30 min |
| First processed construction good | 28–36 min |
| First trade | 28–40 min |
| First Symbiotic residence | 32–45 min |
| Memory Ganglion commitment | 50–62 min |
| Great Work begins | 58–68 min |
| First-success completion | 78–88 min |

---

## 25. Balance assertions to test

1. One opening Photosynthetic Field and Culture Bed provide a temporary surplus, not permanent security.
2. A second field before High Water gives comfortable early food.
3. High Water creates a nutrient-planning problem without threatening basic survival.
4. Upgrading every residence is an understandable workforce mistake with a recoverable outcome.
5. One distant mine is enough to reveal logistics limitations.
6. One Kiln or Composite Workshop supports city development; two or early operation are needed to finish the Great Work promptly.
7. Waste recycling meaningfully contributes to the project but does not cover every Enzyme need automatically.
8. The player can bypass one extraction morphology through trade, but not ignore geography entirely.
9. The Dry Phase is survivable through any two of reserve, fertilisation, extra farms, imports or reduced population growth.
10. The Memory Reef consumes a mature economy's surplus without requiring the player to idle the city completely.

---

## 26. Implementation order for the economy prototype

### Phase A — Headless economic model

1. Goods, inventories and discrete batches.
2. Recipes and building productivity.
3. Residence consumption and workforce classes.
4. Seasons and farm multipliers.
5. Patch reserves and access windows.
6. Construction reservations and Great Work stages.
7. Trade transactions.

Use a scripted reference city to simulate 90 minutes and verify no hidden impossibility.

### Phase B — Spatial logistics

1. Physical stores and carriers.
2. Distance-based dispatch.
3. Distribution Nodes and residence buffers.
4. Flow Channels and Transfer Nodes.
5. Bottleneck telemetry.

### Phase C — Player-facing city systems

1. Housing evolution and Habitat Quality.
2. Services and district coverage.
3. Morphology/caste conversion.
4. Trade partner and contracts.
5. Great Work construction.

### Phase D — Presentation

1. Map chemistry cues.
2. Visible goods and work activity.
3. Residence transformations.
4. Seasonal changes.
5. Memory Reef stages.

No final art production should precede a stable Phase A simulation.

---

## 27. Decisions locked for the first prototype

- Goods are physical and locally stored.
- The economy uses discrete cargo units.
- Residences provide tier-specific workforce classes.
- Housing upgrades convert workforce rather than simply adding better universal labour.
- Basic food uses a short chain; advanced food uses phosphate-derived Growth Nutrient.
- Fertility is crop-specific.
- Phosphate is the opening limiting nutrient.
- Seasons change both productivity and patch access.
- Morphologies unlock economic verbs and caste roles.
- Trade is a valid substitute for one missing local capability.
- Waste feeds a useful Repair Enzyme chain.
- The Memory Reef is the slice's economic culmination.
- The first scenario is winnable without perfect ratios or completion of every optional contract.

---

## 28. Questions left deliberately open

These require simulation or playtesting rather than more prose:

1. Is one cargo unit granular enough, or do low-rate residence needs require internal milli-units?
2. Does conversion of an entire residence to one workforce class create interesting districts or excessive bookkeeping?
3. Is 12 active raw/processed goods by minute 35 comfortable with the proposed UI?
4. Are individual carriers readable and performant at 100 population?
5. Should Distribution Nodes deliver discrete goods or provide service while consuming a district stock?
6. Does the Dry Phase food multiplier create preparation or merely force extra farms?
7. Is the Carbonate decision visible early enough to influence morphology and trade choices?
8. Can one Great Work support replay, or should its final stage accept alternative material packages?
9. Does the Memory Ganglion arrive too late for Coordinators to feel like a city system rather than a victory key?
10. Should first-playthrough victory stop the simulation, or only present a completion choice?

---

## 29. Next artifact

The next artifact should be a small executable balance model—not the game client—that loads these values from data, runs the reference plan and produces:

- minute-by-minute inventories;
- workforce allocation;
- production utilisation;
- seasonal effects;
- Great Work completion time;
- warnings for starvation, negative inventory or impossible workforce assignments.

The values in this document should then be adjusted from model results before `game_v2` begins.
