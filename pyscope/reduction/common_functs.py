import logging
import os
from astropy.io import fits
import prettytable
 
logger = logging.getLogger(__name__)
 
def read_fits_file(file_path):
    try:
        with fits.open(file_path) as hdu:
            header = hdu[0].header
            data = hdu[0].data
            return header, data
    except Exception as e:
        logger.warning(f"Could not open {file_path}: {e}")
        return None, None
 
def file_exists(file_path):
    return os.path.exists(file_path)
 
#create table
