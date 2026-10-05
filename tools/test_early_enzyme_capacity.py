"""Bounded legal-action scheduling comparison; no economy rules change."""
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from economy.engine import Simulation
from economy.engine.definitions import load_definitions
from economy.governor import Governor, load_governor_config
from economy.player_view import observe
from economy.sweep import summarise


class CapacityPlan:
    def __init__(self, at, protect_food_minutes=None, max_paused=None):
        self.max_paused = max_paused
        self.at = at
        self.threshold = protect_food_minutes
        self.ordered = False
        self.paused = set()
        self.prioritised = set()
        self.actions = []
        self.completed_at = None

    def issue(self, sim, cmd, why):
        result = sim.issue(cmd, source='player')
        self.actions.append({'second': sim.second, 'command': cmd, 'why': why, 'ok': result.ok,
                             'result': result.info if result.ok else result.reasons})
        return result.ok

    def act(self, sim):
        if self.at is None or sim.second % 10 or sim.second < self.at:
            return
        view = observe(sim)
        # Wait for the reference governor's first digester order; preserve three total.
        original = any(f['building'] == 'waste_digester' for f in view['facilities'].values()) or any(
            s['target'] == 'waste_digester' for s in view['sites'].values())
        if not self.ordered and original:
            ok = []
            for n in (1, 2):
                ok.append(self.issue(sim, {'do': 'construct', 'building': 'waste_digester',
                                          'id': f'early_digester_{n}', 'priority': 10}, 'order extra paid Enzyme capacity'))
            self.ordered = all(ok)
        digesters = [f for f in view['facilities'].values() if f['building'] == 'waste_digester']
        done = len(digesters) >= 3
        if done and self.completed_at is None:
            self.completed_at = sim.second
            for fid in sorted(self.prioritised):
                self.issue(sim, {'do': 'set_labour_priority', 'target': fid, 'value': None}, 'restore normal kiln priority after capacity construction')
        if self.threshold is None:
            return
        food = view['food_minutes'] or 0
        emergency = view['food_emergency']
        # Player-visible hysteresis: reserve Biomass when food >= threshold; restore
        # food production at 15 minutes or any emergency. Never alter stocks/rules.
        for fid in sorted(self.paused.copy()):
            if done or emergency or food <= 15:
                if self.issue(sim, {'do': 'resume', 'target': fid}, 'restore food production'):
                    self.paused.remove(fid)
        if done or not self.ordered or emergency or food < self.threshold:
            return
        for fid, f in sorted(view['facilities'].items()):
            if f['building'] == 'culture_bed' and not f['paused'] and (self.max_paused is None or len(self.paused) < self.max_paused):
                if self.issue(sim, {'do': 'pause', 'target': fid}, 'temporarily reserve Biomass for Ceramic; food buffer sufficient'):
                    self.paused.add(fid)
            if f['building'] == 'ceramic_kiln' and fid not in self.prioritised:
                if self.issue(sim, {'do': 'set_labour_priority', 'target': fid, 'value': 3}, 'staff the construction-material chain first'):
                    self.prioritised.add(fid)


def run(label, at=None, food=None, max_paused=None):
    defs = load_definitions(overlays=[ROOT / 'economy/data/experiments/candidate_playable_slice_v1.json'])
    defs['scenario']['duration_seconds'] = 14400
    sim = Simulation(defs, {'id': label, 'commands': []})
    governor = Governor(load_governor_config(ROOT / 'economy/data/governors/reference_governor_v3.json'))
    plan = CapacityPlan(at, food, max_paused)
    sim.controllers.extend([governor, plan])
    first_unpaid = None
    snapshots = []
    for t in range(14401):
        sim.step()
        if sim.upkeep.state == 'unpaid' and first_unpaid is None:
            first_unpaid = t
        if t % 600 == 0 or t == sim.upkeep.grace_ended_at:
            v = observe(sim)
            snapshots.append({'second': t, 'food_minutes': v['food_minutes'], 'biomass': v['store'].get('biomass', 0),
                              'enzyme': v['store'].get('repair_enzyme', 0), 'ceramic': v['store'].get('fired_ceramic', 0),
                              'maintenance_weight': sim.diag.maintenance_weight(),
                              'demand_per_minute': sim.diag.maintenance_weight() * sim.upkeep.rules['enzyme_per_weight_per_minute'],
                              'digesters': [{'entity': f.id, 'commissioned_at': f.commissioned_at, 'staffing': f.staffing,
                                            'status': f.status, 'cycles': f.completed_cycles}
                                           for f in sim.facilities.values() if f.building_id == 'waste_digester']})
    summary = summarise(sim.diag.build_report())
    return {'label': label, 'order_at': at, 'food_pause_threshold_minutes': food, 'max_paused_culture_beds': max_paused, 'summary': summary,
            'grace_ended_at': sim.upkeep.grace_ended_at, 'three_commissioned_at': plan.completed_at,
            'first_unpaid_second': first_unpaid, 'actions': plan.actions, 'snapshots': snapshots,
            'upkeep_events': [e for e in sim.events if 'maintenance upkeep' in e],
            'failed_plan_actions': sum(not a['ok'] for a in plan.actions)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed evidence without rewriting it")
    args = parser.parse_args()
    rows = [run('reference'), run('60 min: orders only', 3600),
            run('60 min: protect Biomass above 30 food minutes', 3600, 30),
            run('80 min: protect Biomass above 30 food minutes', 4800, 30),
            run('60 min: protect Biomass above 45 food minutes', 3600, 45),
            run('70 min: orders only', 4200), run('80 min: orders only', 4800),
            run('80 min: protect Biomass above 45 food minutes', 4800, 45),
            run('80 min: protect above 30 food minutes; pause at most one bed', 4800, 30, 1)]
    old = json.loads((ROOT / 'docs/milestone_a/UPKEEP_DIAGNOSIS_2026-10-05.json').read_text())[0]
    assert rows[0]['summary'] == old['summary']
    assert rows[0]['first_unpaid_second'] == old['first_unpaid_second']
    selected = rows[-1]
    for key in ('upkeep_unpaid_minutes', 'food_emergency_minutes', 'staple_shortage_minutes', 'devolutions'):
        assert selected['summary'][key] == 0, (key, selected['summary'][key])
    assert selected['three_commissioned_at'] < selected['grace_ended_at']
    assert selected['failed_plan_actions'] == 0
    assert selected['summary']['first_symbiotic'] == '115:39'
    target = ROOT / 'docs/milestone_a/EARLY_ENZYME_CAPACITY_2026-10-05.json'
    content = json.dumps(rows, indent=2) + '\n'
    if args.check:
        assert target.read_text() == content, 'committed evidence differs from reproduction'
    else:
        target.write_text(content)
    for row in rows:
        print(json.dumps({k: row[k] for k in ('label', 'summary', 'three_commissioned_at', 'grace_ended_at', 'first_unpaid_second', 'failed_plan_actions')}))


if __name__ == '__main__':
    main()
