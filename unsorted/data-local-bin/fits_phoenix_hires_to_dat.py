#!/usr/bin/python

# Extract phoenix hires spectrum from database

import os
import sys
import numpy as np
import pyfits

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_phoenix_hires_to_dat.py wavelength.fits hires.fits outfile.dat  "
  print " "
  sys.exit("Extract data from phoenix database \n")
elif len(sys.argv) == 4:
  wlfile = sys.argv[1]
  spfile = sys.argv[2]
  outfile = sys.argv[3]
else:
  print " "
  print "Usage: fits_phoenix_hires_to_dat.py wavelength.fits hires.fits outfile.dat  "
  print " "
  sys.exit("Extract data from phoenix database \n")


  
# Open the fits files readonly by default and create an input hdulist

try:
  wllist = pyfits.open(wlfile) 

except:
  print " "
  sys.exit("Could not open the wavelength file.\n")

try:
  splist = pyfits.open(spfile) 

except:
  print " "
  sys.exit("Could not open the spectrum file.\n")



# Assign  data to numpy arrays

wlimage =  wllist[0].data.astype('float32')
spimage =  splist[0].data.astype('float32')


# Find image sizes

try:
  wlcols, = wlimage.shape
except:
  print " "
  sys.exit("The wavelength file has more than 1 row. \n")

try:
  spcols, = spimage.shape
except:
  print " "
  sys.exit("The spectrum file has more than 1 row. \n")

if wlcols != spcols:
  print " "
  sys.exit("The spectrum file and wavelength file are different lengths. \n")


  
# Set the output data

xdata = wlimage[:]
ydata = spimage[:]  

# Save the data

dataout = np.column_stack((xdata,ydata))  
np.savetxt(outfile, dataout)

exit()


