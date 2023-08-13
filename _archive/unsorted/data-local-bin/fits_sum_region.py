#!/usr/bin/python

# Sum region of a fits image
# Export value to stdout

import os
import sys
import numpy as np
import pyfits

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_sum_region.py start_col start_row stop_col stop_row infile.fits "
  print " "
  sys.exit("Sum region of a fits image\n")
elif len(sys.argv) == 6:
  start_col = int(float(sys.argv[1]))
  start_row = int(float(sys.argv[2]))
  stop_col = int(float(sys.argv[3]))
  stop_row = int(float(sys.argv[4]))
  infile = sys.argv[5]
else:
  print " "
  print "Usage: fits_sum_region.py start_col start_row stop_col stop_row infile.fits  "
  print " "
  sys.exit("Sum region of  a fits image\n")
  
# Open the fits files readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign image data to numpy arrays

inimage =  inlist[0].data.astype('float32')

# Find image size
# First  index selects a row
# Second index selects a column

nrows, ncols = inimage.shape

# Test for legitimate limits based on row and column count starting at 1

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
elif start_row > nrows:
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
  
imsum = np.sum(inimage[start_row-1:stop_row,start_col-1:stop_col])  

print imsum 

exit()


