FROM osgeo/gdal:ubuntu-full-latest

RUN apt-get update
RUN apt-get install python3-pip -y
 
RUN pip3 install rasterio==1.1.3 --no-binary rasterio
RUN pip3 install tox
RUN apt-get install build-essential python3-dev python3-numpy libhdf4-dev -y
ARG test=3
COPY ./ ./hls_hdf_to_cog

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["cd hls_hdf_to_cog && tox -r"]


