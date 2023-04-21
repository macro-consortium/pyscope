#!/usr/bin/python

#  Bin a stack of fits images

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_bin.py binfactor outprefix infile1.fits infile2.fits ...   "
  print " "
  sys.exit("Bin a stack of  fits images\n ")
elif len(sys.argv) >=6:
  binfactor = int(float(sys.argv[1]))
  outprefix = sys.argv[2]
  infiles = sys.argv[3:]
else:
  print " "
  print "Usage: fits_bin.py binfactor outprefix infile1.fits infile2.fits ...  "
  print " "
  sys.exit("Bin a stack of  fits images\n")
  

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Build an image stack in memory
# Test that all the images are the same shape and exit if not

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
    xsize, ysize = inshape0
    inhdr0 = inlist[0].header
  else:
    inshape = inimage.shape
    if inshape != inshape0:
      sys.exit('File %s not the same shape as %s \n' %(infile, infiles[0]) )  
  inimages.append(inimage.copy())  

  # Close the file reference so that mmap will release the handler

  inlist.close()
  
  # Delete unneeded references to the file content
  
  del inimage
  del inhdr
  # print infile
  nin = nin + 1

if nin < 2:
  sys.exit(' More than 1 image is needed to perform a Fourier Transform \n')

if binfactor == 0:
  sys.exit('  Binning binfactor should be a small non-zero integer \n')

newxsize = xsize/binfactor
newysize = ysize/binfactor

if newxsize*newysize == 0:
  sys.exit(' Binning binfactor is too large for these images \n');
    
print 'Creating new %i x %i images binned by %i \n' % (newysize, newxsize,binfactor)

# Create a numpy cube of input images from the list of images

instack = np.array(inimages)

# Create a numpy cube to receive the binned images

nout = nin
outstack = np.zeros((nout, newxsize, newysize))
mbin = binfactor
nbin = binfactor

# Every pixel in each input image contributes to one pixel in its output image

for i in range(nout):
  for j in range(xsize):
    m = j / mbin
    for k in range(ysize):
      n = k / nbin
      pixval = np.copy(instack[i,j,k])
      outstack[i,m,n] += pixval
          
for i in range(nout):

  outimage = outstack[i,:,:]
          
  outfile = outprefix + '_%04d.fits' % (i,) 
  
  # Create the fits ojbect for this image using the header of the first image

  outlist = pyfits.PrimaryHDU(outimage,inhdr0)

  # Provide a new date stamp

  file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

  # Update the header

  outhdr = outlist.header
  outhdr['DATE'] = file_time
  outhdr['history'] = 'Binned slice %d of %d images by fits_bin' %(i+1,nout)
  outhdr['history'] = 'First image '+  infiles[0]
  outhdr['history'] = 'Last image  '+  infiles[nin-1]

  # Write the fits file

  outlist.writeto(outfile, clobber = clobberflag)

# Exit


exit()

