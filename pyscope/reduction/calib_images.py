import logging
import os
import shutil
from pathlib import Path

import click
from astropy.io import fits

from pyscope.analysis import calc_zmag

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
    zmag=False,
    verbose=0,
    fnames=(),
):
    """
    Calibrate a set of images using `ccd_calib`, optionally overwriting the originals.

    This function processes raw astronomical images in bulk by automatically selecting
    matching calibration frames (`bias`, `dark`, and `flat`) and delegating the calibration
    task to the `ccd_calib` function. By default, calibrated images are saved alongside the
    raw images with a `_cal` suffix. If the `--in-place` option is used, the raw images
    are overwritten, but this requires a backup directory (`--raw-archive-dir`) to avoid
    data loss.


    .. note::

        Ensure all required calibration frames (`bias`, `dark`, `flat`, `flat-dark`) are present in the specified
        `--calib-dir`. If any calibration frames are missing, the process will fail, and the function will
        return `0` without making changes to the images.

    Parameters
    ----------
    camera_type : `str`
        Camera type (`ccd` or `cmos`).
    image_dir : `str`, optional
        Directory containing images to be calibrated. If passed, then
        the `fnames` argument is ignored.
    calib_dir : `str`, optional
        Location of all calibration files.
    raw_archive_dir : `str`, optional
        Directory to archive raw images. If none given, no archiving is done,
        however, the `--in-place` option is not allowed.
    in_place : `bool`, optional
        If given, the raw images are overwritten with the calibrated images.
        If not given, the calibrated images are written to the same directory as the
        raw images, but with the suffix `_cal` added to the filename prior to the extension.
    astro_scrappy : `tuple` of (`int`, `int`), optional
        Number of hot pixel removal iterations and estimated camera read noise.
    bad_columns : `str`, optional
        Comma-separated list of bad columns to fix.
    zmag : `bool`, optional
        If given, the zero-point magnitude is calculated for each image with
        SDSS filters. If not given, the zero-point magnitude is not calculated.
    verbose : `int`, optional
        Print verbose output. `1` = verbose, `2` = more verbose.
    fnames : `list` of `str`
        List of image filenames to be calibrated.

    Returns
    -------
    `int`
    Returns `0` if the calibration process fails due to missing calibration frames.
    `None`
        Returns `None` on successful completion of all calibrations.

    Raises
    ------
    `click.BadParameter`
        If the `--in-place` option is used without specifying a `--raw-archive-dir`.

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
            if not raw_archive_dir.exists():
                raw_archive_dir.mkdir(mode=0o775, parents=True)
            logger.info(f"Archiving {fname} to {raw_archive_dir}")
            shutil.copy(fname, raw_archive_dir)

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
                #                and (
                #                    flat_frame
                #                    and fits.getval(flat_frame, "DATE-OBS") < hdrf["DATE-OBS"]
                #                )
            ):
                flat_frame = Path(calimg)
            elif (
                "master_dark" in calimg.name
                and hdrf["READOUTM"] == readout
                and (gain == "" or hdrf["GAIN"] == gain)
                and (camera_type == "ccd" or hdrf["EXPTIME"] == exptime)
                and hdrf["XBINNING"] == xbin
                and hdrf["YBINNING"] == ybin
                #                and (
                #                    dark_frame
                #                    and fits.getval(dark_frame, "DATE-OBS") < hdrf["DATE-OBS"]
                #                )
            ):
                dark_frame = Path(calimg)
            elif (
                "master_bias" in calimg.name
                and hdrf["READOUTM"] == readout
                and (gain == "" or hdrf["GAIN"] == gain)
                and hdrf["XBINNING"] == xbin
                and hdrf["YBINNING"] == ybin
                #                and (
                #                    bias_frame
                #                    and fits.getval(bias_frame, "DATE-OBS") < hdrf["DATE-OBS"]
                #                )
            ):
                bias_frame = Path(calimg)
            elif (
                "master_flat_dark" in calimg.name
                and hdrf["READOUTM"] == readout
                and (gain == "" or hdrf["GAIN"] == gain)
                and hdrf["EXPTIME"] == exptime
                and hdrf["XBINNING"] == xbin
                and hdrf["YBINNING"] == ybin
                #                and (
                #                    flat_dark_frame
                #                    and fits.getval(flat_dark_frame, "DATE-OBS") < hdrf["DATE-OBS"]
                #                )
            ):
                flat_dark_frame = Path(calimg)

        logger.debug("Found calibration frames:")
        if dark_frame:
            logger.debug(f"Dark: {dark_frame}")
        if bias_frame:
            logger.debug(f"Bias: {bias_frame}")
        if flat_frame:
            logger.debug(f"Flat: {flat_frame}")
        if flat_dark_frame:
            logger.debug(f"Flat dark: {flat_dark_frame}")

        print(filt)
        if filt == "HaGrism" or filt == "OGGrism":
            if dark_frame is None or bias_frame is None:
                logger.exception(
                    "calib-images: Grism image detected: No matching calibration frames found."
                )
                return 0
        elif dark_frame is None or bias_frame is None or flat_frame is None:
            logger.exception("calib-images: No matching calibration frames found.")
            return 0

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

        logger.debug("Done!")

        if zmag:
            logger.info("Calculating zero-point magnitudes...")
            try:
                calc_zmag.calc_zmag(images=(fname,))
            except:
                logger.exception(f"calc-zmag failed with exception on {fname}")

    logger.info("Done!")


"""
Notes: Having an example set up of this function would be helpful.
    This would allow for me to know what the environment looks like when
    calling this function.
"""

calib_images = calib_images_cli.callback
