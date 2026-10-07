"""Export-level checks; visual acceptance remains a separate human gate."""
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/architecture_v03"


class ArchitectureBenchmarkTests(unittest.TestCase):
    def test_fixed_ten_model_scope_and_no_gameplay_claim(self):
        manifest = json.loads((OUT / "manifest.json").read_text())
        self.assertEqual(len(manifest["assets"]), 10)
        self.assertFalse(manifest["gameplay_bound"])
        self.assertEqual(len({r["id"] for r in manifest["assets"]}), 10)

    def test_runtime_exports_and_normal_indices(self):
        manifest = json.loads((OUT / "manifest.json").read_text())
        for record in manifest["assets"]:
            with self.subTest(asset=record["id"]):
                lines = (ROOT / record["path"]).read_text().splitlines()
                vertices = [line.split()[1:] for line in lines if line.startswith("v ")]
                normals = [line.split()[1:] for line in lines if line.startswith("vn ")]
                self.assertTrue(vertices and normals)
                for values in vertices + normals:
                    self.assertTrue(all(math.isfinite(float(v)) for v in values))
                faces = [line.split()[1:] for line in lines if line.startswith("f ")]
                self.assertEqual(len(faces), record["triangles"])
                for face in faces:
                    self.assertEqual(len(face), 3)
                    for corner in face:
                        fields = corner.split("/")
                        self.assertTrue(1 <= int(fields[0]) <= len(vertices))
                        self.assertTrue(1 <= int(fields[2]) <= len(normals))
                self.assertTrue((ROOT / record["path"]).with_suffix(".mtl").exists())

    def test_ports_and_housing_height_progression(self):
        manifest = json.loads((OUT / "manifest.json").read_text())
        houses = manifest["assets"][:6]
        self.assertGreater(houses[-1]["height"], houses[0]["height"] * 3)
        for record in manifest["assets"]:
            anchors = json.loads((OUT / (record["id"] + ".anchors.json")).read_text())
            self.assertEqual(anchors["up_axis"], "+Y")
            self.assertEqual(anchors["status"], "visual_candidate")
            ports = anchors["anchors"]
            self.assertIn("CarrierInput", ports)
            self.assertIn("CarrierOutput", ports)
            self.assertGreater(ports["LabelAnchor"][1], record["height"])
            if "general_store" not in record["id"]:
                self.assertIn("CleanFlowIn", ports)
                self.assertIn("WasteReturnIn" if "digester" in record["id"] else "WasteReturnOut", ports)


if __name__ == "__main__":
    unittest.main()
