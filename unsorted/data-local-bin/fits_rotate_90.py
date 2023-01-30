#!/usr/bin/python

# Rotate an image clockwise n times 90 degrees
# Accepts n or if not sets n to 1

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_rotate_90.py [n] infile.fits outfile.fits  "
  print "       fits_rotate_90.py infile.fits outfile.fits  "
  print " "
  sys.exit("Rotate an image clockwise n times 90 degrees\n")
elif len(sys.argv) == 4:
  n = int(sys.argv[1])
  infile = sys.argv[2]
  outfile = sys.argv[3]
elif len(sys.argv) == 3:
  n = 1
  infile = sys.argv[1]
  outfile = sys.argv[2]
  
else:
  print " "
  print "Usage: fits_rotate_90.py [n] infile.fits outfile.fits  "
  print "       fits_rotate_90.py infile.fits outfile.fits  "
  print " "
  sys.exit("Rotate an image clockwise n times 90 degrees\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header in case it is needed later

inhdr = inlist[0].header

# Assign image data to a numpy array

inimage =  inlist[0].data

# Rotate this image using numpy

outimage = np.rot90(inimage,n)

# Create an output list from the new image and the input header
# Retain the original datatype

outlist = pyfits.PrimaryHDU(outimage,inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

degrees = n*90
outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Rotated %d degrees by fits_rotate' %(degrees,)
outhdr['history'] = 'Image file ' + infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the list and exit

inlist.close()

exit()

