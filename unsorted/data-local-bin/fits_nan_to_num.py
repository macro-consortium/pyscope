#!/usr/bin/python

# Replace nan and infinity with finite numbers in a fits image
# Force float32 data type

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc
import string # for parsing regions

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_nan_to_num.py infile.fits outfile.fits"
  print " "
  sys.exit("Replace nan and infinity with numbers in a fits image\n")
elif len(sys.argv) == 3:
  # Minimum and maximum
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  print " "
  print "Usage: fits_nan_to_num.py infile.fits outfile.fits"
  print " "
  sys.exit("Replace nan and infinity with numbers in a fits image\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header 

inhdr = inlist[0].header

# Assign image data to numpy array and get its size

inimage =  inlist[0].data.astype('float32')
xsize, ysize = inimage.shape

# Use a unit array to assure we treat the whole image in floating point 

fone = np.ones((xsize,ysize))
fimage = fone*inimage

# Replace nan and inf in the image

# Create the output the image

outimage = np.nan_to_num(fimage)

# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Image data modified by fits_nan_to_num' 
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

