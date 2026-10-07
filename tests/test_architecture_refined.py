"""Validate shipped glTF payloads without a Blender installation."""
import json
import math
import struct
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets/architecture_v04"


def glb_json(path):
    data=path.read_bytes()
    magic,version,length=struct.unpack_from("<III",data)
    assert magic==0x46546C67 and version==2 and length==len(data)
    size,kind=struct.unpack_from("<II",data,12)
    assert kind==0x4E4F534A
    return json.loads(data[20:20+size])


class RefinedArchitectureTests(unittest.TestCase):
    def test_ten_assets_are_self_contained_textured_gltf(self):
        manifest=json.loads((OUT/"manifest.json").read_text())
        self.assertEqual(len(manifest["assets"]),10)
        self.assertFalse(manifest["gameplay_bound"])
        for record in manifest["assets"]:
            for key in ("path","lod_path"):
                with self.subTest(asset=record["id"],level=key):
                    data=glb_json(ROOT/record[key])
                    self.assertTrue(data["images"])
                    self.assertTrue(all("bufferView" in image and "uri" not in image for image in data["images"]))
                    self.assertTrue(all("uri" not in buffer for buffer in data["buffers"]))
                    for mat in data["materials"]:
                        self.assertIn("baseColorTexture",mat["pbrMetallicRoughness"])
                        self.assertIn("normalTexture",mat)
                    triangles=0
                    for mesh in data["meshes"]:
                        for primitive in mesh["primitives"]:
                            self.assertEqual(primitive.get("mode",4),4)
                            for attr in ("POSITION","NORMAL","TEXCOORD_0"):
                                self.assertIn(attr,primitive["attributes"])
                            triangles+=data["accessors"][primitive["indices"]]["count"]//3
                    self.assertEqual(triangles,record["lod_triangles" if key=="lod_path" else "triangles"])

    def test_lod_and_binding_metadata(self):
        manifest=json.loads((OUT/"manifest.json").read_text())
        for record in manifest["assets"]:
            self.assertLess(record["lod_triangles"],record["triangles"]*.6)
            self.assertTrue(all(math.isfinite(v) for row in record["bounds_y_up"].values() for v in row))
            anchors=json.loads((OUT/(record["id"]+".anchors.json")).read_text())
            self.assertFalse(anchors["authoritative"])
            for name in ("CarrierInput","CarrierOutput","LabelAnchor","WorkAnchor"):
                self.assertIn(name,anchors["anchors"])
            self.assertIn("Structure",record["states"])
        self.assertGreater(manifest["assets"][5]["bounds_y_up"]["max"][1],manifest["assets"][0]["bounds_y_up"]["max"][1]*3)


if __name__=="__main__":unittest.main()
