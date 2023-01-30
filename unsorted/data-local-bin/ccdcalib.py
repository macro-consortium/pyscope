#!/usr/bin/env python

'''
Fully calibrated a raw science image using master calibration images [bias, dark, flat] using this scheme:
R= raw science frame
B = master bias (median averaged)
D = master dark (median averaged)
T = scaled thermal = (D - B) * t/t0 (per pixel multiply, where t = science exposure time, t0 = thermal exp. time)
F = master flat (filter specfic, median averaged)
NF = (F-B)/mean(F-B): normalized flat 

calibrated frame = (R - B - T) / NF

N.B. 
1. This assumes the flat exposure time is small so no dark correction is needed).
2. Output is 16-bit for compatibility with Talon software
3. Does not use border pixels to calculate mean (outer 20 rows,columns)

RLM 28 Oct  2013
15 Oct 2015:  Modify for Gemini/Apogee F47 camera
'''

# import needed modules
import sys, os, getopt
from numpy import *
import pyfits

 
def usage():
    print 'Usage: cal-image [-b bias_image] [-d [dark_image] [-f flat_image] [-H hot pixel removal] [-v = verbose] [-h = help] raw_fits_file'
    sys.exit(1)
    
def help_usage():
    print 'Cal-image applies bias, thermal, flat and [optionally] hot pixel corrections to input FITS image (in place)'
    print 'Note: All correction images optional: default to those in archive/calib folder' 
    print 'Usage: cal-image [-b bias image] [-d [dark image] [-f flat image] [-H hot pixel removal] [-v = verbose] [-h = help] raw_fits_file'
    sys.exit(1)
    
def getargs():
    ''' retrieves filenames and optional arguments from command line'''
    try:
        opts, arg = getopt.getopt(sys.argv[1:], "vHb:d:f:h")
    except getopt.GetoptError, err:
        print str(err) # Prints  "option -a not recognized"
        usage()
    if len(arg) == 0: usage()
    verbose = False; hot = False   
    bias_image, dark_image, flat_image  = ['','','']; fname = arg[0] 
    for opt in opts:
        if opt[0] in ('-v','--verbose'):
        	verbose = True
        elif opt[0] in ('-H','--Hot'):
        	hot = True
        elif opt[0] in ('-b','--bias'):
        	bias_image = opt[1]
        elif opt[0] in ('-d','--dark'):
        	dark_image = opt[1]
        elif opt[0] in ('-f','--flat'):
        	flat_image = opt[1]
        elif opt[0] in ("-h", "--help"):
            help_usage()
    return verbose, hot, bias_image, dark_image, flat_image, fname
    


# main program   

# Set xmin, xmax, ymin ,ymax for calculating means etc ( i.e., do not use borders) 
border = 16; size = 1047
xmin = ymin  = border; xmax = ymax = size - border

# Set default file names, directory
calib_dir = '/usr/local/telescope/archive/calib/'
#calib_dir = './'
bias_master = calib_dir+'master-bias.fts'
dark_master = calib_dir+'master-dark.fts'

# Get commandline parameters
verbose, hot, bias_image, dark_image, flat_image, raw_image = getargs()

# set bias, dark, flat defaults if filenames not specified
if bias_image == '' : bias_image = bias_master
if dark_image == '' : dark_image = dark_master
if flat_image == '':
	hdr_raw = pyfits.getheader(raw_image)
	filter_raw = hdr_raw['filter'][0]
	flat_image = '%smaster-flat-%s.fts'% (calib_dir,filter_raw)

# Check for existence of user-specified calibration and science images
if not os.path.isfile(raw_image) : sys.exit('Raw image %s does not exist, exiting'  % raw_image)
if not os.path.isfile(bias_image): sys.exit('Bias image %s does not exist, exiting' % bias_image)
if not os.path.isfile(dark_image): sys.exit('Dark image %s does not exist, exiting' % dark_image)
if not os.path.isfile(flat_image): sys.exit('Flat image %s does not exist, exiting' % flat_image)



# set variables
im_raw =  pyfits.getdata(raw_image)  ; hdr_raw =  pyfits.getheader(raw_image)
im_bias = pyfits.getdata(bias_image) ; hdr_bias = pyfits.getheader(bias_image)
im_dark = pyfits.getdata(dark_image) ; hdr_dark = pyfits.getheader(dark_image)
im_flat = pyfits.getdata(flat_image) ; hdr_flat = pyfits.getheader(flat_image)

# Check if flat image has a filter matched to science image
filter_raw = hdr_raw['filter']; filter_flat = hdr_flat['filter']
if filter_raw != filter_flat: sys.exit('Raw (%s), flat (%s) filters do not match, exiting' % (filter_raw, filter_flat) )

# Check if the image has already been calibrated
if  'CALSTAT' in hdr_raw: sys.exit( 'Image %s has already been calibrated, exiting' % raw_image )

# Flat: Normalize by subtracting the bias and normalizing to one
im_flat -= im_bias
im_flat /= mean(im_flat[xmin:xmax,ymin:ymax])

# Dark: subtract bias and scale for ratio of exposure times
im_thermal = im_dark - im_bias
t_ratio = float(hdr_raw['exptime']) / float(hdr_dark['exptime'])
im_thermal *= t_ratio

# Subtract bias and scaled thermal, divide by normalized flat
im_cal = (im_raw - im_bias - im_thermal ) / im_flat

# remove negative values
im_cal = clip(im_cal, 0, 65536)

# Construct new header from original raw image, adding appropriate comments
hdr_cal = pyfits.getheader(raw_image)
s0 = 'Calibrated using ccdcalib'
s1 = 'Bias frame = %s' % bias_image
s2 = 'Dark frame = %s' % dark_image 
s3 = 'Flat frame = %s' % flat_image
hdr_cal.add_comment(s0); hdr_cal.add_comment(s1)
hdr_cal.add_comment(s2); hdr_cal.add_comment(s3)
hdr_cal.update(key='CALSTAT', value='BDF')
hdu = pyfits.PrimaryHDU(im_cal,hdr_cal)
# Convert to 16-bit for Talon (camera,etc)
hdu.scale('int16','',bzero=32768)

# write FITS file
hdulist = pyfits.HDUList([hdu])
outfile = raw_image
# write file
if verbose: print 'writing %s' % (outfile)
hdulist.writeto(outfile, clobber=True, output_verify='ignore')
hdulist.close()

      
