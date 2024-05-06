import glob
import logging
import sys
from pathlib import Path

import click
import numpy as np
import tqdm
from astropy.io import fits

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.argument("fnames", nargs=-1, type=click.Path(exists=True, resolve_path=True))
@click.option(
    "-p",
    "--pre-normalize",
    "pre_normalize",
    is_flag=True,
    default=False,
    help="Normalize each image by its own mean before combining. This mode is most useful for combining sky flats.",
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["0", "1"]),
    default="0",
    show_choices=True,
    show_default=True,
    help="Mode to use for averaging images (0 = median, 1 = mean).",
)
@click.option(
    "-d",
    "--datatype",
    type=click.Choice(
        [
            "int16",
            "int32",
            "int64",
            "uint16",
            "uint32",
            "uint64",
            "float32",
            "float64",
        ]
    ),
    default="uint16",
    show_choices=True,
    show_default=True,
    help="Data type to use for averaged image.",
)
@click.option(
    "-o",
    "--outfile",
    type=click.Path(),
    help="Path to save averaged image.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    help="Print verbose output. Use multiple times for more verbosity.",
)
@click.version_option()
def avg_fits_cli(
    fnames,
    pre_normalize=False,
    mode="0",
    datatype=np.uint16,
    outfile=None,
    verbose=0,
):
    """Averages over a list of images into a single image. Select pre-normalize to normalize each image by its own mean before combining. This mode is most useful for combining sky flats.\b

    Parameters
    ----------
    fnames : path
        path of directory of images to average.

    pre_normalize : bool, default=False
        Normalize each image by its own mean before combining. This mode is most useful for combining sky flats.

    mode : str, default="0"
        Mode to use for averaging images (0 = median, 1 = mean).

    datatype : str, default="uint16"
        Data type to save out the averaged image. If pre_normalize is True, the data type will be float64.

    outfile : path
        Path to save averaged image. If not specified, the averaged image will be saved in the same directory as the input images with the first image's name and _avg.fts appended to it.

    verbose : int, default=0
        Print verbose output.

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

    logger.debug(
        f"Called avg_fits_cli(fname={fnames}, mode={mode}, datatype={datatype}, outfile={outfile}, verbose={verbose})"
    )

    fnames = Path(fnames).resolve()
    fnames = glob.glob(str(fnames), recursive=True)
    logger.debug(f"Found {len(fnames)} images")
    logger.debug(f"images: {fnames}")

    first_hdr = fits.getheader(fnames[0])
    frametyp = first_hdr["FRAMETYP"]
    logger.debug(f"FRAMETYP: {frametype}")
    binx = first_hdr["XBINNING"]
    biny = first_hdr["YBINNING"]
    logger.debug(f"XBINNING: {binx}, YBINNING: {biny}")
    readout = first_hdr["READOUTM"]
    logger.debug(f"READOUTM: {readout}")
    exptime = first_hdr["EXPTIME"]
    logger.debug(f"EXPTIME: {exptime}")
    gain = first_hdr["GAIN"]
    logger.debug(f"GAIN: {gain}")

    # TODO: don't require all images to be in memory at once
    logger.info("Loading images...")
    images = []
    for fname in fnames:
        image = fits.getdata(fname).astype(np.float64)
        hdr = fits.getheader(fname)

        # check for matches in header
        if hdr["FRAMETYP"] != frametyp:
            logger.warning(f"FRAMETYP mismatch: {hdr['FRAMETYP']} != {frametyp}")
        if hdr["BINX"] != binx:
            logger.warning(f"BINX mismatch: {hdr['BINX']} != {binx}")
        if hdr["BINY"] != biny:
            logger.warning(f"BINY mismatch: {hdr['BINY']} != {biny}")
        if hdr["READOUTM"] != readout:
            logger.warning(f"READOUTM mismatch: {hdr['READOUTM']} != {readout}")
        if hdr["EXPTIME"] != exptime and not pre_normalize:
            logger.warning(f"EXPTIME mismatch: {hdr['EXPTIME']} != {exptime}")
        elif hdr["EXPTIME"] != exptime and pre_normalize:
            logger.info(f"EXPTIME mismatch: {hdr['EXPTIME']} != {exptime}")
            logger.info("pre_normalize is True so ignoring EXPTIME mismatch.")
        if hdr["GAIN"] != gain:
            logger.warning(f"GAIN mismatch: {hdr['GAIN']} != {gain}")

        # check for pedestal
        if "PEDESTAL" in hdr.keys():
            logger.info(f"Found pedestal of {hdr['PEDESTAL']}. Subtracting pedestal.")
            image -= hdr["PEDESTAL"]
        images.append(image)
    images = np.array(images)
    logger.info(f"Loaded {images.shape} images")

    if pre_normalize:
        logger.info(
            "pre_normalize is True. Normalizing each image by its own mean before combining."
        )
        logger.info("Normalizing images...")
        images = images / np.mean(images, axis=(1, 2))[:, None, None]
        logger.info("Done!")
        logger.info("pre_normalize is True so setting datatype to float64")
        datatype = np.float64

        logger.info("pre-normalized is True, removing pedestal keyword from header.")
        if "PEDESTAL" in first_hdr:
            logger.info("Removing PEDESTAL keyword rom header.")
            del first_hdr["PEDESTAL"]

    logger.info(f"Averaging images with mode = {mode}...")
    if str(mode) == "0":
        logger.debug("Calculating median...")
        image_avg = np.median(images, axis=0)
    elif str(mode) == "1":
        logger.debug("Calculating mean...")
        image_avg = np.mean(images, axis=0)
    logger.debug(f"Averaged image mean: {np.mean(image_avg)}")
    logger.debug(f"Averaged image median: {np.median(image_avg)}")

    logger.info(f"Converting data type of averaged image to {datatype}...")
    image_avg = image_avg.astype(datatype)
    logger.info(f"Data type of averaged image: {image_avg.dtype}")

    if outfile is None:
        logger.debug("No output file specified. Using default naming convention.")
        outfile = f"{fnames[0]}_avg.fts"

    logger.info(f"Saving averaged image to {outfile}")
    first_hdr.add_comment(f"Averaged {len(images)} images using pyscope")
    first_hdr.add_comment(f"Average mode: {mode}")
    fits.writeto(outfile, image_avg, first_hdr, overwrite=True)

    logger.info("Done!")


avg_fits = avg_fits_cli.callback
