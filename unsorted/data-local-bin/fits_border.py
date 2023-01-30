#!/usr/bin/python

# Set zero level borders in a fits image

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc
import string # for parsing regions
#import re # for parsing regions

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_border.py infile.fits outfile.fits xmin xmax ymin ymax"
  print " "
  sys.exit("Zeros values outside the borders \n")
elif len(sys.argv) == 7:
  # Minimum and maximum
  infile = sys.argv[1]
  outfile = sys.argv[2]
  nxmin = int(float(sys.argv[3])) - 1
  nxmax = int(float(sys.argv[4])) - 1
  nymin = int(float(sys.argv[5])) - 1
  nymax = int(float(sys.argv[6])) - 1 
else:
  print " "
  print "Usage: fits_border.py infile.fits outfile.fits xmin xmax ymin ymax"
  print " "
  sys.exit("Zeros values outside the borders \n")

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
nx = xsize - 1
ny = ysize - 1

# Use a unit array to assure we treat the whole image in floating point 

fone = np.ones((xsize,ysize))
fimage = fone*inimage

# Reject invalid input boundaries

if nxmin > nxmax:
  print " "
  sys.exit("Minimum x must be less or equal to than maximum x \n")

if nymin > nymax:
  print " "
  sys.exit("Minimum y must be less or equal to than maximum y \n")

if nxmin < 0:
  print " "
  sys.exit("Minimum x index must be greater than 0 \n")

if nymin < 0:
  print " "
  sys.exit("Minimum y index must be greater than 0 \n")  
   
if nxmax < 0:
  print " "
  sys.exit("Maximum x index must be greater than 0  \n")

if nymax < 0:
  print " "
  sys.exit("Maximum y index must be greater than 0 \n")

if nxmin > nx:
  print " "
  sys.exit("Minimum x index must be  less than or equal to image width \n")

if nymin > ny:
  print " "
  sys.exit("Minimum y index must be  less than or equal to image height\n") 
  
if nxmax > nx:
  print " "
  sys.exit("Maximum x index must be less than or equal to image width \n")

if nymax > ny:
  print " "
  sys.exit("Maximum y index must be less than or equal to image height\n")



# Zero the image outside the borders 
  
# Use numpy array notation to set regions to zero

fimage[:nymin,:]  = 0.
fimage[nymax:,:] = 0.
fimage[:,:nxmin]  = 0.
fimage[:,nxmax:] = 0.


# Create the output the image

outimage = fimage

# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Image bordered by fits_border' 
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

