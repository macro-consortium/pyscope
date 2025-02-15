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
@click.argument("fname", type=click.Path(exists=True), nargs=-1)
@click.option(
    "--clip-sigma",
    default=3,
    help="""See documentation for astropy.stats.SigmaClip""",
)
@click.option(
    "--clip-maxiters",
    default=5,
    help="""See documentation for astropy.stats.SigmaClip""",
)
@click.option(
    "--clip-cenfunc",
    default="median",
    help="""See documentation for astropy.stats.SigmaClip""",
)
@click.option(
    "--clip-stdfunc",
    default="std",
    help="""See documentation for astropy.stats.SigmaClip""",
)
@click.option(
    "--bkg-estimator",
    type=click.Choice(
        [
            "MeanBackground",
            "MedianBackground",
            "ModeEstimatorBackground",
            "MMMBackground",
            "SExtractorBackground",
            "BiweightLocationBackground",
        ]
    ),
    default="SExtractorBackground",
    help="""Background estimator to use""",
)
@click.option(
    "--bkgrms-estimator",
    type=click.Choice(
        [
            "StdBackgroundRMS",
            "MADStdBackgroundRMS",
            "BiweightScaleBackgroundRMS",
        ]
    ),
    default="StdBackgroundRMS",
    help="""Background RMS estimator to use""",
)
@click.option(
    "--box-size",
    default=50,
    help="""Size of the box used to estimate the background""",
)
@click.option(
    "--filter-size",
    default=3,
    help="""Size of the filter used to smooth the background""",
)
@click.option(
    "--kernel-fwhm",
    default=3,
    help="""Full width at half maximum of the Gaussian kernel used to convolve the image""",
)
@click.option(
    "--kernel-size",
    default=5,
    help="""Size of the kernel used to convolve the image""",
)
@click.option(
    "--effective-gain",
    default=1,
    help="""Effective gain of the image""",
)
@click.option(
    "--detect-threshold",
    default=3,
    help="""Threshold used to detect sources in multiples of the background RMS""",
)
@click.option(
    "--connectivity",
    type=int,
    default=8,
    help="""Connectivity of the sources""",
)
@click.option(
    "--npixels",
    default=5,
    help="""Minimum number of pixels required for a source""",
)
@click.option(
    "--localbkg-width",
    default=10,
    help="""Width in pixels used to compute the local background""",
)
@click.option(
    "--apermask-method",
    type=click.Choice(["correct", "mask", "none"]),
    default="correct",
    help="""Method used to mask out the aperture""",
)
@click.option(
    "--kron-params",
    nargs=3,
    type=float,
    default=(2.5, 1.4, 0.0),
    help="""Parameters used to compute the Kron radius""",
)
@click.option(
    "--deblend/--no-deblend",
    default=True,
    help="""Whether to deblend sources""",
)
@click.option(
    "--nlevels",
    default=32,
    help="""Number of levels used in the deblending""",
)
@click.option(
    "--contrast",
    default=0.001,
    help="""Contrast used in the deblending""",
)
@click.option(
    "--mode",
    type=click.Choice(["exponential", "linear"]),
    default="exponential",
    help="""Mode used in the deblending""",
)
@click.option(
    "--nproc",
    default=1,
    help="""Number of processes to use for deblending""",
)
@click.option(
    "--tbl-save-path",
    type=click.Path(),
    help="""Path to save the source catalog""",
)
@click.option(
    "--progress-bar/--no-progress-bar",
    default=True,
    help="""Whether to show a progress bar for certain time-consuming operations""",
)
@click.option("-v", "--verbose", count=True, help="""Verbosity level""")
@click.version_option()
def detect_sources_photutils_cli(
    fname,
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
    npixels=5,
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
    along with other properties. See https://photutils.readthedocs.io/en/stable/api/photutils.segmentation.SourceCatalog.html for more information.
    """

    fname = str(fname[0])
    image, hdr = fits.getdata(fname, header=True)
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
    kernel = photsegmentation.make_2dgaussian_kernel(
        kernel_fwhm, size=kernel_size
    )
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
                # "bbox",
                "bbox_xmax",
                "bbox_xmin",
                "bbox_ymax",
                "bbox_ymin",
                "centroid",
                "centroid_quad",
                "centroid_win",
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
                # "extra_properties",
                "fwhm",
                "gini",
                "inertia_tensor",
                # "isscalar",
                # "kron_aperture",
                "kron_flux",
                "kron_fluxerr",
                "kron_radius",
                "label",
                "labels",
                "local_background",
                # "local_background_aperture",
                "max_value",
                "maxval_index",
                "min_value",
                "minval_index",
                "moments",
                "moments_central",
                # "nlabels",
                "orientation",
                "perimeter",
                # "properties",
                "segment",
                "segment_area",
                "segment_flux",
                "segment_fluxerr",
                "semimajor_sigma",
                "semiminor_sigma",
                "sky_bbox_ll",
                "sky_bbox_lr",
                "sky_bbox_ul",
                "sky_bbox_ur",
                "sky_centroid",
                "sky_centroid_icrs",
                "sky_centroid_quad",
                "sky_centroid_win",
                # "slices",
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


detect_sources_photutils = detect_sources_photutils_cli.callback
