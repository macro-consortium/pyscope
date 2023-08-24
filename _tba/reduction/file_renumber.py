#!/usr/bin/python

# Rename and sequentially number files

import os
import re
import sys

if len(sys.argv) == 1:
    print(" ")
    print("Usage: file_renumber.py basename file1.ext file2.ext ...")
    print(" ")
    sys.exit("Renumbers sequential files \n")
elif len(sys.argv) >= 3:
    basename = sys.argv[1]
    infiles = sys.argv[2:]
else:
    print(" ")
    print("Usage: file_renumber.py basename file1.ext file2.ext ...")
    print(" ")
    sys.exit("Renumbers sequential files with a new basename\n")

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

n = -1

for infile in infiles:
    n = n + 1

    # Create an output file name

    inbase = os.path.splitext(os.path.basename(infile))[0]
    inext = os.path.splitext(os.path.basename(infile))[1]
    val = re.findall(r"\d+", inbase)
    intval = int(float(val[0]))
    valtxt = "%04d" % (intval,)
    outfile = basename + valtxt + inext
    os.rename(infile, outfile)

exit()
