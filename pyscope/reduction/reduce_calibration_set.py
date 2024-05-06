import logging

import click

from .avg_fits import avg_fits
from .ccd_calib import ccd_calib

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.argument(
    "calibration_set",
    type=click.Path(exists=True),
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
    "-cm" "--combine-method",
    "combine_method",
    type=click.Choice(["median", "average"]),
    default="median",
    show_default=True,
    help="Method to use for averaging images.",
)
@click.option(
    "-pn",
    "--pre-normalize",
    type=bool,
    default=True,
    show_default=True,
    help="Pre-normalize flat images before combining. Useful for sky flats.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity of output.",
)
@click.version_option()
def reduce_calibration_set_cli(
    calibration_set,
    camera="ccd",
    combine_method="median",
    pre_normalize=True,
    verbose=0,
):
    """
    Reduce a calibration set to master frames.\b
    """

    if verbose == 0:
        logger.setLevel(logging.INFO)
    elif verbose >= 1:
        logger.setLevel(logging.DEBUG)

    calibration_set = Path(calibration_set).resolve()

    bias_sets = Path(calibration_set.glob("biases*/"))
    dark_sets = Path(calibration_set.glob("darks*/"))
    flat_sets = Path(calibration_set.glob("flats*/"))

    for bias_set in bias_sets:
        logger.info(f"Reducing bias set: {bias_set}")
        avg_fits(
            bias_set,
            mode=combine_method,
            outfile=calibration_set
            / (str(bias_set.name).replace("biases", "master_bias") + ".fts"),
        )

    for dark_set in dark_sets:
        logger.info(f"Reducing dark set: {dark_set}")
        avg_fits(
            dark_set,
            mode=combine_method,
            outfile=calibration_set
            / (str(dark_set.name).replace("darks", "master_dark") + ".fts"),
        )

    for flat_set in flat_sets:
        logger.info(f"Reducing flat set: {flat_set}")

        if camera == "ccd":
            # flats _ filt _ binxbin _ Readout1 _ texp
            name_str = str(flat_set.name).split("_")

            matching_dark = calibration_set.glob(
                f"master_dark_{name_str[2]}x{name_str[3]}_{name_str[4]}*.fts"
            )[0]
            matching_bias = calibration_set.glob(
                f"master_bias_{name_str[2]}x{name_str[3]}_{name_str[4]}*.fts"
            )[0]

            ccd_calib(
                flat_set,
                matching_dark,
                bias_frame=matching_bias,
                camera_type=camera,
            )

            cal_flat_set = flat_set.glob("*_cal.fts")
            avg_fits(
                cal_flat_set,
                mode=combine_method,
                pre_normalize=pre_normalize,
                outfile=calibration_set
                / (str(flat_set.name).replace("flats", "master_flat") + ".fts"),
            )

        elif camera == "cmos":
            # flats _ filt _ binxbin _ Readout1 _ texp
            name_str = str(flat_set.name).split("_")

            matching_dark = calibration_set.glob(
                f"master_dark_{name_str[2]}x{name_str[3]}_{name_str[4]}_{name_str[5]}*.fts"
            )[0]

            ccd_calib(
                flat_set,
                matching_dark,
                camera_type=camera,
            )

            cal_flat_set = flat_set.glob("*_cal.fts")
            avg_fits(
                cal_flat_set,
                mode=combine_method,
                pre_normalize=pre_normalize,
                outfile=calibration_set
                / (str(flat_set.name).replace("flats", "master_flat") + ".fts"),
            )

    logger.info("Calibration set reduction complete.")


reduce_calibration_set = reduce_calibration_set_cli.callback
