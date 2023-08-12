from .wcs import WCS

import os
import astropy.io.fits as pyfits
from astroquery.astrometry_net import AstrometryNet
import logging

logger = logging.getLogger(__name__)

class AstrometryNetWCS(WCS):
    def __init__(self):
        logger.debug(f"AstrometryNetWCS.__init__() called")
        self._solver = AstrometryNet()
    
    def Solve(self, filepath, **kwargs):
        logger.debug(f"AstrometryNetWCS.Solve({filepath}, {kwargs}) called")

        try_again = True
        submission_id = None
        while try_again:
            try:
                if not submission_id:
                    wcs_header = self._solver.solve_from_image(filepath, submission_id=submission_id, **kwargs)
                else:
                    wcs_header = self._solver.monitor_submission(submission_id, solve_timeout=kwargs.get('solve_timeout', 120))
            except TimeoutError as e:
                submission_id = e.args[1]
            else:
                try_again = False

        if wcs_header:
            with pyfits.open(filepath, mode='update') as hdul:
                hdul[0].header.update(wcs_header)
                return True
        else:
            return False