import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "blockout" / "silica_street"


EXPECTED = {
    "patch_silicate_a": {"max_x": 7.0, "max_z": 6.0, "anchors": {"WorkerAnchor_1", "PayloadAnchor", "LabelAnchor"}},
    "payload_raw_silicate_a": {"max_x": 1.0, "max_z": 1.0, "anchors": {"PayloadAnchor"}},
    "payload_prepared_silica_a": {"max_x": 1.0, "max_z": 1.0, "anchors": {"PayloadAnchor"}},
    "unit_general_carrier_a": {"max_x": 1.5, "max_z": 1.3, "anchors": {"PayloadAnchor", "DeliveryContact", "GroundPivot"}},
    "store_general_a": {"max_x": 6.2, "max_z": 5.2, "anchors": {"InputAnchor_raw_silicate", "WorkerAnchor_1", "CameraAnchor"}},
    "proc_mineral_washery_a": {"max_x": 8.2, "max_z": 6.2, "anchors": {"InputAnchor_raw_silicate", "OutputAnchor_prepared_silica", "ServiceAnchor", "CameraAnchor"}},
    "res_shelter_cluster_a": {"max_x": 7.2, "max_z": 6.2, "anchors": {"WorkerAnchor_1", "ServiceAnchor", "ConstructionAnchor", "CameraAnchor"}},
    "service_clean_flow_a": {"max_x": 3.2, "max_z": 3.2, "anchors": {"WorkerAnchor_1", "ServiceAnchor", "InputAnchor_clean_flow", "OutputAnchor_clean_flow"}},
    "waste_collector": {"max_x": 4.2, "max_z": 4.2, "anchors": {"WorkerAnchor_1", "ServiceAnchor", "InputAnchor_waste"}},
    "farm_photosynthetic_a": {"max_x": 9.0, "max_z": 6.2, "anchors": {"WorkerAnchor_1", "OutputAnchor_photosynthetic_food", "ServiceAnchor"}},
}


def parse_obj(path):
    vertices = []
    faces = []
    materials = set()
    for line in path.read_text().splitlines():
        if line.startswith("v "):
            vertices.append(tuple(float(value) for value in line.split()[1:4]))
        elif line.startswith("f "):
            faces.append([int(item.split("/")[0]) for item in line.split()[1:]])
        elif line.startswith("usemtl "):
            materials.add(line.split(maxsplit=1)[1])
    return vertices, faces, materials


class BlockoutAssetTests(unittest.TestCase):
    def test_manifest_and_expected_assets_exist(self):
        manifest = json.loads((ASSET_DIR / "manifest.json").read_text())
        self.assertEqual(set(manifest["assets"]), set(EXPECTED))
        for asset in EXPECTED:
            self.assertTrue((ASSET_DIR / f"{asset}.obj").is_file())
            self.assertTrue((ASSET_DIR / f"{asset}.anchors.json").is_file())

    def test_meshes_are_valid_grounded_and_within_blockout_envelopes(self):
        for asset, contract in EXPECTED.items():
            with self.subTest(asset=asset):
                vertices, faces, materials = parse_obj(ASSET_DIR / f"{asset}.obj")
                self.assertGreater(len(vertices), 3)
                self.assertGreater(len(faces), 1)
                self.assertTrue(materials)
                self.assertGreaterEqual(min(vertex[1] for vertex in vertices), -0.001)
                self.assertTrue(all(1 <= index <= len(vertices) for face in faces for index in face))
                width = max(v[0] for v in vertices) - min(v[0] for v in vertices)
                depth = max(v[2] for v in vertices) - min(v[2] for v in vertices)
                self.assertLessEqual(width, contract["max_x"])
                self.assertLessEqual(depth, contract["max_z"])

    def test_required_anchors_and_coordinate_contract(self):
        for asset, contract in EXPECTED.items():
            with self.subTest(asset=asset):
                data = json.loads((ASSET_DIR / f"{asset}.anchors.json").read_text())
                self.assertEqual(data["units"], "metres")
                self.assertEqual(data["up_axis"], "+Y")
                self.assertEqual(data["ground_pivot"], [0, 0, 0])
                self.assertTrue(contract["anchors"].issubset(data["anchors"]))


if __name__ == "__main__":
    unittest.main()
