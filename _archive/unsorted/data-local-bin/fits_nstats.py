#!/usr/bin/python

# Provide statistics on a stack of a fits images

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc
  
if len(sys.argv) == 1:
  print " "
  print "Usage: fits_nstats.py infile1.fits infile2.fits ..."
  print " "
  sys.exit("Provide statistics on a stack of two or more fits images\n")
elif len(sys.argv) >= 3:
  infiles = sys.argv[1:]
else:
  print " "
  print "Usage: fits_stats.py infile1.fits infile2.fits ..."
  print " "
  sys.exit("Provide statistics on a stack of two or more fits images\n")

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
    xsize, ysize = inimage.shape
    
  else:
    inshape = inimage.shape
    if inshape != inshape0:
      sys.exit('File %s not the same shape as %s \n' %(infile, infiles[0]) )  
  inlists.append(inlist)
  inimages.append(inimage)  
  inhdrs.append(inhdr)
  inlist.close()
  nimages = nimages + 1
  
zsize = nimages
  
# The image stack is along axis 0 in the 3d numpy array nimages

# Use a unit array to assure we treat the whole stack in floating point 

fone = np.ones((xsize,ysize))
fimages = fone*inimages
totone = np.sum(fone) 
totpix = nimages*totone

fmean = np.mean(fimages)
fmedian = np.median(fimages)
fsigma = np.std(fimages)
fminimum = np.amin(fimages)
fmaximum = np.amax(fimages)

# Print diagnostics for all data 

print '  '
print '  Statistics on the image stack:'
print '  '
print '  Data cube dimensions = %i x %i x %i' %(int(zsize),int(xsize),int(ysize))
print '  Image slice size = %i x %i' %(int(xsize),int(ysize))
print '  Number of slices = %i' %(int(zsize),)
print '  Total pixels = %i' %(int(totpix),)
print '  Minumum value = %f' %(fminimum,)
print '  Maximum value = %f' %(fmaximum,)
print '  Image stack mean = %f' %(fmean,)
print '  Image stack median = %f' %(fmedian,)
print '  Image stack sigma = %f' %(fsigma,)
print ' '

# Use numpy to calculate the median of the stack as a new image

gimage = np.median(fimages,axis=0)
gmean = np.mean(gimage)
gmedian = np.median(gimage)
gsigma = np.std(gimage)
gminimum = np.amin(gimage)
gmaximum = np.amax(gimage)

# Print diagnostics for the median image

print '  '
print '  Statistics on the median image:'
print ' '
print '  Median image size = %i x %i' %(int(xsize),int(ysize))
print '  Total pixels = %i' %(int(totone),)
print '  Minumum value = %f' %(gminimum,)
print '  Maximum value = %f' %(gmaximum,)
print '  Median image mean = %f' %(gmean,)
print '  Median image median = %f' %(gmedian,)
print '  Median image pixel-to-pixel sigma = %f' %(gsigma,)
print ' '

# Use numpy to calculate pseudo-images of mean and standard deviations through the stack

sigmaimage = np.std(fimages,axis=0)
meanimage  = np.mean(fimages,axis=0)
hsigma = np.mean(sigmaimage)
hmean = np.mean(meanimage)

# Print diagnostics for the single pixel mean and standard deviation

print '  '
print '  Statistics on the mean single pixel:'
print ' '
print '  Total pixels sampled = %i' %(int(totpix),)
print '  Total images sampled = %i' %(int(zsize),)
print '  Mean value = %f' %(hmean,)
print '  Image-to-image sigma = %f' %(hsigma,)
print ' '


exit()

