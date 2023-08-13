#!/usr/bin/python

# Center and sum a stack of fits images

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_sum_centered.py regions.txt outfile.fits infile1.fits ...  "
  print " "
  sys.exit("Center and sum a stack of fits images\n")
elif len(sys.argv) >=6:
  regionsfile = sys.argv[1]
  outfile = sys.argv[2]
  infiles = sys.argv[3:]
else:
  print " "
  print "Usage: fits_sum_centered.py regions.txt outfile.fits infile1.fits ...  "
  print " "
  sys.exit("Center and sum a stack of fits images\n")

# Find the centroid offset within an image region centered at x,y estimating the background from the median
# For this x,y is at the center of the pixel
# In a numpy fits image array the first axis is the row number, the second is the column number
# That is, image[i,j] is actually image[y,x]

def centroid(imdata, region):
  x, y, xhw, yhw = region  
  xmin = int(round(x - xhw))
  xmax = int(round(x + xhw))
  ymin = int(round(y - yhw))
  ymax = int(round(y + yhw))  
  pix_sum = 0.0
  pix_x_sum = 0.0
  pix_y_sum = 0.0
  pix_count = 0.0
  pix_bkg = np.median(imdata[ymin:ymax,xmin:xmax])
  for j in range(xmin, xmax + 1):
    for i in range(ymin, ymax + 1):
      pix = imdata[i, j] - pix_bkg
      pix_x_sum += (float(j) - x) * pix
      pix_y_sum += (float(i) - y) * pix
      pix_sum   += pix
      pix_count += 1.0
      
  dx = pix_x_sum/pix_sum
  dy = pix_y_sum/pix_sum
  return dx, dy


# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the regions file
regionsfp = open(regionsfile, 'r')

# Read all the lines into a list
regionstext = regionsfp.readlines()

# Close the regions file
regionsfp.close()

# Create a regions counter and an empty regions list
i = 0
regions = []

# Split regions text and parse into values  

for line in regionstext:
  if 'circle' in line:

    # Remove the leading circle( descriptor
    line = line.replace("circle(", '')

    # Remove the trailing )
    line = line.replace(")", '')

    # Remove the trailing \n and split into text fields
    entry = line.strip().split(",")
    
    # Get the values for these fields
    xcenter = float(entry[0])
    ycenter = float(entry[1])
    xhw = float(entry[2])
    yhw = xhw
    regions.append((xcenter, ycenter, xhw, yhw))
    i = i + 1

  elif 'box' in line:

    # Remove the leading box( descriptor
    line = line.replace("box(", '')

    # Remove the trailing )
    line = line.replace(")", '')

    # Remove the trailing \n and split into text fields
    entry = line.strip().split(",")
     
    # Get the values for these fields
    xcenter = float(entry[0])
    ycenter = float(entry[1])
    xhw = float(entry[2])
    yhw = float(entry[3])
    regions.append((xcenter, ycenter, xhw, yhw))
    i = i + 1
    
# How many regions found?

nregions = i
if nregions < 1:
  sys.exit('No circle or box regions found in %s' % (regionsfile,))
  

# Build the input fits image lists
# Test that all the images are the same shape and exit if not

inlists = []
inhdrs = []
inimages = []
nimages = 0
for infile in infiles:
  inlist = pyfits.open(infile)
  inhdr = inlist[0].header
  
  # This seems to insure that data are handled properly for all fits data types
  inimage = inlist[0].data.astype('float32')
  xsize, ysize = inimage.shape
  fone = np.ones((xsize,ysize))
  fimage = fone*inimage
  
  if nimages == 0:
    inshape0 = inimage.shape
    outimage = np.zeros((xsize,ysize))
  else:
    inshape = inimage.shape
    if inshape != inshape0:
      sys.exit('File %s not the same shape as %s \n' %(infile, infiles[0]) )  

  # Build the lists
  inlists.append(inlist)
  inimages.append(fimage)  
  inhdrs.append(inhdr)
  nimages = nimages + 1

  
# Use regions to centroid, roll, and sum each image in the list

for i in range(nimages):
  tdx = 0.
  tdy = 0.
  
  for j in range(nregions):
    dx, dy = centroid(inimages[i],regions[j])
    tdx = tdx + dx
    tdy = tdy + dy
  
  dxbar = tdx / float(nregions)
  dybar = tdy / float(nregions)
  idxbar = -int(round(dxbar))
  idybar = -int(round(dybar)) 
  inimages[i] = np.roll(inimages[i],idybar,axis=0)
  inimages[i] = np.roll(inimages[i],idxbar,axis=1) 
  outimage = outimage + inimages[i] 

# Create the fits ojbect for this image using the header of the first image

outlist = pyfits.PrimaryHDU(outimage,inhdrs[0])

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Sum of %d images by fits_sum_centered' %(nimages,)
outhdr['history'] = 'First image '+  infiles[0]
outhdr['history'] = 'Last image  '+  infiles[nimages-1]

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the inputs  and exit

for inlist in inlists:
  inlist.close()

exit()

