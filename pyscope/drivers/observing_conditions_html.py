import re
import urllib.request

from . import abstract

class ObservingConditionsHTML(abstract.ObservingConditions):
    def __init__(self, *args, **kwargs):

        self.url = args[0] if len(args) > 0 else kwargs['url']

        self._cloud_cover = None
        self._cloud_cover_keyword = kwargs.get('cloud_cover_keyword', b'CLOUDCOVER')
        self._cloud_cover_units = kwargs.get('cloud_cover_units', b'%')
        self._cloud_cover_numeric = kwargs.get('cloud_cover_numeric', True)
        self._dew_point = None
        self._dew_point_keyword = kwargs.get('dew_point_keyword', b'DEWPOINT')
        self._dew_point_units = kwargs.get('dew_point_units', None)
        self._dew_point_numeric = kwargs.get('dew_point_numeric', True)
        self._humidity = None
        self._humidity_keyword = kwargs.get('humidity_keyword', b'HUMIDITY')
        self._humidity_units = kwargs.get('humidity_units', b'%')
        self._humidity_numeric = kwargs.get('humidity_numeric', True)
        self._pressure = None
        self._pressure_keyword = kwargs.get('pressure_keyword', b'PRESSURE')
        self._pressure_units = kwargs.get('pressure_units', b'inHg')
        self._pressure_numeric = kwargs.get('pressure_numeric', True)
        self._rain_rate = None
        self._rain_rate_keyword = kwargs.get('rain_rate_keyword', b'RAINRATE')
        self._rain_rate_units = kwargs.get('rain_rate_units', None)
        self._rain_rate_numeric = kwargs.get('rain_rate_numeric', True)
        self._sky_brightness = None
        self._sky_brightness_keyword = kwargs.get('sky_brightness_keyword', b'SKYBRIGHTNESS')
        self._sky_brightness_units = kwargs.get('sky_brightness_units', None)
        self._sky_brightness_numeric = kwargs.get('sky_brightness_numeric', True)
        self._sky_quality = None
        self._sky_quality_keyword = kwargs.get('sky_quality_keyword', b'SKYQUALITY')
        self._sky_quality_units = kwargs.get('sky_quality_units', None)
        self._sky_quality_numeric = kwargs.get('sky_quality_numeric', True)
        self._sky_temperature = None
        self._sky_temperature_keyword = kwargs.get('sky_temperature_keyword', b'SKYTEMPERATURE')
        self._sky_temperature_units = kwargs.get('sky_temperature_units', 'C')
        self._sky_temperature_numeric = kwargs.get('sky_temperature_numeric', True)
        self._star_fwhm = None
        self._star_fwhm_keyword = kwargs.get('star_fwhm_keyword', b'STARFWHM')
        self._star_fwhm_units = kwargs.get('star_fwhm_units', None)
        self._star_fwhm_numeric = kwargs.get('star_fwhm_numeric', True)
        self._temperature = None
        self._temperature_keyword = kwargs.get('temperature_keyword', b'TEMPERATURE')
        self._temperature_units = kwargs.get('temperature_units', None)
        self._temperature_numeric = kwargs.get('temperature_numeric', True)
        self._wind_direction = None
        self._wind_direction_keyword = kwargs.get('wind_direction_keyword', b'WINDDIRECTION')
        self._wind_direction_units = kwargs.get('wind_direction_units', None)
        self._wind_direction_numeric = kwargs.get('wind_direction_numeric', True)
        self._wind_gust = None
        self._wind_gust_keyword = kwargs.get('wind_gust_keyword', b'WINDGUST')
        self._wind_gust_units = kwargs.get('wind_gust_units', None)
        self._wind_gust_numeric = kwargs.get('wind_gust_numeric', True)
        self._wind_speed = None
        self._wind_speed_keyword = kwargs.get('wind_speed_keyword', b'WINDSPEED')
        self._wind_speed_units = kwargs.get('wind_speed_units', None)
        self._wind_speed_numeric = kwargs.get('wind_speed_numeric', True)
        self._last_updated = None
        self._last_updated_keyword = kwargs.get('last_updated_keyword', b'LASTUPDATED')
        self._last_updated_units = kwargs.get('last_updated_units', None)
        self._last_updated_numeric = kwargs.get('last_updated_numeric', True)

        self.Refresh()
    
    def Refresh(self):
        stream = urllib.request.urlopen(self.url)
        lines = stream.readlines()

        for line in lines:
            cloud_cover = self._get_number_from_line(line, self._cloud_cover_keyword, self._cloud_cover_units, self._cloud_cover_numeric)
            dew_point = self._get_number_from_line(line, self._dew_point_keyword, self._dew_point_units, self._dew_point_numeric)
            humidity = self._get_number_from_line(line, self._humidity_keyword, self._humidity_units, self._humidity_numeric)
            pressure = self._get_number_from_line(line, self._pressure_keyword, self._pressure_units, self._pressure_numeric)
            rain_rate = self._get_number_from_line(line, self._rain_rate_keyword, self._rain_rate_units, self._rain_rate_numeric)
            sky_brightness = self._get_number_from_line(line, self._sky_brightness_keyword, self._sky_brightness_units, self._sky_brightness_numeric)
            sky_quality = self._get_number_from_line(line, self._sky_quality_keyword, self._sky_quality_units, self._sky_quality_numeric)
            sky_temperature = self._get_number_from_line(line, self._sky_temperature_keyword, self._sky_temperature_units, self._sky_temperature_numeric)
            star_fwhm = self._get_number_from_line(line, self._star_fwhm_keyword, self._star_fwhm_units, self._star_fwhm_numeric)
            temperature = self._get_number_from_line(line, self._temperature_keyword, self._temperature_units, self._temperature_numeric)
            wind_direction = self._get_number_from_line(line, self._wind_direction_keyword, self._wind_direction_units, self._wind_direction_numeric)
            wind_gust = self._get_number_from_line(line, self._wind_gust_keyword, self._wind_gust_units, self._wind_gust_numeric)
            wind_speed = self._get_number_from_line(line, self._wind_speed_keyword, self._wind_speed_units, self._wind_speed_numeric)
            last_updated = self._get_number_from_line(line, self._last_updated_keyword, self._last_updated_units, self._last_updated_numeric)

            if cloud_cover is not None: self._cloud_cover = cloud_cover
            if dew_point is not None: self._dew_point = dew_point
            if humidity is not None: self._humidity = humidity
            if pressure is not None: self._pressure = pressure
            if rain_rate is not None: self._rain_rate = rain_rate
            if sky_brightness is not None: self._sky_brightness = sky_brightness
            if sky_quality is not None: self._sky_quality = sky_quality
            if sky_temperature is not None: self._sky_temperature = sky_temperature
            if star_fwhm is not None: self._star_fwhm = star_fwhm
            if temperature is not None: self._temperature = temperature
            if wind_direction is not None: self._wind_direction = wind_direction
            if wind_gust is not None: self._wind_gust = wind_gust
            if wind_speed is not None: self._wind_speed = wind_speed
            if last_updated is not None: self._last_updated = last_updated

    def SensorDescription(self, PropertyName):
        return abstract.exceptions.MethodNotImplemented()

    def TimeSinceLastUpdate(self, PropertyName):
        stream = urllib.request.urlopen(self.url)
        lines = stream.readlines()

        for line in lines:
            self._last_updated = _get_number_from_line(line, b'LASTUPDATED', b'None', False)
        
        return self.LastUpdated
    
    @property
    def AveragePeriod(self):
        return abstract.exceptions.PropertyNotImplemented()
    @AveragePeriod.setter
    def AveragePeriod(self, value):
        return abstract.exceptions.PropertyNotImplemented()
    
    @property
    def CloudCover(self):
        return self._cloud_cover
    
    @property
    def DewPoint(self):
        return self._dew_point
    
    @property
    def Humidity(self):
        return self._humidity
    
    @property
    def Pressure(self):
        return self._pressure
    
    @property
    def RainRate(self):
        return self._rain_rate

    @property
    def SkyBrightness(self):
        return self._sky_brightness
    
    @property
    def SkyQuality(self):
        return self._sky_quality
    
    @property
    def SkyTemperature(self):
        return self._sky_temperature
    
    @property
    def StarFWHM(self):
        return self._star_fwhm
    
    @property
    def Temperature(self):
        return self._temperature
    
    @property
    def WindDirection(self):
        return self._wind_direction
    
    @property
    def WindGust(self):
        return self._wind_gust
    
    @property
    def WindSpeed(self):
        return self._wind_speed

    def _get_number_from_line(self, line, expected_keyword, expected_units, is_numeric):
        '''
        Check to see if the provided line looks like a valid telemetry line
        from the Winer webpage. A typical line looks like this:
            <!-- TEMPERATURE=7None0 F -->

        If the line matches this format and the contents match expectations, return
        the extracted value from the line.

        line: the line text to inspect
        expected_keyword: the line must contain this keyword ('TEMPERATURE' in the example above)
        expected_units: the line must contain these units after the value ('F' in the example above).
            If this value is None, then units are not validated
        is_numeric: if True, the value is validated and converted to a float before being returned.
                    if False, the string value is returned

        If the line does not match or there is a problem (e.g. converting the value to a float),
        the function returns None.

        Otherwise, the function returns the value, either as a float (if requested) or as a string
        '''

        line = line.strip()
        if not line.startswith(b'<!--'):
            return None
        if not line.endswith(b'-->'):
            return None

        line = line[4:-3] # Strip off beginning and ending comment characters

        fields = line.split(b'=', 1) # Split into at most two fields (keyword and value)
        if len(fields) != 2:
            return None

        line_keyword = fields[0].strip()
        line_value_and_units = fields[1].strip()

        fields = line_value_and_units.split(b' ', 1)
        line_value = fields[0].strip()
        if len(fields) > 1:
            line_units = fields[1]
        else:
            line_units = ''

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
    
    @property
    def LastUpdated(self):
        return self._last_updated