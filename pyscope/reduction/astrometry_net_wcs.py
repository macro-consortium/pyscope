import logging
import os

import click
from astropy.io import fits

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.argument("filepath", type=click.Path(exists=True))
@click.version_option()
def astrometry_net_wcs_cli(filepath, **kwargs):
    """Platesolve images using the Astrometry.net solver. Requires an input filepath. \f

    Keyword arguments are passed to `~astroquery.astrometry_net.AstrometryNet.solve_from_image()`.

    """

    from astroquery.astrometry_net import AstrometryNet

    solver = AstrometryNet()

    try_again = True
    submission_id = None
    while try_again:
        try:
            if not submission_id:
                wcs_header = solver.solve_from_image(
                    filepath, verbose=True, return_submission_id=True, **kwargs
                )
            else:
                wcs_header = solver.monitor_submission(
                    submission_id, verbose=True, return_submission_id=True, **kwargs
                )
        except TimeoutError as e:
            submission_id = e.args[1]
        else:
            try_again = False

    logger.info("Submission ID = %s" % wcs_header[1])

    if wcs_header is not None:
        if wcs_header[0] != {}:
            with fits.open(filepath, mode="update") as hdul:
                hdul[0].header.update(wcs_header[0])
                del hdul[0].header["COMMENT"]
            return True
        else:
            return False
    else:
        return False


astrometry_net_wcs = astrometry_net_wcs_cli.callback
