from pathlib import Path

import numpy
import pytest

from em_tasks.export import (
    export_normalized_uint8,
    export_uint16,
    get_files,
    load_ser_file,
    process_metadata,
)


@pytest.fixture
def sample_ser_file():
    return "./data/Binning4_image1_1.ser"


@pytest.fixture
def sample_data():
    numpy.random.seed(0)
    image = numpy.random.rand(32, 32) * 4096
    return image.astype("uint16")


@pytest.fixture
def sample_metadata():
    return [
        {
            "image_file_name": "1.tif",
            "pixel_size": 1.0,
            "Stage X [um]": 10.0,
            "Stage Y [um]": 40.0,
        },
        {
            "image_file_name": "2.tif",
            "pixel_size": 1.0,
            "Stage X [um]": 20.0,
            "Stage Y [um]": 50.0,
        },
        {"image_file_name": "missing_metadata.tif", "pixel_size": 1.0},
        {
            "image_file_name": "3.tif",
            "pixel_size": 1.0,
            "Stage X [um]": 30.0,
            "Stage Y [um]": 60.0,
        },
    ]


@pytest.fixture
def expected_tileconf():
    return """# Define the number of dimensions we are working on
dim = 2
# Define the image coordinates (in pixels)
1.tif; ; (40.0, 10.0)
2.tif; ; (50.0, 20.0)
3.tif; ; (60.0, 30.0)
"""


def test_get_files(tmp_path):
    files = get_files(tmp_path, "*.tif")
    assert len(files) == 0


def test_load_ser_file(sample_ser_file):
    metadata, data, pixel_size = load_ser_file(sample_ser_file)
    assert data.shape == (512, 512)
    assert pixel_size[0] == pixel_size[1]
    assert pixel_size[0] == 1.1104135456663472e-08
    assert metadata["Stage X [um]"] is not None


def test_export_uint16(tmp_path, sample_data):
    assert sample_data.shape == (32, 32)
    basename = "basename"
    export_uint16(sample_data, [1.0, 1.0], tmp_path, basename)
    assert Path(tmp_path, "16bit", basename + ".tif").exists()


def test_export_normalized_uint8(tmp_path, sample_data):
    assert sample_data.shape == (32, 32)
    basename = "basename"
    export_normalized_uint8(sample_data, [1.0, 1.0], tmp_path, basename)
    assert Path(tmp_path, "8bit", basename + ".tif").exists()


def test_process_metadata(sample_metadata, tmp_path, expected_tileconf):
    process_metadata(sample_metadata, tmp_path)
    tile_conf_file = Path(tmp_path, "TileConfiguration.txt")
    assert tile_conf_file.exists()
    with open(tile_conf_file) as file:
        assert file.read() == expected_tileconf


def test_process_metadata_with_wrong_path(sample_metadata):
    tmp_path = Path("/non/existent/path")
    with pytest.raises(AssertionError):
        process_metadata(sample_metadata, tmp_path)
