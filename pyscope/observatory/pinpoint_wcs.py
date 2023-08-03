import time
import platform

from ..utils import _force_async
from .wcs import WCS

class PinpointWCS(WCS):
    def __init__(self):
        if platform.system() != 'Windows':
            raise Exception('PinPoint is only available on Windows.')
        else:
            from win32com.client import Dispatch
            self._solver = Dispatch('PinPoint.Plate')

    def Solve(self, filepath, scale_est, ra_key='RA', dec_key='DEC',
                ra=None, dec=None, ra_dec_units=('hour', 'deg'), 
                solve_timeout=60, catalog=3, 
                catalog_path='C:\GSC-1.1'):

        self._solver.AttachFITS(filepath)

        if kwargs.get('ra', None) is None or kwargs.get('dec', None) is None:
            with pyfits.open(filepath) as hdul:
                ra = hdul[0].header[ra_key]
                dec = hdul[0].header[dec_key]
        else:
            ra = kwargs.get('ra', self._solver.TargetRightAscension)
            dec = kwargs.get('dec', self._solver.TargetDeclination)

        obj = coord.SkyCoord(ra, dec, unit=ra_dec_units, frame='icrs')
        self._solver.RightAscension = obj.ra.hour
        self._solver.Declination = obj.dec.deg

        self._solver.ArcsecPerPixelHoriz = scale_est
        self._solver.ArcsecPerPixelVert = scale_est
        self.Catalog = catalog
        self.CatalogPath = catalog_path

        solved = None
        solved = self._async_solve()
        start_solve = time.time()
        while time.time() - start_solve < solve_timeout and solved is None:
            time.sleep(1)
        else:
            if solved is None:
                raise Exception('Pinpoint solve timed out.')
            else:
                return solved

        self._solver.UpdateFITS()
        self._solver.DetachFITS()
        return True
    
    @_force_async
    def _async_solve(self):
        self.Solver.Solve()