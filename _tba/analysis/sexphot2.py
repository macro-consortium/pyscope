#!/usr/bin/env python

# sexphot2
# Computes 2-color [G,R] photometric magnitudes using sextractor, plots light curves for G, R filters and g-r color index
# Optionally checks magnitudes using SDSS

# N.B. Requires sextractor!
# [command line sex, config file location defaults to /usr/local/sextractor/default.sex]
# v. 1.0 11 Mar 2017
# v. 1.1 26 Mar 2017  - add fwhm_range in opts
# v. 1.2 31 May 2017  - check photometry
# v. 1.3 13 Jun 2017  - fix problem with some epochs having nan magnitudes

vers = "1.3 (13 Jun 2017)"

import glob
import itertools
import os
import re
import sys
import warnings
from optparse import OptionParser

import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.io.fits import getheader, setval, update
from astropy.time import Time
from astroquery.sdss import SDSS
from matplotlib.pyplot import cm
from scipy.optimize import minimize

# Avoid annoying warning about matplotlib building the font cache
warnings.filterwarnings("ignore")

# Sextractor config file path
sex_path = "/usr/local/sextractor/default.sex"


def get_args():
    global parser
    parser = OptionParser(
        description="Program %prog plots 2-color (Sloan g,r) absolute photometric magnitudes and color index g-r using sextractor, ZP mag",
        version="%s" % vers,
    )
    parser.add_option(
        "-s",
        dest="sigma",
        metavar="sigma",
        action="store",
        type=float,
        default=5,
        help="Sextractor detection threshold [default 5]",
    )
    parser.add_option(
        "-c",
        dest="config",
        metavar="config",
        action="store",
        help="phot config file name [no default]",
    )
    parser.add_option(
        "-d",
        dest="datafile",
        metavar="outfile",
        action="store",
        default="",
        help="Output csv file name",
    )
    parser.add_option(
        "-f",
        dest="fwhm_range",
        metavar="fwhm_range",
        action="store",
        default="1.4,5",
        help="FWHM max (pixels)   [default 1.4,5]",
    )
    parser.add_option(
        "-l",
        dest="line",
        metavar="line",
        action="store_true",
        default=False,
        help="Plot median line",
    )
    parser.add_option(
        "-p",
        dest="plot",
        metavar="plot",
        action="store_true",
        default=True,
        help="Plot solution",
    )
    parser.add_option(
        "-J",
        dest="jdrange",
        metavar="jdrange",
        action="store",
        default="0,0",
        help="JD range (JDmin, JDmax)",
    )
    parser.add_option(
        "-v",
        dest="verbose",
        metavar="Verbose",
        action="store_true",
        default=False,
        help="Verbose output",
    )
    parser.add_option(
        "-y",
        dest="ywidth",
        metavar="ywidth",
        action="store",
        type=float,
        default=2.0,
        help="Differential plot width [mags, default 2 mag]",
    )
    return parser.parse_args()


def get_hdrdata(ftsfile):
    hdr = getheader(ftsfile, 0)
    jd = hdr["JD"]
    date = hdr["DATE-OBS"]
    exptime = hdr["EXPTIME"]
    filter = hdr["FILTER"][0]
    airmass = hdr["AIRMASS"]
    if "ZMAG" in hdr:
        zp = hdr["ZMAG"]
        zperr = hdr["ZMAGERR"]
    else:
        zp = 0
        zperr = 0
    nbin = hdr["XBINNING"]  # Assume same for y binning
    arcsec_pixel = np.abs(hdr["CDELT1"] * 3600.0)
    return jd, date, exptime, filter, arcsec_pixel, airmass, nbin, zp, zperr


def get_sexinfo(sexname, exptime, scale):
    global fwhm_min, fwhm_max
    fn = open(sexname, "r")
    lines = fn.readlines()[15:]
    Nr = []
    Ra = []
    Dec = []
    Snr = []
    Flux = []
    Fluxerr = []
    Fwhm = []
    V = []
    Verr = []
    for line in lines:
        (
            nr,
            dum,
            dum,
            flux,
            fluxerr,
            x_pix,
            y_pix,
            ra_deg,
            dec_deg,
            profile_x,
            profile_y,
            pa,
            fwhm_pixel,
            dum,
            flag,
        ) = [float(x) for x in line.split()]
        v = -2.5 * np.log10(flux / exptime)
        if fluxerr == 0:
            continue
        snr = flux / fluxerr
        verr = 2.5 * (fluxerr / flux)  # Expanding log10(1+x) ~ 2.5x
        Nr.append(nr)
        Ra.append(ra_deg)
        Dec.append(dec_deg)
        Flux.append(flux)
        Fluxerr.append(fluxerr)
        Fwhm.append(fwhm_pixel * np.abs(scale))
        Snr.append(snr)
        V.append(v)
        Verr.append(verr)
    fn.close()
    n1 = len(V)
    # Trim list to stars by restricting fwhm values
    A = zip(Ra, Dec, Snr, Flux, Fluxerr, Fwhm, V, Verr)
    B = []
    for j in range(len(A)):
        if fwhm_min < A[j][5] < fwhm_max:
            B.append(A[j])
    Ra, Dec, Snr, Flux, Fluxerr, Fwhm, V, Verr = zip(*B)
    n2 = len(V)
    if verbose:
        print(
            "Warning, skipped %i stars because they exceeded allowed FWHM range (%.1f,%.1f), use option -f to change"
            % (n1 - n2, fwhm_min, fwhm_max)
        )
    V = np.array(V)
    Verr = np.array(Verr)
    return Nr, Ra, Dec, Snr, Flux, Fluxerr, Fwhm, V, Verr


def get_sdss_magnitudes(ra, dec):
    # Query SDSS online photometric catalog for u,g,r,i,z magnitudes; ra,deg in degrees (ICRS, 2000)
    pos = SkyCoord(ra, dec, unit=(u.deg, u.deg), frame="icrs")
    ids = SDSS.query_region(
        pos, radius=5 * u.arcsec, fields=["ra", "dec", "clean", "u", "g", "r", "i", "z"]
    )  # defaults to 2 arcsec search
    u1 = g = r = i = z = np.nan
    if ids != None:
        for id in ids:
            if (
                id["clean"] == 1 and id["g"] < 20.0
            ):  # Only accept photometry with clean flags & reject very faint stars
                u1 = id["u"]
                g = id["g"]
                r = id["r"]
                i = id["i"]
                z = id["z"]
                return u1, g, r, i, z
    return u1, g, r, i, z


def trim(indices, A):
    # Trims arrays packed in A, dropping elements with given indices
    B = []
    for a in A:
        B.append(np.delete(a, indices))
    return B


def get_magnitudes(Ra, Dec, Nr_sex, Ra_sex, Dec_sex, max_diff, Mag_sex, Mag_sex_err):
    N1 = len(Ra)
    N2 = len(Ra_sex)
    Mag = np.empty(N1) * np.nan
    Mag_err = np.empty(N1) * np.nan
    Nr = np.empty(N1) * np.nan
    for j in range(N1):
        for k in range(N2):
            dra = np.abs(Ra[j] - Ra_sex[k])
            ddec = np.abs(Dec[j] - Dec_sex[k])
            if dra < max_diff and ddec < max_diff:
                Mag[j] = Mag_sex[k]
                Mag_err[j] = Mag_sex_err[k]
                Nr[j] = Nr_sex[k]
    Mag = np.array(Mag)
    Mag_err = np.array(Mag_err)
    return Nr, Mag, Mag_err


def parse_config(config_file):
    Objects = []
    Filters = []
    Ftsfiles_G = []
    Ftsfiles_R = []
    Ra_hms = []
    Dec_dms = []
    Ra_deg = []
    Dec_deg = []
    if not os.path.isfile(config_file):
        sys.exit("Configuration file %s does not exist, try again" % config_file)
    else:
        fn = open(config_file, "r")
        lines = fn.readlines()
        fn.close()
        for line in lines:
            line = line.split()
            if line == []:
                continue  # Skip blank lines
            elif line[0] == "G":
                Ftsfiles_G.append(line[1])
            elif line[0] == "R":
                Ftsfiles_R.append(line[1])
            elif line[0] == "S":
                object, ra_hms, dec_dms = line[1:4]
                Objects.append(object)
                Ra_hms.append(ra_hms)
                Dec_dms.append(dec_dms)
                c = SkyCoord(ra_hms, dec_dms, unit=(u.hourangle, u.deg), frame="icrs")
                Ra_deg.append(c.ra.deg)
                Dec_deg.append(c.dec.deg)
            elif line[0] == "T":
                title = " ".join(line[1:])
    return Objects, Ftsfiles_G, Ftsfiles_R, Ra_hms, Dec_dms, Ra_deg, Dec_deg, title


def get_star_info(Ftsfiles, Filter, Cal_vals):
    JD = []
    Date = []
    Mag_all = []
    Mag_err_all = []
    FitsFile_all = []
    Nr_all = []

    for ftsfile in Ftsfiles:
        # Get useful header info [NB not currently using nbin]
        jd, date, exptime, filter, scale, airmass, nbin, zp, zperr = get_hdrdata(
            ftsfile
        )

        # If wrong filter, skip
        if filter != Filter:
            if verbose:
                print(
                    "%s: Wrong filter [expecting %s, got %s], skipping"
                    % (ftsfile, Filter, filter)
                )
            continue

        # Run sextractor
        if verbose:
            print(
                "Running sextractor on %s with detection threshold = %.1f sigma"
                % (ftsfile, detect_threshold)
            )
        sname = "%s_%s.sexout" % (os.path.basename(ftsfile).split(".")[0], Filter)
        os.system(
            "sex %s -c %s -CATALOG_NAME %s -DETECT_THRESH %.1f -VERBOSE_TYPE QUIET"
            % (ftsfile, sex_path, sname, detect_threshold)
        )

        # Get position, magnitude info for each listed star in output file
        (
            Nr_sex,
            Ra_sex,
            Dec_sex,
            Snr,
            Flux,
            Fluxerr,
            Fwhm_sex,
            Mag_sex,
            Mag_sex_err,
        ) = get_sexinfo(sname, exptime, scale)
        nobs = len(Ra_sex)
        if verbose:
            print("Sextractor found %i stars" % nobs)

        # Get magnitudes for target objects using position match to sextractor output
        Nr, Mag, Mag_err = get_magnitudes(
            Ra_deg, Dec_deg, Nr_sex, Ra_sex, Dec_sex, max_diff, Mag_sex, Mag_sex_err
        )

        # Convert to magnitude by adding ZP. Use user-supplied ZP if specified
        if zp > 0:
            ZP = zp
            k = Cal_vals[Filter][1]
        else:
            ZP, k = Cal_vals[Filter]
            if verbose:
                print(
                    "WARNING: Using default zero-point for %s filter: (ZP = %.2f)"
                    % (filter, ZP)
                )
        # correct for airmass, assume average color correction 0.1
        Mag -= k * airmass - 0.1
        Mag += ZP
        # Add to array, but only if all stars detected
        # if not np.isnan(Mag).any():
        if True:
            JD.append(jd)
            Date.append(date)
            Mag_all.append(Mag)
            Mag_err_all.append(Mag_err)
            FitsFile_all.append(ftsfile)
            Nr_all.append(Nr)
    # Sort by JD
    JD, FitsFile_all, Date, Nr_all, Mag_all, Mag_err_all = (
        list(x)
        for x in zip(*sorted(zip(JD, FitsFile_all, Date, Nr_all, Mag_all, Mag_err_all)))
    )

    # Convert to numpy arrays
    Mag = np.array(Mag_all)
    Mag_err = np.array(Mag_err_all)

    # Calculate median differential magnitudes
    Medians = np.nanmedian(Mag, axis=0)
    Stds = np.nanstd(Mag, axis=0)
    # print 'Medians = %s' % ( (' '.join('%5.2f' % x for x in Medians)))
    return JD, Date, FitsFile_all, Mag, Mag_err, Medians, Stds


def mk_plot(
    j,
    JD0,
    Date0,
    object,
    Ra_hms,
    Dec_dms,
    mjd_g,
    mjd_r,
    G_mag,
    G_mag_err,
    R_mag,
    R_mag_err,
    ywidth,
    line,
):
    fig = plt.figure(j, figsize=(12, 8))
    ax = fig.add_subplot(111)
    ym = np.nanmean(np.append(G_mag, R_mag))
    ymin = ym + ywidth / 2.0
    ymax = ymin - ywidth
    plt.errorbar(mjd_g, G_mag, yerr=G_mag_err, fmt="bs", label="Sloan g")
    plt.errorbar(mjd_r, R_mag, yerr=R_mag_err, fmt="rs", label="Sloan r")
    plt.suptitle(title, fontsize=14)
    plt.title("%s [RA: %s, Dec: %s]" % (object, Ra_hms, Dec_dms), fontsize=12)
    if jdmin != 0.0:
        plt.xlim(jdmin - JD0, jdmax - JD0)
    plt.legend(loc=2)
    plt.ylim(ymin, ymax)
    if line:
        xmin, xmax = ax.get_xlim()
        xline = [xmin, xmax]
        ym_g = np.nanmedian(G_mag)
        ym_r = np.nanmedian(R_mag)
        std_g = np.nanstd(G_mag)
        std_r = np.nanstd(R_mag)
        yline_g = [ym_g, ym_g]
        yline_r = [ym_r, ym_r]
        plt.plot(xline, yline_g, linestyle="dashed", color="blue")
        plt.plot(xline, yline_r, linestyle="dashed", color="red")
        txt = "Median g = %.2f +/- %.2f,  r = %.2f +/- %.2f, g-r = %.2f" % (
            ym_g,
            std_g,
            ym_r,
            std_r,
            ym_g - ym_r,
        )
        plt.text(
            0.05,
            0.05,
            txt,
            fontsize=12,
            transform=ax.transAxes,
            bbox=dict(facecolor="white", alpha=0.5),
        )

    UTDate, UTTime = Date0.split("T")
    plt.xlabel("Days since JD %.5f (%s, %s UT)" % (JD0, UTDate, UTTime))
    plt.ylabel("Magnitude at airmass = 0")
    plt.grid(True)
    plot_title = "%s_lc.pdf" % object
    plt.savefig(plot_title)
    print("Saved differential l.c. plot %s" % plot_title)
    plt.close(fig)


# ======== MAIN ================

# Max difference: config vs Sex position [deg]
max_diff = 5 / 3600.0

# Define dictionary of zero-point values and extinction for filters [guesses except for G, R]
Cal_vals = {
    "N": (21.5, 0.20),
    "B": (21.0, 0.35),
    "G": (22.2, 0.28),
    "V": (20.5, 0.20),
    "R": (21.8, 0.12),
    "W": (20.66, 0.05),
}

# Get command  line arguments, assign parameter values
(opts, args) = get_args()

if not opts.config:
    parser.error("config file (-c) not given, try again")
config_file = opts.config

detect_threshold = opts.sigma  # Sextractor detection threshold [sigma]
plot = opts.plot  # Plot various things
csvfile = opts.datafile  # optional CSV output filename
jdmin, jdmax = [float(x) for x in opts.jdrange.split(",")]  # Julian date range
line = opts.line  # Plot median line
verbose = opts.verbose  # Print diagnostics, more
ywidth = opts.ywidth  # Differential plot width, magnitudes
fwhm_min, fwhm_max = [
    float(x) for x in opts.fwhm_range.split(",")
]  # Maximum allowed FWHM (pixels)

# Parse configuration file
Objects, Ftsfiles_G, Ftsfiles_R, Ra_hms, Dec_dms, Ra_deg, Dec_deg, title = parse_config(
    config_file
)
nstar = len(Objects)


# Expand filenames if needed
if "*" in Ftsfiles_G[0] or "?" in Ftsfiles_G[0]:
    Ftsfiles_G = glob.glob(Ftsfiles_G[0])
if "*" in Ftsfiles_R[0] or "?" in Ftsfiles_R[0]:
    Ftsfiles_R = glob.glob(Ftsfiles_R[0])


Filters = ["G", "R"]
for Filter in Filters:
    if Filter == "G":
        (
            JD_G,
            Date_G,
            FitsFiles_all_G,
            Mag_G,
            Mag_err_G,
            Medians_G,
            Stds_G,
        ) = get_star_info(Ftsfiles_G, Filter, Cal_vals)
    elif Filter == "R":
        (
            JD_R,
            Date_R,
            FitsFiles_all_R,
            Mag_R,
            Mag_err_R,
            Medians_R,
            Stds_R,
        ) = get_star_info(Ftsfiles_R, Filter, Cal_vals)
"""
print 'G'
for k in range(len(JD_G)):
	print JD_G[k], Mag_G[k]
print 'R'
for k in range(len(JD_R)):
	print JD_R[k], Mag_R[k]
"""

# Plot light curves

JD0 = min(JD_G[0], JD_R[0])
if JD0 == JD_G[0]:
    Date0 = Date_G[0]
else:
    Date0 = Date_R[0]
mjd_g = [x - JD0 for x in JD_G]
mjd_r = [x - JD0 for x in JD_R]
marker = itertools.cycle(["s", "d", "p", "*", "8"])

# First plot all stars on same plot
plt.figure(1, figsize=(12, 8))

params = {"legend.fontsize": 10}
plt.rcParams.update(params)

G_mag = np.transpose(Mag_G)
G_mag_err = np.transpose(Mag_err_G)
R_mag = np.transpose(Mag_R)
R_mag_err = np.transpose(Mag_err_R)

# Correct for color

for k in range(nstar):
    mark = marker.next()
    plt.errorbar(
        mjd_g,
        G_mag[k],
        yerr=G_mag_err[k],
        marker=mark,
        markersize=8,
        c="b",
        label="%s [G]" % Objects[k],
    )
    plt.errorbar(
        mjd_r,
        R_mag[k],
        yerr=R_mag_err[k],
        marker=mark,
        markersize=8,
        c="r",
        label="%s [R]" % Objects[k],
    )

plt.title(title)
plt.legend(loc=2)
plt.ylim(18, 12)
if jdmin != 0.0:
    plt.xlim(jdmin - JD[0], jdmax - JD[0])
plt.ylabel("%s Magnitude" % Filter)
plt.xlabel("Days since JD %.5f (%s)" % (JD0, Date0))
plt.grid(True)
plot_title = "%s_lc-all.pdf" % (config_file.split(".")[0])
plt.savefig(plot_title)
print("Saved light curve plot as %s" % plot_title)

# Separate plots for object
for k in range(nstar):
    mk_plot(
        k + 2,
        JD0,
        Date0,
        Objects[k],
        Ra_hms[k],
        Dec_dms[k],
        mjd_g,
        mjd_r,
        G_mag[k],
        G_mag_err[k],
        R_mag[k],
        R_mag_err[k],
        ywidth,
        line,
    )


# write CSV output file if requested
if csvfile != "":
    fn = open(csvfile, "w")
    for j in range(len(JD_G)):
        str1 = " ".join(
            "%s: %.3f %.3f" % (Objects[k], G_mag[k][j], G_mag_err[k][j])
            for k in range(nstar)
        )
        s = "%10.5f	 %30s	G  %s\n" % (JD_G[j], FitsFiles_all_G[j], str1)
        fn.write(s)
    for j in range(len(JD_R)):
        str1 = " ".join(
            "%s: %.3f %.3f" % (Objects[k], R_mag[k][j], R_mag_err[k][j])
            for k in range(nstar)
        )
        s = "%10.5f	 %30s	R  %s\n" % (JD_R[j], FitsFiles_all_R[j], str1)
        fn.write(s)
    print("Wrote data file: %s" % csvfile)
    fn.close()
