#!/usr/bin/python

# Sum rows in a fits image
# Export data with column number and sum of rows

import os
import sys
import numpy as np
import pyfits

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_sum_rows.py start_row stop_row infile.fits outfile.dat  "
  print " "
  sys.exit("Sum rows in a fits image\n")
elif len(sys.argv) == 5:
  start_row = int(float(sys.argv[1]))
  stop_row = int(float(sys.argv[2]))
  infile = sys.argv[3]
  outfile = sys.argv[4]
else:
  print " "
  print "Usage: fits_sum_rows.py start_row stop_row infile.fits outfile.dat  "
  print " "
  sys.exit("Sum rows in a fits image\n")


  
# Open the fits files readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign image data to numpy arrays

inimage =  inlist[0].data.astype('float32')

# Find image size
# First  index selects a row
# Second index selects a column

nrows, ncols = inimage.shape

# Test for legitimate limits based on row count starting at 1

if start_row > nrows:
  print ' Start row larger than image size'
  inlist.close()
  exit()
elif stop_row > nrows:
  print ' Stop row larger than image size'
  inlist.close()
  exit()
elif start_row < 1:
  print ' Start row must be greater than 0'
  inlist.close()
  exit() 
elif stop_row < start_row:
  print ' Stop row must be greater than start row'
  inlist.close()
  exit() 
else:
  pass
  
# Set the output arrays to match the image size

xdata = np.arange(ncols)
xdata = xdata + 1.
ydata = np.zeros(ncols)

imrows = inimage[start_row-1:stop_row-1,:]  

ydata = np.sum(imrows,axis=0)

# Save the data

dataout = np.column_stack((xdata,ydata))  
np.savetxt(outfile, dataout)

exit()


