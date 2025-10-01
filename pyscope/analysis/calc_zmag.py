import logging
import os

import click
import matplotlib.pyplot as plt
import numpy as np
import tqdm
from astropy import units as u
from astropy import wcs
from astropy.io import fits
from astroquery import sdss

from pyscope.analysis import detect_sources_photutils

from ..reduction import astrometry_net_wcs

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.option(
    "-f",
    "--filter",
    "filt",
    type=click.Choice(["u", "b", "g", "r", "i", "z"]),
    show_choices=True,
    help="""Sloan filter to use for computing the
                zero-point magnitude. Overrides the header filter.""",
)
@click.option(
    "-b",
    "--background-params",
    "background_params",
    nargs=2,
    type=(int, int),
    default=(50, 3),
    show_default=True,
    help="""Background2D box_size and filter_size
                parameters in pixels.""",
)
@click.option(
    "-t",
    "--threshold",
    type=float,
    default=3.0,
    show_default=True,
    help="""Threshhold for source detection in units of
                background RMS.""",
)
@click.option(
    "-g",
    "--gaussian-params",
    nargs=2,
    type=(float, int),
    default=(5, 3),
    show_default=True,
    help="Gaussian2D sigma [pixels] and size parameters.",
)
@click.option(
    "-e",
    "--effective-gain",
    "effective_gain",
    type=float,
    default=1,
    show_default=True,
    help="""Effective gain for computing the Poisson noise
                contribution to the total error. In units of electrons
                or photons per count""",
)
@click.option(
    "-c",
    "--connectivity",
    type=int,
    default=8,
    show_default=True,
    show_choices=True,
    help="""Definition of pixel connectivity, i.e. whether
                diagonal pixels are considered to be connected (8 if
                yes, 4 if no).""",
)
@click.option(
    "-n",
    "--npixels",
    type=int,
    default=10,
    show_default=True,
    help="Minimum number of connected pixels",
)
@click.option(
    "-l",
    "--nlevels",
    type=int,
    default=32,
    show_default=True,
    help="""Number of multi-thresholding levels to use
                for source deblending.""",
)
@click.option(
    "-d",
    "--deblend-contrast",
    "deblend_contrast",
    type=float,
    default=0.005,
    show_default=True,
    help="""Contrast ratio used for source deblending.""",
)
@click.option(
    "-s",
    "--search-radius",
    "search_radius",
    type=float,
    default=3.0,
    help="""Radius to search for nearby
                sources in the SDSS catalog [arcsec].""",
)
@click.option(
    "-w",
    "--write",
    is_flag=True,
    default=False,
    help="""Write the ZMAG and ZMAGERR to the header.""",
)
@click.option(
    "-p", "--plot", is_flag=True, default=False, help="""Plot the results."""
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="""Print verbose output.""",
)
@click.argument("images", type=click.Path(exists=True), nargs=-1)
@click.version_option()
def calc_zmag_cli(
    images,
    filt=None,
    background_params=(50, 3),
    threshold=25,
    gaussian_params=(5, 3),
    effective_gain=1,
    connectivity=8,
    npixels=10,
    nlevels=32,
    deblend_contrast=0.005,
    search_radius=3,
    write=False,
    plot=False,
    verbose=False,
):
    if verbose:
        logger.setLevel("DEBUG")
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    logger.debug(
        f"""calc_zmag_cli(filt={filt}, background_params={background_params},
                    threshold={threshold}, gaussian_params={gaussian_params},
                    effective_gain={effective_gain}, connectivity={connectivity},
                    npixels={npixels}, levels={nlevels},
                    deblend_contrast={deblend_contrast}, search_radius={search_radius},
                    write={write}, plot={plot}, verbose={verbose})"""
    )
    logger.info("Starting calc_zmag")

    if type(images) == str:
        images = [images]

    zmags = []
    zmags_err = []
    fig = None
    ax0 = None
    ax1 = None
    ax2 = None

    for im in images:
        os.path.abspath(im)
        logger.info("Processing %s" % im)

        data, hdr = fits.getdata(im), fits.getheader(im)
        try:
            exp = hdr["EXPTIME"]
        except:
            exp = hdr["EXPOSURE"]
        im_filt = hdr["FILTER"]

        w = wcs.WCS(hdr)

        # Get header filter or override with CLI option
        if filt is None:
            filt = im_filt
        filt = filt.lower()
        logger.info("Filter: %s" % filt)

        if filt not in ["u", "g", "r", "i", "z"]:
            logger.error("Invalid filter, continuing to next image...")
            continue

        # Check if WCS solution exists already, if not, try one
        try:
            w = wcs.WCS(hdr)
            sky = w.pixel_to_world(0, 0)
        except:
            logger.info(
                "No WCS solution found. Attempting to solve with Astrometry.net..."
            )
            success = astrometry_net_wcs(im)
            if success:
                logger.info("Solved.")
            else:
                logger.error(
                    "Failed to solve, continuing to next image if present..."
                )
                continue

        # Get the source catalog
        logger.info("Detecting sources...")
        catalog = detect_sources_photutils.detect_sources_photutils(
            (im,),
            box_size=background_params[0],
            filter_size=background_params[1],
            detect_threshold=threshold,
            kernel_fwhm=gaussian_params[0],
            kernel_size=gaussian_params[1],
            effective_gain=effective_gain,
            connectivity=connectivity,
            npixels=npixels,
            nlevels=nlevels,
            contrast=deblend_contrast,
        ).to_table(
            columns=(
                "sky_centroid_icrs",
                "xcentroid",
                "ycentroid",
                "segment_flux",
                "segment_fluxerr",
            )
        )

        logger.info("Found %d sources." % len(catalog))

        catalog["SDSS"] = [None for i in range(len(catalog))]

        # SDSS lookup
        logger.info("Looking up corresponding SDSS sources...")
        for source in tqdm.tqdm(catalog):
            logger.debug("Source:\n%s" % source)

            potential_matches = sdss.SDSS.query_region(
                source["sky_centroid_icrs"],
                radius=search_radius * u.arcsec,
                cache=True,
                fields=["ra", "dec", "clean", filt],
            )

            try:
                for match in potential_matches:
                    if match["clean"] and match[filt] < 24:
                        source["SDSS"] = float(match[filt])
                        logger.debug("Match found:\n%s" % match)
                        break
            except:
                logger.debug(
                    "No SDSS matches found, continuing to next source..."
                )
                continue

        catalog.remove_rows(catalog["SDSS"] == None)

        logger.info("Found %d SDSS matches." % len(catalog))

        # Compute zero-point magnitude
        logger.info("Computing zero-point magnitude...")

        mag = catalog["SDSS"].data
        flux = catalog["segment_flux"].data / exp
        flux_err = catalog["segment_fluxerr"].data / exp

        zmag = mag + 2.5 * np.log10(flux)
        zmag_err = 2.5 * np.log10(1 + flux_err / flux)

        clip_array = (zmag < np.mean(zmag) + 2 * np.std(zmag)) & (
            zmag > np.mean(zmag) - 2 * np.std(zmag)
        )
        zmag = zmag[clip_array]
        zmag_err = zmag_err[clip_array]
        mag = mag[clip_array]
        flux = flux[clip_array]
        flux_err = flux_err[clip_array]

        zmags.append(zmag)
        zmags_err.append(zmag_err)

        mean_zmag = np.mean(zmag)
        mean_zmag_err = np.sqrt(np.sum(zmag_err**2)) / len(zmag)

        logger.info(
            "Mean zero-point magnitude: %.3f +/- %.3f"
            % (mean_zmag, mean_zmag_err)
        )

        if write:
            logger.info("Writing to header...")
            hdr["ZMAG"] = mean_zmag
            hdr["ZPMAG"] = mean_zmag
            hdr["ZMAGERR"] = mean_zmag_err
            hdr["ZPMAGERR"] = mean_zmag_err
            fits.writeto(im, data=data, header=hdr, overwrite=True)

        fig = None
        ax0 = None
        ax1 = None
        ax2 = None
        if plot:
            fig = plt.figure(figsize=(16, 16), dpi=400)
            ax0 = fig.add_subplot(3, 2, (1, 4), projection=w)
            ax1 = fig.add_subplot(3, 2, 5)
            ax2 = fig.add_subplot(3, 2, 6)
            fig.subplots_adjust(wspace=0.15, hspace=0.1)

            # Left plot shows image with sources circled
            ax0.imshow(
                data,
                origin="lower",
                cmap="gray",
                vmin=np.percentile(data, 5),
                vmax=np.percentile(data, 99),
            )
            overlay = ax0.get_coords_overlay("icrs")
            overlay.grid(color="white", lw=2)

            for source in catalog:
                ax0.scatter(
                    source["xcentroid"],
                    source["ycentroid"],
                    marker="o",
                    s=5,
                    color="r",
                )
                ax0.text(
                    source["xcentroid"],
                    source["ycentroid"],
                    ("%.2f" % source["SDSS"]),
                    color="r",
                    fontsize=12,
                )

            ax0.set_xlabel(" ")
            ax0.set_ylabel(" ")

            # Right plot shows flux vs. magnitude
            ax1.errorbar(
                mag,
                flux,
                yerr=flux_err,
                fmt="",
                linestyle="none",
                color="black",
            )
            for i in range(len(mag)):
                ax1.text(
                    mag[i],
                    flux[i],
                    ("%.1f" % flux[i]),
                    color="black",
                    fontsize=12,
                )

            model_mag = np.linspace(14, 24, 100)
            model_flux = 10 ** (-0.4 * (model_mag - mean_zmag))
            ax1.plot(model_mag, model_flux, color="black")

            ax1.axvline(x=mean_zmag, color="red", ls="dashed")
            ax1.text(
                mean_zmag - 0.05,
                0.85,
                ("%.2f +/- %.3f" % (mean_zmag, mean_zmag_err)),
                color="red",
                fontsize=12,
            )

            ax1.set_xlim(24, 14)
            ax1.set_yscale("log")

            ax1.set_xlabel("SDSS Magnitude")
            ax1.set_ylabel("Flux [counts/sec]")

            ax2.scatter(mag, flux / flux_err, color="black", marker=".", s=5)
            for i in range(len(mag)):
                ax2.text(
                    mag[i],
                    flux[i] / flux_err[i],
                    ("%.2f" % (flux[i] / flux_err[i])),
                    color="black",
                    fontsize=12,
                )

            ax2.set_xlim(24, 14)
            ax2.set_ylim(threshold)
            ax2.set_yscale("log")
            ax2.set_xlabel("SDSS Magnitude")
            ax2.set_ylabel("SNR")

            fig.suptitle(
                "%s\nZMAG: %.2f +/- %.3f" % (im, mean_zmag, mean_zmag_err),
                y=0.95,
                fontsize=16,
            )

            # plt.show()

    logger.info("Done.")

    return zmags, zmags_err, fig, (ax0, ax1, ax2)


calc_zmag = calc_zmag_cli.callback
