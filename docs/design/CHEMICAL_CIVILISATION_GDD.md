# Pondlife: Chemical Civilisation

## Foundational game design document — v0.1

**Status:** New design foundation for discussion and prototyping  
**Date:** 2 October 2026  
**Primary inspiration:** *Pharaoh*  
**Supporting inspirations:** *Anno*, *Age of Empires*, *Spore*  
**Genre:** Evolutionary city-builder, production-chain simulation and territory strategy game  
**Platform:** PC first  
**Engine:** Godot remains suitable, but implementation architecture should be reconsidered after the design prototype  

This document supersedes the original three-resource economy and fixed ten-era implementation assumptions. It does not order the deletion of the existing prototype. The current project should be preserved as an archive and source of reusable experiments while a clean vertical slice tests this design.

---

## 1. The game in one sentence

Build an alien civilisation whose bodies, farms, industries, settlements and culture emerge from the chemistry of its world.

## 2. The player fantasy

The player begins with a small community of organisms living in a chemically active patch of an alien biosphere. They learn what the local environment contains, harvest and cultivate its materials, build a settlement, satisfy the changing needs of its inhabitants and develop increasingly complex production chains.

The civilisation does not progress through a conventional human technology tree. It acquires biological capabilities, industrial techniques and social institutions in response to what its world makes possible. A species surrounded by silica, oxygen and strong sunlight develops differently from one living in frigid hydrocarbon seas under a methane-rich atmosphere. Neither route is a cosmetic skin over the same economy.

At the city scale, play should feel principally like *Pharaoh*:

- terrain determines where a viable settlement can exist;
- farms and extractive industries depend on local conditions;
- goods have to be moved, stored, processed and distributed;
- homes evolve when their inhabitants receive the right goods and services;
- districts acquire identity through placement, access and desirability;
- prosperity creates more demanding populations and more complex institutions;
- trade compensates for local scarcity and gives surplus production a purpose;
- environmental events interrupt plans without reducing the game to combat;
- great works turn a successful economy into a visible civilisational achievement;
- missions present different geographical and economic puzzles rather than merely larger maps.

The alien-biosphere premise changes what all of those familiar city-building verbs mean. A “farm” may be a photosynthetic membrane field, a bacterial sulphur bed, a drifting filter garden or an acetylene culture. A “road” may be a mucus track, a controlled current, a mycelial transport web or a pressure-stable tunnel. A “temple” may be a memory reef where the colony maintains inherited biological patterns. The underlying relationships remain legible even when the fiction is unfamiliar.

---

## 3. Design pillars

Every substantial mechanic must serve at least two of these pillars.

### 3.1 Chemistry is destiny, but not a script

Atmosphere, solvent, geology, climate and energy gradients define the opportunities and constraints of a playthrough. The player responds creatively through settlement design, trade, cultivation and evolution. Chemistry establishes the possibility space; it must not prescribe a single correct build order.

### 3.2 The settlement is a living production organism

Resources should be visible moving through the city. Inputs arrive, processors operate, carriers transport goods, stores fill, homes consume supplies and waste leaves productive districts. A functioning settlement can be read from its activity rather than only from counters.

### 3.3 Biology is the technology tree

Evolutionary changes unlock economic verbs. Filter organs enable dissolved-resource extraction. Burrowing morphologies open deep deposits. Mineralised tissues permit cutting and excavation. Photosynthetic membranes convert light into stored energy. Collective nervous structures enable administration and complex trade.

### 3.4 Place matters

Local chemical gradients, fertility, flow, light, temperature, pressure and hazards create meaningful districts. Buildings cannot be placed anywhere with equal effect. Geography should produce the same kind of planning puzzle that the Nile floodplain, meadow farms, clay pits and trade access create in *Pharaoh*.

### 3.5 Prosperity creates complexity

Growth is not merely a larger population cap. More developed inhabitants require varied nutrition, environmental regulation, health, culture and specialist goods. Meeting those needs produces a more capable workforce and unlocks new institutions, but also makes the city more interdependent.

### 3.6 Consequence without cruelty

Specialisation creates strengths, dependencies and trade-offs, not hidden traps. Supply failures cause dormancy, migration, reduced productivity or devolution before death. Recovery is always possible through substitution, trade, adaptation or restructuring.

### 3.7 Peaceful competition with real pressure

Rivals compete for territory, deposits, trade contracts, prestige and great works. Conflict may include obstruction, predation or defensive force where fiction demands it, but extermination is not the centre of the game. Economic competence is the primary expression of power.

### 3.8 Scale is the spectacle

The settlement begins within a tiny ecological niche and eventually alters entire watersheds, atmospheres or planetary cycles. Great works and camera recontextualisation should repeatedly reveal how far the civilisation has come.

---

## 4. Reference-game DNA

This game should learn relationships from its references, not copy their surface content.

### 4.1 What comes from *Pharaoh*

*Pharaoh* is the dominant reference because its economy is inseparable from settlement form and civic life.

- **Map-specific survival puzzle:** every mission begins by reading terrain, water, fertility, raw materials and external connections.
- **Seasonal production:** the Nile's flood cycle creates a rhythm of cultivation, inundation and harvest. Pondlife should use chemical blooms, tides, freezes, rains, vent cycles or atmospheric seasons in the same structural role.
- **Physical distribution:** farms and workshops are insufficient without storage, carriers and access.
- **Housing evolution:** residences improve when nearby services and distributed goods satisfy explicit requirements.
- **Service coverage:** health, maintenance, culture and administration shape where stable neighbourhoods can form.
- **Desirability:** polluting, dangerous or disruptive industries belong somewhere, but not beside advanced residences.
- **Trade permissions and quotas:** routes must be opened, goods authorised and import/export policy managed.
- **Overseers:** complex systems remain readable through specialised management views.
- **Monuments:** surplus labour and materials culminate in enormous, long-running projects that visibly consume the city's output.
- **Mission identity:** a map can focus on farming, trade, survival, remote extraction or a great work while using the same foundational systems.

We should modernise brittle elements rather than reproduce them literally. Service access should be deterministic and inspectable; carriers should not wander unpredictably. Employment should create spatial and demographic decisions without forcing tedious universal road access. Failures should explain themselves.

### 4.2 What comes from *Anno*

- multi-stage production chains with measurable throughput;
- regional fertility and deposits that encourage specialisation;
- population strata with distinct needs and workforce roles;
- trade networks that connect complementary settlements;
- goods that serve both population needs and industrial recipes;
- production ratios that reward planning while allowing deliberate overproduction;
- economic information strong enough to diagnose shortages.

### 4.3 What comes from *Age of Empires*

- immediate, readable gathering and drop-off behaviour;
- territory secured by active economic presence;
- workers whose allocation expresses the player's priorities;
- age transitions as expensive strategic commitments;
- rival pressure that makes efficiency matter now, not only eventually;
- a clear relationship between map control, economic strength and capability.

The game should avoid turning into high-micro military RTS play. Units may be directly selected when useful, but the mature settlement is managed mainly through priorities, district rules and logistics.

### 4.4 What comes from *Spore*

- visible morphological change;
- the delight of seeing an organism become stranger and more capable;
- a civilisation whose history can be read in its body plan;
- the fantasy of progressing from microscopic life toward planetary agency.

The game should not use a free-form creature editor as its primary progression interface. Morphology must be economically and ecologically grounded rather than a collection of arbitrary stat parts.

---

## 5. Scientific-fiction framework

Pondlife should feel scientifically literate without pretending to simulate xenobiology accurately. The goal is coherent speculative ecology: players should understand why a world produces its resources and why a biological adaptation helps there.

### 5.1 A planet is not defined by one gas

Terms such as “carbon planet” or “methane world” are useful shorthand but insufficient as rules. Every world seed is described across five axes:

1. **Atmosphere:** principal gases, trace reactive gases, pressure and opacity.
2. **Solvent system:** water, water-ammonia, liquid hydrocarbons or another authored solvent family.
3. **Geology:** accessible minerals, salts, metals and substrate structure.
4. **Energy regime:** stellar light, geothermal heat, redox gradients, radiation, tides and electrical storms.
5. **Climate and circulation:** temperature, seasonality, precipitation, currents, winds and freeze/thaw behaviour.

Life needs matter, a solvent or transport medium, and exploitable energy gradients. Gameplay should therefore focus less on merely possessing elements and more on bringing complementary substances together through a catalysed process.

### 5.2 Scientific licence

- All playable biospheres may remain broadly carbon-based to preserve recognisable organic chemistry and production logic.
- Water-world and hydrocarbon-world organisms use substantially different membrane, transport and energy assumptions.
- Methane itself is not automatically “methane-based life”; it may be solvent, feedstock, waste product or atmospheric context depending on the authored chemistry.
- Oxygen is treated as a powerful oxidant and industrial enabler, not simply a synonym for habitability.
- Trace elements can be strategically important even when bulk materials are abundant.
- Evolution during a game represents directed selection, symbiosis, cultivation and bioengineering compressed into a playable timescale.
- Every unusual chain needs an in-game plain-language explanation. Real chemical notation may appear in an optional science layer, not as required literacy.

### 5.3 Inspiration, not prediction

Titan demonstrates the useful speculative pattern: a nitrogen-methane atmosphere, photochemically produced organics, hydrocarbon lakes and a surface cycle in which methane occupies some of water's geographical role. NASA also stresses that alternative membranes and actual life in those conditions remain hypothetical. Pondlife can use that uncertainty as creative space while labelling speculative concepts honestly.

---

## 6. The world seed

Each campaign map is generated from an authored **planetary chemistry profile** plus a mission-specific region.

### 6.1 Profile fields

```text
Star spectrum
Atmospheric gases and pressure
Surface solvent
Mean temperature and seasonal amplitude
Primary energy gradients
Crustal/mineral families
Global nutrient limitations
Atmospheric and hydrological cycles
Native ecological guilds
Hazard families
Rare compounds
```

The profile determines which raw resources, processing reactions, farm families, morphologies and architectural materials can appear. The mission region then determines local abundance and geography.

### 6.2 Authored chemistry archetypes

The first game should use a small set of authored archetypes rather than attempting arbitrary procedural chemistry.

#### A. Oxic water world — “Verdant”

- Water solvent; nitrogen/carbon-dioxide atmosphere that becomes increasingly oxygenated.
- Strong photosynthetic economy.
- Common biomass, carbonate, phosphate, clay/silicate and oxidised metal resources.
- Efficient high-energy respiration becomes possible after oxygen management.
- Likely materials: fibre, resin, ceramic, glass, mineral plate and refined metal.
- Principal risks: eutrophication, oxidative stress, fire in exposed late settlements and seasonal drying.

#### B. Reducing hydrocarbon world — “Haze”

- Nitrogen and methane atmosphere; liquid methane/ethane surface cycle; extreme cold.
- Energy derived from authored hydrogenation, photochemical organics and catalytic gradients.
- Common hydrocarbons, nitriles, acetylene-rich deposits, water ice and atmospheric haze solids.
- Likely materials: waxy membranes, polymer fibre, ice composite, nitrogenous films and catalytic alloys.
- Principal risks: slow reaction rates, brittle structures, solvent loss, hydrogen scarcity and thermal disruption.

#### C. Sulphuric vent world — “Ember Sea”

- Water or brine solvent; volcanic archipelagos and strong geothermal/redox gradients.
- Chemosynthetic food webs founded on sulphur, iron and hydrogen chemistry.
- Common sulphides, metal-rich precipitates, acidic brines, silicates and vent biomass.
- Likely materials: mineral shell, sulphur polymer, ceramic, metal sulphide catalysts and heat-resistant composites.
- Principal risks: toxic plumes, pH shifts, eruptions, mineral fouling and thermal shock.

#### D. Ammonia-water cryoworld — post-prototype candidate

- Cold ammonia-water solvent system and nitrogen-rich chemistry.
- Slow biological cycles, high value placed on heat and insulation.
- Distinct farming and construction logic built around cryogenic gradients.

Only A and B are required to prove the design. C establishes that the system can later support more than an Earth/Titan binary.

### 6.3 Planetary constants and local variation

Global chemistry determines what can exist. Local patches determine what the player can reach.

A Verdant world always permits water-based agriculture, but one region may be phosphate-poor, another iron-poor and another plagued by anoxic sediment. A Haze world may contain methane everywhere while useful acetylene fall, exposed water ice and metallic catalysts occur only in particular locations.

This distinction creates strategic geography without making a whole planet economically uniform.

---

## 7. Map anatomy and chemical geography

### 7.1 The map is a set of overlapping fields

Instead of isolated resource blobs, the environment contains continuous and patch-based properties:

- solvent depth;
- substrate type;
- dissolved chemical concentrations;
- atmospheric exposure;
- temperature;
- light intensity and spectrum;
- current or wind;
- acidity/alkalinity;
- salinity;
- oxygenation or relevant oxidant availability;
- fertility;
- contamination;
- hazard exposure.

The player initially perceives broad visual cues. Survey organisms and analytical buildings reveal exact values later.

### 7.2 Patch types

Patches are comprehensible geographical features, not randomly scattered icons.

- **Seeps:** gases or dissolved chemicals emerging from below.
- **Vents:** heat and reduced minerals creating energy-rich boundaries.
- **Sediment beds:** diggable nutrients, organics, clays or salts.
- **Outcrops:** mineable or cuttable solid material.
- **Mats and reefs:** living resources that may be harvested or cultivated.
- **Atmospheric fall:** haze, spores, dust or reactive condensate collected from exposure.
- **Flow channels:** moving solvent carrying filterable resources.
- **Evaporite or freeze margins:** seasonally deposited concentrated salts or hydrocarbons.
- **Impact remnants:** rare metals and anomalous compounds.

### 7.3 Quality, quantity and renewability

Every deposit has three independent qualities:

- **Grade:** output per extraction cycle or refinement efficiency.
- **Reserve:** finite amount remaining.
- **Renewal:** rate and conditions under which it regenerates.

A low-grade renewable filter site and a rich finite deposit create different planning decisions. UI must never hide which category a resource belongs to.

### 7.4 Fertility

Fertility is crop-specific rather than a universal green number. It represents the local combination of solvent, usable carbon or equivalent bulk feedstock, energy, trace nutrients, temperature and waste clearance.

```text
Effective fertility = base substrate suitability
                    × solvent suitability
                    × energy availability
                    × limiting nutrient factor
                    × seasonal factor
                    × pollution/health factor
```

The limiting nutrient rule matters. An area with abundant bulk carbon may still produce poorly if phosphorus, catalytic metal or usable nitrogen is scarce. This gives fertiliser and soil-conditioning industries a reason to exist.

### 7.5 Seasonal transformation

Some patches change function through a predictable calendar:

- flood or tide deposits fertile material, then exposes farmable ground;
- methane rain fills basins and activates filtration sites;
- a dry season concentrates salts but stresses farms;
- vent pulses increase chemical energy and toxicity together;
- a freeze season permits travel over solvent but halts exposed cultivation;
- atmospheric haze fall temporarily enriches collector fields.

Like the Nile cycle in *Pharaoh*, seasons should invite planning rather than act as random punishment.

---

## 8. Resource model

### 8.1 Resource families

Resources are grouped by economic role so an unfamiliar alien name never obscures its use.

| Family | Function | Examples |
|---|---|---|
| Metabolic feedstocks | Energy and basic survival | sugars, methane, hydrogen, sulphides, acetylene |
| Bulk nutrients | Population growth and farming | fixed nitrogen, phosphate, carbon feed, mineral salts |
| Trace catalysts | Enable efficient reactions | iron, nickel, cobalt, molybdenum analogues |
| Structural organics | Flexible construction and goods | fibre, resin, wax, chitin-like plate, polymer film |
| Structural minerals | Rigid construction and tools | silicate, carbonate, clay, water ice, crystal |
| Industrial reactants | Refining and manufacturing | oxidants, acids, alkalis, reducing agents, solvents |
| Specialist biological goods | Health, fertility and evolution | enzymes, cultures, hormones, spores, memory compounds |
| Civic and luxury goods | Prosperity, culture and trade | pigments, scents, ornaments, stimulants, crafted symbionts |
| Waste and by-products | Liability or secondary feedstock | sludge, heat, brine, oxidised residue, exhaust gases |

### 8.2 Resource states

Every good has a state in the economy:

1. **Environmental:** part of a patch or ambient field.
2. **Raw:** extracted and transportable.
3. **Prepared:** cleaned, sorted, dried, crushed or concentrated.
4. **Refined:** chemically or biologically transformed.
5. **Component:** a standardised part used in several recipes.
6. **Finished good:** consumed by homes, institutions, trade or construction.
7. **Waste/by-product:** requires disposal, remediation or reuse.

Not every resource visits every state. Short early chains keep the opening readable; later chains combine branches.

### 8.3 Economic verbs

Extraction and transformation must be visually and mechanically distinct.

#### Extraction

- **Mine:** remove hard deposits using cutting or dissolving morphology.
- **Cut:** harvest structural growths or soft mineral formations.
- **Dig:** remove sediment, buried nodules or substrate-bound nutrients.
- **Pump:** draw liquid or gas from a reservoir.
- **Filter:** collect dissolved or suspended substances from flow.
- **Condense:** capture atmospheric or evaporative material.
- **Graze:** harvest a renewable living surface directly.
- **Farm:** deliberately cultivate a renewable organism or chemical ecology.
- **Scavenge:** recover episodic remains, fallout or debris.
- **Collect:** gather discrete surface deposits.

#### Primary processing

- wash;
- sort;
- crush;
- dry or freeze-separate;
- digest;
- ferment;
- culture;
- concentrate;
- dissolve;
- precipitate.

#### Advanced processing

- refine;
- distil;
- smelt or thermally reduce;
- electrolyse;
- catalyse;
- polymerise;
- weave;
- fire/sinter;
- alloy or composite;
- encode or biologically pattern.

#### Economic use

- consume;
- distribute;
- build;
- maintain;
- manufacture;
- trade;
- gift;
- invest;
- reserve;
- recycle;
- remediate.

### 8.4 The two-use rule

Every resource must matter to at least two systems. A material that exists only as one recipe's intermediate should normally be abstracted into that recipe unless transporting or storing it creates a meaningful decision.

Valid secondary roles include:

- population need;
- construction;
- maintenance;
- morphology;
- farming input;
- trade good;
- civic good;
- strategic reserve;
- ecological side effect;
- alternative recipe.

### 8.5 Substitution

The economy should support authored substitutions, never universal fungibility.

Examples:

- fibre composite or mineral plate may satisfy a “structural material” requirement with different durability and upkeep;
- geothermal heat or stored chemical fuel may power a kiln;
- imported catalyst may replace a less efficient local biological enzyme;
- several staple biomasses can feed basic homes, but advanced homes demand dietary variety.

Substitutions protect against dead ends and encourage trade while preserving chemical identity.

---

## 9. Production chains

### 9.1 Chain design rules

1. Early chains contain one extraction and one processing step.
2. Mid-game chains combine two inputs or require a service condition.
3. Late chains cross previously separate sectors.
4. At least one output from every major sector must feed another sector.
5. Bottlenecks must be diagnosable by rate, stock, carrier capacity and input availability.
6. By-products should create opportunities as well as disposal problems.
7. No chain should exist solely to inflate step count.

### 9.2 Example: Verdant food economy

```text
Sunlight + CO2 + water
    → photosynthetic biomass
    → staple cultures
    → distributed food

Phosphate sediment
    → washed phosphate
    → growth nutrient ─────────┘

Nitrogen-fixing culture
    → fixed nitrogen ──────────┘
```

Advanced population requires dietary variety:

```text
Staple culture + mineral salts → balanced nutrient gel
Protein colony + aromatic pigment → prestige food
```

### 9.3 Example: Verdant construction economy

```text
Fibre crop → retted fibre → woven lattice ─┐
Resin grove → raw resin → cured sealant ───┼→ habitat composite
Silicate sediment → washed silica → glass ─┘
```

Heavy civic construction may instead use:

```text
Clay bed → prepared clay → fired ceramic
Carbonate reef → cut blocks
Metal ore + fuel/energy + oxidant → refined metal
```

### 9.4 Example: Haze metabolic economy

```text
Atmospheric hydrogen ─────────────┐
Photochemical acetylene fall ─────┼→ catalytic metabolic culture → stored energy carrier
Nickel-iron catalyst deposit ─────┘
```

The reaction is an authored speculative metabolism, not a claim of discovered alien biology.

### 9.5 Example: Haze construction economy

```text
Haze organics → separated nitriles → membrane film
Methane/ethane feedstock → polymer precursor → flexible polymer
Water-ice outcrop → cut ice → insulated ice composite
Meteoric silicate/metal → catalyst or rigid reinforcement
```

### 9.6 Example: cross-sector late good

An adaptive pressure habitat might require:

- structural composite from farming and materials;
- refined catalyst from mining;
- environmental membrane from chemical industry;
- stored energy from the metabolic sector;
- a specialist builder caste created by morphology.

This is the point at which a developed settlement feels interdependent rather than merely busy.

### 9.7 Throughput and ratios

Every production building exposes:

- recipe inputs and output;
- batch size;
- cycle time;
- workforce required;
- energy requirement;
- environmental requirements;
- storage capacity;
- current productivity;
- causes of lost productivity during the last period.

The UI may show suggested ratios, but perfect ratios are not mandatory. Distance, fertility, seasons, worker availability and player policy create deliberate inefficiency.

---

## 10. Logistics: the circulatory system of the city

### 10.1 Physical goods

Goods exist in stores and transit. Global totals are summaries, not magical shared inventories. Construction sites and consumers must receive materials from reachable storage.

### 10.2 Network types

Each chemistry archetype reskins and modifies four common network roles:

| Network role | Verdant example | Haze example |
|---|---|---|
| Local path | mucus track/rootway | compacted hydrocarbon trail |
| Bulk route | controlled water current | buoyant channel or pressure conduit |
| Pipeline | vascular tube | insulated capillary |
| Long-range route | river/shore convoy | crawler, floater or seasonal methane route |

The simulation cares about speed, capacity, directionality, maintenance and environmental tolerance.

### 10.3 Haulage

Carriers draw tasks from district logistics rather than being manually ordered for every trip. Player controls include:

- warehouse acceptance rules;
- minimum reserve and export thresholds;
- route priorities;
- building input priority;
- maximum haul distance;
- emergency distribution;
- district import/export permissions.

Direct control remains available for expeditions, urgent construction or tutorial-scale play.

### 10.4 Storage

Storage is specialised enough to matter:

- bulk dry/mineral storage;
- living culture storage;
- volatile or cryogenic reservoir;
- food/nutrient store;
- civic-goods store;
- hazardous-reactant containment.

Storage buildings can sort goods, preserve perishables and act as distribution hubs. Poor storage produces decay, leakage or contamination rather than silently deleting goods.

### 10.5 Distribution

Population goods reach residences through one of three systems:

1. **Local distributor:** collects from storage and serves a deterministic route or radius.
2. **Resident collection:** inhabitants visit a nearby market/distribution organ.
3. **Network service:** later settlements distribute fluid, heat or energy through pipes.

The chosen method is visible and inspectable. The game must not rely on unpredictable roaming walkers.

### 10.6 Traffic and flow

High-throughput routes can congest. Flow networks may be directional or seasonally reversed. The player can build transfer hubs, bypasses and dedicated industrial routes. Congestion should become relevant only after the basic economy is understood.

---

## 11. Population, homes and social development

### 11.1 Population is housed, supplied and embodied

Population is not an abstract villager cap. Individuals belong to residences, consume needs, provide workforce and possess a morphology/caste. A household or colony-cluster is the accounting unit; individual organisms provide visual life and selected specialist control.

### 11.2 Residence evolution: the *Pharaoh* heart of the game

Residences evolve automatically when their district consistently supplies required goods, services and environmental quality. Inspection shows every satisfied and missing requirement.

Generic ladder:

| Stage | Social form | Core requirements | Economic result |
|---|---|---|---|
| I | Shelter cluster | safe solvent, staple feedstock | basic labour |
| II | Stable habitat | staple food, waste removal, maintenance | more residents and reliable labour |
| III | Symbiotic neighbourhood | varied nutrition, health service, local transport | specialist caste access |
| IV | Cultured district | refined household good, education/memory, civic access | administrative and technical workforce |
| V | Transcendent enclave | luxury ecology, environmental control, identity institution | research, diplomacy and great-work leadership |

Names and exact needs vary by biosphere; the economic relationship remains consistent.

### 11.3 Needs categories

- **Survival:** energy/feedstock, solvent balance, safe temperature.
- **Nutrition:** bulk nutrients, trace elements, dietary diversity.
- **Environment:** gas balance, waste removal, flow, pressure or insulation.
- **Health:** pathogen control, repair compounds, detoxification.
- **Reproduction:** nursery capacity, fertility compounds, genetic diversity.
- **Belonging:** communal space, memory, ritual or shared signalling.
- **Comfort:** pigments, scents, stimulants, crafted symbionts or aesthetic structures.
- **Purpose:** education, administration, research and civic participation.

Only a few needs are active at each stage. Complexity unfolds gradually.

### 11.4 Workforce strata

Higher residences provide different labour, not simply more efficient universal workers.

- **General organisms:** gathering, farming, carrying and basic construction.
- **Adapted labour castes:** mining, filtering, cultivation or hazardous work.
- **Artisans/processors:** operate multi-input workshops.
- **Analysts/caretakers:** health, surveying, education and environmental regulation.
- **Coordinators:** administration, trade, diplomacy and major projects.

The player may deliberately retain simple housing near farms and extraction sites. Universal upgrading is neither possible nor desirable.

### 11.5 Labour access

Buildings recruit from a district or transport network. A building without appropriate nearby workforce operates poorly or not at all. Workforce panels show demand, supply and commuting loss by caste.

### 11.6 Fertility and reproduction

Species fertility depends on:

- nursery capacity;
- metabolic surplus;
- limiting reproductive nutrients;
- habitat stability;
- health;
- compatible population/genetic diversity;
- selected morphology.

Population growth consumes real goods and time. A fertility collapse blocks growth before causing decline, giving the player time to respond.

### 11.7 Desirability and habitat quality

Advanced residences respond to local conditions:

Positive influences include gardens, clean flow, civic structures, protection, stable temperature, varied food and attractive bioluminescence. Negative influences include noise/vibration, toxins, waste, heavy extraction, dangerous reactants, congestion and disrepair.

Desirability should create recognisable residential and industrial districts without requiring modern zoning abstractions.

---

## 12. Farming and managed ecologies

### 12.1 Farms are ecosystems

A farm cultivates a biological or chemical cycle, not a generic food tile. Each crop/farm family specifies:

- suitable solvent and substrate;
- light, heat or chemical-energy input;
- bulk feedstock;
- limiting nutrients;
- growing season;
- harvest method;
- waste/by-product;
- crop rotation or recovery behaviour;
- contamination sensitivity.

### 12.2 Farm families

- photosynthetic membranes;
- microbial culture beds;
- filter gardens;
- grazing mats;
- protein colonies;
- structural fibre reefs;
- resin or wax secretors;
- medicinal symbiont nurseries;
- pigment/luxury cultures;
- nitrogen or nutrient fixers;
- catalyst-producing organisms.

### 12.3 Field placement

Farms use irregular field modules shaped by terrain, like floodplain farms rather than free-floating factories. Efficiency depends on connected suitable cells, access and seasonal exposure.

### 12.4 Soil/substrate improvement

Players can improve marginal patches through:

- adding limiting nutrients;
- altering pH or salinity;
- controlling water/solvent flow;
- inoculating symbionts;
- removing toxins;
- warming, shading or insulating;
- rotating cultivated ecologies;
- importing fertile sediment.

Improvement requires ongoing inputs or maintenance; it does not erase planetary geography.

### 12.5 Overexploitation

Aggressive harvest may reduce renewal, compact substrate, strip trace nutrients or trigger disease. Sustainable policy is not morally mandatory, but short-term extraction has legible long-term costs.

---

## 13. Evolution and morphology

### 13.1 Evolution is an economic commitment

An adaptation requires three things:

1. **Environmental pressure or opportunity:** repeated exposure reveals the adaptation path.
2. **Biological knowledge:** analysis, observation, symbiosis or prior morphology.
3. **Material investment:** fertility resources, specialist compounds and nursery capacity.

The result changes both capability and ongoing needs.

### 13.2 Morphology categories

- metabolism;
- feeding/extraction organs;
- locomotion;
- environmental tolerance;
- structural tissue;
- sensing;
- cognition/coordination;
- reproduction;
- symbiosis;
- signalling/culture.

### 13.3 Morphology unlocks verbs

| Morphology | Unlock | Cost/dependency |
|---|---|---|
| Filter crown | dissolved-resource collection | requires steady flow; vulnerable to fouling |
| Burrowing limbs | dig sediment and build tunnels | higher structural nutrient demand |
| Mineralised jaw | mine/cut hard deposits | continuous mineral and repair-compound upkeep |
| Photosynthetic sail | passive light-energy production | needs exposed area; fragile in storms |
| Chemosynthetic organ | exploit vent/redox patches | requires catalyst and detoxification |
| Gas bladder | vertical access and rapid transport | consumes membrane material; pressure sensitive |
| Armour plates | hazard resistance | slows movement; increases mineral demand |
| Vascular network | pipeline buildings and larger bodies | requires fluid balance and maintenance |
| Distributed ganglia | administration and coordinated logistics | high energy consumption |
| Spore cyst | survival through adverse seasons | slower active reproduction |

### 13.4 Species-wide traits and castes

Some adaptations change the whole species. Others create a specialised caste. Species-wide changes are rare and consequential; caste morphologies let the economy diversify without forcing every citizen into a mining body.

### 13.5 Adaptation pressure

The game records meaningful activity:

- filtering large volumes reveals filter improvements;
- mining hard material reveals mineralised tools;
- surviving low-oxygen periods reveals anaerobic or storage adaptations;
- running long trade routes reveals locomotion and navigation paths;
- repeated toxin exposure reveals detoxification.

Pressure reveals options; the player still chooses whether to invest.

### 13.6 Trade-offs and dependencies

No major morphology is a pure percentage upgrade. It introduces at least one new spatial, economic or ecological implication. The cost must be previewed before commitment.

### 13.7 Visible transformation

Organisms and buildings visibly express selected adaptations. Silhouettes, movement and work animations matter more than colour swaps. Settlement architecture inherits available body materials and construction behaviours.

---

## 14. Buildings and districts

### 14.1 Building families

- residences;
- nurseries;
- farms and managed ecologies;
- raw extraction;
- primary processing;
- advanced manufacturing;
- storage and logistics;
- environmental regulation;
- maintenance and hazard response;
- health and fertility;
- education/memory/research;
- trade and administration;
- culture/identity;
- defence and territorial control;
- great works.

### 14.2 Organic construction

Buildings may be grown, secreted, assembled, excavated or symbiotically inhabited. Construction still obeys understandable stages:

1. site prepared;
2. foundation or anchor established;
3. bulk structure delivered/grown;
4. specialist components installed;
5. organism/building matures and begins operation.

Builders and materials physically attend the site.

### 14.3 Building evolution

The principles in `EVOLVING_BUILDINGS.md` remain valuable but should be re-authored against this economy:

- residences evolve through supplied needs and local quality;
- production buildings gain mastery through throughput;
- civic buildings expand through deliberate investment;
- specialisation preserves the foundation building's function;
- visual stages grow from the existing silhouette.

### 14.4 Maintenance

Maintenance represents replacement tissue, structural repair, catalyst replenishment and environmental regulation. Neglect progresses through reduced efficiency, visible strain and dormancy before failure. The player may mothball buildings intentionally.

### 14.5 District identity

Districts emerge from networks, service reach and environmental conditions rather than being painted arbitrarily. The game may let the player name districts and set policies once administrative capacity exists.

Example policies:

- prioritise food deliveries;
- reserve local workforce;
- accept hazardous industry;
- maintain emergency stock;
- export surplus above threshold;
- protect ecological regeneration;
- maximise short-term extraction.

---

## 15. Services, institutions and belief

### 15.1 The alien equivalent of civic life

*Pharaoh*'s cities are held together by more than food and industry. Pondlife needs an alien civic layer with the same systemic role.

- **Maintenance:** prevents structural decay.
- **Health/detoxification:** manages disease, toxins and physiological stress.
- **Waste cycling:** keeps residential districts viable and recovers useful matter.
- **Nursery/fertility:** supports reproduction and caste development.
- **Learning/memory:** preserves techniques and unlocks advanced operation.
- **Coordination:** administers districts, policies and trade.
- **Culture/ritual:** produces belonging, identity and prestige.
- **Environmental stewardship:** stabilises farms, currents and atmospheric balance.

### 15.2 Belief without human gods by default

Civilisations may develop reverence around planetary cycles, ancestors, symbionts, stellar rhythms or the collective organism. These institutions are not mere happiness buffs. They organise festivals, maintain memory, legitimise great works and influence adaptation choices.

Different cultures may interpret the same chemistry differently. A vent may be a sacred ancestor, a civic utility or an exploitable industrial source.

### 15.3 Service delivery

Services may use:

- deterministic route coverage;
- district radius;
- network connection;
- scheduled visits;
- resident attendance.

Every service shows exactly which residences it reaches and why.

---

## 16. Trade, markets and value

### 16.1 Why trade exists

No region has ideal access to every limiting nutrient, catalyst, construction material and luxury ecology. Neighbouring societies may also possess different morphologies that make them efficient producers of particular goods.

Trade turns geographic inequality into strategic interdependence rather than a failure state.

### 16.2 Economic stages

#### Reciprocal exchange

Early colonies barter specified goods and maintain relationship obligations.

#### Accounted trade

Administrative institutions create a unit of account—energy equivalents, stored catalyst credits, shell tokens or another culture-specific representation. Currency is a coordination tool, not a raw natural resource.

#### Markets and contracts

Settlements post demand, negotiate quantities and establish recurring routes.

#### Investment

Surplus value can fund:

- new production capacity;
- expeditions and surveys;
- route infrastructure;
- ecological restoration;
- cultural institutions;
- adaptation programmes;
- great works;
- allied settlements.

### 16.3 Trade controls

For each good the player sets:

- import permission;
- export permission;
- desired reserve;
- maximum import price;
- minimum export price;
- route priority;
- emergency override.

The default interface uses simple reserve sliders; advanced pricing remains optional.

### 16.4 Traders and routes

Trade goods travel physically. Route capacity, season, hazard and travel time matter. A remote settlement can specialise, but relying on one fragile route creates risk.

### 16.5 Market consequences

Prices respond to authored regional supply and demand within bounded ranges. This is not a financial-market simulator. The purpose is to reward specialisation, timing and reliable supply.

### 16.6 Gifts, requests and obligations

Rivals may request scarce compounds, disaster relief, expertise or participation in a shared project. Responding affects trust, access and prestige. These fulfil the diplomatic role of kingdom requests in *Pharaoh* without merely reskinning them.

---

## 17. Rivals, territory and conflict

### 17.1 Rival civilisations obey chemistry

Rivals emerge from the same planetary rules but may possess different starting morphologies, cultural preferences and local resources. Their settlements should visibly specialise rather than receive invisible resource bonuses.

### 17.2 Territory

Territory is established through habitation, maintained routes, farms, extraction structures and civic markers. Claims are strongest near active infrastructure and weak across unused space.

### 17.3 Sources of tension

- overlapping extraction zones;
- control of a rare patch;
- pollution flowing across a boundary;
- competition for a trade contract;
- migration pressure;
- incompatible environmental engineering;
- prestige race;
- contested great-work site;
- predatory ecology or defensive misunderstanding.

### 17.4 Resolution

- negotiate access;
- trade substitutes;
- share or alternate seasonal use;
- buy rights;
- jointly remediate damage;
- demonstrate strength;
- construct barriers;
- deploy defenders;
- accept limited skirmish or predation.

Total annihilation should be rare, costly and outside the intended optimum.

### 17.5 Rival personalities

Personality axes include:

- extractive ↔ regenerative;
- insular ↔ mercantile;
- traditional ↔ adaptive;
- communal ↔ hierarchical;
- risk-averse ↔ expansionist;
- conciliatory ↔ territorial.

These determine observable policies rather than arbitrary hostility scores.

---

## 18. Environment, waste and ecological feedback

### 18.1 Production transforms the world

Industry changes local chemistry:

- consumes limiting nutrients;
- generates waste and heat;
- changes oxygenation/redox state;
- alters pH or solvent purity;
- diverts currents;
- shades or exposes habitats;
- creates new niches for organisms;
- concentrates toxic compounds.

### 18.2 Waste is a resource in the wrong place

Many by-products can later become feedstocks. Early settlements dump metabolic residue; advanced ones separate it into fertiliser, construction filler, fuel or trade goods. Circularity is economically useful but requires infrastructure.

### 18.3 Thresholds and warning

Environmental changes progress through visible thresholds. Before a collapse, the player sees reduced yields, stressed organisms, changing colour/behaviour and explicit warnings. Sudden hazards can occur, but chronic failure should not be mysterious.

### 18.4 Environmental strategies

- tolerate and adapt;
- relocate sensitive activity;
- treat or recycle waste;
- engineer local conditions;
- reduce output temporarily;
- import cleaner goods;
- cultivate remediation organisms;
- redesign the species.

There is no universal “green” path. A regenerative civilisation trades throughput and land use for stability; an extractive civilisation accepts higher remediation, trade and hazard costs.

---

## 19. Seasons, events and disasters

### 19.1 Predictable calendar

The dominant environmental cycle is forecast and integrated into normal planning. Players can view expected patch activation, farm yields, travel changes and hazard risk.

### 19.2 Variability

Actual intensity varies within a readable range. Forecasting institutions narrow uncertainty.

### 19.3 Event families

- solvent flood or retreat;
- drought/evaporation;
- freeze/thaw;
- vent surge;
- atmospheric storm;
- toxic bloom;
- disease or symbiont imbalance;
- predator migration;
- resource fall/deposition;
- rival migration;
- impact event;
- trade-route disruption.

### 19.4 Disaster response

Preparation uses reserves, robust routes, adapted bodies, protective infrastructure and diversified supply. Recovery creates work and may expose new resources. Disasters should rearrange priorities, not routinely erase a city.

---

## 20. Great works

### 20.1 Purpose

Great works are Pondlife's monuments: long projects that consume surplus production, reveal the city's logistical competence and permanently alter the skyline or environment.

### 20.2 Categories

- **Ecological:** restore a dead basin, create an artificial reef, stabilise an atmospheric cycle.
- **Civic:** memory reef, congress organism, archive lattice.
- **Infrastructure:** watershed-scale current network, pressure bridge, continent-spanning migration route.
- **Evolutionary:** planetary nursery, genome commons, symbiotic convergence chamber.
- **Scientific:** stellar observatory, atmosphere analyser, deep-core probe.
- **Transcendent:** surface breach, world-seed vessel, orbital spore launcher.

### 20.3 Construction

Great works are divided into visible stages with distinct material demands. They require bulk materials, specialist components, ordinary labour and elite coordination. Construction sites become major logistics destinations.

### 20.4 Meaning

A great work should resolve or express the mission's theme. A phosphate-starved civilisation might build a planetary nutrient recycler; a divided region might build a shared migration nexus. The end product is not only a score object.

---

## 21. Progression structure

The former fixed ten eras should be replaced by **development thresholds** shared across chemistries, with chemistry-specific content inside them.

### 21.1 Threshold I — Niche

- survive within one favourable patch;
- gather feedstock and one structural material;
- establish shelter, storage and nursery;
- discover the first limiting nutrient;
- select an initial metabolic strategy.

### 21.2 Threshold II — Settlement

- cultivate renewable feedstocks;
- create dependable logistics;
- evolve stable residences;
- support specialised extraction castes;
- manage a complete seasonal cycle.

### 21.3 Threshold III — Polity

- establish civic services and administration;
- process multi-input goods;
- trade with another settlement;
- manage distinct workforce strata;
- undertake a regional project.

### 21.4 Threshold IV — Industry

- refine materials and manufacture components;
- control significant environmental conditions;
- operate interdependent districts;
- manage pollution/by-products;
- compete for regional resources and trade.

### 21.5 Threshold V — Planetary civilisation

- connect multiple regions;
- support advanced morphologies and institutions;
- reshape planetary cycles deliberately;
- complete a planetary great work;
- choose a civilisational legacy.

Progress is measured by capabilities and institutions, not elapsed time or a single research currency.

---

## 22. Knowledge and discovery

### 22.1 No abstract science points as the sole gate

Knowledge comes from:

- surveying patches;
- operating industries;
- exposure to environmental conditions;
- studying native organisms;
- trade and diplomatic exchange;
- specialist institutions;
- experiments that consume materials;
- recovering rare samples.

### 22.2 Discovery sequence

1. Observe a phenomenon.
2. Identify its relevant conditions.
3. Run an experiment or accumulate practical mastery.
4. Reveal one or more applications.
5. Invest materials and workforce to institutionalise the technique.

### 22.3 Information as infrastructure

Early knowledge belongs locally to experienced organisms or buildings. Memory institutions preserve it against migration and disruption. Later communication networks allow settlement-wide policies and coordinated logistics.

---

## 23. Player interface and legibility

### 23.1 World-first information

The player should first see the city working: carriers move goods, farms change with season, processors display inputs, homes visibly mature, and waste accumulates. Panels explain what the world already communicates.

### 23.2 Overseers

Borrow *Pharaoh*'s principle of specialised management views. Proposed overseers:

- **Environment:** patch chemistry, fertility, pollution and forecasts.
- **Provisions:** farms, food variety, reserves and population consumption.
- **Industry:** production rates, inputs, outputs and bottlenecks.
- **Logistics:** stores, routes, carrier workload and congestion.
- **Population:** housing tiers, needs, migration, fertility and workforce.
- **Health:** toxins, disease, waste and physiological stress.
- **Evolution:** adaptation pressure, available morphologies and dependencies.
- **Trade:** routes, contracts, prices, reserves and partner relations.
- **Civic life:** services, culture, identity and district stability.
- **Projects:** construction queues, investments and great works.

### 23.3 Lenses

- chemistry;
- fertility by crop;
- extraction suitability;
- service coverage;
- desirability/habitat quality;
- logistics flow;
- workforce access;
- pollution and waste;
- territorial claim;
- seasonal risk.

### 23.4 Inspection contract

Every stalled entity answers:

- What is it trying to do?
- What does it need?
- Where should that input come from?
- Why has it not arrived?
- What happens if the problem continues?
- What are the player's plausible remedies?

### 23.5 Resource names

Alien flavour names must always carry a functional subtitle until learned:

```text
Tholin Floc
Atmospheric organic feedstock
```

The player may enable real/scientific notation in tooltips.

---

## 24. Mission and campaign design

### 24.1 Campaign purpose

The campaign teaches systemic relationships through distinct regional problems. It also tells the evolutionary history of one lineage as it encounters broader planetary scales.

### 24.2 Mission template

Each mission defines:

- a clear geographic premise;
- a chemistry/economy lesson;
- one primary scarcity;
- one seasonal or environmental rhythm;
- one social/civic challenge;
- available trade partners and rivals;
- a culminating project;
- optional prestige goals;
- recovery paths.

### 24.3 Example early campaign

#### Mission 1 — The Warm Margin

Learn basic gathering, storage, shelter and reproduction at the edge of a favourable pool. A drying cycle establishes the need for reserves.

#### Mission 2 — The Limiting Element

Abundant energy and carbon conceal a phosphate shortage. Survey sediment, establish washing and fertilise farms.

#### Mission 3 — Two Flows

Build separate residential and industrial currents. Introduce waste, desirability, deterministic distribution and evolving homes.

#### Mission 4 — The Other Colony

Meet a settlement adapted to a different local chemistry. Establish barter and specialise around complementary resources.

#### Mission 5 — Memory Reef

Support advanced residences and multiple workforce strata while constructing the first great work through seasonal disruption.

### 24.4 Scenario victory

Victory conditions should combine several ratings rather than one stockpile:

- population and habitat quality;
- prosperity and trade balance;
- ecological stability;
- knowledge/evolutionary capability;
- civic cohesion;
- great-work completion;
- regional obligations.

Optional goals reward alternative strategies and replay.

---

## 25. Failure and recovery

### 25.1 Soft failure ladder

1. Shortage warning.
2. Reduced residence satisfaction or industrial productivity.
3. Dormancy, stalled reproduction or service withdrawal.
4. Residence devolution and emigration.
5. Building abandonment or local ecological collapse.
6. Mission failure only after prolonged loss of viability or a failed explicit obligation.

### 25.2 Recovery tools

- emergency rationing;
- imports;
- substitute recipes;
- temporary building shutdown;
- salvage and relocation;
- migration to a viable patch;
- civic aid from allies;
- reversible caste conversion;
- lower-tier residences that remain functional;
- ecological remediation.

### 25.3 Honest difficulty

Higher difficulty increases tighter reserves, more demanding logistics, sharper seasonal variation and more capable rivals. It should not primarily grant rivals invisible income or hide information.

---

## 26. First playable vertical slice

The design must be proved with one polished economic puzzle, not a miniature version of the entire game.

### 26.1 Slice premise

One Verdant-water basin over one full seasonal cycle. The settlement must grow from a shelter cluster to a stable district and construct a Memory Reef foundation before a severe dry phase.

### 26.2 Map

- sunlit shallow suitable for photosynthetic farming;
- fertile sediment with varying phosphate content;
- silicate outcrop;
- carbonate reef;
- flowing channel containing suspended nutrients;
- anoxic basin containing valuable organics but causing stress;
- one neutral/rival settlement with a complementary resource;
- one external trade connection.

### 26.3 Raw resources

1. Photosynthetic biomass — renewable staple feedstock.
2. Phosphate sediment — limiting farm/fertility nutrient.
3. Suspended nutrient — filterable renewable input.
4. Silicate — finite construction/minufacturing mineral.
5. Carbonate — cuttable structural mineral.
6. Resin secretion — farmed sealant and civic good precursor.
7. Anoxic organics — high-value hazardous energy/chemical feedstock.
8. Pigment culture — optional luxury and export good.

This is deliberately more than three raw resources, but each enters through different geography and extraction.

### 26.4 Processed goods

1. Staple culture.
2. Growth nutrient.
3. Balanced nutrient gel.
4. Prepared silica.
5. Fired ceramic.
6. Woven fibre.
7. Cured resin.
8. Habitat composite.
9. Repair enzyme.
10. Pigment ornament.

### 26.5 Production chains

```text
Photosynthetic biomass → culture bed → staple culture
Phosphate sediment → washer → growth nutrient
Staple culture + growth nutrient → nutrient kitchen → balanced nutrient gel
Silicate → crusher/washery → prepared silica → kiln → fired ceramic
Fibre farm → retting pool → woven fibre
Resin grove → curing organ → cured resin
Woven fibre + cured resin + prepared silica → composite workshop → habitat composite
Culture waste → digester → repair enzyme + fertiliser by-product
Pigment culture → artisan organ → pigment ornament
```

### 26.6 Buildings

#### Survival and housing

- First Nursery
- Shelter Cluster
- Nutrient Store
- Maintenance Organ
- Waste Digester

#### Extraction and farming

- Photosynthetic Field
- Sediment Dredge
- Filter Crown
- Silicate Pit
- Carbonate Cutter
- Fibre Garden
- Resin Grove
- Anoxic Pump
- Pigment Bed

#### Processing

- Culture Bed
- Nutrient Washer
- Nutrient Kitchen
- Mineral Washery
- Ceramic Kiln
- Retting Pool
- Resin Curing Organ
- Composite Workshop
- Artisan Organ

#### Logistics and civic

- General Store
- Living-Goods Store
- Hazard Store
- Distribution Node
- Flow Channel
- Detox Clinic
- Memory Circle
- Survey Organ
- Trade Landing

#### Project

- Memory Reef Foundation

### 26.7 Residence ladder in the slice

| Residence | Needs | Workforce/result |
|---|---|---|
| Shelter Cluster | staple culture, maintenance | general labour |
| Stable Habitat | staple culture, waste service, clean flow | larger population, adapted labour |
| Symbiotic Neighbourhood | balanced nutrient gel, health, local distribution | artisans and analysts |
| Memory Enclave | habitat composite, pigment ornament, memory service | coordinators and project leadership |

### 26.8 Morphologies in the slice

- Filter Crown: operates Filter Crown buildings efficiently.
- Burrowing Limb: enables sediment dredging and silicate pits.
- Mineral Jaw: enables carbonate cutting and improves mining.
- Detox Sac: permits sustained work in the anoxic basin.
- Vascular Carrier: increases haul capacity and unlocks Flow Channels.
- Memory Ganglion: supplies analysts/coordinators and unlocks the Memory Reef.

The player cannot acquire all morphologies immediately. Caste slots and reproductive inputs force prioritisation.

### 26.9 Services

- maintenance;
- waste removal;
- clean flow/environment;
- health/detoxification;
- distribution;
- memory/learning.

### 26.10 Seasonal cycle

1. **Bloom:** high photosynthetic productivity, moderate flow.
2. **High water:** suspended nutrients abundant; low patches flood.
3. **Recession:** sediment extraction and farming peak.
4. **Dry phase:** farm output and clean flow decline; anoxic hazards intensify.

The scenario previews all four phases from the beginning.

### 26.11 Rival and trade

The neighbouring colony begins near a carbonate-rich reef but lacks good phosphate. It exports carbonate and buys growth nutrient. The player can trade, compete for the central silicate outcrop or invest in an expensive substitute ceramic recipe.

### 26.12 Great-work requirement

The Memory Reef Foundation consumes:

- bulk carbonate;
- fired ceramic;
- habitat composite;
- pigment ornament;
- repair enzyme;
- coordinator work cycles.

Its construction tests every major slice system without requiring a late-game tech tree.

### 26.13 Initial balancing targets

- First residence evolution within 12–18 minutes for a new player.
- First seasonal transition within 10 minutes.
- First complete two-stage production chain within 8 minutes.
- First trade opportunity within 25 minutes.
- Slice completion in 60–90 minutes on a first successful play.
- No more than five simultaneous urgent warnings.
- At least two viable solutions to every critical scarcity.

These are prototype targets, not final promises.

---

## 27. Second proof: the Haze variant

After the Verdant slice works, reuse its settlement systems with different chemistry.

The Haze variant must not merely rename goods. It should change:

- which patches are seasonally active;
- the source of metabolic energy;
- construction materials;
- farming shapes;
- storage requirements;
- dominant environmental hazards;
- available morphologies;
- which by-products are valuable;
- the rival's complementary specialisation.

Equivalent functional goals allow comparison:

| Function | Verdant solution | Haze solution |
|---|---|---|
| Staple energy | photosynthetic culture | hydrogen–acetylene catalytic culture |
| Bulk structure | carbonate/ceramic | ice composite/polymer |
| Flexible structure | fibre/resin | nitrile film/hydrocarbon polymer |
| Fertility limiter | phosphate/fixed nitrogen | accessible catalyst/trace inorganic input |
| Environmental control | oxygenation/clean flow | insulation/solvent retention |
| Seasonal opportunity | flood recession | methane rain/haze deposition |

If the two variants lead to different city layouts and priorities while remaining equally legible, the foundational premise is proven.

---

## 28. Procedural generation boundaries

### 28.1 Authored systems, generated arrangement

Procedural generation may arrange:

- terrain;
- patch placement and grade;
- flow networks;
- seasonal severity;
- rival starting regions;
- trade demand;
- rare anomalies.

It should not freely invent reactions, resource names or balance relationships. Those remain authored as chemistry modules.

### 28.2 Solvability pass

Every generated map is validated for:

- access to an opening energy/feedstock source;
- access to shelter material;
- at least one route to every mandatory limiting nutrient;
- a recovery substitute or trade route;
- seasonal refuge;
- viable logistics corridors;
- rival fairness;
- great-work feasibility.

### 28.3 Discovery without restart fishing

The player receives a coarse pre-settlement survey. Critical world facts are not concealed until hours into a save. Unknowns concern quality, rare opportunities and efficient techniques rather than whether the map is viable.

---

## 29. Data and implementation model

This section describes the required conceptual architecture, not a demand to retrofit the existing code.

### 29.1 Chemistry profile

```gdscript
{
  "id": "verdant_oxic_water",
  "solvent": "water",
  "atmosphere": {"n2": 0.72, "co2": 0.12, "o2": 0.15},
  "energy_regimes": ["visible_light", "redox", "geothermal"],
  "resource_modules": ["verdant_bulk", "silicate", "carbonate", "trace_metals"],
  "farm_families": ["photosynthetic", "filter", "culture"],
  "hazards": ["drying", "anoxia", "oxidative_bloom"]
}
```

Values are fictional game parameters rather than claims about a stable real atmosphere.

### 29.2 Resource definition

```gdscript
{
  "id": "phosphate_sediment",
  "family": "bulk_nutrient",
  "state": "environmental",
  "extraction_verbs": ["dig", "dredge"],
  "storage_class": "bulk_mineral",
  "renewability": "seasonal_deposition",
  "roles": ["fertiliser_input", "fertility_compound", "trade_good"]
}
```

### 29.3 Recipe definition

```gdscript
{
  "id": "wash_growth_nutrient",
  "building_tags": ["washer"],
  "inputs": {"phosphate_sediment": 2},
  "outputs": {"growth_nutrient": 1, "mineral_sludge": 1},
  "cycle_seconds": 20,
  "workforce": {"adapted_labour": 3},
  "environment": {"clean_flow": 1},
  "waste": {"turbidity": 2}
}
```

### 29.4 Patch definition

```gdscript
{
  "resource": "phosphate_sediment",
  "geometry": "sediment_bed",
  "grade": 0.75,
  "reserve": 1200,
  "renewal_rule": "high_water_deposition",
  "hazards": {"anoxia": 0.2},
  "seasonal_multipliers": {"recession": 1.4, "high_water": 0.0}
}
```

### 29.5 Morphology definition

```gdscript
{
  "id": "filter_crown",
  "revealed_by": {"filtered_volume": 200},
  "requirements": {"knowledge": "suspended_nutrients", "goods": {"growth_nutrient": 10}},
  "unlocks": ["filter_extraction", "filter_crown_building"],
  "modifiers": {"flow_filter_rate": 1.5},
  "dependencies": {"clean_flow": 1},
  "tradeoffs": {"fouling_sensitivity": 0.25}
}
```

### 29.6 Simulation separation

Keep these as separate but communicating systems:

- environmental field simulation;
- patches and regeneration;
- inventory and logistics;
- production recipes;
- population/needs/workforce;
- residence evolution;
- morphology and caste capability;
- services and district quality;
- trade;
- rivals;
- seasons/events;
- missions and scoring.

Avoid placing every rule inside entity scripts. A headless deterministic economy simulation should run without rendering.

---

## 30. Scope discipline

### 30.1 Do not build yet

- ten progression eras;
- five fully realised world zones;
- arbitrary procedural chemistry;
- multiplayer;
- spaceflight;
- a free-form creature editor;
- complex combat;
- a global commodity exchange;
- dozens of crops per chemistry;
- realistic fluid or atmospheric simulation;
- every proposed overseer;
- final art for unproven production chains.

### 30.2 Build first

- one map with meaningful chemical geography;
- eight raw resources with distinct extraction;
- ten processed goods;
- visible transport and specialised storage;
- four residence tiers;
- six services;
- six economically grounded morphologies;
- one predictable seasonal cycle;
- one trade partner/rival;
- one great-work foundation;
- excellent inspection and bottleneck explanation.

### 30.3 Reuse from the current prototype selectively

Potentially reusable:

- Godot camera and selection experiments;
- environmental rendering studies;
- data-driven content lessons;
- resource depletion/regrowth concepts;
- residence evolution principles;
- visual adapter idea;
- testing patterns;
- selected art-direction work.

Do not assume compatibility is more valuable than clarity. Port a component only after the new slice establishes the interface it needs.

---

## 31. Design tests

The vertical slice succeeds only if playtesting supports these statements:

### World and chemistry

- Players can explain why major resources occur where they do.
- Fertility differences change farm placement.
- The season changes plans in advance rather than merely causing surprise losses.

### Economy

- Players can trace a finished good back through its chain.
- At least one shortage is solved through logistics rather than more extraction.
- Different storage and transport choices create visibly different outcomes.
- Surplus goods have meaningful uses through trade, reserves, investment or projects.

### Settlement

- Residence evolution feels caused by the city, not by a timer.
- Industrial and residential districts emerge for understandable reasons.
- Higher-tier population feels valuable and demanding.
- The player can diagnose why a residence or workshop is stalled.

### Evolution

- Morphologies change available economic actions.
- At least one adaptation changes city layout.
- Players understand an adaptation's dependency before choosing it.
- Different players develop meaningfully different caste mixes on the same map.

### Identity

- Players describe the game as an alien city-builder rather than an RTS with pond graphics.
- The experience evokes *Pharaoh* through relationships, pacing and city readability.
- Players want to see how a chemically different planet changes the economy.

---

## 32. Open questions requiring prototypes

1. Should carriers be individual simulated organisms, aggregated route traffic, or a hybrid by camera scale?
2. How many active goods can players comfortably manage before the first advanced residence tier?
3. Should residence goods be physically distributed to each home or consumed from a serviced market inventory?
4. How strongly should morphology constrain workforce compared with buildings and training?
5. Can local chemical fields update cheaply enough at city scale, or should patches use cached discrete values?
6. How much direct unit control improves the opening before it becomes city-builder friction?
7. Does currency add useful planning, or are stock, barter and civic investment sufficient until later progression?
8. How should spiritual/cultural identity emerge without mapping alien societies too directly onto human institutions?
9. How visible should individual birth, death and migration be?
10. What is the correct balance between scientific terminology and immediate comprehension?

---

## 33. Working glossary

- **Chemistry profile:** authored planetary ruleset defining possible resources, farms, reactions and adaptations.
- **Patch:** spatially bounded environmental concentration or formation that supports extraction or cultivation.
- **Fertility:** crop-specific suitability produced by substrate, solvent, energy and limiting nutrients.
- **Feedstock:** raw matter consumed by a metabolic or industrial reaction.
- **Gradient:** exploitable difference in chemical state, heat, light, pressure or concentration.
- **Morphology:** inherited body capability that changes economic actions or environmental tolerance.
- **Caste:** specialised population morphology within the broader species.
- **Service:** maintained civic function delivered to buildings or residences.
- **Habitat quality:** local environmental and civic suitability for residence development.
- **Great work:** multi-stage civilisational project consuming sustained city-wide output.
- **Verdant:** working name for the oxygenated water-world chemistry archetype.
- **Haze:** working name for the reducing hydrocarbon-world chemistry archetype.

---

## 34. Research basis and further reading

These references inform the design direction; they are not authorities for every speculative game mechanic.

### City-building references

- [*Pharaoh* manual](https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/564530/manuals/Pharaoh_-_manual.pdf?t=1481822384) — city sites, roads, housing evolution, desirability, farming, distribution, commerce, trade, health, monuments, ratings and kingdom service.
- [*Anno 1800* official overview](https://www.anno-union.com/games/anno-1800-lead-the-industrial-revolution/) — production chains, workforce, logistics, trade routes, expeditions and regional settlement.
- [Anno Union: “Treasures of the Soil”](https://www.anno-union.com/devblog-treasures-of-the-soil/) — deposits, fertility and their relationship to production-chain planning.
- [Official *Age of Empires IV* civilisation overview](https://www.ageofempires.com/games/age-of-empires-iv/civilizations/english/) — age progression, economic development, farms and resource competition.

### Astrobiology and planetary chemistry

- [NASA: Titan overview](https://science.nasa.gov/mission/cassini/science/titan/) — nitrogen-rich atmosphere, methane/ethane lakes, hydrocarbon cycle, water ice and organic dunes.
- [NASA Astrobiology: The Habitability of Titan and its Ocean](https://astrobiology.nasa.gov/news/the-habitability-of-titan-and-its-ocean/) — atmospheric photochemistry, complex organics and potential subsurface habitats.
- [NASA: Research Shows Path Toward Protocells on Titan](https://science.nasa.gov/science-research/planetary-science/astrobiology/path-toward-protocells-on-titan/) — current speculative work on vesicles in hydrocarbon lakes and the limits of present knowledge.
- [NASA technical report: *Titan as the Abode of Life*](https://ntrs.nasa.gov/api/citations/20160006882/downloads/20160006882.pdf?attachment=true) — possible chemical-energy sources, environmental limitations and speculative carbon-based life in liquid methane/ethane.
- [NASA: What is a biosignature?](https://science.nasa.gov/astrobiology/learning-resources/alp/what-is-a-biosignature/) — matter/energy flow, atmospheric chemistry and biosphere–planet feedback.

---

## 35. Immediate next decision

The next design pass should specify the Verdant vertical slice as a playable economy sheet:

- exact building recipes and cycle times;
- workforce requirements;
- residence consumption rates;
- farm yields by season and fertility;
- carrier capacity and travel assumptions;
- storage limits;
- morphology costs;
- trade quantities;
- Memory Reef stage costs;
- a paper balance simulation for 90 minutes of play.

Only after that paper economy produces interesting shortages, surpluses and recovery choices should implementation begin.
