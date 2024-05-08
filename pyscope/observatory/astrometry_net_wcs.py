import logging
import os

from astropy.io import fits

from .wcs import WCS

logger = logging.getLogger(__name__)


class AstrometryNetWCS(WCS):
    def __init__(self):
        logger.debug(f"AstrometryNetWCS.__init__() called")

        # Avoid documentation build failure by importing here
        from astroquery.astrometry_net import AstrometryNet

        self._solver = AstrometryNet()

    def Solve(self, filepath, **kwargs):
        logger.debug(f"AstrometryNetWCS.Solve({filepath}, {kwargs}) called")

        try_again = True
        submission_id = None
        while try_again:
            try:
                if not submission_id:
                    wcs_header = self._solver.solve_from_image(
                        filepath,
                        submission_id=submission_id,
                        verbose=True,
                        return_submission_id=True,
                        force_image_upload=True,
                        solve_timeout=300,
                        # **kwargs
                    )
                else:
                    wcs_header = self._solver.monitor_submission(
                        submission_id,
                        solve_timeout=300,
                        verbose=True,
                        return_submission_id=True,
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
