import logging
import os
from pathlib import Path

import click

from .observatory import Observatory

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.option(
    "-o",
    "--observatory",
    type=click.Path(exists=True),
    default="./config/observatory.cfg",
    show_default=True,
    help="Path to observatory configuration file.",
)
@click.option(
    "-c",
    "--camera",
    type=click.Choice(["ccd", "cmos"]),
    default="ccd",
    show_default=True,
    help="Camera type.",
)
@click.option(
    "-d",
    "--dark-exposures",
    type=float,
    multiple=True,
    default=[0.1, 1, 10, 100],
    show_default=True,
    help="Dark exposure times.",
)
@click.option(
    "-f",
    "--filter-exposures",
    type=float,
    multiple=True,
    help="The flat exposure times for each filter.",
)
@click.option(
    "-i",
    "--filter-brightness",
    type=float,
    multiple=True,
    help="The intensity of the calibrator [if present] for each filter.",
)
@click.option(
    "-r",
    "--readouts",
    type=int,
    multiple=True,
    help="Indices of readout modes to iterate through.",
)
@click.option(
    "-b",
    "--binnings",
    type=str,
    multiple=True,
    help="Binnings to iterate through.",
)
@click.option(
    "-n",
    "--repeat",
    type=int,
    default=10,
    show_default=True,
    help="Number of times to repeat each exposure.",
)
@click.option(
    "-s",
    "--save-path",
    type=click.Path(exists=True),
    default="./temp/",
    show_default=True,
    help="Path to save calibration set.",
)
@click.option(
    "-nd",
    "--new-dir",
    "new_dir",
    type=bool,
    default=True,
    show_default=True,
    help="Create a new directory for the calibration set.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity of output.",
)
@click.version_option()
def collect_calibration_set_cli(
    observatory="./config/observatory.cfg",
    camera="ccd",
    readouts=[2],
    binnings=["1x1"],
    repeat=10,
    dark_exposures=[300],
    filters=[],
    filter_exposures=[],
    filter_brightness=None,
    target_counts=None,
    home_telescope=False,
    check_cooler=True,
    tracking=True,
    dither_radius=0,  # arcseconds
    save_path="./temp/",
    new_dir=True,
    verbose=0,
):
    """
    Collects a calibration set for the observatory.\b

    .. warning::
        The filter_exposures and filter_brightnesses must be of equal length.

    Parameters
    ----------
    observatory : str

    camera : str, default="ccd"

    readouts : list, default=[None]

    binnings : list, default=[None]

    repeat : int, default=1

    dark_exposures : list, default=[]

    filters : list, default=[]

    filter_exposures : list, default=[]

    filter_brightness : list, default=None

    home_telescope : bool, default=False

    target_counts : int, default=None

    check_cooler : bool, default=True

    tracking : bool, default=True

    dither_radius : float, default=0

    save_path : str, default="./temp/"

    new_dir : bool, default=True

    verbose : int, default=0

    """

    if type(observatory) == str:
        logger.info(f"Collecting calibration set for {observatory}")
        obs = Observatory(observatory)
    elif type(observatory) == Observatory:
        logger.info(f"Collecting calibration set for {observatory.site_name}")
        obs = observatory
    else:
        logger.exception(f"Invalid observatory type: {type(observatory)}")
        return

    obs.connect_all()

    if len(filter_exposures) != len(filters):
        logger.error("The number of filter exposures must match the number of filters.")
        return

    if new_dir:
        save_path = Path(save_path) / obs.observatory_time.strftime("%Y-%m-%d_%H-%M-%S")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    logger.info(f"Saving calibration set to {save_path}")

    if len(filter_exposures) > 0:
        logger.info("Collecting flats")
        success = obs.take_flats(
            filters,
            filter_exposures,
            filter_brightness=filter_brightness,
            readouts=readouts,
            binnings=binnings,
            repeat=repeat,
            save_path=save_path,
            home_telescope=home_telescope,
            target_counts=target_counts,
            check_cooler=check_cooler,
            tracking=tracking,
            dither_radius=dither_radius,
            final_telescope_position="no change",
        )
        if not success:
            logger.error("Failed to collect flats")

        if camera == "cmos":
            logger.info("Collecting flat-darks")
            success = obs.take_darks(
                exposures=list(set(filter_exposures)),
                readouts=readouts,
                binnings=binnings,
                repeat=repeat,
                save_path=save_path,
            )
            if not success:
                logger.error("Failed to collect flat-darks")
        else:
            logger.warning("Skipping flat-dark collection for non-CMOS camera")

    if len(dark_exposures) > 0:
        logger.info("Collecting darks")
        success = obs.take_darks(
            exposures=dark_exposures,
            readouts=readouts,
            binnings=binnings,
            repeat=repeat,
            save_path=save_path,
        )
        if not success:
            logger.error("Failed to collect darks")

    if camera == "ccd":
        logger.info("Collecting biases")
        success = obs.take_darks(
            exposures=[0],
            readouts=readouts,
            binnings=binnings,
            repeat=repeat,
            save_path=save_path,
            frametyp="Bias",
        )
        if not success:
            logger.error("Failed to collect biases")
    else:
        logger.warning("Skipping bias collection for non-CCD camera")

    logger.info("Collection complete.")


collect_calibration_set = collect_calibration_set_cli.callback
