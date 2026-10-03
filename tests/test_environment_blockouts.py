import json
import unittest
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"assets"/"blockout"/"environment"

EXPECTED={
    "terrain_silt_tile_a","terrain_silt_tile_b","terrain_sand_tile_a",
    "ledge_straight_a","ledge_corner_a","boulder_a","boulder_b","boulder_c",
    "root_arch_a","route_flow_straight_a","route_flow_corner_a","route_flow_junction_a",
    "plant_fan_a","plant_fan_b","plant_ribbon_a","plant_ribbon_b","plant_cup_a",
    "plant_branch_a","plant_branch_b","detail_ripple_a","detail_pebbles_a","detail_scar_a",
    "vegetation_mat_a","vegetation_mat_b","vegetation_mat_c",
    "filter_grove_a","filter_grove_b","anoxic_colony_a","sulphur_colony_a",
    "silica_lichen_a","carbonate_colony_a",
    "channel_bank_straight_a","channel_bank_bend_a","floodplain_shelf_a","silica_cliff_a",
    "methane_seep_a","sulphur_vent_cluster_a","delta_island_a","delta_island_b",
    "silica_outcrop_b","methane_crater_b","sulphur_crust_b","carbonate_shelf_a",
}


def parse(path):
    vertices=[]; faces=[]
    for line in path.read_text().splitlines():
        if line.startswith("v "): vertices.append(tuple(map(float,line.split()[1:4])))
        elif line.startswith("f "): faces.append([int(i.split("/")[0]) for i in line.split()[1:]])
    return vertices,faces


class EnvironmentBlockoutTests(unittest.TestCase):
    def test_manifest_and_files(self):
        data=json.loads((ASSETS/"manifest.json").read_text())
        self.assertEqual(set(data["assets"]),EXPECTED)
        self.assertEqual(data["units"],"metres")

    def test_meshes_are_valid_and_grounded(self):
        for name in EXPECTED:
            with self.subTest(asset=name):
                vertices,faces=parse(ASSETS/f"{name}.obj")
                self.assertGreater(len(vertices),3)
                self.assertGreater(len(faces),0)
                self.assertTrue(all(1<=index<=len(vertices) for face in faces for index in face))
                self.assertGreaterEqual(min(v[1] for v in vertices),-.001)

    def test_terrain_tiles_share_exact_flat_edges(self):
        for name in ("terrain_silt_tile_a","terrain_silt_tile_b","terrain_sand_tile_a"):
            vertices,_=parse(ASSETS/f"{name}.obj")
            edge=[v for v in vertices if abs(abs(v[0])-4)<.001 or abs(abs(v[2])-4)<.001]
            self.assertTrue(edge)
            self.assertTrue(all(abs(v[1])<.001 for v in edge))

    def test_route_snap_points_are_present(self):
        required={"route_flow_straight_a":2,"route_flow_corner_a":2,"route_flow_junction_a":4}
        for name,count in required.items():
            data=json.loads((ASSETS/f"{name}.anchors.json").read_text())
            self.assertEqual(len(data["anchors"]),count)

    def test_basin_landmarks_have_functional_anchors(self):
        required={
            "channel_bank_straight_a":"FlowAnchor",
            "floodplain_shelf_a":"CultivationAnchor",
            "silica_cliff_a":"ExtractionAnchor",
            "methane_seep_a":"HazardAnchor",
            "sulphur_vent_cluster_a":"ExtractionAnchor",
            "delta_island_a":"DepositAnchor",
        }
        for name,anchor in required.items():
            data=json.loads((ASSETS/f"{name}.anchors.json").read_text())
            self.assertIn(anchor,data["anchors"])


if __name__=="__main__":
    unittest.main()
