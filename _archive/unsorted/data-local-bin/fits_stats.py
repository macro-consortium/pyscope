#!/usr/bin/python

# Provide statistics of a fits image

import os
import sys
import numpy as np
import pyfits

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_stats.py infile.fits"
  print " "
  sys.exit("Provide statistics of a fits image\n")
elif len(sys.argv) == 2:
  infile = sys.argv[1]
else:
  print " "
  print "Usage: fits_stats.py infile.fits"
  print " "
  sys.exit("Provide statistics of a fits image\n")

  
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
totpix = np.sum(fone)

fmean = np.mean(fimage)
fmedian = np.median(fimage)
fsigma = np.std(fimage)
fminimum = np.amin(fimage)
fmaximum = np.amax(fimage)

# Print diagnostics 

print ' '
print 'Statistics on image %s: ' %(infile,)
print '  Image size = %i x %i' %(int(xsize),int(ysize))
print '  Total pixels = %i' %(int(totpix),)
print '  Minumum value = %f' %(fminimum,)
print '  Maximum value = %f' %(fmaximum,)
print '  Mean = %f' %(fmean,)
print '  Median = %f' %(fmedian,)
print '  Sigma = %f' %(fsigma,)
print ' '


# Close the input  and exit

inlist.close()
exit()

