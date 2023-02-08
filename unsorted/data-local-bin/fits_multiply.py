#!/usr/bin/python

# Multiply a fits CCD 2D image by another with 32-bit float output

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print ""
  print "Usage: fits_multiply.py in1.fits in2.file.fits outfile.fits"
  print ""
  sys.exit("Multiply one image by another \n")
elif len(sys.argv) == 4:
  in1file = sys.argv[1]
  in2file = sys.argv[2]
  outfile = sys.argv[3]
else:
  print ""
  print "Usage: fits_multiply.py in1.fits in2.file.fits outfile.fits"
  print ""  
  sys.exit("Multiply one image by another \n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the fits files readonly by default and create an input hdulist

in1list = pyfits.open(in1file) 
in2list = pyfits.open(in2file)

# Assign the input header in case it is needed later

inhdr = in1list[0].header

# Assign image data to numpy arrays

in1image =  in1list[0].data.astype('float32')
in2image =  in2list[0].data.astype('float32')

# Test for match of shapes

if in1image.shape != in2image.shape:
  in1list.close()
  in2list.close()
  sys.exit("Image files are of unequal sizes")
  
# Create a product image

outimage = in1image*in2image

# Create an output list from the new image and the input header
# Use float32 for output type 

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = in1file 
outhdr['history'] = 'multiplied by'
outhdr['history'] = in2file 



# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the list and exit

in1list.close()
in2list.close()

exit()

