from astropy import wcs, units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits

def xy_to_radec(filename, x, y):
    """
    Given a filename with Astropy-compatible FITS headers, convert the specified
    (x, y) pixel position to a J2000 RA and Dec.

    Return a tuple containing (RA in hours, Dec in degrees)

    Raises an exception if there was a problem
    """
    try: 
        hdulist = fits.open(filename)
        w = wcs.WCS(hdulist[0].header)
        coord = w.pixel_to_world(x, y)
        
        return coord.ra.hour, coord.dec.deg
    except Exception as ex:
        raise Exception("Error calculating output '%s'" % ex)

def radec_to_xy(filename, ra_hours, dec_degs):
    """
    Given a filename with Talon-compatible FITS headers, convert the specified
    J2000 RA and Dec to an X,Y image pixel position.

    Return a tuple containing (x, y)

    Raises an exception if there was a problem
    """

    try: 
        hdulist = fits.open(filename)
        w = wcs.WCS(hdulist[0].header)
        coord = SkyCoord(ra_hours, dec_degs, unit=(u.hourangle, u.deg))
        pixels = w.world_to_pixel(coord)

        return float(pixels[0]), float(pixels[1])
    except Exception as ex:
        raise Exception("Error calculating output '%s'" % ex)