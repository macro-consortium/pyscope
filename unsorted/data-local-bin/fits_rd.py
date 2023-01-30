#!/usr/bin/python

# Create a random decrement autocorrelation stack from a stack of uniformly temporally cadenced images

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_rd.py  threshold outprefix infile1.fits infile2.fits ...   "
  print " "
  sys.exit("Create a random decrement autocorrelation  stack from a temporal stack of fits images\n")
elif len(sys.argv) >=6:
  threshold = float(sys.argv[1])
  outprefix = sys.argv[2]
  infiles = sys.argv[3:]
else:
  print " "
  print "Usage: fits_rd.py  threshold outprefix infile1.fits infile2.fits ...   "
  print " "
  sys.exit("Create a random decrement autocorrelation  stack from a temporal stack of fits images\n")
  

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Build an image stack in memory
# Test that all the images are the same shape and exit if not
# Note numpy array swaps x and y compared to the FITS image
# Image x is fastest varying which results in 
# First index is image y
# Second index is image x

inlists = []
inhdrs = []
inimages = []
nin = 0
for infile in infiles:
  inlist = pyfits.open(infile)
  inimage = inlist[0].data
  inhdr = inlist[0].header
  if nin == 0:
    inshape0 = inimage.shape
    imysize, imxsize = inshape0
  else:
    inshape = inimage.shape
    if inshape != inshape0:
      sys.exit('File %s not the same shape as %s \n' %(infile, infiles[0]) )  
  inlists.append(inlist)
  inimages.append(inimage)  
  inhdrs.append(inhdr)
  inlist.close()
  nin = nin + 1

if nin < 2:
  sys.exit(' More than 1 image is needed to perform a random decrement transform \n')
nout = nin/2


# Create a numpy cube from the list of images
# Note that this swaps x and y in each image

instack = np.array(inimages)

# Find the real part of the Fourier transform the cube along the time axis
#outstack = np.fft.fft2(instack,axes=(0,)).real

# Copy the array to make a working output array

outstack = np.copy(instack)

# Run the random decrement analysis on all pixels in the image stack
# Store the analysis in the first half of a copy of the input stack
# Use last outimage + 1 as a normalization plane

for j in range(imysize):
  for i in range(imxsize):
    pixvals = np.copy(instack[:,j,i])    
    tcount = 0
    for k in range(nout):
      if pixvals[k+1] >= threshold and pixvals[k] < threshold:
        pixroll = np.roll(pixvals,-k)
        outstack[:,j,i] = outstack[:,j,i] + pixroll
        # print pixvals[k],pixvals[k+1],k,j,i,"up"
        tcount = tcount +1
        outstack[nout+1,j,i] = tcount
      elif pixvals[k+1] <= threshold and pixvals[k] > threshold:
        pixroll = np.roll(pixvals,-k)
        outstack[:,j,i] = outstack[:,j,i] + pixroll
        # print pixvals[k],pixvals[k+1],k,j,i,"down"
        tcount = tcount +1
        outstack[nout+1,j,i] = tcount
      else:
        pass  

# Export the the fully overlapped first half of the outstack 
  
normimage = np.copy(outstack[nout+1,:,:])

for i in range(nout):

  outimage = np.copy(outstack[i,:,:])
  outimage = outimage/normimage
  outimage = np.nan_to_num(outimage)
  outfile = outprefix + '_%04d.fits' % (i,) 
  
  # Create the fits ojbect for this image using the header of the first image

  outlist = pyfits.PrimaryHDU(outimage,inhdrs[0])

  # Provide a new date stamp

  file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

  # Update the header

  outhdr = outlist.header
  outhdr['DATE'] = file_time
  outhdr['history'] = 'Slice %d of %d images by fits_rd' %(i+1,nout)
  outhdr['history'] = 'First image '+  infiles[0]
  outhdr['history'] = 'Last image  '+  infiles[nin-1]

  # Write the fits file

  outlist.writeto(outfile, clobber = clobberflag)

# Exit


exit()

