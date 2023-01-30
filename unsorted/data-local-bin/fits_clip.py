#!/usr/bin/python

# Clip levels in a fits image

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc
import string # for parsing regions
#import re # for parsing regions

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_clip.py infile.fits outfile.fits minval maxval"
  print " "
  sys.exit("Clips at lower and upper levels based on minimum and maximum values \n")
elif len(sys.argv) ==5:
  # Minimum and maximum
  infile = sys.argv[1]
  outfile = sys.argv[2]
  minval = float(sys.argv[3])
  maxval = float(sys.argv[4])
  if minval >= maxval:
    sys.exit("The specified minimum must be less than the maximum \n")
else:
  print " "
  print "Usage: fits_clip.py infile.fits outfile.fits minval maxval"
  print " "
  sys.exit("Clips at lower and upper levels based on minimum and maximum values\n")

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

# Clip the image based on min and max

fimage[fimage < minval] = minval
fimage[fimage > maxval] = maxval

# Create the output the image

outimage = fimage

# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Image clipped by fits_clip' 
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

