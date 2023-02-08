#!/usr/bin/python

# Edit a fits image header 

# Enter input and output files on the command line
# Enter header keyword and value on the command line or in a file
#
# Ignore keywords defined by size and type of data
#
#   SIMPLE
#   BITPIX
#   NAXIS 
#   NAXIS1
#   NAXIS2


import os
import sys
import numpy as np
import pyfits
import re   # To clean tabs from input file
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print ' '
  print 'Usage: fits_edit_head.py infile.fits outfile.fits entry value'
  print '       fits_edit_head.py infile.fits outfile.fits header.txt'
  print ' '
  sys.exit("Edit keywords and values in a fits header \n")
elif len(sys.argv) == 4:
  infile = sys.argv[1]
  outfile = sys.argv[2]
  hdrfile = sys.argv[3]
  hdrfileflag = True
elif len(sys.argv) == 5:
  infile = sys.argv[1]
  outfile = sys.argv[2]
  entry = sys.argv[3]
  value = sys.argv[4]
  hdrfileflag = False
else:
  print ' '
  print 'Usage: fits_edit_head.py infile.fits outfile.fits entry value'
  print '       fits_edit_head.py infile.fits outfile.fits header.txt'
  print ' '
  sys.exit("Edit keywords and values in a fits header \n")

# Open and read the header file if its offered

if hdrfileflag:
  try:
    hdrfp = open(hdrfile, 'r')
    # Read all the lines into a list
    hdrtext = hdrfp.readlines()

    # Close the pixel file
    hdrfp.close()

  except:
    print 'Cannot open the file %s \n' % (hdrfile)
    print 'Usage: fits_edithead.py infile.fits outfile.fits entry value \n'
    print 'Usage: fits_edithead.py infile.fits outfile.fits header.txt \n'
    sys.exit()    


# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  

# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header 

inhdr = inlist[0].header

# Assign input and out image data to  numpy arrays

inimage =  inlist[0].data
outimage = inimage

# Assign the image header

inhdr = inlist[0].header
outhdr = inhdr

# Modify the header

if hdrfileflag:

  # Go through the header file line by line 
  for line in hdrtext:
  
    # Strip and parse entry and value fields using = as separator
    entrytext, valuetext = line.strip().split('=')
   
    # Remove tabs that may appear from hand editing
    entrynotab = re.sub(r"\t", " ", entrytext)
    valuenotab = re.sub(r"\t", " ", valuetext)
   
    # Remove leading and trailing whitespace
    entry = entrynotab.lstrip(' ').rstrip(' ')
    value = valuenotab.lstrip(' ').rstrip(' ')
        
    # Change the header
    outhdr[entry] = value

else:

  # Update the header entry and value from the command line
  outhdr[entry] = value

# Create an output list from the new image and the edited header

outlist = pyfits.PrimaryHDU(outimage,outhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Header edited by fits_edit_head'
outhdr['history'] = 'Image file ' + infile

# Write the fits file

outlist.writeto(outfile, clobber = clobberflag)

# Close the list and exit

inlist.close()

exit()

