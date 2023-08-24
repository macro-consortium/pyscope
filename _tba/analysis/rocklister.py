#!/usr/bin/env python

# Rocklister - lists MPC objects [using MPC database query] in a region and date extracted from a FITS header or specified by RA,Dec, UT Date/time

# Version 1.0 12/6/2016 RLM and Chris Michael
# 1.01 21 Jan 2017 update Optparser with usage string to show FITS image

vers = "rocklister v1.01"

import os
import sys
from optparse import OptionParser

import astropy.io.fits as fits
import requests
from astropy import units as u
from astropy.coordinates import SkyCoord


def get_args():
    parser = OptionParser(
        usage="Uasge: %prog [options] FITSimage",
        description="Program %prog queries MPC online database for Asteroids and Comets",
        version=vers,
    )
    parser.add_option(
        "-R",
        dest="RA",
        metavar="RA",
        action="store",
        help="RA to search [hh:mm:ss] (optional, default use FITS header)",
    )
    parser.add_option(
        "-D",
        dest="DEC",
        metavar="DEC",
        action="store",
        help="DEC to search [dd:mm] (optional, default use FITS header)",
    )
    parser.add_option(
        "-r",
        dest="radius",
        default=15,
        metavar="Radius",
        action="store",
        help="Search radius [arcmin], default 15",
    )
    parser.add_option(
        "-m",
        dest="limmag",
        default=20,
        metavar="LimMag",
        action="store",
        help="Limiting magnitude, default 20",
    )
    parser.add_option(
        "-d",
        dest="date",
        metavar="date",
        action="store",
        help="Date string [yyyy/mm/dd] (optional, default use FITS header)",
    )
    parser.add_option(
        "-t",
        dest="ut",
        metavar="time",
        action="store",
        default="00:00",
        help="UT time [hh:mm] (optional, default use FITS header)",
    )
    return parser.parse_args()


def get_hdr_info(ftsfile):
    im, hdr = fits.getdata(ftsfile, 0, header=True)
    object = hdr["OBJECT"]
    nbin = hdr["XBINNING"]
    D = hdr["DATE-OBS"]
    date = D[0:10]
    ut = D[11:]
    ra = hdr["RA"]
    dec = hdr["DEC"]
    exptime = hdr["EXPTIME"]
    filter = hdr["FILTER"]
    z = hdr["AIRMASS"]
    return object, nbin, date, ut, ra, dec, exptime, filter, z


def substring(string, i, j):
    return string[i:j]


def make2dlist(string):
    objlist = string.split("\n")
    object2d = []
    for index in range(len(objlist) - 1):
        object2d.append([])
        object2d[index].append(substring(str(objlist[index]), 0, 24))
        object2d[index].append(substring(str(objlist[index]), 24, 36))
        object2d[index].append(substring(str(objlist[index]), 36, 47))
        object2d[index].append(substring(str(objlist[index]), 47, 53))
        object2d[index].append(substring(str(objlist[index]), 53, 58))
        object2d[index].append(substring(str(objlist[index]), 59, 65))
        object2d[index].append(substring(str(objlist[index]), 69, 73))
        object2d[index].append(substring(str(objlist[index]), 76, 81))
        object2d[index].append(substring(str(objlist[index]), 82, 86))
        object2d[index].append(
            substring(str(objlist[index]), 87, len(objlist[index]) - 1)
        )
    del object2d[0:4]
    return object2d


def fix_signs(ra_off, dec_off, ra_dot, dec_dot):
    # Crack crazy suffixs N/S and +/- on MPC offsets, rates
    ra_off = ra_off.strip()
    dec_off = dec_off.strip()
    ra_dot = ra_dot.strip()
    dec_dot = dec_dot.strip()
    if ra_off.endswith("E"):
        ra_off = -1 * float(ra_off[:-1])
    else:
        ra_off = float(ra_off[:-1])
    if dec_off.endswith("S"):
        dec_off = -1 * float(dec_off[:-1])
    else:
        dec_off = float(dec_off[:-1])
    if ra_dot.endswith("-"):
        ra_dot = -1 * float(ra_dot[:-1])
    else:
        ra_dot = float(ra_dot[:-1])
    if dec_dot.endswith("-"):
        dec_dot = -1 * float(dec_dot[:-1])
    else:
        dec_dot = float(dec_dot[:-1])
    return ra_off, dec_off, ra_dot, dec_dot


def find_mpc_objects(ftsfile, radius, limmag):
    """Query the MPC database for small bodies within a specified radius [arcmin] and limiting magnitude of the center of a FITS image"""
    Objects = []
    Obj_Coords = []
    Magnitudes = []
    Offsets = []
    Rates = []
    Comments = []
    object, nbin, date, ut, ra, dec, exptime, filter, z = get_hdr_info(ftsfile)
    year, month, day = [int(s) for s in date.split("-")]
    uth, utm, uts = [float(s) for s in ut.split(":")]
    day += (uth + utm / 60.0 + uts / 3600.0) / 24.0
    day = "%.2f" % day
    coord = "%s %s" % (ra, dec)
    Ctr_Coords = SkyCoord(coord, unit=(u.hourangle, u.deg))
    ra = ra.replace(":", " ")
    dec = dec.replace(":", " ")
    payload = {
        "year": year,
        "month": month,
        "day": day,
        "which": "pos",
        "ra": ra,
        "decl": dec,
        "TextArea": " ",
        "radius": radius,
        "limit": limmag,
        "oc": "857",
        "sort": "d",
        "mot": "h",
        "tmot": "s",
        "pdes": "u",
        "needed": "f",
        "ps": "n",
        "type": "p",
    }
    r = requests.get(
        "http://www.minorplanetcenter.net/cgi-bin/mpcheck.cgi", params=payload
    )
    myString = r.text
    # check to see if any objects found
    if "No known minor planets" in r.text:
        return Objects, Ctr_Coords, Obj_Coords, Magnitudes, Offsets, Rates, Comments
    else:
        mySubString = r.text[r.text.find("<pre>") + 5 : r.text.find("</pre>")]
        mySubString = mySubString.replace("&#176;", "d")
        mySubString = mySubString.replace(
            '<a href="http://www.cfa.harvard.edu/iau/info/FurtherObs.html">Further observations?</a>',
            "",
        )
        # make a 2d list of objects for manipulation by other programs
        objectlist = make2dlist(mySubString)
        for line in objectlist:
            objname, ra, dec, mag, ra_off, dec_off, ra_dot, dec_dot, dum, comment = line
            ra_off, dec_off, ra_dot, dec_dot = fix_signs(
                ra_off, dec_off, ra_dot, dec_dot
            )
            mag = float(mag)
            Objects.append(objname)
            coord = "%s %s" % (ra, dec)
            c = SkyCoord(coord, unit=(u.hourangle, u.deg))
            Obj_Coords.append(c)
            Magnitudes.append(mag)
            Offsets.append([ra_off, dec_off])
            Rates.append([ra_dot, dec_dot])
            Comments.append(comment)
    return Objects, Ctr_Coords, Obj_Coords, Magnitudes, Offsets, Rates, Comments


def find_mpc_objects_cl(date, ut, ra, dec, radius, limmag):
    """Query the MPC database for small bodies within a specified radius [arcmin] and limiting magnitude using user-supplied ra,dec,date"""
    Objects = []
    Obj_Coords = []
    Magnitudes = []
    Offsets = []
    Rates = []
    Comments = []
    year, month, day = date.split("/")
    ut_hr, ut_min = [float(x) for x in ut.split(":")]
    frac_day = (ut_hr + ut_min / 60.0) / 24.0
    day = "%.2f" % (float(day) + frac_day)
    coord = "%s %s" % (ra, dec)
    Ctr_Coords = SkyCoord(coord, unit=(u.hourangle, u.deg))
    ra = ra.replace(":", " ")
    dec = dec.replace(":", " ")
    payload = {
        "year": year,
        "month": month,
        "day": day,
        "which": "pos",
        "ra": ra,
        "decl": dec,
        "TextArea": " ",
        "radius": radius,
        "limit": limmag,
        "oc": "857",
        "sort": "d",
        "mot": "h",
        "tmot": "s",
        "pdes": "u",
        "needed": "f",
        "ps": "n",
        "type": "p",
    }
    r = requests.get(
        "http://www.minorplanetcenter.net/cgi-bin/mpcheck.cgi", params=payload
    )
    myString = r.text
    # check to see if any objects found
    if "No known minor planets" in r.text:
        return Objects, Ctr_Coords, Obj_Coords, Magnitudes, Offsets, Rates, Comments
    else:
        mySubString = r.text[r.text.find("<pre>") + 5 : r.text.find("</pre>")]
        mySubString = mySubString.replace("&#176;", "d")
        mySubString = mySubString.replace(
            '<a href="http://www.cfa.harvard.edu/iau/info/FurtherObs.html">Further observations?</a>',
            "",
        )
        # make a 2d list of objects for manipulation by other programs
        objectlist = make2dlist(mySubString)
        for line in objectlist:
            objname, ra, dec, mag, ra_off, dec_off, ra_dot, dec_dot, dum, comment = line
            ra_off, dec_off, ra_dot, dec_dot = fix_signs(
                ra_off, dec_off, ra_dot, dec_dot
            )
            mag = float(mag)
            Objects.append(objname)
            coord = "%s %s" % (ra, dec)
            c = SkyCoord(coord, unit=(u.hourangle, u.deg))
            Obj_Coords.append(c)
            Magnitudes.append(mag)
            Offsets.append([ra_off, dec_off])
            Rates.append([ra_dot, dec_dot])
            Comments.append(comment)
    return Objects, Ctr_Coords, Obj_Coords, Magnitudes, Offsets, Rates, Comments


# ====== MAIN ==========

# Get params from command line
(opts, args) = get_args()
radius = opts.radius
limmag = opts.limmag


# Query MPC, parse output
if len(args) == 1:
    ftsfile = args[0]
    if os.path.isfile(ftsfile):
        (
            Objects,
            Ctr_Coords,
            Obj_Coords,
            Magnitudes,
            Offsets,
            Rates,
            Comments,
        ) = find_mpc_objects(ftsfile, radius, limmag)
        ctr_coords = Ctr_Coords.to_string(
            style="hmsdms", precision=1, sep=":", decimal=False
        )
        object, nbin, date, ut, ra, dec, exptime, filter, z = get_hdr_info(ftsfile)
    else:
        sys.exit("File %s does not exist in current path, exiting" % ftsfile)
else:
    if not opts.RA or not opts.DEC or not opts.date:
        sys.exit("Must specifiy at least -R, -D, -d if no image specified.")
    ra = opts.RA
    dec = opts.DEC
    ut = opts.ut
    date = opts.date
    (
        Objects,
        Ctr_Coords,
        Obj_Coords,
        Magnitudes,
        Offsets,
        Rates,
        Comments,
    ) = find_mpc_objects_cl(date, ut, ra, dec, radius, limmag)
    ctr_coords = Ctr_Coords.to_string(
        style="hmsdms", precision=1, sep=":", decimal=False
    )
# Print results
N = len(Objects)
if N == 0:
    print(
        "No known minor bodies with V < %s  within %s' radius of %s on %s at %s UT"
        % (limmag, radius, ctr_coords, date, ut)
    )
else:
    print()
    print(
        "Found %i  minor bodies with V < %s  within %s' radius of %s on %s at %s UT"
        % (N, limmag, radius, ctr_coords, date, ut)
    )
    print()
    print(
        " Number   Name               V       RA(J2000)    Dec(J2000)      Offsets            Motion        Comment"
    )
    print(
        "----------------------------------------------------------------------------------------------------------------------"
    )
    for j in range(N):
        coords_hmsdms = Obj_Coords[j].to_string(
            style="hmsdms", precision=1, sep=":", decimal=False
        )
        ra_deg = Obj_Coords[j].ra.degree
        dec_deg = Obj_Coords[j].dec.degree
        coords = Obj_Coords[j].to_string(
            style="hmsdms", precision=2, sep=":", decimal=False
        )
        ra_off, dec_off = Offsets[j]
        ra_rate, dec_rate = Rates[j]
        print(
            "%s   %.2f    %s   [%5.1f',%5.1f']   [%3i\"/hr, %3i\"/hr]   %s"
            % (
                Objects[j],
                Magnitudes[j],
                coords,
                ra_off,
                dec_off,
                ra_rate,
                dec_rate,
                Comments[j],
            )
        )
