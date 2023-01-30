#!/usr/bin/python

# List the fits file header 

import os
import sys
import numpy as np
import pyfits

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_listhead.py infile.fits "
  print " "
  sys.exit("List the fits file header\n")
elif len(sys.argv) == 2:
  infile = sys.argv[1]
else:
  print " "
  print "Usage: fits_listhead.py infile.fits "
  print " "
  sys.exit("List the fits file header\n")

# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header in case it is needed later

inhdr = inlist[0].header

# List the header = and spaces for formatting

for key, value in inhdr.items():
   print key, ' = ', value

# Close the list and exit

inlist.close()

exit()

