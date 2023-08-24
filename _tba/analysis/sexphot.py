#!/usr/bin/env python
"""
sexphot: Computes photometric magnitudes using sextractor, plots light curves
Optionally checks magnitudes using SDSS
N.B. Requires sextractor!

1.0 [command line sex, config file location defaults to /usr/local/sextractor/default.sex]
1.1 31 May 2016 - Fixed bug in Sloan lookup function
1.2 13 Jun 2016 - report median magnitudes on plots (if option -l)
1.3 21 Feb 2017 - skip stars with fluxerr = 0
1.4 31 May 2017 - Correctly [?] account for airmass, average color
2.0  2 Dec 2018 - add BJD, solve for minimum time, set ZP mags for IKON camera, changed max  FWHM to 5 pixs, remove SDSS
2.1 10 Jan 2019 - IF AIRMASS keyword not found, calculate using ELEVATION keyword (or give up, use 1.0), add fwhm_filter
2.11 2 Feb 2019 - Check: if sextractor couldn't find stars = skip (try/except)
2.2 17 May 2020 - Fix array integer index problem in time of minimum solver
2.3 22 Jan 2021 - add pDF plot format
2.4 11 Jan 2022 - check Maxim version: do not add 0.5x exposure time to time of observation if version = 6.22+
                  since DATE-OBS and JD keywords are now == observation midpoint (Maxim v.6.22+)
"""
vers = "2.4 (11 Jan 2021)"

import glob
import os
import re
import sys
import warnings
from optparse import OptionParser

import matplotlib.pyplot as plt
import numpy as np
from astropy import coordinates as coord
from astropy import time
from astropy import units as u
from astropy.coordinates import SkyCoord

# from astropy.time import Time
# from astropy import units as u
from astropy.io import fits
from astropy.io.fits import getheader, setval, update
from matplotlib.pyplot import cm
from scipy.optimize import curve_fit, minimize
from scipy.stats import chi2

# Avoid annoying warning about matplotlib building the font cache
warnings.filterwarnings("ignore")

# Sextractor config file path
sex_path = "/usr/local/sextractor/default.sex"


def get_args():
    global parser
    parser = OptionParser(
        description="%prog computes photometric magnitudes using sextractor, plots light curves",
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
        "-F",
        dest="fwhm_off",
        metavar="fwhm_off",
        action="store_true",
        default=False,
        help="Skip FWHM check, default = False",
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
        "-j",
        dest="jdrange",
        metavar="jdrange",
        action="store",
        default="0,0",
        help="BJD range (BJDmin, BJDmax)",
    )
    parser.add_option(
        "-P",
        dest="PDF",
        metavar="PDF",
        action="store_true",
        default=False,
        help="PDF plot format[default png format]",
    )
    parser.add_option(
        "-t",
        dest="tmin",
        metavar="Time_minimum",
        action="store_true",
        default=False,
        help="Solve for time of minimum [default False]",
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
        "-w",
        dest="width",
        metavar="width",
        action="store",
        type=int,
        default=20,
        help="Minimum fit width, sample times [default 20]",
    )
    parser.add_option(
        "-y",
        dest="yrange",
        metavar="yrange",
        action="store",
        default="0,0",
        help="Differential plot yrange [default: autoscale]",
    )
    parser.add_option(
        "-z",
        dest="zp",
        metavar="Zeropoint",
        action="store",
        type=float,
        default=-1,
        help="Zero-point magnitude, defaults to FITS header value",
    )
    return parser.parse_args()


def hms2rad(hms_str):
    import re

    result = 0
    fields = re.split(r"[: _]", hms_str)
    fields = [float(x) for x in fields]
    while len(fields) > 0:
        result = result / 60.0 + fields.pop()
    rad = result * np.pi / 12.0
    return rad


def get_hdrdata(ftsfile):
    hdr = getheader(ftsfile, 0)
    date = hdr["DATE-OBS"]
    exptime = hdr["EXPTIME"]
    filter = hdr["FILTER"][0]
    if "AIRMASS" in hdr:
        airmass = hdr["AIRMASS"]
    elif "ELEVATION" in hdr:
        airmass = 1 / np.sin(hms2rad(hdr["ELEVATION"]))
    else:
        if verbose:
            print(
                "%s: No airmass or elevation in header, assuming airmass = 1.0"
                % ftsfile
            )
        airmass = 1.0
    zp = 0
    zperr = 0
    if "ZMAG" in hdr:
        zp = hdr["ZMAG"]
    if "ZMAGERR" in hdr:
        zperr = hdr["ZMAGERR"]
    nbin = hdr["XBINNING"]  # Assume same for y binning
    arcsec_pixel = np.abs(hdr["CDELT1"] * 3600.0)
    ra_str = hdr["RA"]
    dec_str = hdr["DEC"]
    Maxim_version = float(hdr["SWCREATE"].split()[3])
    jd_utc = hdr["JD"]
    if Maxim_version < 6.22:
        if verbose:
            print(
                "Maxim version %.2f (< 6.22), adding 0.5x exposure time to time of observation"
                % Maxim_version
            )
        jd_utc += exptime / (2.0 * 86400)
    bjd = calc_bjd(jd_utc, ra_str, dec_str)
    return (
        bjd,
        date,
        ra_str,
        dec_str,
        exptime,
        filter,
        arcsec_pixel,
        airmass,
        nbin,
        zp,
        zperr,
    )


def get_sexinfo(sexname, fwhm_filter, exptime, scale):
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
    # Trim list to stars by restricting fwhm values
    fwhm_min = 1.4
    fwhm_max = 7.0
    A = list(zip(Ra, Dec, Snr, Flux, Fluxerr, Fwhm, V, Verr))
    B = []
    for j in range(len(A)):
        if fwhm_min < A[j][5] < fwhm_max or fwhm_off:
            B.append(A[j])
    Ra, Dec, Snr, Flux, Fluxerr, Fwhm, V, Verr = list(zip(*B))
    V = np.array(V)
    Verr = np.array(Verr)
    return Nr, Ra, Dec, Snr, Flux, Fluxerr, Fwhm, V, Verr


def phase_diff(jd, jd0, P):
    # Returns phase and o-c [day] at heliocentric observed date jd given ephemeris jd0,P
    jd_diff = jd - jd0
    phase = (jd_diff % P) / P
    if phase >= 0.5:
        o_c = (phase - 1) * P
    else:
        o_c = phase * P
    return phase, o_c


def fgauss(x, a, b, x0, w):
    t = (x - x0) ** 2 / w**2
    return a * np.exp(-t) + b


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
    Ftsfiles = []
    Mag_catalog = []
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
            elif line[0] == "I":
                Ftsfiles.append(line[1])
            elif line[0] == "F":
                Filter = line[1]
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
            elif line[0] == "E":
                BJD0, P0 = [float(s) for s in line[1:]]
    return (
        Objects,
        Filter,
        Ftsfiles,
        Ra_hms,
        Dec_dms,
        Ra_deg,
        Dec_deg,
        Mag_catalog,
        title,
        BJD0,
        P0,
    )


def calc_bjd(jd_utc, ra_str, dec_str):
    """
    Calculate barycentric dynamical Julian date from UTC Julian date, source coordinates
    Refs: http://docs.astropy.org/en/stable/time
    Eastman, et al. 2010 PASP,122,935
    """
    object = coord.SkyCoord(ra_str, dec_str, unit=(u.hourangle, u.deg), frame="icrs")
    lowell = coord.EarthLocation.of_site(
        "Multiple Mirror Telescope"
    )  # close enough to Winer
    times = time.Time(jd_utc, format="jd", scale="utc", location=lowell)
    ltt_bary = times.light_travel_time(object)
    bjd_tdb = times.tdb + ltt_bary
    return bjd_tdb.value


def calc_tmin(BJD, obj, obj_sigma, width):
    jd_frac, jd_int = np.modf(BJD)
    jd1 = jd_int[0]  # Integer part of first BJD time
    jmin = np.argmax(
        obj
    )  # index of maximum (minimum magnitude), use as guess for fitted minimum
    BJD_min0 = BJD[jmin]
    if verbose:
        print(
            "Found sample minimum at BJD = %.5f (jmin = %i, mag = %.2f)"
            % (BJD_min0, jmin, obj[jmin])
        )
    w = int(width / 2)  # Width of fit in points
    # print(jmin,w)
    x = np.array(BJD[jmin - w : jmin + w]) - BJD[0]
    y = obj[jmin - w : jmin + w]
    s = obj_sigma[jmin - w : jmin + w]

    # weighted Gaussian fit
    init_vals = (obj[jmin], 0, BJD[jmin] - BJD[0], width * exptime / 86400)
    [a_fit, b_fit, x0_fit, w_fit], cov = curve_fit(fgauss, x, y, p0=init_vals)
    [a_s, b_s, x0_s, w_s] = np.sqrt(np.diag(cov))
    delta_jd = x0_fit
    sigma = x0_s  # Uncertainty in delta_jd
    bjd_min = BJD[0] + delta_jd

    # generate a model for plotting
    npts = 100
    xmod = np.linspace(BJD[jmin - w] - BJD[0], BJD[jmin + w] - BJD[0], npts)
    ymod = fgauss(xmod, a_fit, b_fit, x0_fit, w_fit)
    xmod += BJD[0]
    # phs_mod = ( (xmod-jd0) % P)/P
    return bjd_min, sigma, xmod, ymod


# ======== MAIN ================

# Max difference: config vs Sex position [deg]
max_diff = 5 / 3600.0

# Define dictionary of zero-point values and extinction for filters [guesses except for Sloan G, R, I]
# Cal_Apogee = { 'N':(22.0,0.20), 'B':(21.5,0.35), 'G':(22.68,0.28), 'V':(20.6,0.20), 'R':(20.3,0.12), 'I':(20.66,0.05) }
Cal = {
    "N": (23.2, 0.20),
    "C": (23.2, 0.20),
    "L": (23.2, 0.20),
    "B": (22.3, 0.35),
    "G": (22.68, 0.28),
    "V": (22.5, 0.20),
    "R": (22.45, 0.12),
    "I": (21.90, 0.05),
}

# Get command  line arguments, assign parameter values
(opts, args) = get_args()


if not opts.config:
    parser.error("config file (-c) not given, try again")
config_file = opts.config
detect_threshold = opts.sigma  # Sextractor detection threshold [sigma]
csvfile = opts.datafile  # optional CSV output filename
fwhm_off = opts.fwhm_off  # FWHM filter [on by default]
jdmin, jdmax = [float(x) for x in opts.jdrange.split(",")]  # Julian date range
line = opts.line  # Plot median line
solve_tmin = opts.tmin  # Solve for minimum time
verbose = opts.verbose  # Print diagnostics, more
width = opts.width  # Width for finding minimum
ymin, ymax = [
    float(x) for x in opts.yrange.split(",")
]  # Differential plot width, magnitudes
zp_user = opts.zp  # Zeropoint magnitude
PDF = opts.PDF  # Use PDF plot format?

# Parse configuration file
(
    Objects,
    Filter,
    Ftsfiles,
    Ra_hms,
    Dec_dms,
    Ra_deg,
    Dec_deg,
    Mag_catalog,
    title,
    BJD0,
    P0,
) = parse_config(config_file)
nstar = len(Objects)

BJD = []
Date = []
Mag_all = []
Mag_err_all = []
FitsFile_all = []
Nr_all = []

# Expand filenames if needed
if "*" in Ftsfiles[0] or "?" in Ftsfiles[0]:
    Ftsfiles = glob.glob(Ftsfiles[0])
if verbose:
    print("Reading %i FITS image files" % len(Ftsfiles))
for ftsfile in Ftsfiles:
    # Get useful header info [NB not currently using nbin]
    try:
        (
            bjd,
            date,
            ra_str,
            dec_str,
            exptime,
            filter,
            scale,
            airmass,
            nbin,
            zp,
            zperr,
        ) = get_hdrdata(ftsfile)
    except:
        if verbose:
            print("%s header does not have required keywords, skipping" % ftsfile)
        continue
    # If wrong filter, skip
    if filter != Filter:
        if verbose:
            print(
                "%s: Wrong filter [expecting %s, got %s], skipping"
                % (ftsfile, Filter, filter)
            )
        continue

    # If not in user-specified JD range, skip
    if jdmin == 0 and jdmax == 0:
        pass
    else:
        if not jdmin <= bjd <= jdmax:
            if verbose:
                print(
                    "%s: BJD %.5f not in range %.5f - %.5f, skipping"
                    % (ftsfile, bjd, jdmin, jdmax)
                )
            continue
    # Run sextractor
    sexname = os.path.basename(ftsfile).split(".")[0] + ".sexout"
    if verbose:
        print(
            "Running sextractor on %s with detection threshold = %.1f sigma"
            % (ftsfile, detect_threshold)
        )
    os.system(
        "sex %s -c %s -CATALOG_NAME %s -DETECT_THRESH %.1f -VERBOSE_TYPE QUIET"
        % (ftsfile, sex_path, sexname, detect_threshold)
    )

    # Get position, magnitude info for each listed star in output file
    try:
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
        ) = get_sexinfo(sexname, fwhm_off, exptime, scale)
        nobs = len(Ra_sex)
        if verbose:
            print("Sextractor found %i stars" % nobs)
    except:
        if verbose:
            print("Sextractor could'nt find stars, skipping %s" % ftsfile)
        continue
    # Get magnitudes for target objects using position match to sextractor output
    Nr, Mag, Mag_err = get_magnitudes(
        Ra_deg, Dec_deg, Nr_sex, Ra_sex, Dec_sex, max_diff, Mag_sex, Mag_sex_err
    )
    # Convert to magnitude by adding ZP and correcting for extinction. Use user-supplied ZP if specified
    if zp_user > 0:
        ZP = zp_user
        if verbose:
            print("Using user-supplied zero-point (ZP = %.2f)" % ZP)
    elif zp > 0:
        ZP = zp
        if verbose:
            print("Using zero-point found in FITS header: %.2f)" % ZP)
    else:
        ZP = Cal[Filter][0]
        if verbose:
            print("Using preset zero-point for %s filter: (ZP = %.2f)" % (filter, ZP))
    k = Cal[Filter][1]
    # correct for airmass, assume average color correction 0.1
    Mag -= k * airmass - 0.1
    Mag += ZP

    # Add to array, but only if all stars detected
    if not np.isnan(Mag).any():
        BJD.append(bjd)
        Date.append(date)
        Mag_all.append(Mag)
        Mag_err_all.append(Mag_err)
        FitsFile_all.append(ftsfile)
        Nr_all.append(Nr)

nepoch = len(BJD)
if verbose:
    print("Analyzing %i images" % nepoch)

# Sort by BJD
BJD, FitsFile_all, Date, Nr_all, Mag_all, Mag_err_all = (
    list(x)
    for x in zip(*sorted(zip(BJD, FitsFile_all, Date, Nr_all, Mag_all, Mag_err_all)))
)

# Convert to numpy arrays
Mag = np.array(Mag_all)
Mag_err = np.array(Mag_err_all)

# Subtract reference star magnitudes
Ref_Mag = Mag[:, -1]
Diff_mags = Mag - Ref_Mag[:, np.newaxis]

# Target star is first listed
Mag_Target = Diff_mags[:, 0]
Mag_Target_Err = Mag_err[:, 0]
Name_Target = Objects[0].strip()

# Solve for minimum if requested
if solve_tmin:
    bjd_min, sigma, xmod, ymod = calc_tmin(BJD, Mag_Target, Mag_Target_Err, width)
    phs_min, oc = phase_diff(bjd_min, BJD0, P0)
    if verbose:
        print(
            "Fitted minimum at BJD: %.5f +/- %.5f, O-C = %.5f days (%.1f sec +/- %.1f sec). Phase at min = %.3f)"
            % (bjd_min, sigma, oc, oc * 86400, sigma * 86400, phs_min)
        )
else:
    bjd_min = 0
    phs_min = 0
    oc = 0
    jd1 = 0
    sigma = 0
    xmod = 0
    phs_mod = 0
    ymod = 0

# Calculate median differential magnitudes
Medians = np.median(Mag, axis=0)
Stds = np.std(Mag, axis=0)
"""
Diff_mag += Medians[-1]
Diff_err = np.sqrt(Mag_err**2 + Mag_err[-1]**2)
"""
# Plot light curves

# First plot all stars on same plot
fig = plt.figure(figsize=(12, 8))
for j in range(nepoch):
    mjd = BJD[j] - BJD[0]
    color = iter(cm.rainbow(np.linspace(0, 1, nstar + 1)))
    for k in range(nstar):
        c = next(color)
        if j == 0:
            plt.errorbar(
                mjd,
                Mag[j][k],
                yerr=Mag_err[j][k],
                marker="o",
                markersize=5,
                c=c,
                label="%s" % Objects[k],
            )
        else:
            plt.errorbar(
                mjd, Mag[j][k], yerr=Mag_err[j][k], marker="o", markersize=5, c=c
            )
plt.title(title)
plt.legend(loc=2, fontsize=8)
ymin0 = np.max(Medians) + 1
ymax0 = np.min(Medians) - 1
plt.ylim(ymin0, ymax0)
if jdmin != 0.0:
    plt.xlim(jdmin - BJD[0], jdmax - BJD[0])
plt.ylabel("%s Magnitude" % Filter)
plt.xlabel("Days since BJD %.5f (%s)" % (BJD[0], Date[0]))
plt.grid(True)
if PDF:
    plot_title = "%s_lc-all.pdf" % Name_Target
else:
    plot_title = "%s_lc-all.png" % Name_Target
plt.savefig(plot_title)
print("Saved light curve of all stars as %s" % plot_title)
plt.close(fig)

# Plot target star differential magnitude with minimum fit [optional]
fig = plt.figure(figsize=(12, 8))
BJD0_int = np.int(BJD[0])
mBJD = np.array(BJD) - BJD0_int

plt.errorbar(
    mBJD, Mag_Target, yerr=Mag_Target_Err, ls="none", marker="o", markersize=5, c="b"
)
plt.suptitle(title, fontsize=14)
if solve_tmin:
    plt.plot(xmod - BJD0_int, ymod, "r--")
    title = (
        "BJD0: %.6f, P0: %.10f,\n BJDmin: %.5f +/- %.5f,  O-C: %.5f days [%.1f s +/- %.1f s]"
        % (BJD0, P0, bjd_min, sigma, oc, oc * 86400, sigma * 86400)
    )
else:
    title = "%s [RA: %s, Dec: %s] Filter = %s" % (
        Name_Target,
        Ra_hms[0],
        Dec_dms[0],
        Filter,
    )
plt.title(title, fontsize=12)

# Set plot limits
if jdmin != 0.0:
    plt.xlim(jdmin - BJD0_int, jdmax - BJD0_int)
if ymin != 0 or ymax != 0:
    plt.ylim(ymin, ymax)
else:
    mag_range = np.abs(max(Mag_Target) - min(Mag_Target))
    ymin = min(Mag_Target) - 0.2 * mag_range
    ymax = max(Mag_Target) + 0.2 * mag_range
    plt.ylim(ymax, ymin)

UTDate, UTTime = Date[0].split("T")
plt.xlabel("Barycentric JD - %i (Start: %s, %s UT)" % (BJD0_int, UTDate, UTTime))
plt.ylabel("Differential Magnitude (Filter %s)" % Filter)
plt.grid(True)
if PDF:
    plot_file = "%s_%s_lc.pdf" % (Name_Target, UTDate)
else:
    plot_file = "%s_%s_lc.png" % (Name_Target, UTDate)
plt.savefig(plot_file)
print("Saved differential l.c. plot %s" % plot_file)
plt.close(fig)


# write CSV output file if requested
if csvfile != "":
    fn = open(csvfile, "w")
    for j in range(nepoch):
        str1 = " ".join(
            "%s  %.3f %.3f  " % (Objects[k], Mag[j][k], Mag_err[j][k])
            for k in range(nstar)
        )
        s = "%10.5f  %30s   %s\n" % (BJD[j], FitsFile_all[j], str1)
        fn.write(s)
    print("Wrote data file: %s" % csvfile)
    fn.close()
