#!/usr/bin/python

# Remoave all non-essential entries from  a fits image header 

# Enter input and output files on the command line


import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print ' '
  print 'Usage: fits_clean_head.py infile.fits outfile.fits'
  print ' '
  sys.exit('Remove all non-essential entries from a fits image header \n')
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  print ' '
  print 'Usage: fits_clean_head.py infile.fits outfile.fits'
  print ' '
  sys.exit('Remove all non-essential entries from a fits image header \n')

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

inimage =  inlist[0].data
outimage = inimage

outlist = pyfits.PrimaryHDU(outimage)

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the list and exit

inlist.close()

exit()

