# hls-hdf_to_cog
## Transform HLS hdf files to COGs

### Requirements
The use of rasterio for HDF does not allow for the regular pip install of rasterio using wheels. It requires a preinstalled gdal version that supports HDF4 installed on the system and install rasterio using
```
pip install rasterio --no-binary rasterio
```

Installation requires python development libraries and hdf4 binaries. On an Ubuntu/Debian system they can be installed with the following.
```bash
sudo apt-get install build-essential python3-dev python-dev libhdf4-dev # For Python 3

```
### Installation
Install for local testing
```bash
pip install -e .["test"]
```

This will install both the hls_hdf_to_cog package as well as install a hdf_to_cog executable on your path.

### Tests
Run Tests on Docker
```bash
docker build -t hls_hdf_to_cog . && docker run hls_hdf_to_cog
```
