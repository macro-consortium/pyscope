import logging
import os
import shutil
from pathlib import Path

# i will be working on this
import click
from astropy.io import fits

from ..analysis import calc_zmag
from ..observatory import AstrometryNetWCS
from .ccd_calib import ccd_calib

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.option(
    "-t",
    "--camera-type",
    type=click.Choice(["ccd", "cmos"]),
    default="ccd",
    show_choices=True,
    show_default=True,
    help="Camera type.",
)
@click.option(
    "-i",
    "--image-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=None,
    show_default=True,
    help="""Directory containing images to be calibrated. If passed, then
                    the fnames argument is ignored.""",
)
@click.option(
    "-c",
    "--calib-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default="./calibrations/masters",
    show_default=True,
    help="Location of all calibration files.",
)
@click.option(
    "-r",
    "--raw-archive-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=None,
    show_default=True,
    help="""Directory to archive raw images. If none given, no archiving is done,
                however, the '--in-place' option is not allowed.""",
)
@click.option(
    "--in-place",
    is_flag=True,
    default=False,
    show_default=True,
    help="""If given, the raw images are overwritten with the calibrated images.
                If not given, the calibrated images are written to the same directory as the
                raw images, but with the suffix '_cal' added to the filename prior to the extension.""",
)
@click.option(
    "-s",
    "--astro-scrappy",
    nargs=2,
    default=(1, 3),
    show_default=True,
    help="Number of hot pixel removal iterations and estimated camera read noise.",
)
@click.option(
    "-b",
    "--bad-columns",
    default="",
    show_default=True,
    help="Comma-separated list of bad columns to fix.",
)
@click.option(
    "-w",
    "--wcs",
    is_flag=True,
    default=False,
    show_default=True,
    help="""If given, the WCS is solved for each image. If not given, the WCS is
                not solved.""",
)
@click.option(
    "-z",
    "--zmag",
    is_flag=True,
    default=False,
    show_default=True,
    help="""If given, the zero-point magnitude is calculated for each image with
                SDSS filters. If not given, the zero-point magnitude is not calculated.""",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    help="Print verbose output. 1=verbose. 2=more verbose.",
)
@click.argument(
    "fnames", nargs=-1, type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.version_option()
def calib_images_cli(
    camera_type="ccd",
    image_dir=None,
    calib_dir="./calibrations/masters",
    raw_archive_dir=None,
    in_place=False,
    astro_scrappy=(1, 3),
    bad_columns="",
    wcs=False,
    zmag=False,
    verbose=0,
    fnames=(),
):
    """Calibrate a set of images by recursively selecting the
    appropriate flat, dark, and bias frame and then calling
    ccd_calib to do the actual calibration.\f

    Parameters
    ----------
    camera_type : str, optional
        Camera type. By default "ccd".
    image_dir : _type_, optional
        Directory containing images to be calibrated. If passed, then the fnames argument is ignored. By default None.
    calib_dir : str, optional
        Location of all calibration files. By default "./calibrations/masters"
    raw_archive_dir : _type_, optional
        Directory to archive raw images. If none given, no archiving is done, however, the '--in-place' option is not allowed. By default None.
    in_place : bool, optional
        If given, the raw images are overwritten with the calibrated images. If not given, the calibrated images are written to the same directory as the raw images, but with the suffix '_cal' added to the filename prior to the extension. By default False.
    astro_scrappy : tuple, optional
        Number of hot pixel removal iterations and estimated camera read noise. By default (1, 3).
    bad_columns : str, optional
        Comma-separated list of bad columns to fix. By default "".
    wcs : bool, optional
        If given, the WCS is solved for each image. If not given, the WCS is not solved. By default False.
    zmag : bool, optional
        If given, the zero-point magnitude is calculated for each image with SDSS filters. If not given, the zero-point magnitude is not calculated. By default False.
    verbose : int, optional
        Print verbose output. 1=verbose. 2=more verbose. By default 0
    fnames : tuple, optional
        Path of directory of images to calibrate. By default ().

    Returns
    -------
    None
    """
    if verbose == 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    if raw_archive_dir is None and in_place:
        raise click.BadParameter(
            "The --in-place option is not allowed if no raw archive directory is given."
        )

    if image_dir is not None:
        logger.info(
            "--image-dir passed, ignoring fnames argument and using all images in directory."
        )
        fnames = []
        for ext in (".fts", ".fits", ".fit"):
            fnames.extend(Path(image_dir).glob(f"*{ext}"))
        logger.debug(f"fnames = {fnames}")

    logger.info(f"Calibrating {len(fnames)} images.")
    for fname in fnames:
        logger.info(f"Calibrating {fname}")

        hdr = fits.getheader(fname, 0)

        if raw_archive_dir is not None:
            raw_archive_dir_date = Path(raw_archive_dir) / hdr.get("DATE-OBS")[:10]
            if not raw_archive_dir_date.exists():
                raw_archive_dir_date.mkdir(mode=0o775, parents=True)
            logger.info(f"Archiving {fname} to {raw_archive_dir_date}")
            shutil.copy(fname, raw_archive_dir_date)

        if "CALSTAT" in hdr.keys():
            logger.info(f"{fname} has already been calibrated, skipping.")
            continue

        try:
            filt = hdr["FILTER"]
        except KeyError:
            filt = ""

        try:
            readout = hdr["READOUTM"]
        except KeyError:
            readout = hdr["READOUT"]

        try:
            exptime = round(hdr["EXPTIME"], 3)
        except KeyError:
            exptime = round(hdr["EXPOSURE"], 3)

        try:
            gain = hdr["GAIN"]
        except KeyError:
            gain = ""

        try:
            xbin = hdr["XBINNING"]
        except KeyError:
            xbin = hdr["XBIN"]

        try:
            ybin = hdr["YBINNING"]
        except KeyError:
            ybin = hdr["YBIN"]

        flat_frame = None
        dark_frame = None
        bias_frame = None
        flat_dark_frame = None
        calimages = []
        for ext in (".fts", ".fits", ".fit"):
            calimages.extend(Path(calib_dir).rglob(f"*{ext}"))

        for calimg in calimages:
            # find flat_frame, dark_frame, bias_frame, flat_dark_frame
            hdrf = fits.getheader(calimg, 0)
            # if the corresponding header values match, then set the appropriate frame
            if (
                "master_flat" in calimg.name
                and "master_flat_dark" not in calimg.name
                and hdrf["FILTER"] == filt
                and hdrf["READOUTM"] == readout
                and (gain == "" or hdrf["GAIN"] == gain)
                and hdrf["XBINNING"] == xbin
                and hdrf["YBINNING"] == ybin
            ):
                flat_frame = Path(calimg)
            elif (
                "master_dark" in calimg.name
                and hdrf["READOUTM"] == readout
                and (gain == "" or hdrf["GAIN"] == gain)
                and (camera_type == "ccd" or hdrf["EXPTIME"] == exptime)
                and hdrf["XBINNING"] == xbin
                and hdrf["YBINNING"] == ybin
            ):
                dark_frame = Path(calimg)
            elif (
                "master_bias" in calimg.name
                and hdrf["READOUTM"] == readout
                and (gain == "" or hdrf["GAIN"] == gain)
                and hdrf["XBINNING"] == xbin
                and hdrf["YBINNING"] == ybin
            ):
                bias_frame = Path(calimg)
            elif (
                "master_flat_dark" in calimg.name
                and hdrf["READOUTM"] == readout
                and (gain == "" or hdrf["GAIN"] == gain)
                and hdrf["EXPTIME"] == exptime
                and hdrf["XBINNING"] == xbin
                and hdrf["YBINNING"] == ybin
            ):
                flat_dark_frame = Path(calimg)

        # for each image, print out the calibration frames being used
        logger.debug("Using calibration frames:")
        logger.debug(f"Flat: {flat_frame}")
        logger.debug(f"Dark: {dark_frame}")
        if camera_type == "ccd":
            logger.debug(f"Bias: {bias_frame}")
            if not (flat_frame and dark_frame and bias_frame):
                logger.warning(
                    f"Could not find appropriate calibration images for {fname}, skipping"
                )
                continue
        elif camera_type == "cmos":
            logger.debug(f"Flat dark: {flat_dark_frame}")
            if not (flat_frame and dark_frame and flat_dark_frame):
                logger.warning(
                    f"Could not find appropriate calibration images for {fname}, skipping"
                )
                continue

        # After gethering all the required parameters, run ccd_calib
        logger.debug("Running ccd_calib...")
        ccd_calib(
            (fname,),
            dark_frame=dark_frame,
            bias_frame=bias_frame,
            flat_frame=flat_frame,
            camera_type=camera_type,
            astro_scrappy=astro_scrappy,
            bad_columns=bad_columns,
            in_place=in_place,
            verbose=verbose,
        )

        # world coordinate system
        if wcs:
            logger.debug("Running Astrometry.net WCS solver...")
            solver = AstrometryNetWCS()
            solver.solve(fname)

        logger.debug("Done!")

        if zmag:
            logger.info("Calculating zero-point magnitudes...")
            try:
                calc_zmag(images=(fname,))
            except:
                logger.warning(f"calc-zmag failed with exception on {fname}")

    logger.info("Done!")


calib_images = calib_images_cli.callback
