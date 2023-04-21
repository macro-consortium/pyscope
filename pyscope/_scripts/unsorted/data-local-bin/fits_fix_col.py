#!/usr/bin/python

# Replace a bad column by the mean of the columns on either side

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_fix_col.py infile.fits column outfile.fits"
  print " "
  sys.exit("Fix a bad column on a fits image\n")
elif len(sys.argv) == 4:
  infile = sys.argv[1]
  fix_col = int(float(sys.argv[2]))
  outfile = sys.argv[3]
else:
  print " "
  print "Usage: fits_absolute_value.py infile.fits column outfile.fits"
  print " "
  sys.exit("Fix a bad column on a fits image\n")

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


# Use a unit array to assure we treat the whole image in floating point 

fone = np.ones((xsize,ysize))
fimage = fone*inimage

# Create the output the image

outimage = np.abs(fimage)

# Repair the image

if fix_col == 1:
  outimage[:,0] = outimage[:,1]
elif fix_col == xsize:
  outimage[:, xsize - 1] = outimage[:, xsize - 2]
else:      
  outimage[:,fix_col - 1] = 0.5 * outimage[:,fix_col - 2] + 0.5 * outimage[:,fix_col]

# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
file_fix_col = "Column %d repaired" % (fix_col,)

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Processed by fits_fix_col' 
outhdr['history'] = file_fix_col
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

