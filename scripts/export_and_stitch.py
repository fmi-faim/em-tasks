import os
from pathlib import Path

import typer
from tqdm.auto import tqdm

from em_tasks.export import (
    export_normalized_uint8,
    export_uint16,
    get_files,
    load_ser_file,
    process_metadata,
)
from em_tasks.stitch import stitch_tiles


def export_and_stitch(
    input_dir: str,
    save_dir: str,
    filename_filter="*.ser",
    intensity_range=1000,
):
    files = get_files(input_dir=input_dir, filename_filter=filename_filter)
    metadata_list = []
    for f in tqdm(files):
        metadata, data, pixel_size = load_ser_file(ser_file=f)
        basename = Path(f).stem
        export_uint16(
            data=data,
            pixel_size=pixel_size,
            save_dir=save_dir,
            basename=basename,
        )
        export_normalized_uint8(
            data=data,
            pixel_size=pixel_size,
            save_dir=save_dir,
            basename=basename,
            intensity_range=int(intensity_range),
        )
        metadata["image_file_name"] = basename + ".tif"
        metadata["pixel_size"] = pixel_size[0] * 1000 * 1000
        metadata_list.append(metadata)

    # save_position_file from metadata
    tileconf_filename = "TileConfiguration.txt"
    process_metadata(
        metadata_list=metadata_list,
        save_dir=save_dir,
        filename=tileconf_filename,
        prefixes=["8bit", "16bit"],
    )

    # stitch tiles
    subdir = os.path.join(save_dir, "8bit")
    stitch_tiles(input_dir=subdir, tileconf_filename=tileconf_filename)


if __name__ == "__main__":
    typer.run(export_and_stitch)
