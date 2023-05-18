"""
Translate HLS HDF files to Cloud Optimized GeoTIFF aka COG.

Usage: hdf_to_cog.py [OPTIONS] INPUT

  Translate a file to a COG.

Options:
  --output-dir DIRECTORY          [required]

  -p, --cog-profile [jpeg|webp|zstd|lzw|deflate|packbits|lzma|lerc|lerc_deflate|lerc_zstd|raw]
                                  CloudOptimized GeoTIFF profile (default: deflate).

  --blocksize INTEGER             Overwrite internal tile size (default is set to 256).

  --co, --profile NAME=VALUE      Driver specific creation options. See the
                                  documentation for the selected output driver for more information.

  --help                          Show this message and exit.

Example:
$ python -m hdf_to_cog HLS.S30.T52SCG.2019253.v1.5.hdf --output-dir my-dir
or
$ python hdf_to_cog.py HLS.S30.T52SCG.2019253.v1.5.hdf --output-dir my-dir
"""

import os

import click

import rasterio
from rasterio.rio import options
from rio_cogeo.cogeo import cog_translate, cog_validate
from rio_cogeo.profiles import cog_profiles
from rasterio.dtypes import _gdal_typename

S30_BAND_NAMES = (
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B8A",
    "B09",
    "B10",
    "B11",
    "B12",
    "QA",
)

S30_DEBUG_BAND_NAMES = (
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B8A",
    "B09",
    "B10",
    "B11",
    "B12",
    "ACmask",
    "QA",
)

ANGLE_BAND_NAMES = {
    "solar_zenith": "SZA",
    "solar_azimuth": "SAA",
    "view_zenith": "VZA",
    "view_azimuth": "VAA",
}

L30_BAND_NAMES = (
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B09",
    "B10",
    "B11",
    "Fmask",
)

L30_DEBUG_BAND_NAMES = (
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B09",
    "B10",
    "B11",
    "ACmask",
    "Fmask",
)


@click.command()
@options.file_in_arg
@click.option(
    "--output-dir",
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
    required=True,
)
@click.option(
    "--product",
    type=click.Choice(["S30", "L30", "S30_ANGLES", "L30_ANGLES"]),
    required=True,
    help="S30 or L30",
)
@click.option(
    "--cog-profile",
    "-p",
    "cogeo_profile",
    type=click.Choice(list(cog_profiles.keys())),
    default="deflate",
    help="CloudOptimized GeoTIFF profile (default: deflate).",
)
@click.option(
    "--blocksize",
    type=int,
    default=256,
    help="Overwrite internal tile size (default is set to 256).",
)
@click.option(
    "--debug-mode",
    is_flag=True,
    help="Write arbitrary band names for debugging intermediate hdfs."
)
@options.creation_options
def main(input, output_dir, product, cogeo_profile, blocksize, debug_mode, creation_options,):
    """Translate a file to a COG."""
    assert input.endswith(".hdf")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_profile = cog_profiles.get(cogeo_profile)
    output_profile.update(
        dict(blockxsize=str(blocksize), blockysize=str(blocksize), predictor="2")
    )
    if creation_options:
        output_profile.update(creation_options)

    config = dict(GDAL_NUM_THREADS="ALL_CPUS", GDAL_TIFF_OVR_BLOCKSIZE="128")

    if product == "S30":
        if debug_mode:
            band_names = S30_DEBUG_BAND_NAMES
        else:
            band_names = S30_BAND_NAMES
        bname = os.path.splitext(os.path.basename(input))[0]
    if product == "L30":
        if debug_mode:
            band_names = L30_DEBUG_BAND_NAMES
        else:
            band_names = L30_BAND_NAMES
        bname = os.path.splitext(os.path.basename(input))[0]
    if product == "S30_ANGLES" or product == "L30_ANGLES":
        band_names = ANGLE_BAND_NAMES
        name = os.path.splitext(os.path.basename(input))[0]
        # Remove ANGLE suffix from basename
        bname = name.rsplit(".", 1)[0]

    with rasterio.open(input) as src_dst:
        for sds in src_dst.subdatasets:
            band = sds.split(":")[-1]
            if debug_mode:
                index = int(band)
                try:
                    band = band_names[index]
                except IndexError:
                    band = "invalid"
            if (band in band_names) or debug_mode:
                try:
                    fname = "{}.{}.tif".format(bname, band_names[band])
                except TypeError:
                    fname = "{}.{}.tif".format(bname, band)

                output_name = os.path.join(output_dir, fname)

                with rasterio.open(sds) as sub_dst:
                    # add the datum to the CRS
                    # TODO: add a test
                    if debug_mode:
                        metadata = src_dst.tags()
                        if metadata.get("HORIZONTAL_CS_CODE") is None:
                            crs_string = metadata.get("HORIZONTAL_CS_NAME")
                            zone = crs_string.split(" ")[-1]
                            new_crs = rasterio.crs.CRS.from_dict({"proj": "utm", "zone": zone})
                        else:
                            new_crs = rasterio.crs.CRS.from_string(metadata["HORIZONTAL_CS_CODE"])

                        transform = rasterio.transform.from_origin(
                            float(metadata["ULX"]), float(metadata["ULY"]), 30, 30
                        )
                    else:
                        new_crs = sub_dst.crs.to_proj4() + " +datum=WGS84"
                        transform = sub_dst.transform

                    # We create a InMemory dataset using `GDAL MEM driver`
                    # ref: https://github.com/rasterio/rasterio/blob/master/rasterio/_io.pyx#L1946-L1955
                    data = sub_dst.read()
                    info = {
                        "DATAPOINTER": data.__array_interface__["data"][0],
                        "PIXELS": sub_dst.width,
                        "LINES": sub_dst.height,
                        "BANDS": sub_dst.count,
                        "DATATYPE": _gdal_typename(data.dtype.name),
                    }
                    dataset_options = ",".join(f"{name}={val}" for name, val in info.items())
                    datasetname = f"MEM:::{dataset_options}"
                    with rasterio.open(datasetname, "r+") as src:
                        src.nodata = sub_dst.nodata  # set nodata
                        src.crs = new_crs  # set CRS
                        src.transform = transform  # add geotransform
                        # set Metadata
                        src.update_tags(**sub_dst.tags())
                        src._set_all_scales(sub_dst.scales)
                        src._set_all_offsets(sub_dst.offsets)
                        src.colorinterp = sub_dst.colorinterp
                        for i, b in enumerate(sub_dst.indexes):
                            src.set_band_description(i + 1, sub_dst.descriptions[b - 1])
                            src.update_tags(i + 1, **sub_dst.tags(b))

                        # Create COG from the `Mem` dataset
                        cog_translate(
                            src,
                            output_name,
                            output_profile,
                            config=config,
                            forward_band_tags=True,
                            overview_resampling="nearest",
                            quiet=True,
                        )

                assert cog_validate(output_name)


if __name__ == "__main__":
    main()
