#!/usr/bin/python

# Inspect the fits header and list the exposure times
#
# Copyright 2014 John Kielkopf
#
#

import os
import sys
import fnmatch
import pyfits
import string
import subprocess

nofile      = "  "

if len(sys.argv) != 2:
  print " "
  sys.exit("Usage: fits_list_exposure.py directory\n")
  exit()


toplevel = sys.argv[-1]

# Search for files with this extension
pattern = '*.fits'

for dirname, dirnames, filenames in os.walk(toplevel):
  for filename in fnmatch.filter(filenames, pattern):
    fullfilename = os.path.join(dirname, filename)
    
    try:    
    
      # Open a fits image file
      hdulist = pyfits.open(fullfilename)
      
    except IOError: 
      print 'Error opening ', fullfilename
      break       
    

    # Get the primary image header
    prihdr = hdulist[0]
    
    #Parse  primary header elements and set flags

    ccdfilter = 0 
    filtername = ""             
    if 'EXPTIME' in prihdr.header:
      imexposure = prihdr.header['EXPTIME']
      #shortfilename = os.path.splitext(os.path.basename(fullfilename))
      shortfilename = os.path.basename(fullfilename)
      print "File: %s  Exposure: %s\n" % (shortfilename, imexposure)
        
        



