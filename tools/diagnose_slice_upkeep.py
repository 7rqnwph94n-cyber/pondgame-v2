"""Trace unchanged slice rules; compare bounded, legal player actions at 120:00."""
import json
import sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from economy.engine import Simulation
from economy.engine.definitions import load_definitions
from economy.governor import Governor, load_governor_config
from economy.sweep import summarise


def run(label, extra_digesters=0, priority=None):
    defs = load_definitions(overlays=[ROOT / 'economy/data/experiments/candidate_playable_slice_v1.json'])
    defs['scenario']['duration_seconds'] = 14400
    sim = Simulation(defs, {'id': label, 'commands': []})
    governor = Governor(load_governor_config(ROOT / 'economy/data/governors/reference_governor_v3.json'))
    sim.controllers.append(governor)
    snapshots, actions, states = [], [], Counter()
    nominal_demand = 0.0
    first_unpaid = None
    for second in range(14401):
        if second == 7200:
            commands = [{'do': 'construct', 'building': 'waste_digester', 'id': f'diagnosis_digester_{n}', 'priority': 28}
                        for n in range(1, extra_digesters + 1)]
            if priority is not None:
                commands.append({'do': 'set_labour_priority', 'target': 'waste_digester_1', 'value': priority})
            for cmd in commands:
                result = sim.issue(cmd, source='player')
                actions.append({'second': second, 'command': cmd, 'ok': result.ok, 'result': result.info if result.ok else result.reasons})
        sim.step()
        if sim.upkeep.grace_ended_at is not None:
            nominal_demand += sim.diag.maintenance_weight() * sim.upkeep.rules['enzyme_per_weight_per_minute'] / 60
        if sim.upkeep.state == 'unpaid' and first_unpaid is None:
            first_unpaid = second
        digesters = [f for f in sim.facilities.values() if f.building_id == 'waste_digester']
        for f in digesters:
            states[f.id + ':' + f.status] += 1
        if second % 600 == 0 or second == first_unpaid or second == sim.upkeep.grace_ended_at:
            rows = []
            for f in digesters:
                recipe = defs['recipes'][f.recipe_id]
                rows.append({'entity': f.id, 'commissioned_at': f.commissioned_at, 'staffing': f.staffing,
                             'status': f.status, 'cycles': f.completed_cycles, 'paused': f.paused,
                             'nominal_enzyme_per_minute': recipe['outputs']['repair_enzyme'] * 60 / recipe['cycle_seconds']})
            snapshots.append({'second': second, 'maintenance_weight': sim.diag.maintenance_weight(),
                              'demand_per_minute': sim.diag.maintenance_weight() * sim.upkeep.rules['enzyme_per_weight_per_minute'],
                              'enzyme_stock': sim.store(sim.districts[0]).get('repair_enzyme'),
                              'organic_waste_stock': sim.store(sim.districts[0]).get('organic_waste'),
                              'fired_ceramic_stock': sim.store(sim.districts[0]).get('fired_ceramic'),
                              'biomass_stock': sim.store(sim.districts[0]).get('biomass'),
                              'ceramic_kilns': [{'entity': f.id, 'status': f.status, 'paused': f.paused, 'staffing': f.staffing,
                                                'recipe': f.recipe_id, 'inputs': defs['recipes'][f.recipe_id].get('inputs', {})}
                                               for f in sim.facilities.values() if f.building_id == 'ceramic_kiln'],
                              'upkeep_paid': sim.upkeep.paid, 'upkeep_unpaid_minutes': round(sim.upkeep.unpaid_seconds / 60, 2),
                              'state': sim.upkeep.state, 'digesters': rows})
    report = sim.diag.build_report()
    return {'label': label, 'actions': actions, 'first_unpaid_second': first_unpaid,
            'nominal_demand_after_grace': round(nominal_demand, 2), 'summary': summarise(report),
            'digester_state_seconds': dict(states), 'snapshots': snapshots,
            'sites': {sid: {'target': s.target, 'state': s.state, 'missing': s.missing()} for sid, s in sim.sites.items()},
            'upkeep_events': [e for e in sim.events if 'maintenance upkeep' in e],
            'kiln_governor_actions': [entry for entry in governor.log if 'ceramic_kiln' in str(entry)]}


def main():
    rows = [run('reference'), run('staff existing digester first', priority=3),
            run('build one additional digester at 120:00', extra_digesters=1),
            run('build two additional digesters at 120:00', extra_digesters=2)]
    reference = json.loads((ROOT / 'docs/milestone_a/SLICE_EXTENDED_HORIZON_2026-10-05.json').read_text())[-1]
    for key, value in rows[0]['summary'].items():
        assert value == reference[key], (key, value, reference[key])
    assert rows[0]['first_unpaid_second'] == 8189
    target = ROOT / 'docs/milestone_a/UPKEEP_DIAGNOSIS_2026-10-05.json'
    target.write_text(json.dumps(rows, indent=2) + '\n')
    for row in rows:
        print(json.dumps({k: row[k] for k in ('label', 'first_unpaid_second', 'summary', 'sites', 'actions')}))


if __name__ == '__main__':
    main()
