#!/usr/bin/python

# Make a floating point threshold mask matching a fits image
# Converted to Boolean true or 1, will block that part of the image for subsequent processing

# This code is also a prototype for other mask generators  

# See http://docs.scipy.org/doc/numpy/reference/routines.ma.html
# Force float32 data type

import os
import sys
import numpy as np
import numpy.ma as ma
import pyfits
from time import gmtime, strftime  # for utc
import string # for parsing regions

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_make_threshold_mask.py infile.fits lower upper  outfile.fits"
  print " "
  sys.exit("Make a mask between lower and upper values in a fits file.\n")
elif len(sys.argv) == 5:
  infile = sys.argv[1]
  lower  = float(sys.argv[2])
  upper = float(sys.argv[3])
  outfile = sys.argv[4]
else:
  print " "
  print "Usage: fits_make_threshold_mask.py infile.fits lower upper  outfile.fits"
  print " "
  sys.exit("Make a mask between lower and upper values in a fits file. \n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Open the fits files readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header 

inhdr = inlist[0].header


# Assign image data to numpy arrays

inimage =  inlist[0].data.astype('float32')

   
# Create the mask


maskedlower = ma.masked_where(inimage > lower, inimage, copy=True)
maskedupper = ma.masked_where(inimage < upper, inimage, copy=True)
outmask = maskedlower.mask * maskedupper.mask

# Create a numpy array from the masked array with floating point zero in unmasked pixels

outimage = ma.filled( outmask, 0.)


# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Mask of image '+  infile
outhdr['history'] = 'Lower bound '+  ( "%e" % lower) 
outhdr['history'] = 'Upper bound '+  ( "%e" % upper) 

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

