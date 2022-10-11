import logging
import os

import imagej


def stitch_tiles(input_dir, tileconf_filename, save_path=None, logger=logging):
    if save_path is None:
        save_path = os.path.join(input_dir, "Fused.tif")
    logger.info("Initializing Fiji")
    ij = imagej.init("sc.fiji:fiji:2.9.0")
    macro = """
#@ String directory
#@ String layout_file
#@ String fused_path
run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration]\
 directory="+directory+" layout_file="+layout_file+" fusion_method=[Intensity of random input tile]\
 regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50\
 compute_overlap computation_parameters=[Save computation time (but use more RAM)]\
 image_output=[Fuse and display]");
saveAs("Tiff", fused_path);
run("Close");
    """
    args = {
        "directory": input_dir,
        "layout_file": tileconf_filename,
        "fused_path": save_path
    }
    logger.info("Running Grid/Collection Stitching")
    ij.py.run_macro(macro, args)
    logger.info("Done stitching.")
