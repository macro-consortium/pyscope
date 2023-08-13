#!/usr/bin/python

# Extract images from a FITS Multi-Extension file

import os
import sys
import numpy as np
import pyfits

# Set verbose flag True to show headers  and other information

verbose = True

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

if len(sys.argv) == 1:
  print " "
  print "Usage: fits_mef_to_fits_images.py meffile.fits [image number]"
  print " "
  sys.exit("Extract images from a fits Multi-Extension file\n")
elif len(sys.argv) == 2:
  infile = sys.argv[1]
  selectimage = ""
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  selectimage = sys.argv[2]
else:
  print " "
  print "Usage: fits_mef_to_fits_images.py meffile.fits [image number]"
  print " "
  sys.exit("Extract images from a fits Multi-Extension file\n")

  
# Extract the base name of the MEF file

filebase = os.path.splitext(os.path.basename(infile))[0]


# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

nimages = len(inlist) - 1
if (nimages < 1):
  print "This file does not appear to be a FITS MEF file."
  exit()  

if verbose:

  print "The file "+infile+" contains %d images: \n" %(nimages,)
  print inlist.info()
  print ""

  print "with the global header:"
  print inlist[0].header
  print ""

# If asked for a specific image then extract that one and exit

if selectimage !="":
  j = int(selectimage)
  outimage =  inlist[j].data
  outheader = inlist[j].header
  outlist = pyfits.PrimaryHDU(outimage,outheader)
  outfile = filebase+"_im"+str(j)+".fits"
  outlist.writeto(outfile, clobber = clobberflag)
  if verbose:
    print "Image %d written as %s \n" %(j, outfile,)
       

  exit()

# Extract all of them

for i in range (nimages):
  j = i + 1
  outimage =  inlist[j].data
  outheader = inlist[j].header
  outlist = pyfits.PrimaryHDU(outimage,outheader)
  outfile = filebase+"_im"+str(j)+".fits"
  outlist.writeto(outfile, clobber = clobberflag)
  if verbose:
    print "Image %d written as %s \n" %(j, outfile,)
     
exit()

