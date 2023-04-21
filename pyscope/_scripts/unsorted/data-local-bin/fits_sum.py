#!/usr/bin/python

# Sum a stack of fits images

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_sum.py  outfile.fits infile1.fits infile2.fits ... "
  print " "
  sys.exit("Sum a stack of fits images\n")
elif len(sys.argv) >=5:
  outfile = sys.argv[1]
  infiles = sys.argv[2:]
else:
  print " "
  print "Usage: fits_sum.py  outfile.fits infile1.fits infile2.fits ... "
  print " "
  sys.exit("Sum a stack of fits images\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Build an image stack in memory
# Test that all the images are the same shape and exit if not

inlists = []
inhdrs = []
inimages = []
nimages = 0
for infile in infiles:
  inlist = pyfits.open(infile)
  inimage = inlist[0].data
  inhdr = inlist[0].header
  if nimages == 0:
    inshape0 = inimage.shape
  else:
    inshape = inimage.shape
    if inshape != inshape0:
      sys.exit('File %s not the same shape as %s \n' %(infile, infiles[0]) )  
  inlists.append(inlist)
  inimages.append(inimage)  
  inhdrs.append(inhdr)
  inlist.close()
  nimages = nimages + 1
  
# Use numpy to calculate the sum of the stack as a new image

outimage = np.sum(inimages,axis=0)

# Create the fits ojbect for this image using the header of the first image

outlist = pyfits.PrimaryHDU(outimage,inhdrs[0])

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Sum of %d images by fits_sum' %(nimages,)
outhdr['history'] = 'First image '+  infiles[0]
outhdr['history'] = 'Last image  '+  infiles[nimages-1]

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Exit

exit()

