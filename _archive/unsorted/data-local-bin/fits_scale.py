#!/usr/bin/python

# Scale a fits image

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_scale.py infile.fits outfile.fits a0 a1 a2"
  print " "
  sys.exit("Scales a fits file by a0 + a1*s + a2*s^2\n")
elif len(sys.argv) == 6:
  # Quadratic
  infile = sys.argv[1]
  outfile = sys.argv[2]
  a0 = float(sys.argv[3])
  a1 = float(sys.argv[4])
  a2 = float(sys.argv[5])
elif len(sys.argv) == 5:
  # Linear
  infile = sys.argv[1]
  outfile = sys.argv[2]
  a0 = float(sys.argv[3])
  a1 = float(sys.argv[4])
  a2 = 0.
elif len(sys.argv) == 4:
  # Add only
  infile = sys.argv[1]
  outfile = sys.argv[2]
  a0 = float(sys.argv[3])
  a1 = 1.
  a2 = 0.
else:
  print " "
  print "Usage: fits_scale.py infile.fits outfile.fits a0 a1 a2"
  print " "
  sys.exit("Scales a fits file by a0 + a1*s + a2*s^2\n")

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

# Scale the image

outimage = a0 * fone + a1 * fimage + a2 * fimage * fimage

# Create the fits object for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Create strings for the scaling history

scale0 = 'a0 = %.10e ' % (a0,)
scale1 = 'a1 = %.10e ' % (a1,)
scale2 = 'a2 = %.10e ' % (a2,)

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Image scaled by fits_scale'
outhdr['history'] = scale0
outhdr['history'] = scale1
outhdr['history'] = scale2
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

