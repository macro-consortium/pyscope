#!/usr/bin/python

# Convert air wavelengths to vacuum wavelengths
# Requires PyAstronomy pyasl for Edlen's formulae 
import os
import sys
import numpy as np
from PyAstronomy import pyasl



if len(sys.argv) == 1:
  sys.exit("Usage: spectrum_airtovac.py  infile.dat  outfile.dat ")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  sys.exit("Usage: spectrum_airtovac.py  infile.dat  outfile.dat ")
  
spectrum = np.loadtxt(infile)
awl = spectrum[:,0]
flux = spectrum[:,1]

vwl = pyasl.airtovac2(awl,mode='edlen53')

outdata = np.column_stack((vwl,flux))
np.savetxt(outfile, outdata)

exit()
