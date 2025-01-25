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
    """
    Platesolve images using the PinPoint solver in MaxIm DL.

    This script interacts with MaxIm DL's PinPoint solver via its COM interface
    to solve astronomical images for their World Coordinate System (`WCS`). The
    solved image is saved back to the original file if the process is successful.

    .. note::

        This script requires MaxIm DL to be installed on a Windows system. The PinPoint
        solver is accessed through MaxIm DL's COM interface.

    Parameters
    ----------
    `filepath` : `str`
        The path to the FITS file to solve. The file must exist.

    Returns
    -------
    `bool`
        `True` if the plate-solving process is successful, `False` otherwise.

    Raises
    ------
    `Exception`
        If the system is not Windows or if an unexpected error occurs during solving.

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
    
    maxim.Close
    return succeeded


maxim_pinpoint_wcs = maxim_pinpoint_wcs_cli.callback
