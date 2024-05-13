import logging

import click
import photutils.background as photbackground
import photutils.segmentation as photsegmentation
from astropy import convolution, wcs
from astropy.io import fits
from astropy.stats import SigmaClip
from photutils.utils import calc_total_error

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.argument("fnames", type=click.Path(exists=True), nargs=-1)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="""Print verbose output."""
)
@click.version_option()
def detect_sources_photutils_cli(
    fnames,
    clip_sigma=3,
    clip_maxiters=5,
    clip_cenfunc="median",
    clip_stdfunc="std",
    bkg_estimator="SExtractorBackground",
    bkgrms_estimator="StdBackgroundRMS",
    box_size=50,
    filter_size=3,
    kernel_fwhm=3,
    kernel_size=5,
    effective_gain=1,
    detect_threshold=3,
    connectivity=8,
    npixels=10,
    localbkg_width=10,
    apermask_method="correct",
    kron_params=(2.5, 1.4, 0.0),
    deblend=True,
    nlevels=32,
    contrast=0.001,
    mode="exponential",
    nproc=1,
    tbl_save_path=None,
    progress_bar=True,
    verbose=0,
):
    """Finds sources in an image and returns a catalog of their positions
    along with other properties"""

    image, hdr = fits.getdata(fnames, header=True)
    image = image.astype("float64")

    # Set up sigma clipping
    sigma_clip = SigmaClip(
        sigma=clip_sigma,
        maxiters=clip_maxiters,
        cenfunc=clip_cenfunc,
        stdfunc=clip_stdfunc,
    )

    # Set up background estimators
    if bkg_estimator == "MeanBackground":
        bkg_estimator = photbackground.MeanBackground()
    elif bkg_estimator == "MedianBackground":
        bkg_estimator = photbackground.MedianBackground()
    elif bkg_estimator == "ModeEstimatorBackground":
        bkg_estimator = photbackground.ModeEstimatorBackground()
    elif bkg_estimator == "MMMBackground":
        bkg_estimator = photbackground.MMMBackground()
    elif bkg_estimator == "SExtractorBackground":
        bkg_estimator = photbackground.SExtractorBackground()
    elif bkg_estimator == "BiweightLocationBackground":
        bkg_estimator = photbackground.BiweightLocationBackground()
    else:
        bkg_estimator = photbackground.SExtractorBackground()

    # Set up background RMS estimators
    if bkgrms_estimator == "StdBackgroundRMS":
        bkgrms_estimator = photbackground.StdBackgroundRMS()
    elif bkgrms_estimator == "MADStdBackgroundRMS":
        bkgrms_estimator = photbackground.MADStdBackgroundRMS()
    elif bkgrms_estimator == "BiweightScaleBackgroundRMS":
        bkgrms_estimator = photbackground.BiweightScaleBackgroundRMS()
    else:
        bkgrms_estimator = photbackground.StdBackgroundRMS()

    logger.info("Estimating background...")
    bkg = photbackground.Background2D(
        image,
        (box_size, box_size),
        filter_size=(filter_size, filter_size),
        sigma_clip=sigma_clip,
        bkg_estimator=bkg_estimator,
        bkgrms_estimator=bkgrms_estimator,
    )
    image -= bkg.background
    logger.info("Estimating background... Done")

    logger.info("Convolving image with a 2D Gaussian kernel...")
    kernel = photsegmentation.make_2dgaussian_kernel(kernel_fwhm, size=kernel_size)
    convolved_image = convolution.convolve(image, kernel)
    logger.info("Convolving image with a 2D Gaussian kernel... Done")

    logger.info("Detecting sources...")
    segment_map = photsegmentation.detect_sources(
        convolved_image,
        detect_threshold * bkg.background_rms,
        npixels=npixels,
        connectivity=connectivity,
    )
    logger.info("Detecting sources... Done")

    if deblend:
        logger.info("Deblending sources...")
        segment_map = photsegmentation.deblend_sources(
            convolved_image,
            segment_map,
            npixels=npixels,
            nlevels=nlevels,
            contrast=contrast,
            mode=mode,
            connectivity=connectivity,
            nproc=nproc,
            progress_bar=progress_bar,
        )
        logger.info("Deblending sources... Done")

    logger.info("Calculating total error...")
    err = calc_total_error(image, bkg.background_rms, effective_gain)
    logger.info("Calculating total error... Done")

    logger.info("Creating source catalog...")
    cat = photsegmentation.SourceCatalog(
        image,
        segment_map,
        convolved_data=convolved_image,
        error=err,
        background=bkg.background,
        wcs=wcs.WCS(hdr),
        localbkg_width=localbkg_width,
        apermask_method=apermask_method,
        kron_params=kron_params,
        progress_bar=progress_bar,
    )
    logger.info("Creating source catalog... Done")

    if tbl_save_path is not None:
        logger.info(f"Saving source catalog to {tbl_save_path}...")
        tbl = cat.to_table(
            columns=[
                "area",
                "background",
                "background_centroid",
                "background_mean",
                "background_sum",
                "bbox",
                "bbox_xmax",
                "bbox_xmin",
                "bbox_ymax",
                "bbox_ymin",
                "centroid",
                "centroid_quad",
                "centrroid_win",
                "convdata",
                "covar_sigx2",
                "covar_sigxy",
                "covar_sigy2",
                "covariance",
                "covariance_eigvals",
                "cutout_centroid",
                "cutout_centroid_quad",
                "cutout_centroid_win",
                "cutout_maxval_index",
                "cutout_minval_index",
                "cxx",
                "cxy",
                "cyy",
                "data",
                "eccentricity",
                "ellipticity",
                "elongation",
                "equivalent_radius",
                "error",
                "extra_properties",
                "fwhm",
                "gini",
                "inertia_tensor",
                "isscalar",
                "kron_aperture",
                "kron_flux",
                "kron_fluxerr",
                "kron_radius",
                "label",
                "labels",
                "local_background",
                "local_background_aperture",
                "max_value",
                "maxval_index",
                "min_value",
                "minval_index",
                "moments",
                "moments_central",
                "nlabels",
                "orientation",
                "perimeter",
                "properties",
                "segment",
                "segment_area",
                "segment_flux",
                "segment_fluxerr",
                "semimajor_sigma",
                "semiminor_sigma",
                "sky_bbbox_ll",
                "sky_bbbox_lr",
                "sky_bbbox_ul",
                "sky_bbbox_ur",
                "sky_centroid",
                "sky_centroid_icrs",
                "sky_centroid_quad",
                "sky_centroid_win",
                "slices",
                "xcentroid",
                "xcentroid_quad",
                "xcentroid_win",
                "ycentroid",
                "ycentroid_quad",
                "ycentroid_win",
            ],
        )
        tbl.write(tbl_save_path, overwrite=True)
        logger.info(f"Saving source catalog to {tbl_save_path}... Done")

    return cat


detct_sources_photutils = detect_sources_photutils_cli.callback
