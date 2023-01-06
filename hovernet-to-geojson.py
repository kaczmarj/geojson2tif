"""Convert HoverNet outputs to GeoJSON format."""

import argparse
import gzip
import json
from pathlib import Path

import geojson
from shapely.affinity import scale as scale_fn
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


def hovernet_to_feature_dict(instance_id: int, d: dict, scale:float=None):
    # Convert to polygon to verify that coordinates
    # are valid.
    poly = Polygon(d["contour"])

    if scale is not None:
        poly = scale_fn(poly, xfact=scale, yfact=scale, origin=(0, 0))

    coordinates = list(poly.exterior.coords)
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [coordinates],
        },
        "properties": {
            "instance_id": int(instance_id),
            "type_str": type_mapping[d["type"]],
            "type_int": d["type"],
            "type_prob": d["type_prob"],
        },
    }


def hovernet_to_geojson(d: dict, scale: float):
    assert "nuc" in d.keys(), "expected 'nuc' key"
    assert "mag" in d.keys(), "expected 'mag' key"
    assert d["mag"] == 40, "this script was designed for mag=40x"
    features = [hovernet_to_feature_dict(ii, dd, scale=scale) for ii, dd in d["nuc"].items()]
    return {
        "type": "FeatureCollection",
        "features": features,
    }

def get_mag(path):
    import openslide

    oslide = openslide.open_slide(path)
    mag = oslide.properties.get(openslide.PROPERTY_NAME_OBJECTIVE_POWER)
    if mag is not None:
        mag = float(mag)
    return mag


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="JSON file with HoverNet predictions.")
    p.add_argument("output", help="Output GeoJSON file")
    p.add_argument("--slide", help="Path to slide to get magnification level")
    args = p.parse_args()

    if not Path(args.input).exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")
    if Path(args.output).exists():
        raise FileExistsError(f"Output file exists: {args.output}")

    mag = None
    if args.slide is not None:
        mag = get_mag(args.slide)

    print("Reading HoverNet polygons...")
    openfn = gzip.open if args.input.endswith("gz") else open
    with openfn(args.input) as f:
        d = json.load(f)

    print("Converting to GeoJSON...")
    json_dict = hovernet_to_geojson(d, scale=mag / 40)

    print("Checking whether object is valid GeoJSON...")
    geojson_obj: geojson.GeoJSON = geojson.loads(json.dumps(json_dict))
    if not geojson_obj.is_valid:
        raise RuntimeError("geojson object is not valid!")

    print(f"Writing output to {args.output}")
    openfn = gzip.open if args.output.endswith("gz") else open
    with openfn(args.output, "w") as f:
        json.dump(json_dict, f)

    print("Done.")
