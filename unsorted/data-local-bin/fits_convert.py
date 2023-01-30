#!/usr/bin/python

# Convert a fits file of one bitpix to another bitpix

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_convert.py newbitpix infile.fits outfile.fits"
  print " "
  sys.exit("Convert a fits file of one bitpix to another bitpix \n")
elif len(sys.argv) == 4:
  newbitpix = sys.argv[1]
  infile = sys.argv[2]
  outfile = sys.argv[3]
else:
  print " "
  print "Usage: fits_convert.py newbitpix infile.fits outfile.fits"
  print " "
  sys.exit("Convert a fits file of one bitpix to another bitpix \n")

# Assign the numpy type for the requested bitpix

# BITPIX    Numpy Data Type
#   8         numpy.uint8 (note it is UNsigned integer)
#  16         numpy.int16
#  32         numpy.int32
# -32         numpy.float32
# -64         numpy.float64

if int(newbitpix) == 8:
  newdatatype = np.uint8
elif int(newbitpix) == 16:
  newdatatype = np.uint16
elif int(newbitpix) == 32:
  newdatatype = np.uint32
elif int(newbitpix) == -32:
  newdatatype = np.float32
elif int(newbitpix) == -64:
  newdatatype = np.float64
else:
  sys.exit("Requires bitpix 8, 16, 132, -32, or -64")
    
# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the fits files readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header in case it is needed later

inhdr = inlist[0].header

# Assign image data to numpy arrays

inimage =  inlist[0].data

# Diagnostic print the properties of the numpy array

# print inimage.shape
# print inimage.dtype.name

# Create a new image by using an appropriate numpy data type

outlist = pyfits.PrimaryHDU(inimage.astype(newdatatype),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Data type modified by fits_convert'
outhdr['history'] = 'Image file ' + infile

# Create, write, and close the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input image file

inlist.close()

exit ()

