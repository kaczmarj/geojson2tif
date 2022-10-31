FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

# Install wholeslidedata
RUN apt-get update -qq \
    && apt-get install -q -y --no-install-recommends \
        ca-certificates \
        gcc \
        libpython3.8 \
        python3.8 \
        python3.8-dev \
        python3.8-distutils \
        python-is-python3 \
        wget \
    && rm -rf /var/lib/apt/lists/* \
    && wget -qO- https://bootstrap.pypa.io/get-pip.py | python3 - \
    && rm -r ~/.cache/pip/ \
    && python3 -m pip install --no-cache-dir \
        https://github.com/DIAGNijmegen/pathology-whole-slide-data/tarball/247c2429f90a47e42493d43d6bb94316b1179aa7 \
        matplotlib \
    && apt-get autoremove -yq gcc python3-dev

# Install ASAP.
RUN apt-get update -qq \
    && wget -q 'https://github.com/computationalpathologygroup/ASAP/releases/download/ASAP-2.1-(Nightly)/ASAP-2.1-Ubuntu2004.deb' \
    && TZ=Etc/UTC apt-get install --no-install-recommends -yq ./ASAP-2.1-Ubuntu2004.deb \
    && rm -rf ASAP-2.1-Ubuntu2004.deb /var/lib/apt/lists/*
ENV PYTHONPATH=/opt/ASAP/bin:$PYTHONPATH

COPY geojson-to-tif.py /opt/geojson-to-tif/
COPY geojson-to-tif-hovernet.py /opt/geojson-to-tif/
ENTRYPOINT ["python3.8", "/opt/geojson-to-tif/geojson-to-tif.py"]
