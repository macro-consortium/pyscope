import logging
import urllib.request

from .observing_conditions import ObservingConditions

logger = logging.getLogger(__name__)


class HTMLObservingConditions(ObservingConditions):
    def __init__(
        self,
        url,
        cloud_cover_keyword=b"CLOUDCOVER",
        cloud_cover_units=b"%",
        cloud_cover_numeric=True,
        dew_point_keyword=b"DEWPOINT",
        dew_point_units=b"F",
        dew_point_numeric=True,
        humidity_keyword=b"HUMIDITY",
        humidity_units=b"%",
        humidity_numeric=True,
        pressure_keyword=b"PRESSURE",
        pressure_units=b"inHg",
        pressure_numeric=True,
        rain_rate_keyword=b"RAINRATE",
        rain_rate_units=b"inhr",
        rain_rate_numeric=True,
        sky_brightness_keyword=b"SKYBRIGHTNESS",
        sky_brightness_units="magdeg2",
        sky_brightness_numeric=True,
        sky_quality_keyword=b"SKYQUALITY",
        sky_quality_units="",
        sky_quality_numeric=True,
        sky_temperature_keyword=b"SKYTEMPERATURE",
        sky_temperature_units=b"F",
        sky_temperature_numeric=True,
        star_fwhm_keyword=b"STARFWHM",
        star_fwhm_units=b"arcsec",
        star_fwhm_numeric=True,
        temperature_keyword=b"TEMPERATURE",
        temperature_units=b"F",
        temperature_numeric=True,
        wind_direction_keyword=b"WINDDIRECTION",
        wind_direction_units=b"EofN",
        wind_direction_numeric=True,
        wind_gust_keyword=b"WINDGUST",
        wind_gust_units="mph",
        wind_gust_numeric=True,
        wind_speed_keyword=b"WINDSPEED",
        wind_speed_units="mph",
        wind_speed_numeric=True,
        last_updated_keyword=b"LASTUPDATED",
        last_updated_units="",
        last_updated_numeric=True,
    ):
        logger.debug(
            f"""HTMLObservingConditions.__init__(
                    {url},
                    cloud_cover_keyword={cloud_cover_keyword},
                    cloud_cover_units={cloud_cover_units},
                    cloud_cover_numeric={cloud_cover_numeric},
                    dew_point_keyword={dew_point_keyword},
                    dew_point_units={dew_point_units},
                    dew_point_numeric={dew_point_numeric},
                    humidity_keyword={humidity_keyword},
                    humidity_units={humidity_units},
                    humidity_numeric={humidity_numeric},
                    pressure_keyword={pressure_keyword},
                    pressure_units={pressure_units},
                    pressure_numeric={pressure_numeric},
                    rain_rate_keyword={rain_rate_keyword},
                    sky_brightness_keyword={sky_brightness_keyword},
                    sky_brightness_units={sky_brightness_units},
                    sky_brightness_numeric={sky_brightness_numeric},
                    sky_quality_keyword={sky_quality_keyword},
                    sky_quality_units={sky_quality_units},
                    sky_quality_numeric={sky_quality_numeric},
                    sky_temperature_keyword={sky_temperature_keyword},
                    sky_temperature_units={sky_temperature_units},
                    sky_temperature_numeric={sky_temperature_numeric},
                    star_fwhm_keyword={star_fwhm_keyword},
                    star_fwhm_units={star_fwhm_units},
                    star_fwhm_numeric={star_fwhm_numeric},
                    temperature_keyword={temperature_keyword},
                    temperature_units={temperature_units},
                    temperature_numeric={temperature_numeric},
                    wind_direction_keyword={wind_direction_keyword},
                    wind_direction_units={wind_direction_units},
                    wind_direction_numeric={wind_direction_numeric},
                    wind_gust_keyword={wind_gust_keyword},
                    wind_gust_units={wind_gust_units},
                    wind_gust_numeric={wind_gust_numeric},
                    wind_speed_keyword={wind_speed_keyword},
                    wind_speed_units={wind_speed_units},
                    wind_speed_numeric={wind_speed_numeric},
                    last_updated_keyword={last_updated_keyword},
                    last_updated_units={last_updated_units},
                    last_updated_numeric={last_updated_numeric}) called"""
        )

        self._url = url

        self._cloud_cover = None
        self._cloud_cover_keyword = cloud_cover_keyword
        self._cloud_cover_units = cloud_cover_units
        self._cloud_cover_numeric = cloud_cover_numeric
        self._dew_point = None
        self._dew_point_keyword = dew_point_keyword
        self._dew_point_units = dew_point_units
        self._dew_point_numeric = dew_point_numeric
        self._humidity = None
        self._humidity_keyword = humidity_keyword
        self._humidity_units = humidity_units
        self._humidity_numeric = humidity_numeric
        self._pressure = None
        self._pressure_keyword = pressure_keyword
        self._pressure_units = pressure_units
        self._pressure_numeric = pressure_numeric
        self._rain_rate = None
        self._rain_rate_keyword = rain_rate_keyword
        self._rain_rate_units = rain_rate_units
        self._rain_rate_numeric = rain_rate_numeric
        self._sky_brightness = None
        self._sky_brightness_keyword = sky_brightness_keyword
        self._sky_brightness_units = sky_brightness_units
        self._sky_brightness_numeric = sky_brightness_numeric
        self._sky_quality = None
        self._sky_quality_keyword = sky_quality_keyword
        self._sky_quality_units = sky_quality_units
        self._sky_quality_numeric = sky_quality_numeric
        self._sky_temperature = None
        self._sky_temperature_keyword = sky_temperature_keyword
        self._sky_temperature_units = sky_temperature_units
        self._sky_temperature_numeric = sky_temperature_numeric
        self._star_fwhm = None
        self._star_fwhm_keyword = star_fwhm_keyword
        self._star_fwhm_units = star_fwhm_units
        self._star_fwhm_numeric = star_fwhm_numeric
        self._temperature = None
        self._temperature_keyword = temperature_keyword
        self._temperature_units = temperature_units
        self._temperature_numeric = temperature_numeric
        self._wind_direction = None
        self._wind_direction_keyword = wind_direction_keyword
        self._wind_direction_units = wind_direction_units
        self._wind_direction_numeric = wind_direction_numeric
        self._wind_gust = None
        self._wind_gust_keyword = wind_gust_keyword
        self._wind_gust_units = wind_gust_units
        self._wind_gust_numeric = wind_gust_numeric
        self._wind_speed = None
        self._wind_speed_keyword = wind_speed_keyword
        self._wind_speed_units = wind_speed_units
        self._wind_speed_numeric = wind_speed_numeric
        self._last_updated = None
        self._last_updated_keyword = last_updated_keyword
        self._last_updated_units = last_updated_units
        self._last_updated_numeric = last_updated_numeric

        self.Refresh()

    def Refresh(self):
        logger.debug(f"HTMLObservingConditions.Refresh() called")
        stream = urllib.request.urlopen(self._url)
        lines = stream.readlines()

        for line in lines:
            cloud_cover = self._get_number_from_line(
                line,
                self._cloud_cover_keyword,
                self._cloud_cover_units,
                self._cloud_cover_numeric,
            )
            dew_point = self._get_number_from_line(
                line,
                self._dew_point_keyword,
                self._dew_point_units,
                self._dew_point_numeric,
            )
            humidity = self._get_number_from_line(
                line,
                self._humidity_keyword,
                self._humidity_units,
                self._humidity_numeric,
            )
            pressure = self._get_number_from_line(
                line,
                self._pressure_keyword,
                self._pressure_units,
                self._pressure_numeric,
            )
            rain_rate = self._get_number_from_line(
                line,
                self._rain_rate_keyword,
                self._rain_rate_units,
                self._rain_rate_numeric,
            )
            sky_brightness = self._get_number_from_line(
                line,
                self._sky_brightness_keyword,
                self._sky_brightness_units,
                self._sky_brightness_numeric,
            )
            sky_quality = self._get_number_from_line(
                line,
                self._sky_quality_keyword,
                self._sky_quality_units,
                self._sky_quality_numeric,
            )
            sky_temperature = self._get_number_from_line(
                line,
                self._sky_temperature_keyword,
                self._sky_temperature_units,
                self._sky_temperature_numeric,
            )
            star_fwhm = self._get_number_from_line(
                line,
                self._star_fwhm_keyword,
                self._star_fwhm_units,
                self._star_fwhm_numeric,
            )
            temperature = self._get_number_from_line(
                line,
                self._temperature_keyword,
                self._temperature_units,
                self._temperature_numeric,
            )
            wind_direction = self._get_number_from_line(
                line,
                self._wind_direction_keyword,
                self._wind_direction_units,
                self._wind_direction_numeric,
            )
            wind_gust = self._get_number_from_line(
                line,
                self._wind_gust_keyword,
                self._wind_gust_units,
                self._wind_gust_numeric,
            )
            wind_speed = self._get_number_from_line(
                line,
                self._wind_speed_keyword,
                self._wind_speed_units,
                self._wind_speed_numeric,
            )
            last_updated = self._get_number_from_line(
                line,
                self._last_updated_keyword,
                self._last_updated_units,
                self._last_updated_numeric,
            )

            if cloud_cover is not None:
                self._cloud_cover = cloud_cover
            if dew_point is not None:
                self._dew_point = dew_point
            if humidity is not None:
                self._humidity = humidity
            if pressure is not None:
                self._pressure = pressure
            if rain_rate is not None:
                self._rain_rate = rain_rate
            if sky_brightness is not None:
                self._sky_brightness = sky_brightness
            if sky_quality is not None:
                self._sky_quality = sky_quality
            if sky_temperature is not None:
                self._sky_temperature = sky_temperature
            if star_fwhm is not None:
                self._star_fwhm = star_fwhm
            if temperature is not None:
                self._temperature = temperature
            if wind_direction is not None:
                self._wind_direction = wind_direction
            if wind_gust is not None:
                self._wind_gust = wind_gust
            if wind_speed is not None:
                self._wind_speed = wind_speed
            if last_updated is not None:
                self._last_updated = last_updated

    def SensorDescription(self, PropertyName):
        logger.debug("HTMLObservingConditions.SensorDescription({PropertyName}) called")
        return eval(f"self._{PropertyName.lower()}_keyword")

    def TimeSinceLastUpdate(self, PropertyName):
        logger.debug(
            "HTMLObservingConditions.TimeSinceLastUpdate({PropertyName}) called"
        )
        stream = urllib.request.urlopen(self._url)
        lines = stream.readlines()

        for line in lines:
            last_updated = self._get_number_from_line(
                line,
                self._last_updated_keyword,
                self._last_updated_units,
                self._last_updated_numeric,
            )
            if last_updated is not None:
                self._last_updated = last_updated

        return self.LastUpdated

    @property
    def AveragePeriod(self):
        logger.debug("HTMLObservingConditions.AveragePeriod property called")
        return

    @AveragePeriod.setter
    def AveragePeriod(self, value):
        logger.debug(f"HTMLObservingConditions.AveragePeriod({value}) called")
        return

    @property
    def CloudCover(self):
        logger.debug("HTMLObservingConditions.CloudCover property called")
        return self._cloud_cover

    @property
    def DewPoint(self):
        logger.debug("HTMLObservingConditions.DewPoint property called")
        return self._dew_point

    @property
    def Humidity(self):
        logger.debug("HTMLObservingConditions.Humidity property called")
        return self._humidity

    @property
    def Pressure(self):
        logger.debug("HTMLObservingConditions.Pressure property called")
        return self._pressure

    @property
    def RainRate(self):
        logger.debug("HTMLObservingConditions.RainRate property called")
        return self._rain_rate

    @property
    def SkyBrightness(self):
        logger.debug("HTMLObservingConditions.SkyBrightness property called")
        return self._sky_brightness

    @property
    def SkyQuality(self):
        logger.debug("HTMLObservingConditions.SkyQuality property called")
        return self._sky_quality

    @property
    def SkyTemperature(self):
        logger.debug("HTMLObservingConditions.SkyTemperature property called")
        return self._sky_temperature

    @property
    def StarFWHM(self):
        logger.debug("HTMLObservingConditions.StarFWHM property called")
        return self._star_fwhm

    @property
    def Temperature(self):
        logger.debug("HTMLObservingConditions.Temperature property called")
        return self._temperature

    @property
    def WindDirection(self):
        logger.debug("HTMLObservingConditions.WindDirection property called")
        return self._wind_direction

    @property
    def WindGust(self):
        logger.debug("HTMLObservingConditions.WindGust property called")
        return self._wind_gust

    @property
    def WindSpeed(self):
        logger.debug("HTMLObservingConditions.WindSpeed property called")
        return self._wind_speed

    def _get_number_from_line(self, line, expected_keyword, expected_units, is_numeric):
        """
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
        """

        line = line.strip()
        if not line.startswith(b"<!--"):
            return None
        if not line.endswith(b"-->"):
            return None

        line = line[4:-3]  # Strip off beginning and ending comment characters

        fields = line.split(
            b"=", 1
        )  # Split into at most two fields (keyword and value)
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

    @property
    def LastUpdated(self):
        logger.debug("HTMLObservingConditions.LastUpdated property called")
        return self._last_updated
