#!/usr/bin/python

# Convert a fits image to float32

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_to_float32.py infile.fits outfile.fits "
  print " "
  sys.exit("Convert a fits image to float32\n")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  print " "
  print "Usage: fits_to_float32.py infile.fits outfile.fits "
  print " "
  sys.exit("Convert a fits image to float32\n")
 

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header 

inhdr = inlist[0].header

# Assign image data to numpy array

inimage =  inlist[0].data.astype('float32')

# Convert the image

outimage = inimage

# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Converted to float32 by fits_to_float32' 
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

