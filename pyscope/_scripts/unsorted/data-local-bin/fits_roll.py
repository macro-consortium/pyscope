#!/usr/bin/python

# Roll data in a fits image

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc
import string # for parsing regions
#import re # for parsing regions

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_roll.py infile.fits outfile.fits dx dy \n"
  print " "
  sys.exit("Rolls and wraps by dx and dy within the same image size \n")
elif len(sys.argv) == 5:
  # dx and dy 
  infile = sys.argv[1]
  outfile = sys.argv[2]
  dx = int(float(sys.argv[3]))
  dy = int(float(sys.argv[4]))
else:
  print " "
  print "Usage: fits_roll.py infile.fits outfile.fits dx dy \n"
  print " "
  sys.exit("Rolls and wraps by dx and dy within the same image size \n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header 

inhdr = inlist[0].header

# Assign image data to numpy array and get its size

inimage =  inlist[0].data.astype('float32')
xsize, ysize = inimage.shape

# Create a unit array to assure we treat the whole image in floating point 

fone = np.ones((xsize,ysize))

# Roll the image by dx and dy and create a floating point output image 

newimage1 = np.roll(inimage,dy,axis=0)
newimage2 = np.roll(newimage1,dx, axis=1)
outimage = fone*newimage2


# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Image clipped by fits_clip' 
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

