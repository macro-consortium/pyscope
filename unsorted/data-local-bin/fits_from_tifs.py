#!/usr/bin/python

# Convert several tif images to its 32-bit fits floating point equivalents

import os
import sys
import numpy as np
from PIL import Image
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_from_tifs.py file1.tif file2.tif ..."
  print " "
  sys.exit("Converts tif image files to a fits files\n")
elif len(sys.argv) >= 2:
  # Add only
  infiles = sys.argv[1:]
else:
  print " "
  print "Usage: fits_from_tifs.py file1.tif file2.tif ..."
  print " "
  sys.exit("Converts tif image files to a fits files\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
for infile in infiles:
  
  # Create an output file name with a fits extension from the input name

  inbase = os.path.splitext(os.path.basename(infile))[0]
  outfile = inbase + '.fits'

  # Open the fits file readonly by default and create an input hdulist

  intif = Image.open(infile) 

  # Assign the tif image data to a numpy array and get its size for future use

  fimage =  np.array(intif) 
  xsize, ysize = fimage.shape

  # Additional image processing could go here

  outimage = fimage


  # Create the fits object for this output image
  # Use float32 for output type

  outlist = pyfits.PrimaryHDU(outimage.astype('float32'))

  # Provide a date stamp

  file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

  # Update the header

  outhdr = outlist.header
  outhdr['DATE'] = file_time
  outhdr['history'] = 'Image created by fits_from_tif'

  # Write the fits file

  outlist.writeto(outfile, clobber = clobberflag)

exit()

