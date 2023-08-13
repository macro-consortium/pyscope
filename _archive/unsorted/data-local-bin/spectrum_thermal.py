#!/usr/bin/python

# Compute a black body spectrum at requested temperature
# SI units of B_nu versus frequency
# For B_lambda multiply by nu^2/c

import os
import sys
import numpy as np
import math as ma



if len(sys.argv) == 1:
  sys.exit("Usage: spectrum_thermal.py temperature  outfile.dat ")
elif len(sys.argv) == 3:
  temperature = float(sys.argv[1])
  outfile = sys.argv[2]
else:
  sys.exit("Usage: spectrum_thermal.py temperature  outfile.dat ")
  
numin = 1.e9
numax = 5.e14
nnus = 4096
hplanck = 6.62607004e-34
clight = 299792458.
kboltzmann = 1.38064852e-23

dnu = (numax - numin) / float(nnus)

freq = [0.] * (nnus)
flux = [0.] * (nnus)

for i in range (nnus):
  nu = numin + dnu * i
  bnu = (2.*hplanck*nu*nu*nu/(clight*clight))/(ma.exp(hplanck*nu/(kboltzmann*temperature)) - 1.)
  freq[i] = nu
  flux[i] = bnu


outdata = np.column_stack((freq,flux))
np.savetxt(outfile, outdata)

exit()
