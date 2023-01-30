#!/usr/bin/python

# Convert fits pixel coordinates to ds9 regions

from __future__ import division # Use true division everywhere

import os
import sys
import numpy as np
import pyfits

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_pix_to_ds9.py pixfile.txt ds9file.reg  "
  print " "
  sys.exit("Convert pixel coordinates to ds9 regions\n")
elif len(sys.argv) == 3:
  pixfile = sys.argv[1]
  ds9file = sys.argv[2]
else:
  print " "
  print "Usage: fits_pix_to_ds9.py pixfile.txt ds9file.txt  "
  print " "
  sys.exit("Convert pixel coordinates to ds9 regions\n")
  
# Take x,y coordinates from a plain text file
# Export a ds9 regions file

# Open the file with pixel coordinates
pixfp = open(pixfile, 'r')

# Read all the lines into a list
pixtext = pixfp.readlines()

# Split pixels text and parse into x,y values  
# We try various formats looking for one with a valid entry and take the first one we find
# This searches ds9 box and circle regions, comma separated, and space separated

# Create an empty list

pixels = []
i = 0

for line in pixtext:

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
  sys.exit('No objects found in %s' % (pixfile,))
  

# Open the ds9 circle regions file
ds9fp = open(ds9file, 'w')
  
# Write some useful global parameters
ds9fp.write("image\n") 

# Write the regions
for i in range(npixels):   
  x, y = pixels[i]
  ds9line = "circle(%7.2f,%7.2f,10.)\n" % (x,y)
  ds9fp.write(ds9line)

# Close the output file
ds9fp.close()


exit()

