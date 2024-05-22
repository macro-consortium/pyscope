import glob
import logging
import os
import sys
from pathlib import Path

import click

from .avg_fits import avg_fits
from .ccd_calib import ccd_calib

logger = logging.getLogger(__name__)

def custom_exit(status=0):
    try:
        sys.exit(status)
    except SystemExit as e:
        # Handle the exit cleanly in an interactive environment or during tests
        print(f"Exiting with status: {e.code}")
        # Optionally re-raise or do nothing, which could just print a message

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
    "mode",
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
    mode="0",
    pre_normalize=True,
    verbose=0,
):
    """
    Reduce a calibration set to master frames.\b
    """

    calibration_set = Path(calibration_set).resolve()

    # try:
    #     bias_sets = list(calibration_set.glob("biases*"))
    #     if not bias_sets:
    #         logging.error("No bias sets found. Exiting program.")
    #         custom_exit(1)
    #     logging.debug(f"Found {len(bias_sets)} bias set(s).")
    # except Exception as e:
    #     logging.error("Failed to retrieve bias sets:", exc_info=True)
    #     custom_exit(1)

    # try:
    #     dark_sets = list(calibration_set.glob("darks*"))
    #     if not dark_sets:
    #         logging.error("No dark sets found. Exiting program.")
    #         custom_exit(1)
    #     logging.debug(f"Found {len(dark_sets)} dark set(s).")
    # except Exception as e:
    #     logging.error("Failed to retrieve dark sets:", exc_info=True)
    #     custom_exit(1)

    # try:
    #     flat_sets = list(calibration_set.glob("flats*"))
    #     if not flat_sets:
    #         logging.error("No flat sets found. Exiting program.")
    #         custom_exit(1)
    #     logging.debug(f"Found {len(flat_sets)} flat set(s).")
    # except Exception as e:
    #     logging.error("Failed to retrieve flat sets:", exc_info=True)
    #     custom_exit(1)
        
    bias_sets = calibration_set.glob("biases*")
    dark_sets = calibration_set.glob("darks*")
    flat_sets = calibration_set.glob("flats*")

    for bias_set in bias_sets:
        logger.info(f"Reducing bias set: {bias_set}")
        avg_fits(
            glob.glob(str(bias_set) + "/*.fts"),
            mode=mode,
            outfile=calibration_set
            / (str(bias_set.name).replace("biases", "master_bias") + ".fts"),
        )

    for dark_set in dark_sets:
        logger.info(f"Reducing dark set: {dark_set}")
        avg_fits(
            glob.glob(str(dark_set) + "/*.fts"),
            mode=mode,
            outfile=calibration_set
            / (str(dark_set.name).replace("darks", "master_dark") + ".fts"),
        )

    for flat_set in flat_sets:
        logger.info(f"Reducing flat set: {flat_set}")

        if camera == "ccd":
            # flats _ filt _ binxbin _ Readout1 _ texp
            name_str = str(flat_set.name).split("_")

            matching_dark = list(
                calibration_set.glob(f"master_dark_{name_str[2]}_{name_str[3]}*.fts")
            )
            matching_dark = matching_dark[0] if matching_dark else None
            matching_bias = list(
                calibration_set.glob(f"master_bias_{name_str[2]}_{name_str[3]}*.fts")
            )
            matching_bias = matching_bias[0] if matching_bias else None

            if os.path.isdir(flat_set):
                flat_set_list = glob.glob(str(flat_set) + "/*.fts")

            ccd_calib(
                flat_set_list,
                matching_dark,
                bias_frame=matching_bias,
                camera_type=camera,
            )

            cal_flat_set = str(flat_set) + "/*_cal.fts"
            avg_fits(
                glob.glob(str(cal_flat_set)),
                mode=mode,
                pre_normalize=pre_normalize,
                outfile=calibration_set
                / (str(flat_set.name).replace("flats", "master_flat") + ".fts"),
            )

        elif camera == "cmos":
            # flats _ filt _ binxbin _ Readout1 _ texp
            name_str = str(flat_set.name).split("_")

            matching_dark = list(
                calibration_set.glob(
                    f"master_dark_{name_str[2]}_{name_str[3]}_{name_str[4]}*.fts"
                )
            )
            matching_dark = matching_dark[0] if matching_dark else None

            ccd_calib(
                flat_set,
                matching_dark,
                camera_type=camera,
            )

            cal_flat_set = str(flat_set) + "/*_cal.fts"
            avg_fits(
                glob.glob(str(cal_flat_set)),
                mode=mode,
                pre_normalize=pre_normalize,
                outfile=calibration_set
                / (str(flat_set.name).replace("flats", "master_flat") + ".fts"),
            )

    logger.info("Calibration set reduction complete.")


reduce_calibration_set = reduce_calibration_set_cli.callback
