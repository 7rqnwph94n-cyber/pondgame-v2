"""The playable opening must be an empty, funded settlement, not a hidden ready-made city."""
import unittest
from economy.bridge import Session
from economy.engine import load_definitions

OVERLAYS = ['economy/data/experiments/candidate_playable_slice_v1.json',
            'economy/data/experiments/empty_settlement_start_v1.json']
OPENING = ['shelter'] * 3 + ['photosynthetic_field', 'culture_bed', 'first_nursery',
           'general_store', 'maintenance_organ', 'survey_organ', 'clean_flow_node', 'waste_collector']

class EmptyStartTests(unittest.TestCase):
    def test_empty_initial_view_and_exact_budget(self):
        s = Session(OVERLAYS)
        v = s.view()
        self.assertEqual((v['facilities'], v['residences'], v['sites']), ({}, {}, {}))
        self.assertEqual(v['population'], 0)
        self.assertEqual(s.sim.founders_remaining, 24)
        for good, count in s.defs['starting_state']['inventory'].items():
            self.assertEqual(v['store'][good], count)
        self.assertAlmostEqual(v['food_minutes'], 40 / .6)

    def test_budget_funds_real_opening_and_survives_first_season(self):
        s = Session(OVERLAYS)
        for i, building in enumerate(OPENING):
            self.assertTrue(s.command({'do': 'construct', 'building': building, 'id': f'opening_{i}'})['ok'])
        s.advance(600)
        self.assertEqual(len(s.sim.residences), 3)
        self.assertEqual(len(s.sim.facilities), 8)
        self.assertEqual(s.sim.founders_remaining, 0)
        self.assertEqual(s.view()['population'], 24)
        for _ in range(8): s.advance(600)
        self.assertEqual(s.sim.food_emergency.seconds_active, 0)
        self.assertGreater(s.view()['food_minutes'], 20)
        self.assertTrue(all(n >= 0 for n in s.view()['store'].values()))

    def test_founders_do_not_duplicate_on_landing(self):
        s = Session(OVERLAYS)
        before = s.sim.workforce_supply('core')['general']
        s.command({'do': 'construct', 'building': 'shelter', 'id': 'first_home'})
        s.advance(60)
        self.assertEqual(s.sim.residences['first_home'].population, 8)
        self.assertEqual(s.sim.founders_remaining, 16)
        self.assertEqual(sum(r.population for r in s.sim.residences.values()) + s.sim.founders_remaining, 24)
        self.assertEqual(s.sim.workforce_supply('core')['general'], before)

    def test_waiting_founders_eat_and_cannot_work_without_food(self):
        s = Session(OVERLAYS)
        s.advance(600)
        self.assertLess(s.view()['store']['staple'], 40)
        s.sim.store('core').take({'staple': s.sim.store('core').get('staple')})
        s.sim.founder_food_buffer = 0
        s.advance(1)
        self.assertTrue(s.sim.founder_food_shortage)
        self.assertEqual(s.sim.workforce_supply('core')['general'], 0)

    def test_original_slice_start_is_unchanged(self):
        original = load_definitions(overlays=OVERLAYS[:1])
        self.assertEqual(len(original['starting_state']['buildings']), 6)
        self.assertEqual(len(original['starting_state']['residences']), 3)
        self.assertFalse(original['buildings']['first_nursery']['constructible'])
        self.assertNotIn('founding_party', original['starting_state'])

    def test_autoplay_constructs_foundation_instead_of_spawning_it(self):
        s = Session(OVERLAYS)
        s.autoplay(True)
        self.assertFalse(s.sim.facilities)
        self.assertFalse(s.sim.residences)
        for _ in range(3): s.advance(600)
        self.assertTrue(any(f.building_id == 'first_nursery' for f in s.sim.facilities.values()))
        self.assertEqual(s.sim.founders_remaining, 0)
        self.assertEqual(s.sim.food_emergency.seconds_active, 0)

    def test_opening_budget_also_supports_first_stable_home(self):
        s = Session(OVERLAYS)
        for i, building in enumerate(OPENING):
            s.command({'do': 'construct', 'building': building, 'id': f'opening_{i}'})
        s.advance(600)
        self.assertTrue(s.command({'do': 'evolve', 'residence': 'opening_0'})['ok'])
        for _ in range(3): s.advance(600)
        self.assertEqual(s.sim.residences['opening_0'].tier, 'stable')
        self.assertEqual(s.sim.food_emergency.seconds_active, 0)
