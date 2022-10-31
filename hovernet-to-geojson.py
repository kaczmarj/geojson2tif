"""Convert HoverNet outputs to GeoJSON format."""

import argparse
import json
from pathlib import Path

from shapely.geometry import Polygon

# https://github.com/vqdang/hover_net/blob/842964dc5d26ffe196d236d16fad16643a103850/type_info.json
type_mapping = {
    0: "nolabel",
    1: "neoplastic",
    2: "inflammatory",
    3: "connective",
    4: "necrosis",
    5: "non-neoplastic",
}


def hovernet_to_feature_dict(instance_id: int, d: dict):
    # Convert to polygon to verify that coordinates
    # are valid.
    poly = Polygon(d["contour"])
    coordinates = list(poly.exterior.coords)
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates,
        },
        "properties": {
            "instance_id": int(instance_id),
            "type_str": type_mapping[d["type"]],
            "type_int": d["type"],
            "type_prob": d["type_prob"],
        },
    }


def hovernet_to_geojson(d: dict):
    assert "nuc" in d.keys(), "expected 'nuc' key"
    assert "mag" in d.keys(), "expected 'mag' key"
    assert d["mag"] == 40, "this script was designed for mag=40x"
    features = [hovernet_to_feature_dict(ii, dd) for ii, dd in d["nuc"].items()]
    return {
        "type": "FeatureCollection",
        "features": features,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="JSON file with HoverNet predictions.")
    p.add_argument("output", help="Output GeoJSON file")
    args = p.parse_args()

    if not Path(args.input).exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")
    if Path(args.output).exists():
        raise FileExistsError(f"Output file exists: {args.output}")

    print("Reading HoverNet polygons...")
    with open(args.input) as f:
        d = json.load(f)

    print("Converting to GeoJSON...")
    geojson = hovernet_to_geojson(d)

    print(f"Writing output to {args.output}")
    with open(args.output, "w") as f:
        json.dump(geojson, f)

    print("Done.")
