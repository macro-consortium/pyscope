import logging
import os
import platform
import time

import click

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.option(
    "-f",
    "--filepath",
    type=click.Path(exists=True),
    help="""The path to the image file you want to solve.""",
)
@click.version_option()
def maxim_pinpoint_wcs_cli(filepath):
    """Platesolve images using the PinPoint solver in MaxIm DL.

    .. Note::
        This script requires MaxIm DL to be installed on your system, as it uses the PinPoint solver in MaxIm DL. \b

    Parameters
    ----------
    filepath : str

    Returns
    -------
    None
    """

    if type(filepath) is not str:
        filepath = str(filepath.resolve())

    if platform.system() != "Windows":
        raise Exception("MaxIm DL PinPoint is only available on Windows.")
    else:
        from win32com.client import Dispatch

    maxim = Dispatch("Maxim.Document")
    maxim.OpenFile(filepath)
    logger.info(f"Attempting to solve {filepath}")
    maxim.PinPointSolve()
    succeeded = False
    try:
        while maxim.PinPointStatus == 3:
            time.sleep(0.1)
        if maxim.PinPointStatus == 2:
            logger.info("Solve successful")
            succeeded = True
        else:
            logger.info("Solve failed")
            maxim.PinPointStop()
        maxim.SaveFile(filepath, 3, False, 1)
        c = maxim.Close()
        logger.info(f"Closed image: {c}")
    except Exception as e:
        logger.error(f"Solve failed: {e}, saving unsolved image")

    return succeeded


maxim_pinpoint_wcs = maxim_pinpoint_wcs_cli.callback
