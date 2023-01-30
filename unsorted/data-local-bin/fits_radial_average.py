#!/usr/bin/python

# Average a circularly symmetric file to make a radial section

import os
import sys
import math
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: radial_average.py x_center y_center infile.fits outfile.dat  "
  print " "
  sys.exit("Average a circularly symmetric file to make a radial section\n")
elif len(sys.argv) == 5:
  ncx = int(float(sys.argv[1]))
  ncy = int(float(sys.argv[2]))
  infile = sys.argv[3]
  outfile = sys.argv[4]
else:
  print " "
  print "Usage: radial_average.py x_center y_center infile.fits outfile.dat  "
  print " "
  sys.exit("Average a circularly symmetric file to make a radial section\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Open the fits files readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign image data to numpy arrays

inimage =  inlist[0].data

# Set center of symmetry here to override values on the command line
# Note that first index of a numpy image array is y and second is x

#ncx = 128
#ncy = 128

#ncx = 144
#ncy = 125

inimage_xmax, inimage_ymax = inimage.shape

if ncx > inimage_xmax or ncy > inimage_ymax:
  print 'Center of sample zone is outside image boundary.'
  
  # Close the input image file and exit

  inlist.close()  
  exit()
  
# Set maximum  radius and image boundaries

rcount = 100
xmin = ncx - rcount
xmax = ncx + rcount
ymin = ncy - rcount
ymax = ncy + rcount

# Set initial values

pixcount = [0] * (rcount)
pixtotal = [0.] * (rcount)
pixavg = [0.] * (rcount)
radius = [0.] * (rcount)

# Generate the data

for i in range (rcount):
  pixcount[i] = 0
  pixtotal[i] = 0.
  rmin = float(i - 1)
  if rmin < 0. :
    rmin = 0.
  rmax = float(i + 1)
  if rmax > rcount :
    rmax = rcount
  for j in range(xmin, xmax):
    for k in range(ymin, ymax):
      xdist2 = (j - ncx)*(j - ncx)
      ydist2 = (k - ncy)*(k - ncy)
      dist = math.sqrt(xdist2 + ydist2)
      if dist <= rmax and dist >= rmin:
        pixcount[i] = pixcount[i] + 1   
        pixtotal[i] = pixtotal[i] + inimage[k, j]
  pixavg[i] = pixtotal[i]/pixcount[i] 
  radius[i] = float(i)
dataout = np.column_stack((radius,pixavg))  
np.savetxt(outfile, dataout)

# Mark the center of symmetry and 4 reference points

outimage = inimage
outimage[ncy][ncx]   = 100000.
outimage[ymin][xmin] = 100000.
outimage[ymin][xmax] = 100000.
outimage[ymax][xmin] = 100000.
outimage[ymax][xmax] = 100000.

outlist = pyfits.PrimaryHDU(outimage)

# Create, write, and close the output marker fits file

outlist.writeto('marker.fits', clobber = clobberflag)


# Close the input image file

inlist.close()

exit ()


