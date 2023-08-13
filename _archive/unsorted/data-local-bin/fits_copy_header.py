#!/usr/bin/python

# Convert a fits image to float32

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_copy_header.py headerfile.fits datafile.fits outfile.fits "
  print " "
  sys.exit("Copy header from one fits file to another\n")
elif len(sys.argv) == 4:
  inhdrfile = sys.argv[1]
  indatfile = sys.argv[2]
  outfile = sys.argv[3]  
else:
  print " "
  print "Usage: fits_copy_header.py headerfile.fits datafile.fits outfile.fits "
  print " "
  sys.exit("Copy header from one fits file to another\n")
 

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Open the fits header file readonly by default and create an input hdulist

inhdrlist = pyfits.open(inhdrfile) 

# Assign the output header 

outhdr = inhdrlist[0].header

# Open the fits data file readonly by default and create an input hdulist

indatlist = pyfits.open(indatfile) 

# Assign image data to numpy array

inimage =  indatlist[0].data.astype('float32')

# Convert the image

outimage = inimage

# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),outhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Header added with fits_copy_header.py' 
outhdr['history'] = 'Header file '+  inhdrfile
outhdr['history'] = 'Image file '+  indatfile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the inputs  and exit

inhdrlist.close()
indatlist.close()
exit()

