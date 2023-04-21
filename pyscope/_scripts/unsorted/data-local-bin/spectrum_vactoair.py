#!/usr/bin/python

# Convert vacuum wavelengths to air wavelengths
# Requires PyAstronomy pyasl for Edlen's formulae 

import os
import sys
import numpy as np
from PyAstronomy import pyasl



if len(sys.argv) == 1:
  sys.exit("Usage: spectrum_vactoair.py  infile.dat  outfile.dat ")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  sys.exit("Usage: spectrum_vactoair.py  infile.dat  outfile.dat ")
  
spectrum = np.loadtxt(infile)
vwl = spectrum[:,0]
flux = spectrum[:,1]

awl = pyasl.vactoair2(vwl,mode='edlen53')

outdata = np.column_stack((awl,flux))
np.savetxt(outfile, outdata)

exit()
