from typing import Tuple, Any

import prefect
from prefect import task

from em_tasks.task.export import get_files, load_ser_file, export_uint16, export_normalized_uint8, process_metadata


@task()
def get_files_task(input_dir, filename_filter):
    return get_files(input_dir=input_dir, filename_filter=filename_filter, logger=prefect.context.get("logger"))


@task(nout=3)
def load_ser_file_task(ser_file) -> Tuple[Any, Any, Any]:
    return load_ser_file(ser_file=ser_file, logger=prefect.context.get("logger"))


@task()
def export_uint16_task(data, pixel_size, save_dir, basename, prefix="16bit"):
    export_uint16(data=data, pixel_size=pixel_size, save_dir=save_dir, basename=basename, prefix=prefix)


@task()
def export_normalized_uint8_task(data, pixel_size, save_dir, basename, prefix, intensity_range):
    export_normalized_uint8(data=data,
                            pixel_size=pixel_size,
                            save_dir=save_dir,
                            basename=basename,
                            prefix=prefix,
                            intensity_range=intensity_range
                            )


@task()
def process_metadata_task(metadata_list, save_dir, prefixes, filename):
    process_metadata(metadata_list=metadata_list, save_dir=save_dir, filename=filename,
                     prefixes = prefixes, logger=prefect.context.get("logger"))

