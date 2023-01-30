#!/usr/bin/python

# Unmask a fits image based on a second binary image of the same size
# This is the complement of fits_mask and shows only the part of the image under the mask

# Value greater than 0 in mask will block that part of the image for processing
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
  print "Usage: fits_unmask.py infile.fits maskfile.fits outfile.fits"
  print " "
  sys.exit("Unmask pixels in a fits file\n")
elif len(sys.argv) == 4:
  infile = sys.argv[1]
  maskfile = sys.argv[2]
  outfile = sys.argv[3]
else:
  print " "
  print "Usage: fits_unmask.py infile.fits maskfile.fits outfile.fits"
  print " "
  sys.exit("Unmask pixels in a fits file\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Open the fits files readonly by default and create an input hdulist

inlist = pyfits.open(infile) 
masklist = pyfits.open(maskfile)

# Assign the input header 

inhdr = inlist[0].header
maskhdr = masklist[0].header


# Assign image data to numpy arrays and get their sizes

inimage =  inlist[0].data.astype('float32')
xsize, ysize = inimage.shape

maskimage =  masklist[0].data.astype('bool')
maskxsize, maskysize = maskimage.shape

if xsize != maskxsize or ysize != maskysize:
  print "Mask and image must be the same size."
  print "\n"
  exit()
   
# Create the output image by masking the input image with the complement of the input mask


maskedinimage = ma.array(data = inimage, mask = ~maskimage, copy = True)
outimage = ma.filled( maskedinimage, 0.)



# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Image data modified by fits_mask' 
outhdr['history'] = 'Image file '+  infile
outhdr['history'] = 'Mask file '+  maskfile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

