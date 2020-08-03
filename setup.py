from setuptools import setup, find_packages

setup(
    name="hls_hdf_to_cog",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click", "rasterio", "rio_cogeo", ],
    extras_require={"dev": ["flake8", "black"], "test": ["flake8", "pytest"]},
    entry_points={"console_scripts": ["hdf_to_cog=hls_hdf_to_cog.hls_hdf_to_cog:main", ]},
)
