import logging

import click
import numpy as np
from astropy.io import fits
import astropy.units as u
import ccdproc
from astropy.nddata import CCDData
import os

logger = logging.getLogger(__name__)

"""
TODO: use ccdproc to average FITS files

for reading in files as CCDData types: 
    default to user specified, then header BUNIT, then default to adu

    if unit == None:
        then the user didn't specify a unit, so check the header for BUNIT
        if BUNIT exists, use that, 
            unit = header["BUNIT"]
        else:
            unit = "adu"
    
            

    or if the header doesn't contain BUNIT, set BUNIT to adu, then use that
"""

@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["0", "1"]),
    default="0",
    show_choices=True,
    show_default=True,
    help="Mode to use for averaging FITS files (0 = median, 1 = mean).",
)
@click.option(
    "-o",
    "--outfile",
    type=click.Path(),
    required=True,
    help="Path to save averaged FITS file.",
)
@click.option(
    "-d",
    "--datatype",
    type=click.Choice([
        np.int_, np.int8, np.int16, 
        np.int32, np.int64,
        
        np.uint, np.uint8, np.uint16, 
        np.uint32, np.uint64,
        
        np.float_, np.float32, np.float64
    ]),
    default=np.uint16,
    show_choices=True,
    show_default=True,
    help="Data type to use for averaged FITS file.",
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
    type=click.Choice([float, None]),
    default=None,
    show_default=True,
    help="",
)
@click.option(
    "-mcx",
    "--minmax_clip_max",
    type=click.Choice([float, None]),
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
    type=click.Choice([float, None]),
    default=3,
    show_default=True,
    help="",
)
@click.option(
    "-scht",
    "--sigma_clip_high_thresh",
    type=click.Choice([float, None]),
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
@click.argument("fnames", nargs=-1, type=click.Path(exists=True, resolve_path=True))
@click.version_option()
def avg_fits_ccdproc_cli(
    mode, 
    outfile, 
    fnames, 
    datatype=np.uint16,
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
    unit='adu', 
    verbose=False):
    """Advanced version of avg_fits. Averages fits files using ccdproc.combine method.

    Parameters
    ----------
    mode : str
        mode to use for averaging FITS files (0 = median, 1 = mean).

    outfile : str
        path to save averaged FITS file.
    
    fnames : list
        list of FITS file paths to average.
    
    datatype : np.datatype, optional
        intermediate and resulting dtype for combined CCDs, by default np.uint16
    
    weights : np.ndarray, optional
        Weights to be used when combining images. An array with the weight values. The dimensions should match the the dimensions of the data arrays being combined., by default None
    
    scale : callable or np.ndarray, optional
        Scaling factor to be used when combining images. Images are multiplied by scaling prior to combining them. Scaling may be either a function, which will be applied to each image to determine the scaling factor, or a list or array whose length is the number of images in the Combiner, by default None
    
    mem_limit : float, optional
        Maximum memory which should be used while combining (in bytes), by default 16000000000.0
    
    clip_extrema : bool, optional
        Set to True if you want to mask pixels using an IRAF-like minmax clipping algorithm. The algorithm will mask the lowest nlow values and the highest nhigh values before combining the values to make up a single pixel in the resulting image. For example, the image will be a combination of Nimages-low-nhigh pixel values instead of the combination of Nimages. Parameters below are valid only when clip_extrema is set to True, by default False
    
    nlow : int, optional
        Number of low values to reject from the combination, by default 1
    
    nhigh : int, optional
        Number of high values to reject from the combination, by default 1
    
    minmax_clip : bool, optional
        Set to True if you want to mask all pixels that are below minmax_clip_min or above minmax_clip_max before combining, by default False
    
    minmax_clip_min : float, optional
        All pixels with values below min_clip will be masked, by default None
    
    minmax_clip_max : flaot, optional
        All pixels with values above min_clip will be masked, by default None
    
    sigma_clip : bool, optional
        Set to True if you want to reject pixels which have deviations greater than those set by the threshold values. The algorithm will first calculated a baseline value using the function specified in func and deviation based on sigma_clip_dev_func and the input data array. Any pixel with a deviation from the baseline value greater than that set by sigma_clip_high_thresh or lower than that set by sigma_clip_low_thresh will be rejected, by default False
    
    sigma_clip_low_thresh : int, optional
        Threshold for rejecting pixels that deviate below the baseline value. If negative value, then will be convert to a positive value. If None, no rejection will be done based on low_thresh, by default 3
    
    sigma_clip_high_thresh : int, optional
        Threshold for rejecting pixels that deviate above the baseline value. If None, no rejection will be done based on high_thresh, by default 3
    
    sigma_clip_func : callable, optional
        The statistic or callable function/object used to compute the center value for the clipping. If using a callable function/object and the axis keyword is used, then it must be able to ignore NaNs (e.g., numpy.nanmean) and it must have an axis keyword to return an array with axis dimension(s) removed. The default is 'median', by default None
    
    sigma_clip_dev_func : callable, optional
        The statistic or callable function/object used to compute the standard deviation about the center value. If using a callable function/object and the axis keyword is used, then it must be able to ignore NaNs (e.g., numpy.nanstd) and it must have an axis keyword to return an array with axis dimension(s) removed. The default is 'std', by default None
    
    combine_uncertainty_function : callable, optional
        If None use the default uncertainty func when using average, median or sum combine, otherwise use the function provided, by default None
    
    overwrite_output : bool, optional
        If output_file is specified, this is passed to the astropy.nddata.fits_ccddata_writer under the keyword overwrite; has no effect otherwise., by default False
    
    unit : str, optional
        unit for CCDData objects, by default 'adu'
    
    verbose : bool, optional
        verbosity of logger, by default False
    """
    
    if verbose:
        logger.setLevel(logging.DEBUG)

    if unit == None:
        if "BUNIT" in fits.open(fnames[0])[0].header:
            unit = fits.open(fnames[0])[0].header["BUNIT"]
        else:
            unit = "adu"

    logger.debug(f"avg_fits(mode={mode}, outfile={outfile}, fnames={fnames})")

    logger.info("Loading FITS files...")

    images = np.array([fits.open(fname)[0].data for fname in fnames])
    
    
    images = images.astype(datatype)
    
    logger.info(f"Loaded {len(images)} FITS files")

    logger.info("Averaging FITS files...")

    if str(mode) == "0":
        logger.debug("Calculating median...")
        image_avg = ccdproc.combine(
            img_list=fnames, 
            method='median', 
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
            format='fits', 
            unit=unit)
    elif str(mode) == "1":
        logger.debug("Calculating mean...")
        image_avg = ccdproc.combine(
            fnames, 
            method='average', 
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
            format='fits', 
            unit=unit)


    logger.debug(f"Image mean: {np.mean(image_avg.data)}")
    logger.debug(f"Image median: {np.median(image_avg.data)}")


    logger.info(f"Saving averaged FITS file to {outfile}")


    with fits.open(fnames[-1]) as hdul:
        hdr = hdul[0].header

    
    hdr.add_comment(f"Averaged {len(images)} FITS files using pyscope")
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
    hdr.add_comment(f"Combine uncertainty func: {combine_uncertainty_function}")
    hdr.add_comment(f"Overwrite output: {overwrite_output}")

    fits.writeto(outfile, image_avg, hdr, overwrite=True)

    logger.info("Done!")




avg_fits_ccdproc = avg_fits_ccdproc_cli.callback
