#!/usr/bin/python

# Create a set of RGB FITS file from an EXR file
# Assumes a 16-bit EXR file tested with Sony AXS-5 output

import os
import sys
import numpy as np
import pyfits
import OpenEXR as exr
from time import gmtime, strftime  # for utc

if len(sys.argv) == 2:
  infile = sys.argv[1]
else:
  print " "
  print "Usage: fits_from_exr.py infile.fits"
  print " "
  sys.exit("Create RGB FITS files from a 16-bit color EXR file.\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the EXR file
inexr = exr.InputFile(infile)

# RGB channels from the file
(inexr_r, inexr_g, inexr_b) = inexr.channels("RGB")

#print "Found RGB channels of lengths %d, %d, %d \n" % (len(inexr_r),len(inexr_r),len(inexr_r))

indata =  inexr.header()['dataWindow']
xsize = indata.max.x - indata.min.x + 1
ysize = indata.max.y - indata.min.y + 1

inimage_r = np.fromstring(inexr.channel('R'), dtype = np.int16)
inimage_g = np.fromstring(inexr.channel('G'), dtype = np.int16)
inimage_b = np.fromstring(inexr.channel('B'), dtype = np.int16)

# Diagnostics for image type or try Image package

#print inimage_r.shape
#print inimage_g.shape
#print inimage_b.shape
#print xsize, ysize, xsize*ysize

# Shape the image arrays
outimage_r = np.reshape(inimage_r, (ysize, xsize))
outimage_g = np.reshape(inimage_g, (ysize, xsize))
outimage_b = np.reshape(inimage_b, (ysize, xsize))
outimage_w = np.zeros((ysize, xsize))
outimage_w = outimage_r.astype(np.float64) + outimage_g.astype(np.float64) + outimage_b.astype(np.float64)

# Construct the FITS lists
outlist_r = pyfits.PrimaryHDU(outimage_r)
outlist_g = pyfits.PrimaryHDU(outimage_g)
outlist_b = pyfits.PrimaryHDU(outimage_b)
outlist_w = pyfits.PrimaryHDU(outimage_w.astype(np.float64))

# Provide a new date stamp
file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the headers
outhdr_r = outlist_r.header
outhdr_r['DATE'] = file_time
outhdr_r['history'] = 'Red image loaded by fits_from_exr'
outhdr_r['history'] = 'Image file ' + infile
outhdr_g = outlist_g.header
outhdr_g['DATE'] = file_time
outhdr_g['history'] = 'Green image loaded by fits_from_exr'
outhdr_g['history'] = 'Image file ' + infile
outhdr_b = outlist_b.header
outhdr_b['DATE'] = file_time
outhdr_b['history'] = 'Blue image loaded by fits_from_exr'
outhdr_b['history'] = 'Image file ' + infile
outhdr_w = outlist_w.header
outhdr_w['DATE'] = file_time
outhdr_w['history'] = 'Gray scale image computer by fits_from_exr'
outhdr_w['history'] = 'Image file ' + infile


# Construct FITS file names from EXR file name
exrbase = os.path.splitext(os.path.basename(infile))[0]
outfile_r = exrbase + '_r.fits'
outfile_g = exrbase + '_g.fits'
outfile_b = exrbase + '_b.fits'
outfile_w = exrbase + '_w.fits'

# Create, write, and close the output files
outlist_r.writeto(outfile_r, clobber = clobberflag)
outlist_g.writeto(outfile_g, clobber = clobberflag)
outlist_b.writeto(outfile_b, clobber = clobberflag)
outlist_w.writeto(outfile_w, clobber = clobberflag)

# Close the input and exit
inexr.close()
exit()

