#!/usr/bin/python

# Extract data from a 1d fits image

import os
import sys
import numpy as np
import pyfits

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_1d_to_dat.py infile.fits outfile.dat  "
  print " "
  sys.exit("Extract data from a 1d fits image\n")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  print " "
  print "Usage: fits_1d_to_dat.py infile.fits outfile.dat  "
  print " "
  sys.exit("Extract data from a 1d fits image\n")


  
# Open the fits files readonly by default and create an input hdulist

try:
  inlist = pyfits.open(infile) 

except:
  print " "
  sys.exit("Could not open the file.\n")




# Assign image data to numpy arrays

inimage =  inlist[0].data.astype('float32')


# Find image size
# First  index selects a row
# Second index selects a column

try:
  ncols, = inimage.shape

except:
  print " "
  sys.exit("This file has more than 1 row. \n")


  
# Set the output arrays to match the image size

xdata = np.arange(ncols)
xdata = xdata + 1.

ydata = inimage[:]  

# Save the data

dataout = np.column_stack((xdata,ydata))  
np.savetxt(outfile, dataout)

exit()


