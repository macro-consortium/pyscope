#!/usr/bin/python

# Dark subtract with exposure time scaling a fits CCD 2D image with 32-bit float output

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_scaled_dark.py infile.fits darkfile.fits biasfile.fits outfile.fits "
  print " "
  sys.exit("Dark subtract with exposure time scaling and 32-bit float output\n")
elif len(sys.argv) == 5:
  infile = sys.argv[1]
  darkfile = sys.argv[2]
  biasfile = sys.argv[3]
  outfile = sys.argv[4]
else:
  print " "
  print "Usage: fits_scaled_dark.py infile.fits darkfile.fits biasfile.fits outfile.fits "
  print " "
  sys.exit("Dark subtract with exposure time scaling and 32-bit float output\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the fits files readonly by default and create an input hdulist

inlist = pyfits.open(infile) 
darklist = pyfits.open(darkfile)
biaslist = pyfits.open(biasfile)

# Assign the input header in case it is needed later

inhdr = inlist[0].header

# Assign image data to numpy arrays

inimage =  inlist[0].data
indark = darklist[0].data
inbias = biaslist[0].data

# Test for match of shapes

if inimage.shape != indark.shape:
  inlist.close()
  darklist.close()
  biaslist.close()
  sys.exit("Image and dark files are of unequal sizes")
  
if inimage.shape != inbias.shape:
  inlist.close()
  darklist.close()
  biaslist.close()
  sys.exit("Image and bias files are of unequal sizes")

# Find the exposures for the image and dark files

inhdr = inlist[0].header
darkhdr = darklist[0].header 
inexp = float(inhdr['EXPTIME'])
darkexp = float(darkhdr['EXPTIME'])
darkscale = inexp/darkexp


# Create a dark-subtracted image

outimage = (inimage -inbias) - darkscale * (indark -inbias)

# Create an output list from the new image and the input header
# Use float32 for output type 

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Dark subtracted by scaled fits_dark'
outhdr['history'] = 'Image file ' + infile
outhdr['history'] = 'Dark file '  + darkfile
outhdr['history'] = 'Bias file '  + biasfile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the list and exit

inlist.close()
darklist.close()

exit()

