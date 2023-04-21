"""
Various conversion functions
"""

import math
import re

import ephem

_use_pyephem = False # Set by client code via use_pyephem() or use_novas()

def hours_to_rads(hours):
    return math.radians(hours*15)

def hours_to_degs(hours):
    return hours*15

def rads_to_hours(rads):
    return math.degrees(rads)/15.0

def rads_to_degs(rads):
    return math.degrees(rads)

def degs_to_hours(degs):
    return degs/15.0

def degs_to_rads(degs):
    return math.radians(degs)

def use_pyephem():
    """
    Force the PyEphem library to be used for precession/nutation
    """

    global _use_pyephem
    _use_pyephem = True

def use_novas():
    """
    Force the NOVAS library to be used for precession/nutation
    """

    global _use_pyephem
    _use_pyephem = False

def j2000_to_jnow(ra_j2000_hours, dec_j2000_degs):
    """
    Given J2000 coordinates (ra in hours, dec in degrees),
    return Jnow coordinates as a tuple:
      (ra_hours, dec_degs)
    """

    if _use_pyephem:
        return j2000_to_jnow_pyephem(ra_j2000_hours, dec_j2000_degs)
    else:
        return j2000_to_jnow_novas(ra_j2000_hours, dec_j2000_degs)

def jnow_to_j2000(ra_app_hours, dec_app_degs):
    """
    Given apparent (Jnow) coordinates (ra in hours, dec in degrees),
    return J2000 coordinates as a tuple:
      (ra_hours, dec_degs)
    """

    if _use_pyephem:
        return jnow_to_j2000_pyephem(ra_app_hours, dec_app_degs)
    else:
        return jnow_to_j2000_novas(ra_app_hours, dec_app_degs)


def j2000_to_jnow_pyephem(ra_j2000_hours, dec_j2000_degs):
    """
    Given J2000 coordinates (ra in hours, dec in degrees),
    return Jnow coordinates as a tuple:
      (ra_hours, dec_degs)
    
    Uses PyEphem to do the calculation
    """
    
    star = ephem.FixedBody()
    star._ra = hours_to_rads(ra_j2000_hours)
    star._dec = degs_to_rads(dec_j2000_degs)
    star.compute(epoch=ephem.now())
    # Changed .ra, .dec to .g_ra, .g_dec RLM 13 Dec 19 (ephem problem)
    return rads_to_hours(star.g_ra), rads_to_degs(star.g_dec)

def jnow_to_j2000_pyephem(ra_app_hours, dec_app_degs):
    """
    Given apparent (Jnow) coordinates (ra in hours, dec in degrees),
    return J2000 coordinates as a tuple:
      (ra_hours, dec_degs)
    
    Uses PyEphem to do the calculation
    """
    
    star = ephem.FixedBody()
    star._ra = hours_to_rads(ra_app_hours)
    star._dec = degs_to_rads(dec_app_degs)
    star._epoch = ephem.now()
    star.compute(when=ephem.J2000)
    return rads_to_hours(star.a_ra), rads_to_degs(star.a_dec)

def jnow_to_j2000_novas(ra_app_hours, dec_app_degs):
    """
    Given apparent (Jnow) coordinates (ra in hours, dec in degrees),
    return J2000 coordinates as a tuple:
      (ra_hours, dec_degs)
    
    Uses the NOVAS library to do the calculation.
    Requires that the ASCOM Platform 6 is installed, available from:
      http://ascom-standards.org/
    """

    from win32com.client import Dispatch # Import library only if function is called

    transform = Dispatch("ASCOM.Astrometry.Transform.Transform")
    transform.SetApparent(ra_app_hours, dec_app_degs)
    return (transform.RAJ2000, transform.DECJ2000)
    
def j2000_to_jnow_novas(ra_j2000_hours, dec_j2000_degs):
    """
    Given J2000 coordinates (ra in hours, dec in degrees),
    return Jnow coordinates as a tuple:
      (ra_hours, dec_degs)
    
    Uses the NOVAS library to do the calculation.
    Requires that the ASCOM Platform 6 is installed, available from:
      http://ascom-standards.org/
    """

    from win32com.client import Dispatch # Import library only if function is called
    
    transform = Dispatch("ASCOM.Astrometry.Transform.Transform")
    transform.SetJ2000(ra_j2000_hours, dec_j2000_degs)
    return (transform.RAApparent, transform.DECApparent)

def from_dms(dms_string):
    """
    Converts a string from sexagesimal format to a numeric value, in the same
    units as the major unit of the sexagesimal number (typically hours or degrees).
    The value can have one, two, or three fields representing hours/degrees, minutes,
    and seconds respectively. Fields can be separated by any consecutive number 
    of the following characters:
    
      :, _, d, h, m, s, or space
    
    This allows the following types of inputs (as examples):
      "3.5"
      "3 30.2"
      "3:40:55.6"
      "3h 22m 45s"
      "-20 30 40.5"
    """
    
    dms_string = str(dms_string) # So we can technically accept floats and ints as well

    SEPARATORS = ": _dhms"
    
    dms_string = dms_string.strip()
    
    sign = 1
    if dms_string.startswith("-"):
        sign = -1
        dms_string = dms_string[1:]
    
    separator_regex = '[' + SEPARATORS + ']+'  # One or more of any of the separator characters
    fields = re.split(separator_regex, dms_string)
    
    # In case of input like "3h30m" or "6d 10m 04.5s", split() will produce an empty
    # field following the final separator character. If one exists, strip it out.
    if fields[-1] == '':
        fields = fields[:-1]

    value = float(fields[0])
    if len(fields) > 1:
        value += float(fields[1]) / 60.0
    if len(fields) > 2:
        value += float(fields[2]) / 3600.0
    if len(fields) > 3:
        raise ValueError("Too many fields in sexagesimal number")
        
    return sign*value
    
    

def to_dms(value):
    """
    Convert a number to sexagesimal format (DD:MM:SS.ss).
    "dms" is a mnemonic for "degrees minutes seconds", but it will 
    maintain whatever units happen to be passed in (e.g. hours)
    """
    
    sign = ''
    if value < 0:
        sign = '-'
        value = -value
    
    degrees = int(value)
    value = (value-degrees)*60.0
    minutes = int(value)
    seconds = (value-minutes)*60.0
    
    seconds_str = "%05.2f" % seconds
    if seconds_str == "60.0":
        seconds_str = "00.0"
        minutes += 1
        
    if minutes == 60:
        minutes = 0
        degrees += 1    
    
    # Avoid situations like 9.99999999 -> "9:59:60.00"
    # i.e. where the seconds portion is >= 59.995 and would round up to 60
    # Truncate instead of rounding in this special case
    if seconds > 59.99:
        seconds = 59.99
    
    return "%s%02d:%02d:%05.2f" % (sign, degrees, minutes, seconds)

def miles_to_kilometers(miles):
    return miles*1.60934

def inches_hg_to_millibars(inches_hg):
    return inches_hg*33.8639

def fahrenheit_to_celsius(degs_f):
    return (degs_f-32)*5.0/9.0