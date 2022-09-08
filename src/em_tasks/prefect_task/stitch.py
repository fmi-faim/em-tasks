import prefect
from prefect import task

from em_tasks.task.stitch import stitch_tiles


@task()
def stitch_tiles_task(input_dir, tileconf_filename, save_path=None, logger=prefect.context.get("logger")):
    stitch_tiles(input_dir, tileconf_filename, save_path)
