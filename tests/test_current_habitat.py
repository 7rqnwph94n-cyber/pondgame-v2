"""Submerged current habitat (Rich 'go' to the underwater correction, Codex 1924Z request).

Optional overlay current_lanes_v1 on top of spatial_roads_v1: no water/bank exclusion, shared natural
obstacles and footprints, intake spurs, light and extraction-zone suitability, and services that reach homes
only by lane distance. The v4 roads mode and every non-spatial scenario stay as they were.
"""
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

from economy.bridge import Session, handle, residence_blockers
from economy.engine import Simulation, load_definitions

ROOT = Path(__file__).resolve().parents[1]
ROADS = ['economy/data/experiments/candidate_playable_slice_v1.json',
         'economy/data/experiments/empty_settlement_start_v1.json',
         'economy/data/experiments/spatial_roads_v1.json']
CURRENT = ROADS + ['economy/data/experiments/current_lanes_v1.json']
PLAN = json.loads((ROOT / "economy/data/plans/current_opening_v1.json").read_text())
MAIN = [[-64, -2], [-20, -2]]
HALF_PI = math.pi / 2


def make_sim(overlays=CURRENT, work=None):
    defs = load_definitions(overlays=[ROOT / o for o in overlays])
    if work is not None:
        for building in defs["buildings"].values():
            if "work" in building:
                building["work"] = work
    sim = Simulation(defs, {"id": "test", "commands": []})
    sim.step()
    return sim


def issue(sim, cmd):
    return sim.issue(cmd, source="test")


def run(sim, seconds):
    for _ in range(seconds):
        sim.step()


class HabitatLegalityTests(unittest.TestCase):
    def test_shared_geometry_is_loaded(self):
        sim = make_sim()
        self.assertEqual(sim.spatial.mode, "current")
        self.assertEqual(len(sim.spatial.obstacles), 26)
        self.assertEqual(sim.spatial.footprint_for("photosynthetic_field", None), (9.0, 7.0))

    def test_no_blanket_water_ban(self):
        roads, current = make_sim(ROADS), make_sim()
        across = [[-30, -2], [-20, -2], [-10, -2], [2, -2]]          # crosses the old channel bed
        self.assertEqual(issue(roads, {"do": "build_road", "points": across}).reasons, ["spatial:water"])
        self.assertTrue(issue(current, {"do": "build_road", "points": across}).ok)
        # Lanes still respect substrate grade: the escarpment face is too steep to climb straight.
        self.assertEqual(issue(current, {"do": "build_road", "points": [[2, -2], [2, -20], [30, -20]]}).reasons,
                         ["spatial:too_steep"])

    def test_natural_obstacles_block_buildings_and_lanes(self):
        sim = make_sim()
        issue(sim, {"do": "build_road", "points": MAIN})
        rock = [[-41, -2], [-41, 25]]                                    # through the rock at (-41, 13.8)
        self.assertEqual(issue(sim, {"do": "build_road", "points": rock}).reasons, ["spatial:obstacle"])
        r = issue(sim, {"do": "construct", "building": "shelter", "position": [-41, 6], "yaw": math.pi})
        self.assertEqual(r.reasons, ["spatial:obstacle"])

    def test_intake_spur_may_not_cross_rock(self):
        sim = make_sim()
        issue(sim, {"do": "build_road", "points": MAIN})
        ok = {"do": "construct", "building": "shelter", "position": [-40, -7.5], "dry_run": True}
        self.assertTrue(issue(sim, ok).ok)
        sim.spatial.obstacles.append(((-40.0, -2.6), (1.0, 0.6)))     # a small rock between intake and lane
        self.assertEqual(issue(sim, ok).reasons, ["spatial:spur_blocked"])
        self.assertTrue(sim.spatial._spur_blocked((-40, -3), (-40, -2)))

    def test_light_is_sampled_at_the_field(self):
        sim = make_sim()
        issue(sim, {"do": "build_road", "points": MAIN})
        bright = issue(sim, {"do": "construct", "building": "photosynthetic_field", "id": "f",
                             "position": [-25, -7.5], "dry_run": True})
        self.assertTrue(bright.ok)
        light = bright.data["suitability"]["light"]
        h = sim.spatial.terrain.height(-25, -7.5)
        self.assertAlmostEqual(light, round((h + 1.0) / 2.2, 3), places=3)
        dark = issue(sim, {"do": "construct", "building": "photosynthetic_field", "position": [-36, 26]})
        self.assertTrue(dark.reasons[0].startswith("spatial:too_dark:"), dark.reasons)

    def test_light_scales_field_output(self):
        def biomass(position):
            sim = make_sim(work=1)
            issue(sim, {"do": "build_road", "points": [[-64, -2], [-20, -2], [-20, 30]]})
            issue(sim, {"do": "construct", "building": "shelter", "id": "h", "position": [-50, -7.5]})
            issue(sim, {"do": "construct", "building": "photosynthetic_field", "id": "f", **position})
            run(sim, 1800)
            return sim.diag.produced.get("biomass", 0), sim.spatial.placements["f"].suitability["light"]
        lit, lit_light = biomass({"position": [-25, -7.5]})
        dim, dim_light = biomass({"position": [-25, 10], "yaw": HALF_PI})
        self.assertGreater(lit_light, dim_light)
        self.assertGreater(lit, dim)

    def test_silicate_pits_need_the_published_zone(self):
        sim = make_sim()
        issue(sim, {"do": "build_road", "points": MAIN})
        self.assertTrue(issue(sim, {"do": "build_road", "points": [[-20, -2], [18, -10], [22, -18], [28, -26], [28, -40], [42, -50]]}).ok)
        outside = issue(sim, {"do": "construct", "building": "silicate_pit", "position": [60, -50]})
        self.assertEqual(outside.reasons, ["spatial:outside_extraction_zone:silicate_pit"])
        inside = issue(sim, {"do": "construct", "building": "silicate_pit", "position": [42, -55.5], "dry_run": True})
        self.assertTrue(inside.ok, inside.reasons)
        self.assertEqual(inside.data["suitability"], {"zone": "silica_exposure"})
        zone = sim.spatial.rules["geography"]["extraction_zones"][0]
        self.assertLessEqual(math.dist((42, -55.5), zone["centre"]), zone["radius"])


class LocalServiceTests(unittest.TestCase):
    def setUp(self):
        self.sim = make_sim(work=1)
        sim = self.sim
        issue(sim, {"do": "build_road", "points": MAIN})
        issue(sim, {"do": "build_road", "points": [[-20, -2], [-20, 40]]})
        issue(sim, {"do": "construct", "building": "shelter", "id": "near", "position": [-50, -7.5]})
        issue(sim, {"do": "construct", "building": "shelter", "id": "far", "position": [-15.5, 36], "yaw": -HALF_PI})
        issue(sim, {"do": "construct", "building": "shelter", "id": "mid", "position": [-34, -7.5]})
        issue(sim, {"do": "construct", "building": "clean_flow_node", "id": "flow", "position": [-58, -7.5]})
        run(sim, 300)

    def test_coverage_is_by_lane_distance_with_no_district_fallback(self):
        sim = self.sim
        self.assertIn("flow", sim.facilities)
        near = sim.spatial.coverage["near"]["clean_flow"]
        far = sim.spatial.coverage["far"]["clean_flow"]
        self.assertTrue(near["covered"])
        self.assertEqual(near["provider"], "flow")
        self.assertFalse(far["covered"])
        self.assertEqual(far["provider"], "flow")
        self.assertGreater(far["distance"], far["range"])
        self.assertIn("clean_flow", sim.services["core"])                 # available somewhere...
        self.assertIn("clean_flow", sim.services_for(sim.residences["near"]))
        self.assertNotIn("clean_flow", sim.services_for(sim.residences["far"]))   # ...but not at the far home
        blocker = [b for b in residence_blockers(sim, sim.residences["far"]) if b["params"].get("service") == "clean_flow"][0]
        self.assertEqual(blocker["params"]["provider"], "flow")
        self.assertGreater(blocker["params"]["distance"], blocker["params"]["range"])

    def test_distance_is_exact_lane_distance(self):
        sim = self.sim
        flow, near = sim.spatial.placements["flow"], sim.spatial.placements["near"]
        expected = math.dist(flow.entrance, flow.attach) + math.dist(flow.attach, near.attach) + math.dist(near.attach, near.entrance)
        self.assertAlmostEqual(sim.spatial.coverage["near"]["clean_flow"]["distance"], round(expected, 2), places=2)
        self.assertEqual(sim.spatial.reach["flow"]["homes"], ["mid", "near"])

    def test_a_second_provider_moves_coverage(self):
        sim = self.sim
        issue(sim, {"do": "construct", "building": "clean_flow_node", "id": "flow_east", "position": [-15.5, 28], "yaw": -HALF_PI})
        run(sim, 300)
        far = sim.spatial.coverage["far"]["clean_flow"]
        self.assertTrue(far["covered"])
        self.assertEqual(far["provider"], "flow_east")

    def test_pausing_the_provider_removes_coverage(self):
        sim = self.sim
        issue(sim, {"do": "pause", "target": "flow"})
        run(sim, 2)
        self.assertFalse(sim.spatial.coverage["near"]["clean_flow"]["covered"])
        self.assertNotIn("clean_flow", sim.services_for(sim.residences["near"]))

    def test_preview_plans_service_placement(self):
        sim = self.sim
        home = issue(sim, {"do": "construct", "building": "shelter", "position": [-26, -7.5], "dry_run": True})
        self.assertTrue(home.ok)
        row = home.data["coverage"]["clean_flow"]
        self.assertTrue(row["covered"])
        self.assertTrue(row["needed_for_next_tier"])
        self.assertFalse(home.data["coverage"]["health"]["needed_for_next_tier"])
        provider = issue(sim, {"do": "construct", "building": "waste_collector", "position": [-42, -7.5], "dry_run": True})
        self.assertEqual(provider.data["serves"]["service"], "waste")
        self.assertIn("near", provider.data["serves"]["homes"])
        self.assertNotIn("far", provider.data["serves"]["homes"])
        self.assertFalse(sim.sites.get("waste_collector_1"))


class CurrentCustodyTests(unittest.TestCase):
    def test_conservation_cancel_and_disconnect_in_current_mode(self):
        goods = ("carbonate", "biomass", "prepared_silica")
        sim = make_sim(work=10**6)
        issue(sim, {"do": "build_road", "id": "main", "points": MAIN})
        issue(sim, {"do": "build_road", "id": "spur", "points": [[-56, -2], [-56, -26]]})
        issue(sim, {"do": "construct", "building": "general_store", "id": "a", "position": [-50, -7.5]})
        issue(sim, {"do": "construct", "building": "waste_collector", "id": "b", "position": [-61, -18], "yaw": HALF_PI})
        count = lambda: {g: sim.custody().get(g, 0) for g in goods}
        start = count()
        for _ in range(120):
            sim.step()
            self.assertEqual(count(), start)
        delivered = dict(sim.sites["a"].delivered)
        self.assertTrue(delivered)
        issue(sim, {"do": "cancel", "target": "a"})
        expected = {g: start[g] - (delivered.get(g, 0) - int(delivered.get(g, 0) * 0.9 + 1e-9)) for g in goods}
        self.assertTrue(issue(sim, {"do": "remove_road", "target": "spur"}).ok)
        self.assertFalse(sim.spatial.connected("b"))
        for _ in range(300):
            sim.step()
            self.assertEqual(count(), expected)
        self.assertNotIn("a", sim.spatial.placements)
        self.assertFalse(sim.spatial.inbound("b"))


class OpeningProofTests(unittest.TestCase):
    """The committed fixture: an ordinary player opening, 90 minutes, first Stable home, real cargo."""

    def test_opening_evidence_reproduces(self):
        out = subprocess.run([sys.executable, "tools/verify_current_opening.py", "--check"], cwd=ROOT,
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_opening_acceptance(self):
        evidence = json.loads((ROOT / "tests/fixtures/current_opening_evidence.json").read_text())
        self.assertTrue(all(r["ok"] for r in evidence["results"]), evidence["results"])
        self.assertEqual({r["do"] for r in evidence["results"]}, {"build_road", "construct", "evolve"})
        self.assertTrue(evidence["all_sites_paid_in_full"])
        self.assertEqual(evidence["founders_remaining"], 0)
        self.assertEqual(evidence["food_emergency_seconds"], 0)
        self.assertEqual(evidence["devolutions"], 0)
        self.assertLessEqual(evidence["first_stable_second"], 40 * 60)
        self.assertGreater(evidence["carrier_trips"]["deliver"], 50)
        self.assertGreater(evidence["carrier_trips"]["collect"], 20)
        final = evidence["snapshots"][-1]
        self.assertEqual(final["time"], "90:00")
        self.assertEqual(final["sites"], [])
        self.assertIn("stable", final["tiers"].values())
        for service in ("clean_flow", "waste", "maintenance"):
            self.assertTrue(evidence["coverage_home_1"][service]["covered"])
        start = evidence["start_store"]
        self.assertLessEqual(evidence["construction_paid"]["carbonate"], start["carbonate"])

    def test_autoplay_stays_disabled(self):
        s = Session([str(ROOT / o) for o in CURRENT])
        self.assertFalse(handle(s, {"id": 1, "op": "autoplay", "enabled": True})["ok"])


class BridgeV5Tests(unittest.TestCase):
    def test_hello_and_view_shape(self):
        s = Session([str(ROOT / o) for o in CURRENT])
        hello = handle(s, {"id": 1, "op": "hello"})["spatial"]
        self.assertEqual(hello["mode"], "current")
        self.assertEqual(hello["service_ranges"], {"clean_flow": 40, "waste": 40, "maintenance": 50, "default": 45})
        geo = hello["geography"]
        self.assertEqual(set(geo), {"source", "obstacles", "light", "extraction_zones"})
        self.assertEqual(len(geo["obstacles"]), 26)
        self.assertEqual(geo["extraction_zones"][0]["centre"], [40, -54])
        self.assertEqual(geo["extraction_zones"][0]["radius"], 12)
        self.assertEqual(hello["rules"]["road_water_margin"], 0)
        for entry in PLAN["commands"][:4]:
            self.assertTrue(s.command(entry["cmd"])["ok"])
        self.assertTrue(s.command({"do": "construct", "building": "clean_flow_node", "id": "flow", "position": [-34, -7.5]})["ok"])
        preview = s.command({"do": "construct", "building": "shelter", "position": [-26, -7.5], "dry_run": True})
        self.assertEqual(set(preview["preview"]), {"entrance", "attach", "spur", "route_length", "suitability", "coverage"})
        view = s.advance(400)
        spatial = view["spatial"]
        self.assertEqual(spatial["mode"], "current")
        home = spatial["placements"]["home_1"]
        self.assertTrue({"spur", "suitability", "coverage"} <= set(home))
        self.assertEqual(set(home["coverage"]["clean_flow"]), {"covered", "provider", "distance", "range", "needed_for_next_tier"})
        self.assertEqual(set(spatial["placements"]["flow"]["serves"]), {"service", "range", "active", "homes"})
        facility = next(iter(view["facilities"].values()))
        self.assertIn("cycle_progress", facility)
        json.dumps(view)

    def test_roads_mode_view_has_no_v5_fields(self):
        s = Session([str(ROOT / o) for o in ROADS])
        hello = handle(s, {"id": 1, "op": "hello"})["spatial"]
        self.assertEqual(hello["mode"], "roads")
        self.assertNotIn("geography", hello)
        s.command({"do": "build_road", "points": [[-45, 0], [-25, 0]]})
        s.command({"do": "construct", "building": "shelter", "id": "h", "position": [-40, -5]})
        placement = s.view()["spatial"]["placements"]["h"]
        self.assertNotIn("coverage", placement)
        self.assertNotIn("spur", placement)


if __name__ == "__main__":
    unittest.main()
