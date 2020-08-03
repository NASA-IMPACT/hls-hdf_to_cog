import os
from click.testing import CliRunner
from hls_hdf_to_cog.hls_hdf_to_cog import main


current_dir = os.path.dirname(__file__)
test_dir = os.path.join(current_dir, "data")

# granule_basename = "HLS.S29.T12XWF.2020071T191201.v1.5{}"
granule_basename = "HLS.S30.T01LAH.2020097T222759.v1.5{}"


def test_hls_hdf_to_cog():
    inputfile = os.path.join(test_dir, granule_basename.format(".hdf"))
    runner = CliRunner()
    result = runner.invoke(main, [inputfile, "--output-dir", test_dir])
    print(result.exception)
    assert result.exit_code == 0
