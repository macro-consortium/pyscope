#!/usr/bin/python

# Sum columns in a fits image
# Export data with row number and sum of columns

import os
import sys
import numpy as np
import pyfits

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_sum_cols.py start_col stop_col infile.fits outfile.dat  "
  print " "
  sys.exit("Sum columns in a fits image\n")
elif len(sys.argv) == 5:
  start_col = int(float(sys.argv[1]))
  stop_col = int(float(sys.argv[2]))
  infile = sys.argv[3]
  outfile = sys.argv[4]
else:
  print " "
  print "Usage: fits_sum_cols.py start_col stop_col infile.fits outfile.dat  "
  print " "
  sys.exit("Sum columns in a fits image\n")
  
# Open the fits files readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign image data to numpy arrays

inimage =  inlist[0].data.astype('float32')

# Find image size
# First  index selects a row
# Second index selects a column

nrows, ncols = inimage.shape

# Test for legitimate limits based on row count starting at 1

if start_col > ncols:
  print ' Start col larger than image size'
  inlist.close()
  exit()
elif stop_col > ncols:
  print ' Stop col larger than image size'
  inlist.close()
  exit()
elif start_col < 1:
  print ' Start col must be greater than 0'
  inlist.close()
  exit() 
elif stop_col < start_col:
  print ' Stop col must be greater than start col'
  inlist.close()
  exit() 
else:
  pass
  
# Set the output arrays to match the image size

xdata = np.arange(nrows)
xdata = xdata + 1.
ydata = np.zeros(nrows)

imcols = inimage[:,start_col-1:stop_col-1]  

ydata = np.sum(imcols,axis=1)

# Save the data

dataout = np.column_stack((xdata,ydata))  
np.savetxt(outfile, dataout)

exit()


