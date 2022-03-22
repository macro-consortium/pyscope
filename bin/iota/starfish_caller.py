### S T A R F I S H ###        (Calling Script)

# import Python libraries
import datetime
import os
import sys
import tempfile
import time
from win32com.client import Dispatch
#import seabreeze.spectrometers as sb
import matplotlib.pyplot as plt
import csv


# import spectrometer libraries
from iotalib import convert
from iotalib import talonwcs
#import VAOSpec.py
import calibrate_target_pixel_sf
import center_target_on_pixel_sf
import slew_grid_sf


# User configuration values
configuration_file = sys.argv[1]

TARGET_RA_J2000_HOURS = sys.argv[2]
TARGET_DEC_J2000_DEGS = sys.argv[3]
EXPOSURE_LENGTH_SECONDS = sys.argv[4]
RASTER_GRID_RA_COLUMNS = sys.argv[5]
RASTER_GRID_DEC_ROWS = sys.argv[6]
RA_GRID_SPACING_ARCSEC = sys.argv[7]
DEC_GRID_SPACING_ARCSEC = sys.argv[8]
CENTER_RA_J2000_HOURS = sys.argv[9]
CENTER_DEC_J2000_HOURS = sys.argv[10]

# Tasks
final_task = int(sys.argv[11])
if final_task == 1:    #Take a spectrum
    command1 = "python center_target_on_pixel_sf.py" + " " + str(configuration_file) + " " + str(TARGET_RA_J2000_HOURS) + " " + str(TARGET_DEC_J2000_DEGS)
    os.system(command1)
    continue_to_spectrum = input("Press enter to take your spectrum.")
    '''VAOSpec.MayaSpectrometer.multipleExposures(EXPOSURE_LENGTH_SECONDS)
    VAOSpec.MayaSpectrometer.showLastSpec()
    save = raw_input("Would you like to save this spectra? Please enter Y or N (case sensitive): ")
    if save == "Y":
        filepath = raw_input("Please enter the full directory path of the folder you would like to save your spectrum in: ")
        target = raw_input("Please enter the name of your target object: ")
        VAOSpec.MayaSpectrometer.saveLastSpec(filepath, target)
    elif save == "N":
        print "You will now be returned to the main menu."
        VAOSpec.MayaSpectrometer.close()
        sys.exit()
        os.system("python starfish.py")'''
elif final_task == 2:    #Slew grid
    command2 = "python slew_grid_sf.py" + " " + str(configuration_file) + " " + str(CENTER_RA_J2000_HOURS) + " " + str(CENTER_DEC_J2000_HOURS) + " " + sys(EXPOSURE_LENGTH_SECONDS) + " " + str(RASTER_GRID_RA_COLUMNS) + " " + str(RASTER_GRID_DEC_ROWS) + " " + str(RA_GRID_SPACING_ARCSEC) + " " + str(DEC_GRID_SPACING_ARCSEC)
    os.system(command2)
else:    #Calculate target pixel
    command3= "python calibrate_target_pixel_sf.py" + " " + str(configuration_file) + " " + str(TARGET_RA_J2000_HOURS) + " " + str(TARGET_DEC_J2000_DEGS) + " " + str(EXPOSURE_LENGTH_SECONDS)
    os.system(command3)
    print("You have now recalculated the spectrometer pointing position.  For this position to be used for future observations, you must now edit the default configuration file.")
    print()
    print("*******************************")
    print("WARNING: The values defined in the default configuration file are in use by multiple programs. Please be careful not to change any values other than those specified in the steps below.")
    print("*******************************")
    print()
    print("Follow these steps to edit the default configuration values:")
    print("1. Find and open the file vao_default_config_spec.txt in a text editor.")
    print("3. Edit the value in line 5 to be the new value of TARGET_PIXEL_X_UNBINNED.")
    print("4. Edit the value in line 6 to be the new value of TARGET_PIXEL_Y_UNBINNED.")
    print("5. Save your changes and exit.")