import logging
import os

import astropy.units as u
import ccdproc
import click
import numpy as np
from astropy.io import fits
from astropy.nddata import CCDData

logger = logging.getLogger(__name__)

"""
TODO: fix click options
"""


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.option(
    "-m" "--method",
    type=click.Choice(["average", "median", "sum"]),
    default="median",
    show_default=True,
    help="Method to use for averaging images.",
)
@click.option(
    "-o",
    "--outfile",
    type=click.Path(),
    required=True,
    help="Path to save averaged image.",
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
    default=np.uint16,
    show_choices=True,
    show_default=True,
    help="Data type to use for averaged image.",
)
@click.option(
    "-u",
    "--unit",
    type=click.Choice(["adu", "counts", "photon"]),
    default=None,
    show_choices=True,
    show_default=True,
    help="Unit of CCD data.",
)
@click.option(
    "-w",
    "--weights",
    type=np.ndarray,
    default=None,
    show_default=True,
    help="Weights to be used when combining images. An array with the weight values. The dimensions should match the the dimensions of the data arrays being combined.",
)
@click.option(
    "-s",
    "--scale",
    type=click.Choice([callable, np.ndarray]),
    default=None,
    show_default=True,
    help="Scaling factor to be used when combining images. Images are multiplied by scaling prior to combining them. Scaling may be either a function, which will be applied to each image to determine the scaling factor, or a list or array whose length is the number of images in the Combiner.",
)
@click.option(
    "-ml",
    "--mem_limit",
    type=float,
    default=16e9,
    show_default=True,
    help="Maximum memory which should be used while combining (in bytes).",
)
@click.option(
    "-ce",
    "--clip_extrema",
    type=bool,
    default=False,
    show_default=True,
    help="Set to True if you want to mask pixels using an IRAF-like minmax clipping algorithm. The algorithm will mask the lowest nlow values and the highest nhigh values before combining the values to make up a single pixel in the resulting image. For example, the image will be a combination of Nimages-low-nhigh pixel values instead of the combination of Nimages.",
)
@click.option(
    "-nl",
    "--nLow",
    type=int,
    default=1,
    show_default=True,
    help="",
)
@click.option(
    "-nh",
    "--nHigh",
    type=int,
    default=1,
    show_default=True,
    help="",
)
@click.option(
    "-mc",
    "--minmax_clip",
    type=bool,
    default=False,
    show_default=True,
    help="Set to True if you want to mask all pixels that are below minmax_clip_min or above minmax_clip_max before combining.",
)
@click.option(
    "-mcn",
    "--minmax_clip_min",
    type=click.Choice([click.FLOAT, None]),
    default=None,
    show_default=True,
    help="",
)
@click.option(
    "-mcx",
    "--minmax_clip_max",
    type=click.Choice([click.FLOAT, None]),
    default=None,
    show_default=True,
    help="",
)
@click.option(
    "-sc",
    "--sigma_clip",
    type=bool,
    default=False,
    show_default=True,
    help="Set to True if you want to reject pixels which have deviations greater than those set by the threshold values. The algorithm will first calculated a baseline value using the function specified in func and deviation based on sigma_clip_dev_func and the input data array. Any pixel with a deviation from the baseline value greater than that set by sigma_clip_high_thresh or lower than that set by sigma_clip_low_thresh will be rejected.",
)
@click.option(
    "-sclt",
    "--sigma_clip_low_thresh",
    type=click.Choice([click.FLOAT, None]),
    default=3,
    show_default=True,
    help="",
)
@click.option(
    "-scht",
    "--sigma_clip_high_thresh",
    type=click.Choice([click.FLOAT, None]),
    default=3,
    show_default=True,
    help="",
)
@click.option(
    "-scf",
    "--sigma_clip_func",
    type=callable,
    default=None,
    show_default=True,
    help="",
)
@click.option(
    "-scdf",
    "--sigma_clip_dev_func",
    type=callable,
    default=None,
    show_default=True,
    help="",
)
@click.option(
    "-cuf",
    "--combine_uncertainty_func",
    type=callable,
    default=None,
    show_default=True,
    help="If None use the default uncertainty func when using average, median or sum combine, otherwise use the function provided.",
)
@click.option(
    "-oo",
    "--overwrite_output",
    type=bool,
    default=False,
    show_default=True,
    help="If output_file is specified, this is passed to the astropy.nddata.fits_ccddata_writer under the keyword overwrite; has no effect otherwise.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    show_default=True,
    help="Print verbose output.",
)
@click.argument(
    "fnames", nargs=-1, type=click.Path(exists=True, resolve_path=True)
)
@click.version_option()
def avg_fits_ccdproc_cli(
    mode,
    outfile,
    fnames,
    method="median",
    datatype="uint16",
    weights=None,
    scale=None,
    mem_limit=16000000000.0,
    clip_extrema=False,
    nlow=1,
    nhigh=1,
    minmax_clip=False,
    minmax_clip_min=None,
    minmax_clip_max=None,
    sigma_clip=False,
    sigma_clip_low_thresh=3,
    sigma_clip_high_thresh=3,
    sigma_clip_func=None,
    sigma_clip_dev_func=None,
    combine_uncertainty_function=None,
    overwrite_output=False,
    unit="adu",
    verbose=False,
):
    """
    Combine multiple images into a single averaged image using `ccdproc`.

    This function uses the `ccdproc.combine` method to combine a set of FITS images
    into a single output image, supporting various combination methods like "median",
    "average", and "sum". The output file is saved in the specified format, with
    optional data scaling, weighting, and clipping algorithms.

    Parameters
    ----------
    outfile : `str`
        Path to save the combined image.
    fnames : `list` of `str`
        List of FITS file paths to be combined.
    method : `str`, optional
        Method used for combining images. Options are:
        - `"average"`
        - `"median"` (default)
        - `"sum"`
    datatype : `str`, optional
        Data type for the intermediate and resulting combined image.
        Options include:
        - `"int16"`
        - `"float32"` (default: `"uint16"`).
    weights : `numpy.ndarray`, optional
        Array of weights to use when combining images. Dimensions must match the data arrays.
    scale : `callable` or `numpy.ndarray`, optional
        Scaling factors for combining images. Can be a function applied to each image
        or an array matching the number of images.
    mem_limit : `float`, optional
        Maximum memory (in bytes) allowed during combination (default: `16e9`).
    clip_extrema : `bool`, optional
        If `True`, masks the lowest `nlow` and highest `nhigh` values for each pixel
        before combining.
    nlow : `int`, optional
        Number of low pixel values to reject when `clip_extrema=True` (default: 1).
    nhigh : `int`, optional
        Number of high pixel values to reject when `clip_extrema=True` (default: 1).
    minmax_clip : `bool`, optional
        If `True`, masks all pixels below `minmax_clip_min` or above `minmax_clip_max`.
    minmax_clip_min : `float`, optional
        Minimum pixel value for masking when `minmax_clip=True`.
    minmax_clip_max : `float`, optional
        Maximum pixel value for masking when `minmax_clip=True`.
    sigma_clip : `bool`, optional
        If `True`, performs sigma clipping based on deviation thresholds.
    sigma_clip_low_thresh : `float`, optional
        Threshold for rejecting pixels below the baseline value (default: 3).
    sigma_clip_high_thresh : `float`, optional
        Threshold for rejecting pixels above the baseline value (default: 3).
    sigma_clip_func : `callable`, optional
        Function used to calculate the baseline value for sigma clipping (default: `median`).
    sigma_clip_dev_func : `callable`, optional
        Function used to calculate deviations for sigma clipping (default: `std`).
    combine_uncertainty_function : `callable`, optional
        Custom function to compute uncertainties during combination.
    overwrite_output : `bool`, optional
        If `True`, overwrites the output file if it exists (default: `False`).
    unit : `str`, optional
        Unit of the CCD data (e.g., `"adu"`, `"counts"`, `"photon"`) (default: `"adu"`).
    verbose : `bool`, optional
        If `True`, enables verbose logging for debugging.

    Returns
    -------
    `None`
        The function writes the combined image to disk and does not return any value.

    """

    if verbose:
        logger.setLevel(logging.DEBUG)

    if unit is None:
        if "BUNIT" in fits.open(fnames[0])[0].header:
            unit = fits.open(fnames[0])[0].header["BUNIT"]
        else:
            unit = "adu"

    logger.debug(f"avg_fits(mode={mode}, outfile={outfile}, fnames={fnames})")

    logger.info("Loading images...")

    images = np.array([fits.open(fname)[0].data for fname in fnames])

    images = images.astype(datatype)

    logger.info(f"Loaded {len(images)} images")

    logger.info("Averaging images...")

    logger.debug("Calculating combined image...")
    image_avg = ccdproc.combine(
        img_list=fnames,
        method=method,
        dtype=datatype,
        weights=weights,
        scale=scale,
        mem_limit=mem_limit,
        clip_extrema=clip_extrema,
        nlow=nlow,
        nhigh=nhigh,
        minmax_clip=minmax_clip,
        minmax_clip_min=minmax_clip_min,
        minmax_clip_max=minmax_clip_max,
        sigma_clip=sigma_clip,
        sigma_clip_low_thresh=sigma_clip_low_thresh,
        sigma_clip_high_thresh=sigma_clip_high_thresh,
        sigma_clip_func=sigma_clip_func,
        sigma_clip_dev_func=sigma_clip_dev_func,
        combine_uncertainty_function=combine_uncertainty_function,
        overwrite_output=overwrite_output,
        format="fits",
        unit=unit,
    )

    logger.debug(f"Image mean: {np.mean(image_avg.data)}")
    logger.debug(f"Image median: {np.median(image_avg.data)}")

    logger.info(f"Saving averaged image to {outfile}")

    with fits.open(fnames[-1]) as hdul:
        hdr = hdul[0].header

    hdr.add_comment(f"Averaged {len(images)} images using pyscope")
    hdr.add_comment(f"Average mode: {mode}")
    hdr.add_comment(f"Unit: {unit}")
    hdr.add_comment(f"Data type: {datatype}")
    hdr.add_comment(f"Weights: {weights}")
    hdr.add_comment(f"Scale: {scale}")
    hdr.add_comment(f"Memory limit: {mem_limit}")
    hdr.add_comment(f"Clip extrema: {clip_extrema}")
    hdr.add_comment(f"nLow: {nlow}")
    hdr.add_comment(f"nHigh: {nhigh}")
    hdr.add_comment(f"Minmax clip: {minmax_clip}")
    hdr.add_comment(f"Minmax clip min: {minmax_clip_min}")
    hdr.add_comment(f"Minmax clip max: {minmax_clip_max}")
    hdr.add_comment(f"Sigma clip: {sigma_clip}")
    hdr.add_comment(f"Sigma clip low thresh: {sigma_clip_low_thresh}")
    hdr.add_comment(f"Sigma clip high thresh: {sigma_clip_high_thresh}")
    hdr.add_comment(f"Sigma clip func: {sigma_clip_func}")
    hdr.add_comment(f"Sigma clip dev func: {sigma_clip_dev_func}")
    hdr.add_comment(
        f"Combine uncertainty func: {combine_uncertainty_function}"
    )
    hdr.add_comment(f"Overwrite output: {overwrite_output}")

    fits.writeto(outfile, image_avg, hdr, overwrite=True)

    logger.info("Done!")


avg_fits_ccdproc = avg_fits_ccdproc_cli.callback
