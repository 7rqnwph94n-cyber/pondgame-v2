"""Presentation-only Blender kit: export and anchor sanity, no gameplay semantics."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "blockout" / "environment"
NAMES = ("node_current_junction_a", "node_building_intake_a", "node_transfer_fan_a")


class CurrentOrganAssetTests(unittest.TestCase):
    def test_exports_have_materials_geometry_and_bounded_size(self):
        for name in NAMES:
            with self.subTest(name=name):
                obj = (ASSETS / f"{name}.obj").read_text(encoding="utf-8")
                mtl = (ASSETS / f"{name}.mtl").read_text(encoding="utf-8")
                self.assertIn(f"mtllib {name}.mtl", obj)
                self.assertIn("newmtl ", mtl)
                self.assertIn("Kd ", mtl)
                faces = [line for line in obj.splitlines() if line.startswith("f ")]
                self.assertGreater(len(faces), 150)
                self.assertLess(len(faces), 5000)
                self.assertTrue(all(4 <= len(line.split()) <= 5 for line in faces))
                for line in obj.splitlines():
                    if line.startswith("usemtl "):
                        self.assertEqual(len(line.split()), 2, line)

    def test_anchors_are_y_up_and_point_to_ports(self):
        for name in NAMES:
            with self.subTest(name=name):
                data = json.loads((ASSETS / f"{name}.anchors.json").read_text(encoding="utf-8"))
                self.assertEqual(name, data["asset"])
                self.assertEqual("+Y", data["up_axis"])
                self.assertEqual([0, 0, 0], data["ground_pivot"])
                self.assertTrue(any("Port" in key for key in data["anchors"]))
                self.assertTrue(all(len(value) == 3 for value in data["anchors"].values()))

    def test_editable_source_and_camera_sheet_exist(self):
        self.assertTrue((ROOT / "assets/source/blender/submerged_current_organs_v01.blend").is_file())
        self.assertTrue((ROOT / "docs/art/renders/submerged_current_organs_v01.png").is_file())


if __name__ == "__main__":
    unittest.main()
