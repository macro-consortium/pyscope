#!/usr/bin/python

# Lucy-Richardson deconvolution of an image
# Uses a Gaussian psf that is represented by a (2*psfsize + 1) array 

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc
from skimage import restoration

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_lucy_richardson.py [psfsize] [psfhwhm] [interations] infile.fits outfile.fits"
  print " "
  sys.exit("Lucy-Richardson deconvolution of an image\n")
elif len(sys.argv) == 3:
  # Defaults
  psfsize = 1 + 2*2
  psfhwhm = 2.
  a2 = np.log(2.) * psfhwhm**2
  niter = 10  
  infile = sys.argv[1]
  outfile = sys.argv[2]
elif len(sys.argv) == 6:
  psfsize = 1 + 2*int(float(sys.argv[1]))
  psfhwhm = float(sys.argv[2])
  a2 = np.log(2.) * psfhwhm**2
  a = np.sqrt(a2)
  niter = int(float(sys.argv[3]))
  infile = sys.argv[4]
  outfile = sys.argv[5]
else:
  print " "
  print "Usage: fits_lucy_richardson.py [psfsize] [psfhwhm] [interations] infile.fits outfile.fits"
  print " "
  sys.exit("Lucy-Richardson deconvolution of an image\n")

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

# Estimate an area-normalized Gaussian PSF 

psf = np.ones((psfsize, psfsize)) / (psfsize*psfsize)
offset = np.ones((psfsize, psfsize))
anorm = np.sqrt(a/np.pi)
for j in range(0, psfsize):
  for i in range(0, psfsize):
    x = (float(j - psfsize/2))
    y = (float(i - psfsize/2))
    pix = anorm * np.exp(-(x**2 + y**2)/a2)
    psf[i,j] = pix

# Create a deconvolved image

outimage = restoration.richardson_lucy(inimage, psf, iterations=niter, clip=False)

# Create the fits object for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())


# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Image deconvolved by fits_restore'
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

