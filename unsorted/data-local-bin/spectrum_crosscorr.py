#!/usr/bin/python

# Cross-correlate a spectrum with a reference

# Returns the relative spectral shift or radial velocity

# Uses the pyastronomy library function

import os
import sys
import numpy as np
from PyAstronomy import pyasl
import matplotlib.pylab as plt


if len(sys.argv) == 1:
  sys.exit("Usage: spectrum_crosscorr.py spectrum template rvmin rvmax rvstep skip ")
elif len(sys.argv) == 7:
  spfile = sys.argv[1]
  tpfile = sys.argv[2]
  rvmin = float(sys.argv[3])
  rvmax = float(sys.argv[4])
  rvstep = float(sys.argv[5])
  skip = int(float(sys.argv[6]))
else:
  sys.exit("Usage: spectrum_crosscorr.py  spectrum template rvmin rvmax rvstep skip ")

spectrum = np.loadtxt(spfile)
spwl = spectrum[:,0]
spfl = spectrum[:,1]

# print spwl
# print spflux

template = np.loadtxt(tpfile)
tpwl = template[:,0]
tpfl = template[:,1]

# print spwl
# print spfl

# Plot a preview of the spectrum and the template

plt.title("Spectrum (red) and the template (blue)")
plt.plot(spwl, spfl, 'r.-')
plt.plot(tpwl, tpfl, 'b.-')

plt.show()


# Carry out the cross-correlation.
# The RV-range is -rvmin to rvmax  km/s in steps of rvstep
# The first and last skipedge points of the data are skipped.

rv, cc = pyasl.crosscorrRV(spwl, spfl, tpwl, tpfl, rvmin, rvmax, rvstep, mode='doppler', skipedge=skip)


# Find the index of maximum cross-correlation function

maxind = np.argmax(cc)

print "Cross-correlation function is maximized at relative RV = ", rv[maxind], " (km/s)"
if rv[maxind] > 0.0:
  print "  This is a red-shift  with respect to the template."
else:
  print "  This is a blue-shift with respect to the template."

plt.plot(rv, cc, 'bp-')
plt.plot(rv[maxind], cc[maxind], 'ro')
plt.show()

print "Relative RV [km/s]: ", rv[maxind]

exit()
