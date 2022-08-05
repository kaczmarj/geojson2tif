# GeoJSON to TIFF

[![Docker Pulls](https://img.shields.io/docker/pulls/kaczmarj/geojson2tif)](https://hub.docker.com/r/kaczmarj/geojson2tif)

An entirely non-general tool to convert a GeoJSON set of polygons into a multi-resolution TIF image.

This code was written to convert polygons of nuclear segmentations (https://doi.org/10.1038/s41597-020-0528-1)
to TIF images. It may need to be tweaked to work with other datasets.

# Example

Here I demonstrate using this within an Apptainer (formerly Singularity) container.

1. First, get the container. Feel free to swap out the `apptainer` command for `singularity`.

    ```
    apptainer pull docker://kaczmarj/geojson2tif:latest
    ```

2. Run the tool. You will need a GeoJSON file with the labels and the corresponding whole slide image.

    ```
    apptainer exec --pwd $(pwd) geojson2tif_latest.sif \
        --wsi image.tif --geojson polygons.json --output mask.tif
    ```

# Installation

Use the Docker image for a hassle-free experience.

Otherwise, please install [ASAP](https://github.com/computationalpathologygroup/ASAP) version 2.1
and [wholeslidedata](https://github.com/DIAGNijmegen/pathology-whole-slide-data) from
commit [247c2429f90a47e42493d43d6bb94316b1179aa7](https://github.com/DIAGNijmegen/pathology-whole-slide-data/tree/247c2429f90a47e42493d43d6bb94316b1179aa7).
