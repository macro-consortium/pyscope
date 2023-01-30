#!/usr/bin/python

# Rotationally broaden a stellar spectrum 
# Requires PyAstronomy pyasl for rotBroad implementing Gray's method
# Command line input of vsin (km/s) and linear limbdarkening (0. to 1.)

import os
import sys
import numpy as np
from PyAstronomy import pyasl



if len(sys.argv) == 1:
  sys.exit("Usage: spectrum_rotbroad.py  infile1.dat  vsini eps outfile.dat ")
elif len(sys.argv) == 5:
  infile = sys.argv[1]
  vsini = float(sys.argv[2])
  eps = float(sys.argv[3])
  outfile = sys.argv[4]
else:
  sys.exit("Usage: spectrum_rotbroad.py  infile1.dat  vsini eps outfile.dat ")
  
spectrum = np.loadtxt(infile)
wl = spectrum[:,0]
flux = spectrum[:,1]

# print wl
# print flux

# Obtain the broadened spectrum using
# vsini and limb-darkening from the command line

bflux = pyasl.rotBroad(wl, flux, eps, vsini)

outdata = np.column_stack((wl,bflux))
np.savetxt(outfile, outdata)

exit()
