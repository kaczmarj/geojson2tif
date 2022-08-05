"""Convert original representation of nuclei polygons to GeoJSON.

In the original format, nuclei are saved in CSV files. Each row contains the coordinates
for one nucleus. Each whole slide image has multiple CSV files, because each CSV file
covers a patch of the whole slide.

Requires installation of shapely.
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Optional

import shapely.geometry


class WSINucleiHelper:
    """Make segmentation masks from polygon coordinate data.

    Original data from Le Hou's Scientific Data paper.
    """
    def __init__(self, parent_path):
        self.parent_path = Path(parent_path)
        self._feature_files = list(self.parent_path.glob("*-features.csv"))

    @staticmethod
    def _read_coords_from_feature_file(path):
        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row["Polygon"] for row in reader]

    @staticmethod
    def _coords_string_to_polygon(coords: str) -> Optional[shapely.geometry.Polygon]:
        # Chop off [ and ]
        coords = coords[1:-1]
        coords = [float(num) for num in coords.split(":")]
        # Must be even to get xy pairs.
        if len(coords) % 2 != 0:
            return None
        if len(coords) == 0:
            return None
        coords = list(zip(coords[0::2], coords[1::2]))
        # Need at least 3 coordinates to make a polygon.
        if len(coords) < 3:
            return None
        return shapely.geometry.Polygon(coords)

    def all_polygons(self, skip_invalid=True):
        for feature_file in self._feature_files:
            rows_of_coords = self._read_coords_from_feature_file(feature_file)
            for row in rows_of_coords:
                polygon = self._coords_string_to_polygon(row)
                if polygon is None:
                    continue
                if skip_invalid and not polygon.is_valid:
                    continue
                else:
                    yield polygon


def polygon_to_feature_dict(poly: shapely.geometry.Polygon):
    coordinates = list(poly.exterior.coords)
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates,
        },
        "properties": {},
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("dir", help="Directory containing CSV files for one slide")
    p.add_argument("output", help="Output JSON file")
    args = p.parse_args()

    if not Path(args.dir).exists():
        raise FileNotFoundError(f"Directory not found: {args.dir}")
    if Path(args.output).exists():
        raise FileExistsError(f"Output file exists: {args.output}")

    print("Reading all polygons...")
    helper = WSINucleiHelper(args.dir)
    features = [polygon_to_feature_dict(poly) for poly in helper.all_polygons()]
    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }
    print(f"Writing output to {args.output}")
    with open(args.output, "w") as f:
        json.dump(geojson, f)
    print("Done.")
