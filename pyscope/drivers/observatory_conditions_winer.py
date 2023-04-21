import re
import urllib.request, urllib.parse, urllib.error

from . import relimport
from iotalib import convert
from iotalib.weather import WeatherReading

WINER_WEATHER_URL = "https://winer.org/Site/Weather.php"

def initialize():
    pass

def get_weather():
    reading = WeatherReading()

    stream = urllib.request.urlopen(WINER_WEATHER_URL)
    lines = stream.readlines()

    for line in lines:
        windspeed_mph = get_number_from_line(line, b"WINDSPEED", b"MPH", True)
        winddir_degs_eofn = get_number_from_line(line, b"WINDDIR", b"EofN", True)
        humidity_percent = get_number_from_line(line, b"HUMIDITY", b"%", True)
        pressure_inhg = get_number_from_line(line, b"PRESSURE", b"inHg", True)
        temperature_f = get_number_from_line(line, b"TEMPERATURE", b"F", True)
        last_update_msd = get_number_from_line(line, b"LASTUPDATED", None, True)

        if windspeed_mph is not None:
            reading.wind_speed_kph = convert.miles_to_kilometers(windspeed_mph)
        if winddir_degs_eofn is not None:
            reading.wind_direction_degs_east_of_north = winddir_degs_eofn
        if humidity_percent is not None:
            reading.humidity_percent = humidity_percent
        if pressure_inhg is not None:
            reading.pressure_millibars = convert.inches_hg_to_millibars(pressure_inhg)
        if temperature_f is not None:
            reading.temperature_celsius = convert.fahrenheit_to_celsius(temperature_f)
        if last_update_msd is not None:
            reading.timestamp_jd = last_update_msd

    return reading

def _arizona_msd_to_jd(msd):
    """
    The Winer webpage reports the LASTUPDATED value in a very strange way.
    It looks like a standard Julian day, but it actually something
    called a MONSOON star date, which seems to be like a JD, but expressed
    in local time rather than UTC and with half a day added to it (so that
    the integer part of the number increases at midnight local time).

    This function takes a MONSOON star date and converts it to a regular JD
    """

    offset_from_utc_hours = 7

    return msd - 0.5 + offset_from_utc_hours/24.0

def get_number_from_line(line, expected_keyword, expected_units, is_numeric):
    """
    Check to see if the provided line looks like a valid telemetry line
    from the Winer webpage. A typical line looks like this:
        <!-- TEMPERATURE=70.00 F -->

    If the line matches this format and the contents match expectations, return
    the extracted value from the line.

    line: the line text to inspect
    expected_keyword: the line must contain this keyword ("TEMPERATURE" in the example above)
    expected_units: the line must contain these units after the value ("F" in the example above).
        If this value is None, then units are not validated
    is_numeric: if True, the value is validated and converted to a float before being returned.
                if False, the string value is returned

    If the line does not match or there is a problem (e.g. converting the value to a float),
    the function returns None.

    Otherwise, the function returns the value, either as a float (if requested) or as a string
    """

    line = line.strip()
    if not line.startswith(b"<!--"):
        return None
    if not line.endswith(b"-->"):
        return None

    line = line[4:-3] # Strip off beginning and ending comment characters

    fields = line.split(b"=", 1) # Split into at most two fields (keyword and value)
    if len(fields) != 2:
        return None

    line_keyword = fields[0].strip()
    line_value_and_units = fields[1].strip()

    fields = line_value_and_units.split(b" ", 1)
    line_value = fields[0].strip()
    if len(fields) > 1:
        line_units = fields[1]
    else:
        line_units = ""

    if line_keyword != expected_keyword:
        return None
    if expected_units is not None and line_units != expected_units:
        return None
    if is_numeric:
        try:
            return float(line_value)
        except:
            return None
    else:
        return line_value