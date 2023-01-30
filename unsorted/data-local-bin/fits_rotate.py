#!/usr/bin/python

# Rotate an image an arbitrary angle in degrees

import os
import sys
import numpy as np
import scipy.ndimage
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_rotate.py  degrees infile.fits outfile.fits "
  print " "
  sys.exit("Rotate an image an arbitrary angle in degrees with spline interpolation\n")
elif len(sys.argv) == 4:
  degrees = float(sys.argv[1])
  infile = sys.argv[2]
  outfile = sys.argv[3]
else:
  print " "
  print "Usage: fits_rotate.py  degrees infile.fits outfile.fits "
  print " "
  sys.exit("Rotate an image an arbitrary angle in degrees with spline interpolation\n")


# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header in case it is needed later

inhdr = inlist[0].header

# Assign image data to a numpy array

inimage =  inlist[0].data

# Rotate this image using scipy

outimage = scipy.ndimage.rotate(inimage, degrees)

# Create an output list from the new image 
# Use float32 for output type 

outlist = pyfits.PrimaryHDU(outimage.astype('float32'))

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Rotated %7.3f degrees by fits_rotate' %(degrees,)
outhdr['history'] = 'Image file ' + infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the list and exit

inlist.close()

exit()

