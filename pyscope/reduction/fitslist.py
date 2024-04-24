import glob
import logging
import os
import re

import click
import numpy as np
from astropy import coordinates as coord  # can have as part of astropy table
from astropy import time
from astropy.io import fits
from astropy.table import Table

logger = logging.getLogger(__name__)

### --- Constants ---
micron = 1e-6
deg = np.pi / 180.0
arcmin = deg / 60.0
arcsec = deg / 3600.0
date = time.Time("2003-11-11")
# extra_keys = []
### --- End of Constants ---


### --- Phillip's Functions ---
def get_offsets(hdr):
    """
    Input : FITS header
    Output  RA, Dec pointing errors [Radians]
    """
    deg = np.pi / 180.0
    arcsec = deg / 3600.0
    has_wcs = "CRVAL1" in hdr
    # grism = hdr['FILTER'][0] in ['8','9','6']
    if has_wcs:
        ra0 = float(hdr["CRVAL1"]) * deg
        dec0 = float(hdr["CRVAL2"]) * deg
        if "OBJRA" in hdr:
            RA = hdr["OBJRA"]
            DEC = hdr["OBJDEC"]
        else:
            RA = hdr["OBJCTRA"]
            DEC = hdr["OBJCTDEC"]
        ra_hr, ra_min, ra_sec = [float(x) for x in re.split(":| ", RA)]
        dec_deg, dec_min, dec_sec = [float(x) for x in re.split(":| ", DEC)]
        ra = (ra_hr + ra_min / 60.0 + ra_sec / 3600.0) * 15 * deg
        sign = -1 if DEC[0] == "-" else 1
        dec = (dec_deg + sign * dec_min / 60.0 + sign * dec_sec / 3600.0) * deg
        dra = (ra - ra0) * np.cos(dec0)
        ddec = dec - dec0
        if abs(dra) > 999 * arcsec:
            dra = 999 * arcsec
        if abs(ddec) > 999 * arcsec:
            ddec = 999 * arcsec
    else:
        dra = np.nan
        ddec = np.nan
    return dra, ddec


def get_fwhm(hdr):
    # Returns airmass, mean FWHM [arcsec] - actual and zenith corrected
    if "AIRMASS" in hdr:
        z = hdr["AIRMASS"]
    else:
        z = 1.0
    pixel = hdr["XPIXSZ"] * micron
    # If filter is '8' or '9' or '6' then it is a grism
    grism = hdr["FILTER"][0] in ["8", "9", "6"]
    if "FWHMH" in hdr and not grism:
        if "CDELT1" in hdr:
            plate_scale = np.abs(hdr["CDELT1"] * deg / pixel)
        else:
            plate_scale = np.nan
        fh = hdr["FWHMH"]
        fv = hdr["FWHMV"]
        fwhm = np.sqrt(fh * fv) * pixel
        fwhm *= plate_scale / arcsec
        fwhm_zenith = fwhm * (z**-0.6)
        fh *= pixel * plate_scale / arcsec
        fv *= pixel * plate_scale / arcsec
    else:
        fwhm = np.nan
        fwhm_zenith = np.nan
        fh = np.nan
        fv = np.nan
    return z, fwhm, fwhm_zenith, fh, fv


def get_zp(hdr):
    if "ZMAG" in hdr:
        zp = hdr["ZMAG"]
        if "ZMAGERR" in hdr:
            zp_err = hdr["ZMAGERR"]
        else:
            zp_err = 0.0
    else:
        zp = np.nan
        zp_err = np.nan
    return zp, zp_err


def zp_stats(filter, mode, zp_stats_list):
    # Make list of [filter, zp, cmos_mode]
    S = zp_stats_list
    Zp = []
    for s in S:
        fil, zp, cmos_mode = s
        if fil == filter and cmos_mode == mode:
            Zp.append(zp)
    zp = np.array(Zp)
    if len(zp) != 0:
        zp_med = np.nanmedian(zp)
        zp_std = np.nanstd(zp)
    else:
        zp_med = np.nan
        zp_std = np.nan
    return zp_med, zp_std


### --- End of Phillip's Functions ---


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.option("-d", "--date", default="", help="Date [default all].")
@click.option("-f", "--filt", default="", help="Filter name [default all].")
@click.option("-r", "--readout", default="", help="Readout mode [default all].")
@click.option("-b", "--binning", default="", help="Binning [default all].")
@click.option(
    "-e",
    "--exptime",
    default="",
    help=f"""Approximate exposure time [default all].
                Note that an error of up to 1% is permitted to allow for imprecisions
                in the camera.""",
)
@click.option("-t", "--target", default="", help="Target name [default all].")
@click.option(
    "-v", "--verbose", count=True, type=click.IntRange(0, 1), help="Verbose output."
)
@click.option("-k", "--add_keys", default="", help="Additional header keys to print.")
@click.option(
    "-n", "--fnames", default="./", type=click.Path(exists=True, file_okay=False)
)  ##need default = "?"
@click.option("-s", "--save", is_flag=True, help="Save output to a file")
@click.option("-o", "--offsets", is_flag=True, help="Save output to a file")
@click.option("-z", "--zp_stats", is_flag=True, help="Save output to a file")
@click.version_option()
def fitslist_cli(
    date,
    filt,
    readout,
    binning,
    exptime,
    target,
    verbose,
    fnames,
    save,
    add_keys,
    offsets,
    zp_stats,
):
    """List FITS files and their properties."""
    # Set up logging
    logger.setLevel(int(10 * (1 - verbose)))
    logger.debug(
        f"""filt={filt}, readout={readout}, binning={binning}, exptime={exptime},
                target={target}, verbose={verbose}, fnames={fnames}"""
    )

    # Get list of files
    ftsfiles = []
    original_names = {}
    if os.path.isdir(fnames):  # Check if fnames is a directory
        files = os.listdir(fnames)
        for file in files:
            if file.endswith((".fits", ".fts", ".fit")):
                filename = fnames + "/" + file
                ftsfiles.append(filename)
                original_names[filename] = file
    else:
        ftsfiles.append(fnames)

    if len(ftsfiles) == 0:
        click.echo("No FITS files found in the specified directory.")
        return  # Return if no FITS files are found

    logger.debug(f"fnames={fnames}")
    logger.debug(f"Found {len(fnames)} files.")

    if len(add_keys) == 0:
        extra_keys = []
    else:
        extra_keys = add_keys.split(",")
    logger.debug(f"Extra keys: {extra_keys}")
    extra_keys = [x.upper() for x in extra_keys]

    print_rows = []
    for ftsfile in ftsfiles:
        try:
            header = fits.getheader(ftsfile)
        except:
            logger.warning(f"Could not open {ftsfile}.")
            continue

        # Get properties
        date = time.Time(header["DATE-OBS"], format="fits", scale="utc")

        # Filter
        try:
            filt = header["FILTER"]
        except KeyError:
            try:
                filt = header["FILT"]
            except KeyError:
                filt = ""
        if filt not in filt.split(",") or filt == "":
            logger.debug(f"Filter {filt} not in {filt}. Skipping {ftsfile}.")
            continue

        # Readout mode
        try:
            readout = header["READOUTM"]
        except KeyError:
            try:
                readout = header["READOUT"]
            except KeyError:
                readout = ""

        # Binning
        x_binning = ""
        y_binning = ""
        try:
            x_binning = header["XBINNING"]
            y_binning = header["YBINNING"]
        except KeyError:
            x_binning = ""
            y_binning = ""

        # Exposure time
        exptime = ""
        try:
            exptime = header["EXPTIME"]
        except KeyError:
            try:
                exptime = header["EXPOSURE"]
            except KeyError:
                exptime = -1

        # Target
        target_name = ""
        try:
            target_name = header["OBJECT"]
        except KeyError:
            try:
                target_name = header["OBJNAME"]
            except KeyError:
                try:
                    target_name = header["SOURCE"]
                except KeyError:
                    try:
                        target_name = header["TARGNAME"]
                    except KeyError:
                        target_name = ""
        if target_name not in target.split(",") or target == "":
            logger.debug(f"Target {target_name} not in {target}. Skipping {ftsfile}.")
            target_name = "n/a"

        # Actual coordinates
        try:
            ra = header["OBJCTRA"]
            dec = header["OBJCTDEC"]
        except KeyError:
            try:
                ra = header["OBJRA"]
                dec = header["OBJDEC"]
            except KeyError:
                try:
                    ra = header["RA"]
                    dec = header["DEC"]
                except KeyError:
                    try:
                        logger.warning(
                            "No coordinates found. Using telescope coordinates."
                        )
                        ra = header["TELRA"]
                        dec = header["TELDEC"]
                    except KeyError:
                        ra = ""
                        dec = ""

        # Get institute
        try:
            institute = header["IN"]
        except KeyError:
            try:
                institute = header["ORIGIN"]
            except KeyError:
                try:
                    institute = header["OBSERVER"]
                except KeyError:
                    institute = ""

        # ZP
        try:
            zp, zp_err = get_zp(header)
        except KeyError:
            zp = ""
            zp_err = ""
        #     zp = header["ZMAG"]
        #     zp_err = header["ZMAGERR"]
        # except KeyError:
        #     zp = ""
        #     zp_err = ""
        # # OFFSETS
        # dx, dy = get_offsets(header)

        # FWHM

        try:
            fwhmh = header["FWHMH"]
            fwhmhs = header["FWHMHS"]
            fwhmv = header["FWHMV"]
            fwhmvs = header["FWHMVS"]
        except KeyError:
            try:
                z, fwhm, fwhm_zenith, fwhmh, fwhmv = get_fwhm(header)
            except KeyError:
                fwhmh = ""
                fwhmhs = ""
                fwhmv = ""
                fwhmvs = ""

        # Moon
        try:
            moon_angle = header["MOONANGL"]
            moon_phs = header["MOONPHAS"]
        except KeyError:
            moon_angle = ""
            moon_phs = ""

        # Offsets
        offset_keys = []
        offset_values = []
        if offsets:
            dra, ddec = get_offsets(header)
            offset_keys.append("DRA")
            offset_keys.append("DDEC")
            offset_values = [dra, ddec]
        else:
            offset_values = []

        # Extra keys
        extra_values = []
        for key in extra_keys:
            try:
                extra_values.append(header[key])
            except KeyError:
                extra_values.append("")
        extra_values = [str(x) for x in extra_values]

        print_rows.append(
            [
                original_names[ftsfile],
                target_name,
                date.jd,
                date.iso,
                filt,
                readout,
                str(x_binning) + "x " + str(y_binning) + "y",
                f"{exptime:.3f}",
                ra,
                dec,
                zp,
                fwhmh,
                fwhmv,
                moon_angle,
                moon_phs,
                institute,
                *extra_values,
                *offset_values,
            ]
        )

    ##switch to astropy table which can be saved to a file
    standard_names = [
        "FITS file",
        "Target",
        "JD",
        "UT",
        "Filter",
        "Readout",
        "Binning",
        "Exp. time [s]",
        "RA",
        "Dec",
        "ZP",
        "FWHM H [pix]",
        "FWHM V [pix]",
        "Moon angle [deg]",
        "Moon phase [0-1]",
        "Institute",
        *extra_keys,
        *offset_keys,
    ]
    table = Table(rows=print_rows, names=standard_names)
    table.pprint(max_lines=-1, max_width=-1)

    if save:
        table.write("fitslist.csv", format="ascii", overwrite=True)
        logger.info("Table saved to fitslist.csv")

    return table


fitslist = fitslist_cli.callback
