#!/usr/bin/python

# Aperture photometry on a fits image file 
# Accepts input list of pixel or ds9 coordinates
# Returns a file with photometry and coordinates

from __future__ import division # Use true division everywhere

import os
import sys
import math as ma
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc


def hms(hours):

  # Format floating point hours into a hh:mm:ss.sss string

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


def dms(degrees):
  
  # Format floating point degrees into a +/-dd:mm:ss.sss string
  
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


def apphot(scidata, px, py, r0, r1, r2):

  # AIJ or ds9 floating point pixel coordinates (px,py) indexed from 1.0
  # Photometry aperture r0
  # Photometry inner radius r1
  # Photometry outer radius r2
  # Finds the signal inside the inner radius centered at  (px,py)
  # Subtracts a background from the outer annulus with outlier removal
  # The numpy array scidata is a fits image in the usual flipped numpy format

  # Calculate squares once
  
  r02 = r0*r0
  r12 = r1*r1
  r22 = r2*r2
  
  # What are the image limits inside the outer annulus
  
  ny, nx = scidata.shape
  
  pxmin = max(1,  int(px - r2))
  pxmax = min(nx, int(px + r2))
  pymin = max(1,  int(py - r2))
  pymax = min(ny, int(py + r2))
  
  # Initialize sums in the aperture and in the annulus
    
  sum_ap = 0.0
  sum_an = 0.0
  sum_an2 = 0.0
  
  # Initialize pixel counts in aperture and in annulus
  
  count_ap = 0
  count_an = 0

  # Find totals inside aperture and annulus
  # Note numpy image array scidata has first index y, second x 
  
  for j in range(pxmin, pxmax + 1):
    for k in range(pymin, pymax + 1):
      dpx = (j - px)
      dpy = (k - py)
      dp2 = dpx*dpx + dpy*dpy
      pixval = scidata[k-1, j-1]
      if dp2 < r02:
        sum_ap = sum_ap + pixval
        count_ap = count_ap + 1
      elif dp2 >= r12 and dp2 <= r22:
        sum_an = sum_an + pixval
        sum_an2 = sum_an2 + pixval*pixval
        count_an = count_an + 1

  # When there are no pixels this prevents a divide by zero error
  
  count_ap = max(1, count_ap)
  count_an = max(1, count_an)

  # Determine average values in the annulus
  
  average_an = sum_an/float(count_an)
  average_an2 = sum_an2/float(count_an)
  
  # Estimate the standard deviation for the annulus
    
  sigma_an = ma.sqrt(abs(average_an2 - average_an*average_an))

  # Make several more passes to exclude outliers in the annulus
  
  npasses = 10
  
  for i in range (npasses):
    sum_an = 0.0
    sum_an2 = 0.0
    count_an = 0
    for j in range(pxmin, pxmax + 1):
      for k in range(pymin, pymax + 1):
        dpx = (j - px)
        dpy = (k - py)
        dp2 = dpx*dpx + dpy*dpy
        pixval = scidata[k-1, j-1] 
        if dp2 >= r12 and dp2 <= r22 and abs(pixval - average_an) <= 2.*sigma_an:
          sum_an = sum_an + pixval
          sum_an2 = sum_an2 + pixval*pixval
          count_an = count_an + 1  
    count_an = max(1, count_an)
    average_an = sum_an/float(count_an)
    average_an2 = sum_an2/float(count_an)
    sigma_an = ma.sqrt(abs(average_an2 - average_an*average_an))

  # Calculate target signal - background and return
  
  signal  = sum_ap - float(count_ap)*average_an
  
  return signal

def apphot_nobkg(scidata, px, py, r0):

  # AIJ or ds9 floating point pixel coordinates (px,py) indexed from 1.0
  # Photometry aperture r0
  # Finds the signal inside the inner radius centered at  (px,py)
  # The numpy array scidata is a fits image in the usual flipped numpy format

  # Calculate squares once
  
  r02 = r0*r0
  
  # What are the image limits inside the radius
  
  ny, nx = scidata.shape
  
  pxmin = max(1,  int(px - r02))
  pxmax = min(nx, int(px + r02))
  pymin = max(1,  int(py - r02))
  pymax = min(ny, int(py + r02))
  
  # Initialize sums in the aperture
    
  sum_ap = 0.0
  
  # Initialize pixel counts in aperture and in annulus
  
  count_ap = 0

  # Find totals inside aperture 
  # Note numpy image array scidata has first index y, second x 
  
  for j in range(pxmin, pxmax + 1):
    for k in range(pymin, pymax + 1):
      dpx = (j - px)
      dpy = (k - py)
      dp2 = dpx*dpx + dpy*dpy
      pixval = scidata[k-1, j-1]
      if dp2 < r02:
        sum_ap = sum_ap + pixval
        count_ap = count_ap + 1

  # When there are no pixels this prevents a divide by zero error
  
  count_ap = max(1, count_ap)
  
  # Calculate target signal - background and return
  
  signal  = sum_ap
  
  return signal


# Main code begins here


if len(sys.argv) == 1:
  print " "
  print "Usage: fits_pixel_photometry.py r_aperture [r_inner r_outer] infile.fits pixels.txt skydata.txt  "
  print " "
  sys.exit("Aperture photometry on an input fits image\n")
elif len(sys.argv) == 5:
  rphot = float(sys.argv[1])
  bkgflag = 0
  fitsfile = sys.argv[2]
  pixfile = sys.argv[3]
  skyfile = sys.argv[4]
elif len(sys.argv) == 7:
  rphot = float(sys.argv[1])
  rinner = float(sys.argv[2])
  router = float(sys.argv[3])
  bkgflag = 1
  fitsfile = sys.argv[4]
  pixfile = sys.argv[5]
  skyfile = sys.argv[6]
else:
  print " "
  print "Usage: fits_pixelphotometry.py r_aperture [r_inner r_outer] infile.fits pixels.txt skydata.txt  "
  print " "
  sys.exit("Aperture photometry on input fits image \n")
  
# Take x,y coordinates from a ds9 regions file or a plain text file
# Calculate photometry and export data with coordinates


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
  

# Read the FITS image file

fitslist = pyfits.open(fitsfile)
fitshdr = fitslist[0].header
fitsdata = fitslist[0].data

# Convert pixels list to numpy floating point array

pix_coord = np.array(pixels, dtype=np.float32)


# Close in the image file
fitslist.close()

# Unpack the sky_coord numpy array
nsky, nxy  =  pix_coord.shape

# Test that there are coordinates to write
if nsky < 1:
  sysexit("No coordinates found. ")

# Open the output file for appending 
skyfp = open(skyfile, 'a')

for i in range(nsky):
  x = pix_coord[i,0]
  y = pix_coord[i,1]
  if bkgflag == 1:
    sky = apphot(fitsdata, x, y, rphot, rinner, router)    
  else:
    sky = apphot_nobkg(fitsdata, x, y, rphot)
  skyline = "%5.2f  %5.2f  %f \n" % (x, y, sky)
  skyfp.write(skyline)

# Close the output file
skyfp.close()

exit()

