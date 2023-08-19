from datetime import datetime
import math
import os
import sys
import tempfile
import time
import astropy.io.fits as fits
import numpy

import relimport
from iotalib import convert
from iotalib import talonwcs
from iotalib import rst
import pulsar_dimmer

import ephem
from win32com.client import Dispatch

"""
This script attempts to put a target RA and Dec at a particular pixel position
(which may be outside the bounds of the physical CCD in the case of an off-axis
spectrometer fiber).

The script slews to a target, takes an image, finds a WCS solution and offsets
the mount to place the target RA/Dec at the requested pixel position. This process
repeats until the target is positioned within a specified tolerance or the maximum
number of attempts has been exceeded.

The target pixel position can be calibrated by manually positioning a star at the
target position and running the calibrate_target_pixel script.
"""

### CONFIGURATION VALUES ########################

#configuration_file = sys.argv[1]
configuration_file = "calibration_config.txt"
config = []
with open(configuration_file) as infile:
    for line in infile:
        config.append((line.split()[0]))    

#MOUNT_DRIVER = "ASCOM.SoftwareBisque.Telescope"  # Use this for the Paramount ME (controlled through TheSky)
MOUNT_DRIVER = "SiTech.Telescope"
HOME_MOUNT = True

OBJECT_NAME = ""                       # Provides the name of an object to search for in the SIMBAD Database (If empty string, use provided coordinates)
TARGET_AZ = float(config[1]) # RA coordinates of the target star, in J2000 hours
TARGET_ALT = float(config[2]) # Dec coordinates of the target star, in J2000 degrees
SETTLE_TIME_SECONDS = float(config[3])               # Pause for this many seconds after slewing to each target before taking an image

BINNING = float(config[4])                            # Image binning (higher binning reduces resolution but speeds up image readout time) 

EXPOSURE_LENGTH_SECONDS_DARK = float(config[8])           # Exposure length of each dark image, in seconds
NUMBER_DARKS = float(config[6])
NUMBER_BIAS = float(config[7])
NUMBER_FLATS = float(config[5])
FILTER_NAMES = config[9].split(',') #["L","R","V","B","H","G","W","N"]
#FILTER_EXPOSURE_TIME = [2,2,2.5,7,15,0,2,2]
FILTER_EXPOSURE_TIME = [float(x) for x in config[10].split(',')]
FILTER_LAMP_INTENSITY =[int(x) for x in config[11].split(',')] #[1,100,150,254,254,0,150,1]

MIRRORED = False                       # If image can be rotated so that North is Up and East is Right, this should be True to ensure that a WCS solution can be found.

SAVE_IMAGES = True                     # If True, each image will be saved to SAVE_DATA_PATH
#SAVE_DATA_PATH = r"{MyDocuments}\Calibration\{Timestamp}"
SAVE_DATA_PATH = config[0] # Script data will be saved to this location.
MASTER_DATA_PATH = config[12]

print(SAVE_DATA_PATH)


### END CONFIGURATION VALUES ########################


def main():
    """
    Starting point for the center_target_on_pixel script
    """

    print("Launching mount control software...")
    mount = Dispatch(MOUNT_DRIVER)

    print("Connecting to mount...")
    mount.Connected = True

    print("Launching MaxIm DL...")
    maxim = Dispatch("MaxIm.Application")
    maxim.LockApp = True
    
    camera = Dispatch("MaxIm.CCDCamera")
    camera.DisableAutoShutdown = True

    print("Connecting to camera...")
    camera.LinkEnabled = True

    if HOME_MOUNT:
        print("Homing Mount")
        mount.FindHome
    
    if mount.CanSetTracking:
        # Not all mount drivers support turning tracking on/off.
        # For example, the ASCOM driver for TheSky does not support it.
        # However, if it is supported, make sure tracking is on before slewing
        mount.Tracking = False
    
    save_data_path = parse_filepath_template(SAVE_DATA_PATH)
    master_data_path = parse_filepath_template(MASTER_DATA_PATH)
    
    if SAVE_IMAGES and not os.path.isdir(save_data_path):
        print("Creating directory %s" % save_data_path)
        os.makedirs(save_data_path)


        
    print("Slewing to Azimuth %s, Altitude %s" % (TARGET_AZ,TARGET_ALT))
    
    mount.SlewToAltAz(TARGET_AZ, TARGET_ALT)
    mount.Tracking = False
    print("Settling...")
    time.sleep(SETTLE_TIME_SECONDS)
    
    darknum = 0
    print("Taking %d dark images with %d second exposure..." % (NUMBER_DARKS,EXPOSURE_LENGTH_SECONDS_DARK))
    while darknum < NUMBER_DARKS:
        
        camera.BinX = BINNING
        camera.BinY = BINNING
        camera.Expose(EXPOSURE_LENGTH_SECONDS_DARK, 0) #The 0 indicates that the shutter is closed
        while not camera.ImageReady:
            time.sleep(0.1)
        
        darknum = darknum+1
        print("Dark %d of %d complete" % (darknum,NUMBER_DARKS))
        
        tempfilename = os.path.join(tempfile.gettempdir(), "Dark.fits")
        camera.SaveImage(tempfilename)

        if SAVE_IMAGES:
            filename = "Dark_%03d.fits" % (darknum)
            #filename = "Dark.fits"
            filepath = os.path.join(save_data_path, filename)
            #print "Saving image to", filepath
            camera.SaveImage(filepath)
    
    biasnum = 0
    print("Taking %d bias images..." % (NUMBER_BIAS))
    while biasnum < NUMBER_BIAS:
        camera.BinX = BINNING
        camera.BinY = BINNING
        camera.Expose(0, 0) #Bias image take as a 0 second dark exposure
        while not camera.ImageReady:
            time.sleep(0.1)

        biasnum = biasnum+1
        print("Bias %d of %d complete" % (biasnum,NUMBER_BIAS))


        tempfilename = os.path.join(tempfile.gettempdir(), "Bias.fits")
        camera.SaveImage(tempfilename)

        if SAVE_IMAGES:
            filename = "Bias_%03d.fits" % (biasnum)
            #filename = "Bias.fits" 
            filepath = os.path.join(save_data_path, filename)
            #print "Saving image to", filepath
            camera.SaveImage(filepath)
    
    filternum=0
    for fname in FILTER_NAMES:
        #camera.set_active_filter(filternum)
        if FILTER_EXPOSURE_TIME[filternum] == 0:
            print("Skipping filter %s." % (fname))
        else:
            flatnum=0
            print("Setting flat field lamps to brightness level %d" % (FILTER_LAMP_INTENSITY[filternum]))
            pulsar_dimmer.dimmer(FILTER_LAMP_INTENSITY[filternum])
            time.sleep(2)
            print("Taking %d flat images with %d second exposure in filter %s..." % (NUMBER_FLATS,FILTER_EXPOSURE_TIME[filternum],fname))
            while flatnum < NUMBER_FLATS:
                camera.BinX = BINNING
                camera.BinY = BINNING
                camera.Expose(FILTER_EXPOSURE_TIME[filternum], 1, filternum)
                while not camera.ImageReady:
                    time.sleep(0.1)
                flatnum=flatnum+1
                print("Flat %d of %d for filter %s complete" % (flatnum,NUMBER_FLATS,fname))
                camera.SetFITSKey('IMAGETYP','FLAT    ')
                tempfilename = os.path.join(tempfile.gettempdir(), "Flat.fits")
                camera.SaveImage(tempfilename)

                if SAVE_IMAGES:
                    filename = "Flat_%03d%s.fits" % (flatnum,fname)
                    filepath = os.path.join(save_data_path, filename)
                    #print "Saving image to", filepath
                    camera.SaveImage(filepath)
        filternum=filternum + 1
        print('30 second cooldown...')
        time.sleep(30)
    print("Turning off calibration lamps...")
    pulsar_dimmer.dimmer(0) # Turn off the flat field lamps when finished exposing
    
"""
    print "Now median averaging the dark frames..."
    darknum=0
    while darknum < NUMBER_DARKS-1:
        darknum = darknum+1
        filename = "Dark_%03d.fits" % (darknum)
        filepath = os.path.join(save_data_path,filename)
        print "Loading dark image %s" % (filename)

        # if not 'dark_stack' in locals():
        #     hdu_list = fits.open(filepath)
        #     prihdr = hdu_list[0].header
        #     dark_stack = fits.getdata(filepath)
        #     #dark_stack = fits.getdata(filepath)
        # else:
        #     dark_stack = numpy.dstack((dark_stack,fits.getdata(filepath)))

        hdu_list = fits.open(filepath)
        prihdr = hdu_list[0].header
        dark_image = fits.getdata(filepath)
        if not 'dark_stack' in locals(): 
            dark_stack = numpy.zeros(shape=dark_image.shape + (NUMBER_DARKS,))
        dark_stack[:,:,darknum]


    if not darknum == 0:
        dark_master = numpy.median(dark_stack, axis=2)
        prihdr['IMAGETYP'] = 'DARK'
        hdu = fits.PrimaryHDU(dark_master,prihdr)
        darkhdulist = fits.HDUList([hdu])
        filename = "Master_Dark.fits"
        filepath = os.path.join(save_data_path,filename)
        print "Saving master dark image"
        darkhdulist.writeto(filepath)
        filepath = os.path.join(master_data_path,filename)
        darkhdulist.writeto(filepath,clobber=True)
        darkhdulist.close()
        hdu_list.close()
        dark_stack=None
        dark_master=None

    print "Now median averaging the bias frames..."
    biasnum=0
    while biasnum < NUMBER_BIAS-1:
        biasnum = biasnum+1
        filename = "Bias_%03d.fits" % (biasnum)
        filepath = os.path.join(save_data_path,filename)
        print "Loading bias image %s" % (filename)
        hdu_list = fits.open(filepath)
        prihdr = hdu_list[0].header
        bias_image = fits.getdata(filepath)
        if not 'bias_stack' in locals(): 
            bias_stack = numpy.zeros(shape=bias_image.shape + (NUMBER_BIAS,))
        bias_stack[:,:,biasnum]
        # if not 'bias_stack' in locals():
        #     hdu_list = fits.open(filepath)
        #     prihdr = hdu_list[0].header
        #     hdu_list.close()
        #     bias_stack = fits.getdata(filepath)
        #     #dark_stack = fits.getdata(filepath)
        # else:
        #     bias_stack = numpy.dstack((bias_stack,fits.getdata(filepath)))
    if not biasnum == 0:
        bias_master = numpy.median(bias_stack, axis=2)
        prihdr['IMAGETYP'] = 'BIAS    '
        hdu = fits.PrimaryHDU(bias_master,prihdr)
        biashdulist = fits.HDUList([hdu])
        filename = "Master_Bias.fits"
        filepath = os.path.join(save_data_path,filename)
        print "Saving master Bias image"
        biashdulist.writeto(filepath)
        filepath = os.path.join(master_data_path,filename)
        biashdulist.writeto(filepath,clobber=True)
        biashdulist.close()
        
        bias_stack=None
        bias_master=None

    filternum=0
    for fname in FILTER_NAMES:
        if FILTER_EXPOSURE_TIME[filternum] == 0:
            print "Skiping filter %s." % (fname)
        else:
            flatnum=0
            print "Now median averaging the flat frames for the %s filter..." % (fname)
            while flatnum < NUMBER_FLATS:
                flatnum = flatnum+1
                filename = "Flat_%03d%s.fits" % (flatnum,fname)
                filepath = os.path.join(save_data_path,filename)
                print "Loading flat image %s" % (filename)

                hdu_list = fits.open(filepath)
                prihdr = hdu_list[0].header
                flat_image = fits.getdata(filepath)
                if not 'flat_stack' in locals(): 
                    flat_stack = numpy.zeros(shape=flat_image.shape + (NUMBER_FLATS,))
                #if flat_stack is None:
                #    flat_stack = numpy.zeros(shape=flat_image.shape + (NUMBER_FLATS,))
                
                flat_stack[:,:,flatnum-1]

                # if flatnum==1:
                #     hdu_list = fits.open(filepath)
                #     prihdr = hdu_list[0].header
                #     flat_stack = fits.getdata(filepath)
                # else:
                #     flat_stack = numpy.dstack((flat_stack,fits.getdata(filepath)))
            if not flatnum == 0:
                flat_master = numpy.median(flat_stack, axis=2)
                prihdr['IMAGETYP'] = 'FLAT    '
                hdu = fits.PrimaryHDU(flat_master,prihdr)

                flathdulist = fits.HDUList([hdu])
                filename = "Master_Flat_%s.fits" % (fname)
                filepath = os.path.join(save_data_path,filename)
                print "Saving master flat image for filter %s" % (fname)
                flathdulist.writeto(filepath)
                filepath = os.path.join(master_data_path,filename)
                flathdulist.writeto(filepath,clobber=True)
                flathdulist.close()
                hdu_list.close()
 
        filternum=filternum+1
"""

def parse_filepath_template(template):
    my_documents_path = os.path.expanduser(r'~\My Documents')
    timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    
    template = template.replace('{MyDocuments}', my_documents_path)
    template = template.replace('{Timestamp}', timestamp)
    
    return template

if __name__ == "__main__":
    main()

