FROM osgeo/gdal:ubuntu-full-3.0.3

# Required for click with Python 3.6
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update
RUN apt-get install python3-pip -y
 
RUN pip3 install rasterio==1.1.3 --no-binary rasterio
RUN pip3 install tox
RUN apt-get install build-essential python3-dev python3-numpy libhdf4-dev -y
COPY ./ ./hls_hdf_to_cog

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["cd hls_hdf_to_cog && tox -r"]
