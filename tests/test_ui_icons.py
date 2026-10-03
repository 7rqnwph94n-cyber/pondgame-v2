import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
ICONS=ROOT/"assets"/"ui"/"icons"


class UIIconTests(unittest.TestCase):
    def test_manifest_icons_exist_and_parse(self):
        manifest=json.loads((ICONS/"manifest.json").read_text())
        self.assertGreaterEqual(len(manifest["icons"]),18)
        for name in manifest["icons"]:
            with self.subTest(icon=name):
                path=ICONS/f"{name}.svg"
                self.assertTrue(path.is_file())
                root=ET.parse(path).getroot()
                self.assertEqual(root.attrib.get("viewBox"),"0 0 64 64")

    def test_icons_have_accessible_background_and_vector_content(self):
        for path in ICONS.glob("*.svg"):
            with self.subTest(icon=path.name):
                text=path.read_text()
                self.assertIn('role="img"',text)
                self.assertIn("<circle",text)
                self.assertTrue("<path" in text or text.count("<circle")>1)
                self.assertNotIn("<text",text)

    def test_failure_colour_is_limited_to_failure_icons(self):
        coral="#dc5a4b"
        allowed={"output_blocked.svg","food_emergency.svg"}
        actual={p.name for p in ICONS.glob("*.svg") if coral in p.read_text()}
        self.assertEqual(actual,allowed)


if __name__=="__main__":
    unittest.main()
