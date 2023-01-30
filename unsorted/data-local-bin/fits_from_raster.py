#!/usr/bin/python

# Convert a set of rastered data files to one fits image 

import os
import sys
import argparse
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

parser= argparse.ArgumentParser(description = 'Create a fits image from text data')

if len(sys.argv) == 1:
  sys.exit("Usage: fits_from_raster outfile.fits  infile1.dat infile2.dat ... ")
elif len(sys.argv) > 2:
  outfile = sys.argv[1]
  infiles = sys.argv[2:]
else:
  sys.exit("Usage: fits_from_raster outfile.fits  infile1.dat infile2.dat ... ")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Set data type for output

newdatatype = np.float32  

nfile = -1
for infile in infiles:
  nfile = nfile + 1
  newdata = np.loadtxt(infile)
  if nfile == 0:
    outdata = newdata
  else:
    outdata = np.vstack((outdata,newdata))

outlist = pyfits.PrimaryHDU(outdata.astype(newdatatype))

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Image data loaded by fits_from_raster'
outhdr['history'] = 'Image files ' + infiles[0] + ' ... ' + infiles[nfile]

# Create, write, and close the output fits file

outlist.writeto(outfile, clobber = clobberflag)


exit()
