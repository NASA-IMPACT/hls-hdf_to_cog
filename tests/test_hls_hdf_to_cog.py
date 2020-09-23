import os
from click.testing import CliRunner
from hls_hdf_to_cog.hls_hdf_to_cog import main


current_dir = os.path.dirname(__file__)
test_dir = os.path.join(current_dir, "data")
data_dir = "/hls-testing_data"


def test_hls_hdf_to_cog_S30():
    granule_basename = "HLS.S30.T01LAH.2020097T222759.v1.5{}"
    inputfile = os.path.join(data_dir, granule_basename.format(".hdf"))
    runner = CliRunner()
    result = runner.invoke(main, [inputfile, "--output-dir", test_dir,
                                  "--product", "S30"])
    print(result.exception)
    assert result.exit_code == 0


def test_hls_hdf_to_cog_L30():
    granule_basename = "HLS.L30.39TVF.2020158.165.v1.5{}"
    inputfile = os.path.join(data_dir, granule_basename.format(".hdf"))
    runner = CliRunner()
    result = runner.invoke(main, [inputfile, "--output-dir", test_dir,
                                  "--product", "L30"])
    print(result.exception)
    assert result.exit_code == 0


def test_hls_hdf_to_cog_S30_Angle():
    granule_basename = "HLS.S30.T35JMG.2020192T074619.v1.5.ANGLE{}"
    inputfile = os.path.join(data_dir, granule_basename.format(".hdf"))
    runner = CliRunner(echo_stdin=True)
    result = runner.invoke(main, [inputfile, "--output-dir", test_dir,
                                  "--product", "S30_ANGLES"])
    print(result.exception)
    assert result.exit_code == 0
