#!/usr/bin/python

# Write a linearly scaled png image from a fits image file

import os
import sys
import numpy as np
import pyfits
import scipy
import scipy.misc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_to_lin_png.py infile.fits outfile.png"
  print "       fits_to_lin_png.py infile.fits outfile.png minval maxval"
  print " "
  sys.exit("Create a linearly scaled png image\n")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
  minmaxflag = False
elif len(sys.argv) ==5:
  # Minimum and maximum
  infile = sys.argv[1]
  outfile = sys.argv[2]
  minval = float(sys.argv[3])
  maxval = float(sys.argv[4])
  if minval >= maxval:
    sys.exit("The specified minimum must be less than the maximum\n")
  minmaxflag = True  
else:
  print " "
  print "Usage: fits_to_lin_png.py infile.fits outfile.png"
  print "       fits_to_lin_png.py infile.fits outfile.png minval maxval"
  print " "
  sys.exit("Create a linearly scaled png image\n")
  
# Open the fits file and create an hdulist

inlist = pyfits.open(infile) 

# Assign image data to a numpy array

inimage =  inlist[0].data

print 'Image size: ', inimage.size
print 'Image shape: ', inimage.shape

# Scale the image data linearly
if minmaxflag:
  pass
else:  
  minval = float(np.min(inimage))
  maxval = float(np.max(inimage))

delta = maxval - minval
newimage = 255.0*(inimage - minval)/(delta)
newimage[newimage > 255.] = 255.
newimage[newimage < 0.] = 0.

# Flip the image so that it will appear in the png as it does in ds9

outimage = np.flipud(newimage)

# Save the image as a png file
scipy.misc.imsave(outfile, outimage)

# Close the input image file

inlist.close()

exit()


