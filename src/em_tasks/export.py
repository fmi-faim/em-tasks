import logging
import shutil
from pathlib import Path

import ncempy.io as nio
import numpy as np
from scipy import stats
from skimage.exposure import rescale_intensity
from tifffile import imwrite

tile_conf_header = ["# Define the number of dimensions we are working on\n",
                    "dim = 2\n",
                    "# Define the image coordinates (in pixels)\n"]


def get_files(input_dir, filename_filter, logger=logging):
    files = sorted(Path(input_dir).glob(filename_filter))
    logger.info(f"Found {len(files)} files matching '{filename_filter}'.")
    return files


def load_ser_file(ser_file, logger=logging):
    # read .ser file
    ser_data = nio.ser.serReader(ser_file)
    if "metadata" not in ser_data:
        logger.warning(f"No metadata found for file {ser_file}. Returning empty dict.")
        return {}, ser_data['data'], ser_data['pixelSize']
    return ser_data['metadata'], ser_data['data'], ser_data['pixelSize']


def process_metadata(metadata_list, save_dir, prefixes=[], filename="TileConfiguration.txt", logger=logging):
    # assert save_dir exists
    assert Path(save_dir).exists(), f"Output directory {save_dir} doesn't exist"
    with open(Path(save_dir, filename), 'w') as f:
        f.writelines(tile_conf_header)
        for meta in metadata_list:
            if 'Stage X [um]' not in meta:
                logger.warning(f"Skipping file {meta['image_file_name']}.")
                continue
            # NB: x and y are flipped in the metadata, compared to the pixel data
            logger.info(f"Processing file: {meta['image_file_name']}")
            logger.info(
                f"Metadata: {meta['Stage Y [um]'] / meta['pixel_size']} {meta['Stage X [um]'] / meta['pixel_size']}")
            f.write(
                f"{meta['image_file_name']}; ; " +
                f"({meta['Stage Y [um]'] / meta['pixel_size']}, {meta['Stage X [um]'] / meta['pixel_size']})\n")
    for p in prefixes:
        shutil.copy(Path(save_dir, filename), Path(save_dir, p))


def export_uint16(data, pixel_size, save_dir, basename, prefix="16bit"):
    dest_dir = Path(save_dir) / prefix
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    dest_path = Path(dest_dir) / (basename + '.tif')
    _write_image_with_calibration(dest_path, data, pixel_size)


def export_normalized_uint8(data, pixel_size, save_dir, basename, prefix="8bit", intensity_range=500):
    dest_dir = Path(save_dir) / prefix
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    dest_path = Path(dest_dir) / (basename + '.tif')
    mode = stats.mode(data.flatten(), keepdims=False)
    normalized = rescale_intensity(data,
                                   in_range=(mode[0] - intensity_range, mode[0] + intensity_range),
                                   out_range=np.uint8)
    _write_image_with_calibration(dest_path, normalized, pixel_size)


def _write_image_with_calibration(dest_path, image, pixel_size):
    imwrite(dest_path,
            image,
            resolution=(1. / (pixel_size[0] * 1000 * 1000), 1. / (pixel_size[1] * 1000 * 1000)),
            imagej=True,
            metadata={'unit': 'um'}
            )
