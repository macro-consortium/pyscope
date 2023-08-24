#!/usr/bin/env python

# plot-photom: Plots Talon program photom output both vs. UT and phase
# RLM May 2016
# 26 May 2016 add JDrange option [-j]
# 27 Oct 2016 sort data by UT date, add period in hr to plot title
# 09 Dec 2016 RLM add error column on ASCII output file for Czech submissions
# 27 Mar 2017 check for reasonable V1, V1 err values, skip otherwise
# 1.41 reverse default y limits to 1,-1
# 1.50 Add reference line option, change output plot to PDF
# 1.60 Fixed O-C calculation, used numpy.polyfit for fitting, tweaked  phase plot, added width option for minimum fit
# 2.0 Switched to Gaussian fitting using scipy.curvefit [much better fits]
# 2.01 30 Oct 2018 add option to exclude output lines with calsource mag. much fainter than reference image magnitude
# 2.10 2 Nov 2018 switch to BJD time
# 2.11 23 Nov 2018 change default plot type to png
# 2.2 11-Dec-2019 make reading FITS files optional
# 3  Python 3 compatible, remove extraneous [?] imp library import

vers = "v.3.0  (4 March 2020)"

import math
import sys

# suppress warning message when object not found
import warnings
from operator import itemgetter
from optparse import OptionParser

import astropy.io.fits as pyfits
import ephem as ep  # pyephem library
import matplotlib.pyplot as plt
import numpy as np
from astropy import coordinates as coord
from astropy import time
from astropy import units as u
from astroquery.simbad import Simbad
from numpy import linalg
from scipy.optimize import curve_fit
from scipy.stats import chi2

warnings.filterwarnings("ignore")


def get_args():
    global parser
    d_txt = "Program plot-photom: plots output from program photom"
    parser = OptionParser(description=d_txt, version="%s" % vers)
    parser = OptionParser(
        description="%prog plots light curves using output file from program photom",
        version=vers,
    )
    parser.add_option(
        "-a",
        dest="plottype",
        metavar="plottype",
        action="store",
        default="png",
        help="Plot type [default png]",
    )
    parser.add_option(
        "-b",
        dest="barycenter",
        metavar="use barycenter time",
        action="store_true",
        default=False,
        help="Use barycenter time (requires FITS images) [def. False]",
    )
    parser.add_option(
        "-c",
        dest="check",
        metavar="show checkstar",
        action="store_true",
        default=False,
        help="Show check star False]",
    )
    parser.add_option(
        "-d",
        dest="double",
        metavar="show double",
        action="store_true",
        default=False,
        help="Show double phase (0.0-2.0) [default False]",
    )
    parser.add_option(
        "-P",
        dest="period",
        metavar="period",
        action="store",
        type=float,
        default=1,
        help="Period (days)",
    )
    parser.add_option(
        "-p",
        dest="plot_phase",
        metavar="plot_phase",
        action="store_true",
        default=False,
        help="Plot phase [default off]",
    )
    parser.add_option(
        "-j",
        dest="jdrange",
        metavar="jdmin, jdmax",
        action="store",
        default="0,0",
        help="JD range e.g. 2456722.73,2456724.56 [default all]",
    )
    parser.add_option(
        "-l",
        dest="line",
        metavar="line",
        action="store_true",
        default=False,
        help="Draw median line for check star",
    )
    parser.add_option(
        "-J",
        dest="JD0",
        metavar="JD0",
        action="store",
        type=float,
        default=5,
        help="Reference Barycentric Julian date, phase =0",
    )
    parser.add_option(
        "-m",
        dest="mag_ref",
        metavar="Ref. mag.",
        type=float,
        default=0.0,
        help="Reference star magnitude [default =0]",
    )
    parser.add_option(
        "-r",
        dest="refmag",
        metavar="refmag",
        action="store",
        type=float,
        default=1,
        help="Exclude images whose ref. star diff. mag exceeds refmag",
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
        "-w",
        dest="width",
        metavar="width",
        action="store",
        type=int,
        default=20,
        help="Minimum fit width, sample times [default 20]",
    )
    parser.add_option(
        "-T",
        dest="title",
        metavar="title",
        action="store",
        default="",
        help="Alternate plot suptitle [default object]",
    )
    parser.add_option(
        "-v",
        dest="verbose",
        metavar="verbose",
        action="store_true",
        default=False,
        help="Verbose output [default False]",
    )
    parser.add_option(
        "-y",
        dest="yminmax",
        metavar="ymin,ymax",
        action="store",
        default="1,-1",
        help="y axis min, max [default -1,1]",
    )

    return parser.parse_args()


def plot_lc_jd(
    bjd,
    ymin,
    ymax,
    jdmin,
    jdmax,
    obj,
    obj_sigma,
    ck,
    ck_sigma,
    pltname,
    plottype,
    suptitle,
    jd0,
    show_check,
    solve_tmin,
    tmin_args,
    box_text,
    line,
):
    fig, ax = plt.subplots(1)

    if solve_tmin:
        bjd_min, sigma, phs_min, jd1, oc, xmod, phs_mod, ymod = tmin_args
        bjd_min_frac = bjd_min - jd1
        title = (
            "BJD0: %.5f, P: %.9f, \n BJDmin: %.5f +/- %.5f, O-C: %.5f days [%.1f s+/- %.1f s]"
            % (jd0, P, bjd_min, sigma, oc, oc * 86400, sigma * 86400)
        )
    if jdmin != 0:
        jd_offset = jdmin
        xmax = jdmax - jdmin
    else:
        jd_offset = bjd[0]
        xmax = bjd[-1] - bjd[0]
    plt.xlim(0, xmax)
    plt.errorbar(
        bjd - jd_offset, obj, yerr=obj_sigma, ls="none", marker="o", markersize=3
    )
    if show_check:
        plt.errorbar(bjd - jd_offset, ck, yerr=ck_sigma, ls="none", marker=".")
    if use_barycenter:
        plt.xlabel("Barycentric JD - %.3f" % jd_offset)
    else:
        plt.xlabel("Heliocentric JD - %.3f" % jd_offset)
    if np.abs(ref_mag) < 0.01:
        plt.ylabel("Differential magnitude")
    else:
        plt.ylabel("Magnitude (Ref = %.2f)" % ref_mag)

    plt.grid(True)
    plt.suptitle(suptitle)
    if solve_tmin:
        plt.title(title, fontsize=9)
        plt.plot(xmod - jd_offset, ymod, "r-")
        plt.axvline(bjd_min - jd_offset, color="r", lw=1.5, linestyle="dashed")
    plt.ylim(ymin, ymax)
    if line:
        ymed = np.nanmedian(ck)
        plt.axhline(y=ymed, ls="dashed", color="green", label="Check star")
        plt.legend()

    # place a text box in lower right  in axes coords
    if use_barycenter:
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.25)
        ax.text(
            0.75,
            0.15,
            box_text,
            transform=ax.transAxes,
            fontsize=8,
            verticalalignment="top",
            bbox=props,
        )

    plotname = pltname + "_lc_jd." + plottype
    plt.savefig(plotname)
    print("JD-magnitude plot file = %s" % plotname)
    return


def plot_lc_phs(
    phs,
    ymin,
    ymax,
    jdmin,
    jdmax,
    obj,
    obj_sigma,
    ck,
    ck_sigma,
    pltname,
    plottype,
    suptitle,
    jd0,
    show_check,
    show_double,
    solve_tmin,
    tmin_args,
    box_text,
):
    plt.figure()
    fig, ax = plt.subplots(1)
    if solve_tmin:
        bjd_min, sigma, phs_min, jd1, oc, xmod, phs_mod, ymod = tmin_args
        bjd_min_frac = bjd_min - jd1
        title = (
            "BJD0: %.5f, P: %.9f,\n BJDmin: %.5f +/- %.5f,  O-C: %.5f days [%.1f s +/- %.1f s]"
            % (jd0, P, bjd_min, sigma, oc, oc * 86400, sigma * 86400)
        )
    else:
        title = "BJD0: %.5f, P: %.9f day (%.3f hr)" % (jd0, P, P * 24.0)
    xmin = 0
    xmax = 1.0
    if show_double:
        xmax = 2.0
        phs = list(phs) + list(phs + 1)
        if solve_tmin:
            phs_mod = list(phs_mod) + list(phs_mod + 1)
            ymod = list(ymod) + list(ymod)
        obj = list(obj) + list(obj)
        obj_sigma = list(obj_sigma) + list(obj_sigma)
        ck = list(ck) + list(ck)
        ck_sigma = list(ck_sigma) + list(ck_sigma)

    plt.suptitle(suptitle)
    plt.title(title, fontsize=8)

    # place a text box in lower right  in axes coords
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.25)
    ax.text(
        0.75,
        0.15,
        box_text,
        transform=ax.transAxes,
        fontsize=8,
        verticalalignment="top",
        bbox=props,
    )

    plt.errorbar(phs, obj, yerr=obj_sigma, ls="none", marker="o", markersize=2)
    if show_check:
        plt.errorbar(phs, ck, yerr=ck_sigma, color="g", ls="none", marker=".")
    if solve_tmin:
        plt.axvline(phs_min, color="r", lw=1.5, linestyle="dashed")
        plt.plot(phs_mod, ymod, "r.")
    plt.grid(True)
    plt.xlabel("Phase")
    plt.ylabel("Differential magnitude")
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    plotname = pltname + "_lc_phase." + plottype
    plt.savefig(plotname)
    print("Phase-magnitude plot file = %s" % plotname)
    return


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


def get_hdr_info(fts_image):
    # returns usefule FITS header information, including Barycentric JD [calculated from RA,Dec,JD)
    try:
        hdr = pyfits.getheader(fts_image)
    except:
        sys.exit("Cannot find FITS image %s in current directory, exiting" % fts_image)
    ra_str = hdr["RA"]
    dec_str = hdr["DEC"]
    object = hdr["OBJECT"].replace(" ", "")
    filter = hdr["FILTER"]
    telescope = hdr["TELESCOP"]
    exptime = hdr["EXPTIME"]
    date_obs = hdr["DATE-OBS"][0:10].replace("-", "_")
    jd_utc = hdr["JD"] + exptime / (2.0 * 86400)
    bjd = calc_bjd(jd_utc, ra_str, dec_str)

    return object, ra_str, dec_str, exptime, filter, telescope, date_obs, jd_utc, bjd


# MAIN

deg = np.pi / 180.0

# Get command  line arguments, assign parameter values
(opts, args) = get_args()

fname = args[0]
plottype = opts.plottype
use_barycenter = opts.barycenter
show_check = opts.check
show_double = opts.double
refmag = opts.refmag
jd0 = opts.JD0
jdmin, jdmax = [float(x) for x in opts.jdrange.split(",")]
ref_mag = opts.mag_ref
line = opts.line
P = opts.period
plot_phase = opts.plot_phase
solve_tmin = opts.tmin
width = opts.width
suptitle = opts.title
ymin, ymax = [float(x) for x in opts.yminmax.split(",")]
verbose = opts.verbose

# Open photom output file
fn = open(fname, "r")
hdr = fn.readline()[1:-1]

# Read data
lines = fn.readlines()
BJD = []
ut_hr = []
obj = []
obj_sigma = []
ck = []
ck_sigma = []
phs = []
n = 0
for line in lines:
    mjd, dum, dum, a1, a2, a3, a4, a5, a6 = [float(x) for x in line.split()[6:]]
    if use_barycenter:
        ftsname = line.split()[1] + ".fts"
        if n == 0:
            (
                objname,
                ra_str,
                dec_str,
                exptime,
                filter,
                telescope,
                date,
                jd_utc,
                bjd,
            ) = get_hdr_info(ftsname)
        else:
            dum, dum, dum, dum, dum, dum, dum, jd_utc, bjd = get_hdr_info(ftsname)
    else:
        jd_utc = mjd + 2449000  # Heliocentric JD at start of exposure)
        bjd = jd_utc  # Hack!
        date = "JD_%7i" % int(jd_utc)  # why not
        objname = fname.split(".")[0]
        telescope = "Gemini"
        filter = ""
        exptime = 0
        ra_str = ""
        dec_str = ""

    if verbose:
        print(ftsname, jd_utc, bjd, a1)
    jd_ok = (jdmin == 0 and jdmax == 0) or jdmin <= bjd <= jdmax
    v1_ok = -8 < a1 < 8
    v1_sigma_ok = a2 < 1.0
    vref_ok = a5 < refmag
    if v1_ok and v1_sigma_ok and jd_ok and vref_ok:
        hr = math.modf(bjd + 0.5)[0] * 24
        ut_hr.append(hr)
        BJD.append(bjd)
        a1 += ref_mag
        a3 += ref_mag
        obj.append(a1)
        obj_sigma.append(a2)
        ck.append(a3)
        ck_sigma.append(a4)
        phs.append(((bjd - jd0) % P) / P)
        n += 1

if verbose:
    print("%i points read, computing plot..." % n)

# Time sort using BJD
vals = [
    [BJD[i], ut_hr[i], obj[i], obj_sigma[i], ck[i], ck_sigma[i], phs[i]]
    for i in range(len(BJD))
]
sorted_vals = sorted(vals, key=itemgetter(0))
for i in range(n):
    BJD[i], ut_hr[i], obj[i], obj_sigma[i], ck[i], ck_sigma[i], phs[i] = sorted_vals[i]

# Convert to numpy arrays, so means can be subtracted, and offsets applied
ut_hr = np.array(ut_hr)
BJD = np.array(BJD)
obj = np.array(obj)
obj_sigma = np.array(obj_sigma)
ck = np.array(ck)
ck_sigma = np.array(ck_sigma)

# If plotting differential magnitudes, subtract means
if np.abs(ref_mag < 0.01):
    obj -= np.mean(obj)
    ck -= np.mean(ck) + 0.0
phs = np.array(phs)

# Solve for time of minimum using weighted Gaussian LSQ fit centered on minimum of l.c.
if solve_tmin:
    jd_frac, jd_int = np.modf(BJD)
    jd1 = jd_int[0]  # Integer part of first BJD time
    jmin = np.argmax(obj)
    BJD_min0 = BJD[jmin]
    if verbose:
        print(
            "Found sample minimum at BJD = %.5f (jmin = %i, mag = %.2f)"
            % (BJD_min0, jmin, obj[jmin])
        )
    w = width / 2  # Width of fit in points
    x = BJD[jmin - w : jmin + w] - BJD[0]
    y = obj[jmin - w : jmin + w]
    s = obj_sigma[jmin - w : jmin + w]

    # weighted Gaussian fit
    init_vals = (obj[jmin], 0, BJD[jmin] - BJD[0], width * exptime / 86400)
    [a_fit, b_fit, x0_fit, w_fit], cov = curve_fit(fgauss, x, y, p0=init_vals)
    [a_s, b_s, x0_s, w_s] = np.sqrt(np.diag(cov))
    delta_jd = x0_fit
    sigma = x0_s  # Uncertainty in delta_jd
    bjd_min = BJD[0] + delta_jd
    phs_min, oc = phase_diff(bjd_min, jd0, P)

    # generate a model for plotting
    npts = 100
    xmod = np.linspace(BJD[jmin - w] - BJD[0], BJD[jmin + w] - BJD[0], npts)
    ymod = fgauss(xmod, a_fit, b_fit, x0_fit, w_fit)
    xmod += BJD[0]
    phs_mod = ((xmod - jd0) % P) / P
    if verbose:
        print(
            "Fitted minimum at BJD: %.5f +/- %.5f, O-C = %.5f days (%.1f sec +/- %.1f sec). Phase at minimum = %.3f)"
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

# Plot differential magnitude of target, check star vs heliocentric jd
pltname = "%s_%s" % (objname, date)
if suptitle == "":
    suptitle = objname
Ymin = np.mean(obj) + ymin
Ymax = np.mean(obj) + ymax
tmin_args = (bjd_min, sigma, phs_min, jd1, oc, xmod, phs_mod, ymod)
obj_args = (objname, ra_str, dec_str, exptime, filter, telescope, date)
box_text = "%s\nDate: %s\nFilter: %s\nExp time:  %.1f sec" % (
    telescope,
    date,
    filter,
    exptime,
)
plot_lc_jd(
    BJD,
    Ymin,
    Ymax,
    jdmin,
    jdmax,
    obj,
    obj_sigma,
    ck,
    ck_sigma,
    pltname,
    plottype,
    suptitle,
    jd0,
    show_check,
    solve_tmin,
    tmin_args,
    box_text,
    line,
)

# If requested, also plot vs. phase using user-supplied ephemeris
if plot_phase:
    plot_lc_phs(
        phs,
        ymin,
        ymax,
        jdmin,
        jdmax,
        obj,
        obj_sigma,
        ck,
        ck_sigma,
        pltname,
        plottype,
        suptitle,
        jd0,
        show_check,
        show_double,
        solve_tmin,
        tmin_args,
        box_text,
    )

# Write a 2-column bjd, magnitude output file(s)
outfile = pltname + "_jd.dat"
f = open(outfile, "w")
for j in range(len(BJD)):
    f.write("%.5f   %.3f   %.3f\n" % (BJD[j], obj[j], obj_sigma[j]))
f.close()
print("Wrote file %s" % outfile)

if plot_phase:
    outfile = pltname + "_phase.dat"
    f = open(outfile, "w")
    for j in range(len(ut_hr)):
        f.write("%.4f   %.3f   %0.3f\n" % (phs[j], obj[j], obj_sigma[j]))
    f.close()
    print("Wrote file %s" % outfile)
