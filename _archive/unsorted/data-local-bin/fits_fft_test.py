#!/usr/bin/python

# A template program for creating a temporal test stack


import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_test.py  outprefix "
  print " "
  sys.exit("Create a temporal test stack of  fits images\n ")
elif len(sys.argv) == 2:
  outprefix = sys.argv[1]
else:
  print " "
  print "Usage: fits_test.py outprefix   "
  print " "
  sys.exit("Create a temporal test stack of  fits images\n ")
  

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Set a flag determining whether the test oscillators decay

decayflag = False

# Create a numpy cube of 1024 images 256x256 with random background

outstack = np.random.rand(1024, 256, 256)

# Scale noise and add a constant uniform background

noise = 0.1
val0 = 10.
val1 = 0.
val2 = 4.

outstack = noise * outstack
outstack += val0


# Add time-varying signals
  
nout = 1024
fps = 50.

for i in range(nout):

  outimage = outstack[i,:,:]
  t = float(i)/fps
  f1 = 10
  f2 = 14.
  a1 = 0.1
  a2 = 0.02
  phase1 = 2. * np.pi * f1 * t
  phase2 = 2. * np.pi * f2 * t
  decay1 = t/a1
  decay2 = t/a2

  if (decayflag):
    sig1 = val1 * np.cos(phase1)*np.exp(-decay1)
    sig2 = val2 * np.cos(phase2)*np.exp(-decay2)
  else:
    sig1 = val1 * np.cos(phase1)
    sig2 = val2 * np.cos(phase2)
  
  outimage[120:130,120:130] += sig1
  outimage[120:130,140:150] += sig2
 
  outfile = outprefix + '_%04d.fits' % (i,) 
  outlist = pyfits.PrimaryHDU(outimage)

  # Provide a new date stamp

  file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

  # Update the header

  outhdr = outlist.header
  outhdr['DATE'] = file_time
  outhdr['history'] = 'Test slice %d of %d images by fits_fft_test' %(i+1,nout)
  outhdr['history'] = 'Time  %6.3f seconds' %(t,)
  outhdr['history'] = 'Frequencies %f and %f' %(f1, f2)
  
  if (decayflag):
    outhdr['history'] = 'Decay constants %f and %f' %(a1, a2)    

  # Write the fits file

  outlist.writeto(outfile, clobber = clobberflag)

exit()

