#!/usr/bin/python

# Create frequency FFT stack from a stack of uniformly temporally cadenced images

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_fft.py  outprefix infile1.fits infile2.fits ...   "
  print " "
  sys.exit("Create a frequency stack from a temporal stack of  fits images\n ")
elif len(sys.argv) >=5:
  outprefix = sys.argv[1]
  infiles = sys.argv[2:]
else:
  print " "
  print "Usage: fits_fft.py outprefix infile1.fits infile2.fits ...  "
  print " "
  sys.exit("Create a frequency stack from a temporal stack of  fits images\n")
  
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


# Create a numpy cube from the list of images

instack = np.array(inimages)

# Find the Fourier transform of real data along the time axis

spectrum = np.fft.rfft(instack,axis=0)


# Find the magnitudes and select the positive frequencies

nout = nin/2


outstack = spectrum

outstack[0,:,:] = 0.5 * outstack[0,:,:]
  
for i in range(nout):

  outimage = outstack[i,:,:]
  
  outimage = np.absolute(outimage)
  
  outimage = outimage/float(nout)
          
  outfile = outprefix + '_%04d.fits' % (i,) 
  
  # Create the fits ojbect for this image using the header of the first image

  outlist = pyfits.PrimaryHDU(outimage,inhdr0)

  # Provide a new date stamp

  file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

  # Update the header

  outhdr = outlist.header
  outhdr['DATE'] = file_time
  outhdr['history'] = 'FFT slice %d of %d images by fits_fft' %(i+1,nout)
  outhdr['history'] = 'First image '+  infiles[0]
  outhdr['history'] = 'Last image  '+  infiles[nin-1]

  # Write the fits file

  outlist.writeto(outfile, clobber = clobberflag)

# Exit


exit()

