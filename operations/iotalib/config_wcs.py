"""
Read and validate the expected config files from wcs.cfg
"""

from . import config

values = None
valid_config = False

def read():
    global values
    global valid_config

    values = config.read("wcs.cfg")

    values.require_float("arcsec_per_pixel_unbinned") # Approximate image scale of UNBINNED image, in arcseconds per pixel
    values.require_bool("mirrored") # If image can be rotated so that North is Up and East is Right, this should be True to ensure that a WCS solution can be found.

    valid_config = True

