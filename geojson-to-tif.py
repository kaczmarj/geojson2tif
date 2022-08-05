"""Convert an GeoJSON-based annotation to a pyramidal TIF image.

This script was written to convert nuclei segmentations
(https://doi.org/10.1038/s41597-020-0528-1) to pyramidal TIF images.

This code is not meant to be general, but I hope it serves as a reference for others.

Requires ASAP (https://github.com/computationalpathologygroup/ASAP) version 2.1
and wholeslidedata (https://github.com/DIAGNijmegen/pathology-whole-slide-data) from
commit 247c2429f90a47e42493d43d6bb94316b1179aa7.
"""

import argparse
import gzip
import json
from pathlib import Path
import tempfile

from wholeslidedata.accessories.asap.write_mask2 import convert_annotations_to_mask
from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
from wholeslidedata.image.wholeslideimage import WholeSlideImage


def _is_gz_file(filepath) -> bool:
    with open(filepath, "rb") as f:
        return f.read(2) == b"\x1f\x8b"


def make_mask(*, wsi_path, wsa_path, output_path):

    if Path(output_path).exists():
        raise FileExistsError(output_path)
    if not Path(output_path).parent.exists():
        raise FileNotFoundError(f"parent directory does not exist: {output_path}")
    wsi = WholeSlideImage(wsi_path)
    wsa = WholeSlideAnnotation(wsa_path)
    spacing = wsi.spacings[0]

    print(f"[geojson2tif] wsi path  = {wsi.path}")
    print(f"[geojson2tif] json path = {wsa.path}")
    print(f"[geojson2tif] spacing   = {spacing}")
    print(f"[geojson2tif] wsi path  = {output_path}", flush=True)

    convert_annotations_to_mask(
        wsi=wsi,
        annotations=wsa.annotations,
        spacing=spacing,
        mask_output_path=output_path,
        tile_size=1024,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--wsi", required=True, help="Path to WSI")
    p.add_argument("--geojson", required=True, help="Path to GeoJSON ")
    p.add_argument("--output", required=True, help="Path to output TIF file")
    p.add_argument("--temp-dir", help="Dir to store temp files (cleaned up at end)")
    args = p.parse_args()

    print("[geojson2tif] Converting GeoJSON to TIF...")
    print("[geojson2tif] I don't check whether the input GeoJSON is valid")

    open_fn = gzip.open if _is_gz_file(args.geojson) else open

    with open_fn(args.geojson) as f:
        geojson_data = json.load(f)
    if "features" not in geojson_data.keys():
        raise KeyError("'features' key not found at top-level (is this valid GeoJSON?)")

    # Transform the geojson data to a wholeslidedata-compatible format.
    # We adhere to the schema at
    # https://github.com/DIAGNijmegen/pathology-whole-slide-data/blob/e6ba4338ed2528e4fd40552edaee3c845973e7f8/wholeslidedata/annotation/parser.py#L18
    print("[geojson2tif] Transforming GeoJSON to a different format for processing...")
    transformed = [
        {
            "index": i,
            "type": "polygon",
            "coordinates": row["geometry"]["coordinates"],
            "label": {"name": "nucleus", "value": 1},
        }
        for i, row in enumerate(geojson_data["features"])
    ]

    with tempfile.NamedTemporaryFile(
        mode="wt", suffix=".json", dir=args.temp_dir
    ) as tempf:
        json.dump(transformed, tempf)
        tempf.flush()  # Without forcing write, subsequent stuff doesn't work.
        print("[geojson2tif] Making mask image...", flush=True)
        make_mask(wsi_path=args.wsi, wsa_path=tempf.name, output_path=args.output)

    print("[geojson2tif] Wrote output to")
    print(f"[geojson2tif] {args.output}")
    print("[geojson2tif] Finished!")
