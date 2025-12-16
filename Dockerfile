ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} python:3.12-slim

# Required for click with Python 3.6
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgdal-dev \
        libexpat1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY setup.py .
# compile rasterio against container GDAL to get HDF4 support
RUN pip install --no-binary rasterio --no-cache-dir '.[test]'

COPY ./ ./

# https://gdal.org/en/stable/drivers/raster/mem.html#dataset-name-format
# Starting with GDAL 3.10, opening a MEM dataset using the above syntax (DATAPOINTER) is no longer enabled
# by default for security reasons. If you want to allow it, define the GDAL_MEM_ENABLE_OPEN
# configuration option to YES, or build GDAL with the GDAL_MEM_ENABLE_OPEN compilation definition.
ENV GDAL_MEM_ENABLE_OPEN=YES

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["cd hls_hdf_to_cog && tox -r"]
