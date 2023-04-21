"""
Given the names of two FITS files, compare the FITS headers 
to determine which entries are unique to each image and 
which entries are common to both.

Useful for figuring out what needs to be added to a Maxim
FITS image to make it compatible with Talon tools.
"""

import os
import sys

from astropy.io import fits as pyfits

def main():
    if len(sys.argv) != 3:
        print("Usage: %s file1.fits file2.fits" % os.path.basename(__file__))
        sys.exit(1)
    
    filename1 = sys.argv[1]
    filename2 = sys.argv[2]

    hdulist1 = pyfits.open(filename1)
    hdulist2 = pyfits.open(filename2)

    header1 = hdulist1[0].header
    header2 = hdulist2[0].header

    keys1 = list(header1.keys())
    keys2 = list(header2.keys())

    file1_key_lines = []
    file2_key_lines = []
    common_key_lines = []

    for key in keys1:
        if key in keys2:
            common_key_lines.append("1: %s" % str(header1.cards[key]).rstrip())
            common_key_lines.append("2: %s" % str(header2.cards[key]).rstrip())
            common_key_lines.append("")
        else:
            file1_key_lines.append(str(header1.cards[key]).rstrip())

    for key in keys2:
        if key not in keys1:
            file2_key_lines.append(str(header2.cards[key]).rstrip())

    print("Common keys (file1=%s, file2=%s):" % (filename1, filename2))
    for key in common_key_lines:
        print(key)
    print()

    print("Keys in %s only:" % filename1)
    if len(file1_key_lines) == 0:
        print("(none)")
    for key in file1_key_lines:
        print(key)

    print()

    print("Keys in %s only:" % filename2)
    if len(file2_key_lines) == 0:
        print("(none)")
    for key in file2_key_lines:
        print(key)
    print()



if __name__ == "__main__":
    main()