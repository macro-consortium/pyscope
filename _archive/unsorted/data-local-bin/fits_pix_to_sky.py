#!/usr/bin/python

# Convert pixel coordinates to sky coordinates

from __future__ import division # Use true division everywhere

import os
import sys
import numpy as np
import pyfits
import pywcs
from time import gmtime, strftime  # for utc

# Format hours as hh:mm:ss.sss string

def hms(hours):
  hr = int(hours)
  subhours = abs( hours - float(hr) )
  minutes = subhours * 60.
  mn = int(minutes)
  subminutes = abs( minutes - float(mn) )
  seconds = subminutes * 60.
  ss = int(seconds)
  subseconds = abs( seconds - float(ss) )
  subsecstr = ("%.3f" % (subseconds,)).lstrip('0')
  timestr = "%02d:%02d:%02d%s" % (hr, mn, ss, subsecstr) 
  return timestr


# Format degrees as +/-dd:mm:ss.sss string

def dms(degrees):
  dg = int(abs(degrees))
  subdegrees = abs( abs(degrees) - float(dg) )
  minutes = subdegrees * 60.
  mn = int(minutes)
  subminutes = abs( minutes - float(mn))
  seconds = subminutes * 60.
  ss = int(seconds)
  subseconds = abs( seconds - float(ss) )
  subsecstr = ("%.3f" % (subseconds,)).lstrip('0')
  if degrees > 0:
    dsign = '+'
  elif degrees == 0.0:
    dsign = ' '
  else:
    dsign = '-'
  anglestr = "%s%02d:%02d:%02d%s" % (dsign, dg, mn, ss, subsecstr) 
  return anglestr


if len(sys.argv) == 1:
  print " "
  print "Usage: fits_pix_to_sky.py wcsfile.fits pixels.txt skycoords.txt  "
  print " "
  sys.exit("Convert pixel coordinates to sky coordinates\n")
elif len(sys.argv) == 4:
  wcsfile = sys.argv[1]
  pixfile = sys.argv[2]
  skyfile = sys.argv[3]
else:
  print " "
  print "Usage: fits_pix_to_sky.py wcsfile.fits pixels.txt skycoords.txt  "
  print " "
  sys.exit("Convert pixel coordinates to sky coordinates\n")
  
# Take x,y coordinates from a ds9 regions file or a plain text file
# Use the wcs header of an image file for the celestial coordinate conversion parameters
# Calculate and export corresponding celestial coordinates

# Set this True for decimal instead of hh:mm:ss.sss +/-dd:mm:ss.sss output

decimalflag = False

# Set this True for verbose output

verboseflag = False


# Open the file with pixel coordinates
pixfp = open(pixfile, 'r')

# Read all the lines into a list
pixtext = pixfp.readlines()

# Close the pixel file
pixfp.close()

# Create a pixels counter and an empty pixels list
i = 0
pixels = []

# Split pixels text and parse into x,y values  
# We try various formats looking for one with a valid entry and take the first one we find
# This searches ds9 box and circle regions, comma separated, and space separated

for line in pixtext:

  if 'circle' in line:
    # Treat the case of a ds9 circle region
    
    # Remove the leading circle( descriptor
    line = line.replace("circle(", '')

    # Remove the trailing )
    line = line.replace(")", '')

    # Remove the trailing \n and split into text fields
    entry = line.strip().split(",")
    
    # Get the x,y values for these fields
    xcenter = float(entry[0])
    ycenter = float(entry[1])
    pixels.append((xcenter, ycenter))
    i = i + 1

  elif 'box' in line:
    # Treat the case of a ds9 box region
    
    # Remove the leading box( descriptor
    line = line.replace("box(", '')

    # Remove the trailing )
    line = line.replace(")", '')

    # Remove the trailing \n and split into text fields
    entry = line.strip().split(",")
     
    # Get the x,y values for these fields
    xcenter = float(entry[0])
    ycenter = float(entry[1])
    pixels.append((xcenter, ycenter))
    i = i + 1
  
  else:
    # Treat the cases of plain text pixel coordinates
    # Try to remove the trailing \n and split into text fields
    
    try:    
      # Treat the case of a plain text comma separated entry
      
      entry = line.strip().split(",")  
      # Get the x,y values for these fields
      xcenter = float(entry[0])
      ycenter = float(entry[1])
      pixels.append((xcenter, ycenter))
      i = i + 1    
    except:      
      
      try: 
        # Treat the case of a plane text blank space separated entry
        entry = line.strip().split()
        xcenter = float(entry[0])
        ycenter = float(entry[1])
        pixels.append((xcenter, ycenter))
        i = i + 1    
           
      except:
        pass
        

      
# How many pixels found?

npixels = i
if npixels < 1:
  sys.exit('No objects found in %s' % (pixelsfile,))
  

# Read the wcs fits reference file and create the reference to the WCS data

wcslist = pyfits.open(wcsfile)
wcshdr = wcslist[0].header
wcs = pywcs.WCS(wcshdr)

# Conversion is based on "1" pixel origin used in ds9 and aij
# Uses http://stsdas.stsci.edu/astrolib/pywcs/examples.html
# Convert pixels list to numpy floating point array

pix_coord = np.array(pixels, dtype=np.float32)
sky_coord = wcs.wcs_pix2sky(pix_coord, 1)

# Inverse transformation
#pix_coord = wcs.wcs_sky2pix(sky_coord,1)

# Close in the image file
wcslist.close()

# Unpack the sky_coord numpy array
nsky, nradec  =  sky_coord.shape

# Test that there are coordinates to write
if nsky < 1:
  sysexit("No coordinates found. ")

# Open the output file for appending 
skyfp = open(skyfile, 'a')
  
if decimalflag: 
  for i in range(nsky):
    ra = sky_coord[i,0] / 15.
    dec = sky_coord[i,1]
    if verboseflag:
      print ra, dec
    skyline = "%f  %f" % (ra, dec)   
    skyfp.write(skyline)
else:
  for i in range(nsky):
    ra = sky_coord[i,0] / 15.
    dec = sky_coord[i,1]
    if verboseflag:
      print hms(ra), dms(dec)
    skyline = hms(ra) + '  ' +  dms(dec) + '\n'  
    skyfp.write(skyline)

# Close the output file
skyfp.close()

exit()

