import glob
import logging
import os
import time
from pathlib import Path

import astroscrappy
import click
import numpy as np
from astropy.io import fits

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
    "-d",
    "--dark-frame",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to master dark frame. If camera type is CMOS, then the exposure time of the dark frame should match the exposure time of the target images.",
)
@click.option(
    "-b",
    "--bias-frame",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to master bias frame. Ignored if camera type is CMOS.",
)
@click.option(
    "-f",
    "--flat-frame",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to master flat frame. The script assumes the master flat frame has already been calibrated. The flat frame is normalized by the mean of the entire image before being applied to the target images.",
)
@click.option(
    "-s",
    "--astro-scrappy",
    nargs=2,
    default=(1, 3),
    show_default=True,
    help="Number of hot pixel removal iterations and estimated camera read noise in root-electrons per pixel per second.",
)
@click.option(
    "-c",
    "--bad-columns",
    default="",
    show_default=True,
    help="Comma-separated list of bad columns to fix by averaging the value of each pixel in the adjacent column.",
)
@click.option(
    "-i",
    "--in-place",
    is_flag=True,
    default=False,
    show_default=True,
    help="Overwrite input files.",
)
@click.option(
    "-p",
    "--pedestal",
    default=1000,
    show_default=True,
    help="Pedestal value to add to calibrated image.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    help="Print verbose output. 1=verbose. 2=more verbose.",
)
@click.argument("fnames", nargs=-1, type=click.Path(exists=True, resolve_path=True))
@click.version_option()
def ccd_calib_cli(
    fnames,
    dark_frame=None,
    bias_frame=None,
    flat_frame=None,
    camera_type="ccd",
    astro_scrappy=(1, 3),
    bad_columns="",
    in_place=False,
    verbose=0,
    pedestal=1000,
):
    """
    Calibrate astronomical images using master calibration frames.

    The `ccd_calib_cli` function applies bias, dark, and flat corrections to raw CCD or CMOS images
    to produce calibrated versions. Calibrated images are saved with the suffix `_cal` appended
    to the original filename unless the `--in-place` option is used, which overwrites the raw files.
    The calibration process supports additional features like hot pixel removal and bad column correction.

    Parameters
    ----------
    fnames : `list` of `str`
        List of filenames to calibrate.
    dark_frame : `str`, optional
        Path to master dark frame. If the camera type is `cmos`, the exposure time of the
        dark frame must match the exposure time of the target images.
    bias_frame : `str`, optional
        Path to master bias frame. Ignored if the camera type is `cmos`.
    flat_frame : `str`, optional
        Path to master flat frame. The script assumes the master flat frame has already been
        bias and dark corrected. The flat frame is normalized by the mean of the entire image
        before being applied to the target images.
    camera_type : `str`, optional
        Camera type. Must be either `ccd` or `cmos`. Defaults to `"ccd"`.
    astro_scrappy : `tuple` of (`int`, `int`), optional
        Number of hot pixel removal iterations and estimated camera read noise (in
        root-electrons per pixel per second). Defaults to `(1, 3)`.
    bad_columns : `str`, optional
        Comma-separated list of bad columns to fix by averaging the value of each pixel
        in the adjacent column. Defaults to `""`.
    in_place : `bool`, optional
        If `True`, overwrites the input files with the calibrated images. Defaults to `False`.
    pedestal : `int`, optional
        Pedestal value to add to calibrated images after processing to prevent negative
        pixel values. Defaults to `1000`.
    verbose : `int`, optional
        Verbosity level for logging output:
        - `0`: Warnings only (default).
        - `1`: Informational messages.
        - `2`: Debug-level messages.

    Returns
    -------
    `None`
        The function does not return any value. It writes calibrated images to disk.

    Raises
    ------
    `FileNotFoundError`
        Raised if any of the specified input files do not exist.
    `ValueError`
        Raised if the calibration frames (e.g., `dark_frame`, `bias_frame`, `flat_frame`) do not
        match the target images in terms of critical metadata, such as:
        - Exposure time
        - Binning (X and Y)
        - Readout mode
    `KeyError`
        Raised if required header keywords (e.g., `IMAGETYP`, `FILTER`, `EXPTIME`, `GAIN`) are
        missing from the calibration frames or the raw image files.
    """

    if verbose == 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    logger.debug(
        f"""ccd_calib(\n\tcamera_type={camera_type}, \n\tdark_frame={dark_frame}, \n\tflat_frame={flat_frame}, \n\tbias_frame={bias_frame}, \n\tastro_scrappy={astro_scrappy}, \n\tbad_columns={bad_columns}, \n\tin_place={in_place}, \n\tfnames={fnames}, \n\tverbose={verbose}, \n\tpedestal={pedestal}\n)"""
    )

    logger.info("Loading calibration frames...")

    camera_type = camera_type.lower()
    if camera_type == "ccd":
        if bias_frame is not None:
            logger.info(f"Loading bias frame: {bias_frame}")
            bias, bias_hdr = fits.getdata(bias_frame).astype(
                np.float64
            ), fits.getheader(bias_frame)

            try:
                bias_frametyp = bias_hdr["IMAGETYP"]
            except KeyError:
                bias_frametyp = ""
            if "bias" not in bias_frametyp.lower():
                logger.warning(
                    f"Bias frame frametype ({bias_frametyp}) does not match 'bias'"
                )

            try:
                bias_readout_mode = bias_hdr["READOUTM"]
            except KeyError:
                bias_readout_mode = bias_hdr["READOUT"]

            try:
                bias_exptime = round(bias_hdr["EXPTIME"], 3)
            except KeyError:
                bias_exptime = round(bias_hdr["EXPOSURE"], 3)

            try:
                bias_xbin = bias_hdr["XBINNING"]
            except:
                bias_xbin = bias_hdr["XBIN"]

            try:
                bias_ybin = bias_hdr["YBINNING"]
            except:
                bias_ybin = bias_hdr["YBIN"]

            try:
                bias_gain = bias_hdr["GAIN"]
            except:
                bias_gain = ""

            logger.debug(f"Bias frame frametype: {bias_frametyp}")
            logger.debug(f"Bias frame readout mode: {bias_readout_mode}")
            logger.debug(f"Bias gain: {bias_gain}")
            logger.debug(f"Bias frame exposure time: {bias_exptime}")
            logger.debug(f"Bias frame X binning: {bias_xbin}")
            logger.debug(f"Bias frame Y binning: {bias_ybin}")

    if dark_frame is not None:
        logger.info(f"Loading dark frame: {dark_frame}")
        dark, dark_hdr = fits.getdata(dark_frame).astype(np.float64), fits.getheader(
            dark_frame
        )

        try:
            dark_frametyp = dark_hdr["IMAGETYP"]
        except KeyError:
            dark_frametyp = ""
        if "dark" not in dark_frametyp.lower():
            logger.warning(
                f"Dark frame frametype ({dark_frametyp}) does not match 'dark'"
            )

        try:
            dark_readout_mode = dark_hdr["READOUTM"]
        except KeyError:
            dark_readout_mode = dark_hdr["READOUT"]

        try:
            dark_exptime = round(dark_hdr["EXPTIME"], 3)
        except KeyError:
            dark_exptime = round(dark_hdr["EXPOSURE"], 3)

        try:
            dark_xbin = dark_hdr["XBINNING"]
        except:
            dark_xbin = dark_hdr["XBIN"]

        try:
            dark_ybin = dark_hdr["YBINNING"]
        except:
            dark_ybin = dark_hdr["YBIN"]

        try:
            dark_gain = dark_hdr["GAIN"]
        except:
            dark_gain = ""

        logger.debug(f"Dark frame frametype: {dark_frametyp}")
        logger.debug(f"Dark frame readout mode: {dark_readout_mode}")
        logger.debug(f"Dark gain: {dark_gain}")
        logger.debug(f"Dark frame exposure time: {dark_exptime}")
        logger.debug(f"Dark frame X binning: {dark_xbin}")
        logger.debug(f"Dark frame Y binning: {dark_ybin}")

    if flat_frame is not None:
        logger.info(f"Loading flat frame: {flat_frame}")
        flat, flat_hdr = fits.getdata(flat_frame).astype(np.float64), fits.getheader(
            flat_frame
        )

        try:
            flat_frametyp = flat_hdr["IMAGETYP"]
        except KeyError:
            flat_frametyp = ""
        if "flat" not in flat_frametyp.lower() and "light" not in flat_frametyp.lower():
            logger.warning(
                f"Flat frame frametype ({flat_frametyp}) does not match 'flat'"
            )

        try:
            flat_filter = flat_hdr["FILTER"]
        except KeyError:
            flat_filter = ""

        try:
            flat_readout_mode = flat_hdr["READOUTM"]
        except KeyError:
            flat_readout_mode = flat_hdr["READOUT"]

        try:
            flat_exptime = round(flat_hdr["EXPTIME"], 3)
        except KeyError:
            flat_exptime = round(flat_hdr["EXPOSURE"], 3)

        try:
            flat_xbin = flat_hdr["XBINNING"]
        except:
            flat_xbin = flat_hdr["XBIN"]

        try:
            flat_ybin = flat_hdr["YBINNING"]
        except:
            flat_ybin = flat_hdr["YBIN"]

        try:
            flat_gain = flat_hdr["GAIN"]
        except:
            flat_gain = ""

        try:
            flat_pedestal = flat_hdr["PEDESTAL"]
        except:
            flat_pedestal = 0

        logger.debug(f"Flat frame frametype: {flat_frametyp}")
        logger.debug(f"Flat frame readout mode: {flat_readout_mode}")
        logger.debug(f"Flat gain: {flat_gain}")
        logger.debug(f"Flat frame exposure time: {flat_exptime}")
        logger.debug(f"Flat frame X binning: {flat_xbin}")
        logger.debug(f"Flat frame Y binning: {flat_ybin}")
        logger.debug(f"Flat pedestal: {flat_pedestal}")

    logger.debug(f"Calibrating {len(fnames)} image(s): {fnames}")

    for fname in fnames:
        logger.info(f"Calibrating {fname}...")
        image, hdr = fits.getdata(fname).astype(np.float64), fits.getheader(fname)

        if "CALSTAT" in hdr.keys():
            if hdr["CALSTAT"]:
                logger.warning("Image already calibrated. Skipping...")
                continue

        try:
            image_frametyp = hdr["IMAGETYP"]
        except KeyError:
            image_frametyp = ""
        if (
            "light" not in image_frametyp.lower()
            and "flat" not in image.frametyp.lower()
        ):
            logger.warning(
                f"Image frametype ({image_frametyp}) does not match 'light' or 'flat'"
            )

        try:
            image_filter = hdr["FILTER"]
        except KeyError:
            image_filter = ""

        try:
            image_readout_mode = hdr["READOUTM"]
        except KeyError:
            image_readout_mode = hdr["READOUT"]

        try:
            image_exptime = round(hdr["EXPTIME"], 3)
        except KeyError:
            image_exptime = round(hdr["EXPOSURE"], 3)

        try:
            image_xbin = hdr["XBINNING"]
        except:
            image_xbin = hdr["XBIN"]

        try:
            image_ybin = hdr["YBINNING"]
        except:
            image_ybin = hdr["YBIN"]

        try:
            image_gain = hdr["GAIN"]
        except:
            image_gain = ""

        logger.debug(f"Image readout mode: {image_readout_mode}")
        logger.debug(f"Image gain: {image_gain}")
        logger.debug(f"Image exposure time: {image_exptime}")
        logger.debug(f"Image X binning: {image_xbin}")
        logger.debug(f"Image Y binning: {image_ybin}")

        if dark_frame is not None:
            if image_readout_mode != dark_readout_mode:
                logger.warning(
                    f"Image readout mode ({image_readout_mode}) does not match dark readout mode ({dark_readout_mode})"
                )

            if image_xbin != dark_xbin:
                logger.warning(
                    f"Image X binning ({image_xbin}) does not match dark X binning ({dark_xbin})"
                )

            if image_ybin != dark_ybin:
                logger.warning(
                    f"Image Y binning ({image_ybin}) does not match dark Y binning ({dark_ybin})"
                )

            if image_gain != dark_gain:
                logger.warning(
                    f"Image gain ({image_gain}) does not match dark gain ({dark_gain})"
                )

        if flat_frame is not None:
            if image_readout_mode != flat_readout_mode:
                logger.warning(
                    f"Image readout mode ({image_readout_mode}) does not match flat readout mode ({flat_readout_mode})"
                )

            if image_xbin != flat_xbin:
                logger.warning(
                    f"Image X binning ({image_xbin}) does not match flat X binning ({flat_xbin})"
                )

            if image_ybin != flat_ybin:
                logger.warning(
                    f"Image Y binning ({image_ybin}) does not match flat Y binning ({flat_ybin})"
                )

            if image_filter != flat_filter:
                logger.warning(
                    f"Image filter ({image_filter}) does not match flat filter ({flat_filter})"
                )

            if image_gain != flat_gain:
                logger.warning(
                    f"Image gain ({image_gain}) does not match flat gain ({flat_gain})"
                )

        if camera_type == "cmos":
            if image_exptime != dark_exptime:
                logger.warning(
                    f"""Image exposure time ({image_exptime}) does not match dark exposure time ({dark_exptime}),
                    recommended for a CMOS camera"""
                )

        elif camera_type == "ccd":
            if image_readout_mode != bias_readout_mode:
                logger.warning(
                    f"Image readout mode ({image_readout_mode}) does not match bias readout mode ({bias_readout_mode})"
                )

            if image_xbin != bias_xbin:
                logger.warning(
                    f"Image X binning ({image_xbin}) does not match bias X binning ({bias_xbin})"
                )

            if image_ybin != bias_ybin:
                logger.warning(
                    f"Image Y binning ({image_ybin}) does not match bias Y binning ({bias_ybin})"
                )

            if image_gain != bias_gain:
                logger.warning(
                    f"Image gain ({image_gain}) does not match bias gain ({bias_gain})"
                )

        hdr.add_comment(f"Calibrated using pyscope")
        hdr.add_comment(f"Calibration mode: {camera_type}")
        if dark_frame is not None:
            hdr.add_comment(f"Calibration dark frame: {dark_frame}")
        else:
            hdr.add_comment(
                f"Calibration dark frame not provided - dark subtraction NOT performed"
            )
        if flat_frame is not None:
            hdr.add_comment(f"Calibration flat frame: {flat_frame}")
        else:
            hdr.add_comment(
                f"Calibration flat frame not provided - flat correction NOT performed"
            )
        if bias_frame is not None:
            hdr.add_comment(f"Calibration bias frame: {bias_frame}")
        else:
            hdr.add_comment(
                f"Calibration bias frame not provided - bias subtraction NOT performed"
            )
        hdr.add_comment(f"Calibration astro-scrappy: {astro_scrappy}")
        hdr.add_comment(f"Calibration bad columns: {bad_columns}")

        cal_image = image.copy()
        if camera_type == "ccd":
            if bias_frame is not None:
                logger.info("Applying bias frame (CCD selected)...")
                cal_image = np.subtract(cal_image, bias)

            if dark_frame is not None:
                logger.info(
                    """Applying the dark frame. CCD selected so a bias-subtracted
                            dark frame is scaled by the ratio of the image exposure time over
                            the dark exposure time then subtracted from the image."""
                )

                cal_image = np.subtract(
                    cal_image, (dark - bias) * (image_exptime / dark_exptime)
                )

        elif camera_type == "cmos":
            if dark_frame is not None:
                logger.info(
                    """Applying the dark frame. CMOS selected so a dark
                            is subtracted from the image with no bias and no exposure time scaling."""
                )
                cal_image = np.subtract(cal_image, dark)

        if flat_frame is not None:
            logger.info("Checking if flat frame has a pedestal...")
            if "PEDESTAL" in flat_hdr:
                logger.info(f"Pedestal keyword found, value: {flat_hdr['PEDESTAL']}")
                flat_pedestal = flat_hdr["PEDESTAL"]
                logger.info(f"Subtracting pedestal of {flat_pedestal} from flat frame.")
                flat = np.subtract(flat, flat_pedestal)

            logger.info("Normalizing the flat frame by the mean of the entire image.")
            flat_mean = np.mean(flat)
            logger.info(f"flat_mean: {flat_mean}")
            flat = np.divide(flat, flat_mean)

            logger.info("Applying the flat frame...")
            cal_image = np.divide(cal_image, flat)

        logger.info("Flooring the calibrated image...")
        cal_image = np.floor(cal_image)

        logger.info(f"Adding pedestal of {pedestal}")
        hdr["PEDESTAL"] = pedestal
        cal_image += pedestal

        if astro_scrappy[0] > 0:
            logger.info("Removing hot pixels...")
            t0 = time.time()
            mask, cal_image = astroscrappy.detect_cosmics(
                cal_image, niter=astro_scrappy[0], readnoise=astro_scrappy[1]
            )
            t = time.time() - t0
            hdr.add_comment(
                f"Removed hot pixels using astroscrappy, {astro_scrappy[0]} iterations"
            )
            hdr.add_comment("Hot pixel removal took %.1f seconds" % t)
            logger.debug(f"Hot pixel removal took {t} seconds")

        if len(bad_columns) > 0:
            logger.info("Fixing bad columns...")
            for badcol in bad_columns:
                cal_image[:, badcol] = (
                    cal_image[:, badcol - 1] + cal_image[:, badcol + 1]
                ) / 2

        logger.info("Clipping to uint16 range...")
        cal_image = np.clip(cal_image, 0, 65535)
        cal_image = cal_image.astype(np.uint16)

        logger.info("Writing calibrated status to header...")
        hdr["CALSTAT"] = True
        if in_place:
            logger.info(f"Overwriting {fname}")
            fits.writeto(fname, cal_image, hdr, overwrite=True)
        else:
            logger.info(f"Writing calibrated image to {fname}")
            fits.writeto(
                str(fname).split(".")[:-1][0] + "_cal.fts",
                cal_image,
                hdr,
                overwrite=True,
            )

        logger.info("Done!")


ccd_calib = ccd_calib_cli.callback
