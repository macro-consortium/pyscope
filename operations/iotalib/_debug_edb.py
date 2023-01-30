"""
Main telrun script. Called from telrun.py, which catches any
errors we may throw and attempts to send e-mail notification.
"""

# Built-in Python imports
import atexit
import logging
import math
import os
import shutil
import signal
import sys
import time

# Third-party imports
import ephem
from astropy.io import fits as pyfits
from win32com.client import Dispatch

# iotalib imports
from . import airmass
from . import center_target
from . import comhelper
from . import convert
from . import config_focus_offsets
from . import config_observatory
from . import config_telrun
from . import config_wcs
from . import consoleutil
from . import email_warnings_thread
from . import observatory
from . import paths
from . import telrunfile
from . import telrun_gui
from . import telrun_status
from . import check_roof

def read_configs():
    config_observatory.read()
    config_focus_offsets.read()
    config_telrun.read()
    config_wcs.read()

def setup_observatory_connections():
    #telrun_status.camera_state = "Connecting"
    #observatory.setup_camera()
    #telrun_status.camera_state = "Connected"

    #telrun_status.mount_state = "Connecting"
    observatory.setup_mount()
    #telrun_status.mount_state = "Connected"

    #observatory.setup_focuser()

    #telrun_status.autofocus_state = "Connecting"
    #observatory.setup_autofocus()
    #telrun_status.autofocus_state = "Connected"

    #observatory.setup_weather()
    pass



def run():
    FORMAT = '%(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, stream=sys.stdout)
    logging.info("Hello")
    
    read_configs()
    setup_observatory_connections()
    
    main_operation_loop()


# Keep track of the file modification time for any 
# telrun.sls files that we get all the way through, so
# that we don't try to reload the same file on the next
# pass through this loop
completed_telrun_file_modification_time = 0

def main_operation_loop():

    telrun_sls_path = paths.telrun_sls_path("telrun.sls")
    

    logging.info("Loading existing telrun.sls")
    telrun_file = telrunfile.TelrunFile(telrun_sls_path)    
    telrun_file_finished = run_scans(telrun_file)
        


def run_scans(telrun_file):
    num_scans = len(telrun_file.scans)
    telrun_status.total_scan_count = num_scans

    for scan_index in range(num_scans):
        scan = telrun_file.scans[scan_index]

        #logging.info("Processing scan %d of %d:", scan_index+1, num_scans)
        logging.info("%s, %s" % (scan.imagefn, scan.obj))

        scan.obj.compute(observatory.get_site_now())
        
        target_ra_app_hours = convert.rads_to_hours(scan.obj.ra)
        target_dec_app_degs = convert.rads_to_degs(scan.obj.dec)

        (target_ra_j2000_hours, target_dec_j2000_degs) = convert.jnow_to_j2000(target_ra_app_hours, target_dec_app_degs)

        logging.info("J2000 RA = %s, Dec = %s" % (convert.to_dms(target_ra_j2000_hours), convert.to_dms(target_dec_j2000_degs)))


if __name__ == "__main__":
    run()

