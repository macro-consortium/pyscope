import glob
import logging

import click
import prettytable
from astropy import coordinates as coord
from astropy import time
from astropy.io import fits

logger = logging.getLogger(__name__)


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
@click.argument("fnames", nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.version_option(version="0.1.0")
@click.help_option("-h", "--help")
def fitslist_cli(
    check_date,
    check_filt,
    check_readout,
    check_binning,
    check_exptime,
    check_target,
    verbose,
    fnames,
):
    """List FITS files and their properties."""

    # Set up logging
    logger.setLevel(int(10 * (1 - verbose)))
    logger.debug(
        f"""filt={check_filt}, readout={check_readout}, binning={check_binning}, exptime={check_exptime},
                target={check_target}, verbose={verbose}, fnames={fnames}"""
    )

    # Get list of files
    ftsfiles = []
    if len(fnames) == 0:
        logger.debug("No arguments passed. Using glob to find files.")
        for ext in (".fts", ".fits", ".fit"):
            ftsfiles.extend(glob.glob(f"./*{ext}"))
    else:
        ftsfiles = fnames
    logger.debug(f"fnames={fnames}")
    logger.debug(f"Found {len(fnames)} files.")

    print_rows = []
    for ftsfile in ftsfiles:
        try:
            with fits.open(ftsfile) as hdu:
                header = hdu[0].header
                data = hdu[0].data
        except:
            logger.warning(f"Could not open {ftsfile}.")
            continue

        # Get properties
        date = time.Time(header["DATE-OBS"], format="fits", scale="utc")
        if date.strftime("%Y-%m-%d") not in check_date.split(",") or check_date == "":
            logger.debug(
                f"Date {date.strftime('%Y-%m-%d')} not in {check_date}. Skipping {ftsfile}."
            )
            continue

        # Filter
        try:
            filt = header["FILTER"]
        except KeyError:
            try:
                filt = header["FILT"]
            except KeyError:
                filt = ""
        if filt not in check_filt.split(",") or check_filt == "":
            logger.debug(f"Filter {filt} not in {check_filt}. Skipping {ftsfile}.")
            continue

        # Readout mode
        try:
            readout_mode = header["READOUTM"]
        except KeyError:
            try:
                readout_mode = header["READOUT"]
            except KeyError:
                readout_mode = ""
        if readout_mode not in check_readout.split(",") or check_readout == "":
            logger.debug(
                f"Readout mode {readout_mode} not in {check_readout}. Skipping {ftsfile}."
            )
            continue

        # Binning
        try:
            x_binning = header["XBINNING"]
            y_binning = header["YBINNING"]
        except KeyError:
            x_binning = ""
            y_binning = ""
        if (
            x_binning + "x" + y_binning not in check_binning.split(",")
            or check_binning == ""
        ):
            logger.debug(
                f"Binning {x_binning}x{y_binning} not in {check_binning}. Skipping {ftsfile}."
            )
            continue

        # Exposure time
        try:
            exptime = header["EXPTIME"]
        except KeyError:
            try:
                exptime = header["EXPOSURE"]
            except KeyError:
                exptime = -1
        if check_exptime != "":
            for c_exp in check_exptime.split(","):
                if exptime < float(c_exp) * 0.99 or exptime > float(c_exp) * 1.01:
                    logger.debug(
                        f"Exposure time {exptime} not in {check_exptime}. Skipping {ftsfile}."
                    )
                    continue

        # Target
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
        if target_name not in check_target.split(",") or check_target == "":
            logger.debug(
                f"Target {target_name} not in {check_target}. Skipping {ftsfile}."
            )
            continue

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
                    logger.warning("No coordinates found. Using telescope coordinates.")
                    ra = header["TELRA"]
                    dec = header["TELDEC"]
                except KeyError:
                    ra = ""
                    dec = ""
        if "" not in (ra, dec):
            obj = coord.SkyCoord(ra, dec)

        # Scheduled coordinates
        try:
            sched_ra = header["SCHEDRA"]
            sched_dec = header["SCHEDDEC"]
        except KeyError:
            sched_ra = ""
            sched_dec = ""
        if "" not in (sched_ra, sched_dec):
            sched_obj = coord.SkyCoord(sched_ra, sched_dec)

        if "" not in (ra, dec, sched_ra, sched_dec):
            dra = (obj.ra - sched_obj.ra).to("arcsec")
            ddec = (obj.dec - sched_obj.dec).to("arcsec")
        else:
            dra = ""
            ddec = ""

        # ZP
        try:
            zp = header["ZMAG"]
            zp_err = header["ZMAGERR"]
        except KeyError:
            zp = ""
            zp_err = ""

        # FWHM
        try:
            fwhmh = header["FWHMH"]
            fwhmhs = header["FWHMHS"]
            fwhmv = header["FWHMV"]
            fwhmvs = header["FWHMVS"]
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

        print_rows.append(
            [
                fitsfile,
                target_name,
                date.jd,
                date.iso,
                filt,
                readout_mode,
                x_binning + "x" + y_binning,
                f"{exptime:.3f}",
                obj.ra.hms,
                obj.dec.dms,
                f"{zp:.3f}+/-{zp_err:.3f}",
                f"{fwhmh:.2f}+/-{fwhmhs:.2f}",
                f"{fwhmv:.2f}+/-{fwhmvs:.2f}",
                f"{moon_angle:.1f}",
                f"{moon_phs:.1f}",
                f"{dra:.2f}",
                f"{ddec:.2f}",
            ]
        )

    logger.debug(f"Found {len(print_rows)} files matching criteria.")

    logger.debug("Sorting by JD...")
    print_rows.sort(key=lambda x: x[2])

    table = prettytable.PrettyTable()
    table.add_rows(print_rows)
    table.set_style(prettytable.SINGLE_BORDER)
    table.field_names = [
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
        "dRA [arcsec]",
        "dDec [arcsec]",
    ]

    T.align["FITS file"] = "l"
    click.echo(table)
    click.echo()
    click.echo(f"Number of images = {len(print_rows)}")

    fwhmh = np.median([row[11] for row in print_rows])
    fwhmhs = np.std([row[11] for row in print_rows])
    fwhmv = np.median([row[12] for row in print_rows])
    fwhmvs = np.std([row[12] for row in print_rows])
    click.echo(f"Median FWHM H = {fwhmh:.2f} +/- {fwhmhs:.2f} pix")
    click.echo(f"Median FWHM V = {fwhmv:.2f} +/- {fwhmvs:.2f} pix")

    moon_phs = np.mean([row[14] for row in print_rows])
    click.echo(f"Mean Moon phase = {moon_phs:.2f}")

    click.echo("\nMedian zero-point magnitudes")
    table = prettytable.PrettyTable()
    table.set_style(prettytable.SINGLE_BORDER)
    table.field_names = ["Readout", "Filter", "ZP"]
    for filt in ["u", "b", "g", "r", "i", "z"]:
        rows = [row for row in print_rows if row[4] == filt]
        if len(rows) == 0:
            continue
        for readout in np.unique([row[5] for row in rows]):
            zp = np.median([row[10] for row in rows if row[5] == readout])
            zp_err = np.std([row[10] for row in rows if row[5] == readout])
            table.add_row([readout, filt, f"{zp:.3f}+/-{zp_err:.3f}"])
    click.echo(table)

    return print_rows


fitslist = fitslist_cli.callback
