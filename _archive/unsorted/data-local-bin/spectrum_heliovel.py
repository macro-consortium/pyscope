#!/usr/bin/python

# Find radial velocity  of an observatory with respect to an object

# Returns the barycentric correction accounting for the motion of the observer.

# Uses the pyastronomy library helcorr function that is imported from the REDUCE IDL package
# This function calculates the motion of an observer in the direction of a star taking into account
# the motion of the Earth including its rotation relative to the solar system barycenter.

import os
import sys
from PyAstronomy import pyasl

if len(sys.argv) == 1:
  sys.exit("Usage: spectrum_heliovel.py  longitude (+east)  latitude (deg)  altitude (m) jd  ra2000 (deg) dec2000 (deg)")
elif len(sys.argv) == 7:
  longitude = float(sys.argv[1])
  latitude = float(sys.argv[2])
  altitude = float(sys.argv[3])
  jd = float(sys.argv[4])
  ra2000 = float(sys.argv[5])
  dec2000 = float(sys.argv[6])
else:
  sys.exit("Usage: spectrum_heliovel.py  longitude (+east)  latitude (deg)  altitude (m) jd  ra2000 (deg) dec2000 (deg)")


# Example: coordinates of European Southern Observatory UT1 + east
# longitude = 289.5967661
# latitude = -24.62586583
# altitude = 2635.43

# Example: coordinates of AAT at Siding Spring + east
# longitude = 149.0613889
# latitude = -31.2733333
# altitude = 1149.0

# Example: Moore Observatory near Crestwood, Kentucky USA + east 
# longitude = 274.4711
# latitude = 38.34444444
# altitude = 229.2

# Example: Mt. Kent Observatory  near Toowoomba, Queensland Australia + east
# longitude =  151.855528 
# latitude = -27.7977777
# altitude = 682.0

# Example: coordinates of Sirius (J2000)
# Coordinates of Sirius (J2000)

# ra2000  = 101.28715535
# dec2000 = -16.71611587

# Example: Time of observation (20:00 EST Moore Observatory 1997-3-21)
# jd = 2450528.54167


# Test values from pyasl: 
# longitude = 289.5967661
# latitude = -24.62586583
# altitude = 2635.43
# ra2000 = 030.20313477
# dec2000 = -12.87498346
# jd = 2450528.2335


corr, hjd = pyasl.helcorr(longitude, latitude, altitude, ra2000, dec2000, jd, debug=True)

print "Geocentric JD: ", jd
print "Heliocentric JD: ", hjd
print "Target RA [degrees]: ", ra2000
print "Target Declination [degrees]: ", dec2000
print "Barycentric velocity (+ is toward the star) [km/s]: ", corr
print "Add this as a correction to a topocentric measurement of radial velocity."

exit()
