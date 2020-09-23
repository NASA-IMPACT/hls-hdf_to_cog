FROM osgeo/gdal:ubuntu-full-3.0.3

# Required for click with Python 3.6
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update
RUN apt-get install python3-pip python3-venv git -y
RUN pip3 install rasterio==1.1.3 --no-binary rasterio
RUN pip3 install tox tox-venv

RUN git clone https://github.com/NASA-IMPACT/hls-testing_data
COPY ./ ./hls_hdf_to_cog
COPY ./tests/data/HLS.S30.T35JMG.2020192T074619.v1.5.ANGLE.hdf ./hls-testing_data


ENTRYPOINT ["/bin/sh", "-c"]
CMD ["cd hls_hdf_to_cog && tox -r"]
