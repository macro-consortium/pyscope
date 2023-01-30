#!/usr/bin/python

# View a fits image

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc
import matplotlib.pyplot as plt

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_viewer.py [lower upper]"
  print " "
  sys.exit("Views a fits file on a linear scale from lower to upper.\n")
elif len(sys.argv) == 2:
  # Unbounded
  infile = sys.argv[1]
  upper = 65536.
  lower = 0.
elif len(sys.argv) == 4:
  # Bounded
  infile = sys.argv[1]
  lower = float(sys.argv[2])
  upper = float(sys.argv[3]) 
else:
  print " "
  print "Usage: fits_viewer.py [lower upper]"
  print " "
  sys.exit("Views a fits file on a linear scale from lower to upper.\n")
  
# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header 

inhdr = inlist[0].header

# Assign image data to numpy array and get its size

inimage =  inlist[0].data.astype('float32')

# Display the image

thisfig = plt.figure()
thisfig.canvas.set_window_title(infile)

plt.imshow(inimage,vmin=lower,vmax=upper,cmap='gray')
plt.show()

# Close the input  and exit

inlist.close()
exit()

