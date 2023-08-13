#!/usr/bin/python

# Level a fits image

import os
import sys
import numpy as np
import pyfits
from time import gmtime, strftime  # for utc
import string # for parsing regions

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_level.py infile.fits outfile.fits"
  print "       fits_level.py infile.fits outfile.fits regions.txt"
  print "       fits_level.py infile.fits outfile.fits minval maxval"
  print "       fits_level.py infile.fits outfile.fits minval maxval regions.txt"
  print " "
  sys.exit("Levels an image based on minimum and maximum values and regions\n")
elif len(sys.argv) ==3:
  # No restrictions
  infile = sys.argv[1]
  outfile = sys.argv[2]
  minval = 0.
  maxval = 0.
  minmaxflag = False
  regionsflag = False
elif len(sys.argv) ==4:
  # Regions file
  infile = sys.argv[1]
  outfile = sys.argv[2]
  regionsfile = sys.argv[3]  
  regionsflag = True
  minmaxflag = False 
elif len(sys.argv) ==5:
  # Minimum and maximum
  infile = sys.argv[1]
  outfile = sys.argv[2]
  minval = float(sys.argv[3])
  maxval = float(sys.argv[4])
  if minval >= maxval:
    sys.exit("The specified minimum must be less than the maximum\n")
  minmaxflag = True
  regionsflag = False
elif len(sys.argv) ==6:
  # Minimum, maximum, and regions
  infile = sys.argv[1]
  outfile = sys.argv[2]
  minval = float(sys.argv[3])
  maxval = float(sys.argv[4])
  if minval >= maxval:
    sys.exit("The specified minimum must be less than the maximum\n")
  minmaxflag = True
  regionsfile = sys.argv[5]
  regionsflag = True
else:
  print " "
  print "Usage: fits_level.py infile.fits outfile.fits"
  print "       fits_level.py infile.fits outfile.fits regions.txt"
  print "       fits_level.py infile.fits outfile.fits minval maxval"
  print "       fits_level.py infile.fits outfile.fits minval maxval regions.txt"
  print " "
  sys.exit("Levels an image based on minimum and maximum values and regions\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header 

inhdr = inlist[0].header

# Assign image data to numpy array and get its size

inimage =  inlist[0].data.astype('float32')
xsize, ysize = inimage.shape


# FITS image starts with x,y = 0,0 at the lower left
# inimage[y][x] indexes the array sequentially 
# newimage = np.reshape(inimage, xsize*ysize) 
# newimage[x] indexes the array first along x then to the next y

# Use numpy to level the image

# For f(x,y) = a + bx + cy with N pixels                                   
#                                                                          
# sy2 = Sum(y^2)                                                           
# sxf = Sum(xf)                                                            
# sxy = Sum(xy)                                                            
# syf = Sum(yf)                                                            
# sx2 = Sum(x^2)                                                           
# sx  = Sum(x)                                                             
# sy  = Sum(y)                                                             
# sf  = Sum(f)                                                             

# Set the parameter arrays matching the image size
# Each array contains the value for the corresponding pixel 

x = np.zeros((xsize,ysize))
y = np.zeros((xsize,ysize))

# Construct arrays that have the x and y for each pixel

for i in range(ysize):
  x[:,i] = float(i)
for i in range(xsize):
  y[i,:] = float(i)


# Use a unit array to assure we treat the whole image in floating point 

fone = np.ones((xsize,ysize))
fzero = np.zeros((xsize,ysize))
fimage = fone*inimage


# Modify the image mask based on regions

if regionsflag:

  print " "
  print "Selecting allowed regions \n"
  
  
  # Default mask does not allow any data 
  fmask = fzero*inimage
  
  # Open the regions file
  regionsfp = open(regionsfile, 'r')

  # Read all the lines into a list
  regionstext = regionsfp.readlines()

  # Close the regions file

  regionsfp.close()
  
  # Regions counter
  i = 0
  
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
      radius = float(entry[2])
      xmin = xcenter - radius
      ymin = ycenter - radius
      xmax = xcenter + radius
      ymax = ycenter + radius     
      print 'Region[%i]: (%f, %f) to (%f, %f)' %(i, xmin, ymin, xmax, ymax)
      print "--"
      i = i + 1
      fmask[((x>xmin)&(x<xmax))&((y>ymin)&(y<ymax))] = 1.
    
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
      print xcenter, ycenter, xhw, yhw
      xmin = xcenter - xhw
      ymin = ycenter - yhw
      xmax = xcenter + yhw
      ymax = ycenter + yhw
      print 'Region[%i]: (%f, %f) to (%f, %f)' %(i, xmin, ymin, xmax, ymax)
      print "--"
      i = i + 1
      fmask[((x>xmin)&(x<xmax))&((y>ymin)&(y<ymax))] = 1.
      

  print "Fitting only selected regions \n" 
    
else:
  
  # Use the entire image    
  fmask = fone
  print "Fitting entire image \n"



# Modify the image mask based on minmum and maximum signals

if minmaxflag:

  # construct a min-max image mask that allows only some values
 fmask[fimage < minval] = 0.
 fmask[fimage > maxval] = 0.
 print 'Fitting data between %f and %f \n' %(minval, maxval)
 


# Calculate the sums for the fit to a plane masking only wanted pixels

sx2 = np.sum(x*x*fmask)
sy2 = np.sum(y*y*fmask)
sxy = np.sum(x*y*fmask)
sfx = np.sum(fimage*x*fmask)
sfy = np.sum(fimage*y*fmask)
sx  = np.sum(x*fmask)
sy = np.sum(y*fmask)
sf = np.sum(fimage*fmask)
totpix = np.sum(fmask)

# Test for enough data

if totpix < 5.:
  inlist.close()
  print " "
  sys.exit("Insufficient data within the selection criteria\n")

# Scale the sums 
   
sy2 = sy2/totpix
sfx = sfx/totpix
sxy = sxy/totpix
sfy = sfy/totpix
sx2 = sx2/totpix
sx  = sx/totpix
sy  = sy/totpix 
sf  = sf/totpix 
 
# Compute the least-squares fit for a plane f = a + b*x + c*y

d = (sxy - sx*sy)*(sxy - sx*sy) - (sy2 - sy*sy)*(sx2 - sx*sx)
b = (sxy - sx*sy)*(sfy - sf*sy) - (sy2 - sy*sy)*(sfx - sf*sx)
b = b/d
c = (sxy - sx*sy)*(sfx - sf*sx) - (sx2 - sx*sx)*(sfy - sf*sy)
c = c/d
a = sf - b*sx - c*sy

# print diagnostics on plane image

print ' '
print 'Fitted gradient plane parameters: '
print '  a = %f' %(a,)
print '  b = %f' %(b,)
print '  c = %f' %(c,)
print '  s = %f' %(sf,)
print ' '

# Create the plane image

planeimage = (a - sf)*np.ones((xsize,ysize)) + b*x + c*y

# Create the output the image

outimage = fimage - planeimage

# Create the fits ojbect for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Leveled  by fits_level' 
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the input  and exit

inlist.close()
exit()

