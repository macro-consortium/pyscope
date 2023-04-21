#!/usr/bin/python

# Flip an image left to right

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_flip_lr.py  infile.fits outfile.fits"
  print " "
  sys.exit("Flip an image left to right \n")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]  
else:
  print " "
  print "Usage: fits_flip_lr.py  infile.fits outfile.fits"
  print " "
  sys.exit("Flip an image left to right \n") 

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header in case it is needed later

inhdr = inlist[0].header

# Assign image data to a numpy array

inimage =  inlist[0].data

# Flip this image using numpy

outimage = np.fliplr(inimage)

# Create an output list from the new image and the input header
# Retain the original datatype

outlist = pyfits.PrimaryHDU(outimage,inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Flipped left-right by fits_flip_lr'
outhdr['history'] = 'Image file ' + infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the list and exit

inlist.close()

exit()

