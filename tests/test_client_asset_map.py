import json
import unittest
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
MAP_PATH=ROOT/"client"/"presentation"/"asset_map.json"


class ClientAssetMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(MAP_PATH.read_text())

    def test_domain_asset_references_exist(self):
        asset_dir=(ROOT/"client"/self.data["asset_dir"]).resolve()
        for section in ("buildings","residence_tiers"):
            for domain_id,asset in self.data[section].items():
                with self.subTest(domain_id=domain_id):
                    self.assertTrue((asset_dir/f"{asset}.obj").is_file())

    def test_environment_references_exist(self):
        env_dir=(ROOT/"client"/self.data["environment_dir"]).resolve()
        names=list(self.data["environment"]["terrain_tiles"])
        names += [item["asset"] for item in self.data["environment"]["routes"]]
        names += [item["asset"] for item in self.data["environment"]["scenery"]]
        for name in names:
            with self.subTest(asset=name):
                self.assertTrue((env_dir/f"{name}.obj").is_file())

    def test_icon_source_set_is_available(self):
        icon_dir=(ROOT/"client"/self.data["icon_dir"]).resolve()
        manifest=json.loads((icon_dir/"manifest.json").read_text())
        self.assertIn("raw_silicate",manifest["icons"])
        self.assertIn("output_blocked",manifest["icons"])
        self.assertIn("food_emergency",manifest["icons"])

    def test_scenery_stays_outside_core_settlement_corridor(self):
        for item in self.data["environment"]["scenery"]:
            x,_,z=item["position"]
            self.assertGreaterEqual(max(abs(x),abs(z)),20)


if __name__=="__main__":
    unittest.main()
