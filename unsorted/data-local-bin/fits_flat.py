#!/usr/bin/python

# Flatfield correct a fits CCD 2D image with 32-bit float output

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print ""
  print "Usage: fits_flat.py infile.fits flatfile.fits outfile.fits"
  print ""
  sys.exit("Correct fits image for flat field \n")
elif len(sys.argv) == 4:
  infile = sys.argv[1]
  flatfile = sys.argv[2]
  outfile = sys.argv[3]
else:
  print ""
  print "Usage: fits_flat.py infile.fits flatfile.fits outfile.fits"
  print ""  
  sys.exit("Correct fits image for flat field \n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the fits files readonly by default and create an input hdulist

inlist = pyfits.open(infile) 
flatlist = pyfits.open(flatfile)

# Assign the input header in case it is needed later

inhdr = inlist[0].header

# Assign image data to numpy arrays

inimage =  inlist[0].data.astype('float32')
inflat = flatlist[0].data.astype('float32')

# Test for match of shapes

if inimage.shape != inflat.shape:
  inlist.close()
  flatlist.close()
  sys.exit("Image and flat files are of unequal sizes")
  
# Create a flat-divided image

outimage = inimage/inflat

# Create an output list from the new image and the input header
# Use float32 for output type 

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Flat corrected by fits_flat'
outhdr['history'] = 'Image file ' + infile
outhdr['history'] = 'Flat file ' + flatfile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the list and exit

inlist.close()
flatlist.close()

exit()

