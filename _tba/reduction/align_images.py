#!/usr/bin/env python
"""
align_images: Aligns FITS image[s] to a reference image.

INPUT: filepath1 and filepath2 pointing toward images
The first image is used as a reference, and the second image has its WCS information as well as size changed
to be pixel-aligned with the first image for easier comparison.
OUTPUT: Saves a copy of the aligned image as imagename_aligned.fits

Version 1.0 -- Developed by Jacob Isbell, 9 April 2017, modified for batch operation by RLM 16 April 2017
"""

vers = "%prog 1.0 16 Apr 2017"
import glob
import sys
from optparse import OptionParser
from sys import argv

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS


def get_args():
    usage = "Usage: %prog [options] comma-separated FITS files[s]"
    parser = OptionParser(description="Program %prog", usage=usage, version=vers)
    parser.add_option(
        "-r",
        dest="reference",
        metavar="Reference",
        action="store",
        help="Reference FITS image ",
    )
    parser.add_option(
        "-v",
        dest="verbose",
        metavar="Verbose",
        action="store_true",
        default=False,
        help="Verbose output",
    )

    return parser.parse_args()


def round_to_int(x):
    if x - int(x) >= 0.5:
        return int(x) + 1
    else:
        return int(x)


def align_and_crop(im1, im2):
    ref_image = fits.open(im1)[0]
    new_image = fits.open(im2)[0]

    # ---read the central ra and dec of the ref image ---
    ref_ra = ref_image.header["crval1"]
    ref_ctr_px1 = ref_image.header["crpix1"]
    ref_dec = ref_image.header["crval2"]
    ref_ctr_px2 = ref_image.header["crpix2"]
    ref_px_scale = abs(ref_image.header["amdx1"]) / degrees

    # ------ read in the same info for the other image ------
    new_ra = new_image.header["crval1"]
    new_ctr_px1 = new_image.header["crpix1"]
    new_dec = new_image.header["crval2"]
    new_ctr_px2 = new_image.header["crpix2"]
    new_px_scale = abs(new_image.header["amdy1"]) / degrees

    # ----- find the distance between the two image centers ------
    dist_dec = round_to_int((ref_dec - new_dec) / ref_px_scale)
    dist_ra = round_to_int((ref_ra - new_ra) / ref_px_scale)
    if verbose:
        print("Moving %i in x direction" % (dist_ra))
        print("Moving %i in y direction" % (dist_dec))

    if dist_ra > new_image.data.shape[0] or dist_dec > new_image.data.shape[1]:
        print(
            "The images are separated by too much distance and cannot be aligned. Exiting..."
        )
        sys.exit(1)

    new_im = []
    temp = np.copy(new_image.data)

    # sys.exit()
    if dist_dec >= 0:  # the new image moves up
        temp = np.roll(temp, dist_dec, axis=0)
        for x in range(temp.shape[0]):
            for y in range(dist_dec):
                temp[-y][x] = 0
    elif dist_dec < 0:  # the new image moves down
        temp = np.roll(temp, dist_dec, axis=0)
        for x in range(temp.shape[0]):
            for y in range(dist_dec):
                temp[y][x] = 0
    if dist_ra >= 0:  #  the new image moves left
        temp = np.roll(temp, dist_ra, axis=1)
        for y in range(temp.shape[1]):
            for x in range(dist_ra):
                temp[y][-x] = 0
    elif dist_ra < 0:  #  the new image moves right
        temp = np.roll(temp, dist_ra, axis=1)
        for y in range(temp.shape[1]):
            for x in range(dist_ra):
                temp[y][x] = 0

    """
	fig,(ax1,ax2,ax3) = plt.subplots(3)
	ax2.imshow(np.log10(temp),cmap='hot')
	ax1.imshow(np.log10(ref_image.data),cmap='hot')
	ax3.imshow(np.log10(temp-ref_image.data),vmin=-100,vmax=100,cmap='hot')
	plt.show()
	"""
    # ------ create the headers for the images based on their original headers

    new_hdu = fits.PrimaryHDU(temp)
    new_hdu.header = new_image.header
    new_hdu.header["crval1"] = ref_ra
    new_hdu.header["crval2"] = ref_dec
    # new_hdu.header['crpix1'] = new_image.data.shape[0]/2
    # new_hdu.header['crpix2'] = new_image.data.shape[1]/2
    # new_hdu.header['naxis1'] = new_image.data.shape[0]
    # new_hdu.header['naxis2'] = new_image.data.shape[1]

    return new_hdu


# ------------ MAIN --------------------

degrees = np.pi / 180.0

# Get command  line arguments, assign parameter values
(opts, args) = get_args()

ftsfiles = args[
    0
]  # FITS input file mask (either single file or wildcard - parsed by glob)
ref_image = opts.reference  # Reference FITS image name
verbose = opts.verbose  # Print diagnostics, more
for ftsfile in ftsfiles.split(","):
    ftsroot = ftsfile.split(".")[0]
    new_hdu = align_and_crop(ref_image, ftsfile)
    aligned_name = "%s_aligned.fts" % ftsroot
    new_hdu.writeto(aligned_name, overwrite=True)
    if verbose:
        print("Successfully aligned %s with %s" % (ftsfile, ref_image))
        print("Saved %s as %s" % (ftsfile, aligned_name))
        print()
