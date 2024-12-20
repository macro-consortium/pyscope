import logging
import urllib.request

from ..utils import _get_number_from_line
from .observing_conditions import ObservingConditions

logger = logging.getLogger(__name__)


class HTMLObservingConditions(ObservingConditions):
    def __init__(
        self,
        url,
        cloud_cover_keyword="CLOUDCOVER",
        cloud_cover_units="%",
        cloud_cover_numeric=True,
        dew_point_keyword="DEWPOINT",
        dew_point_units="F",
        dew_point_numeric=True,
        humidity_keyword="HUMIDITY",
        humidity_units="%",
        humidity_numeric=True,
        pressure_keyword="PRESSURE",
        pressure_units="inHg",
        pressure_numeric=True,
        rain_rate_keyword="RAINRATE",
        rain_rate_units="inhr",
        rain_rate_numeric=True,
        sky_brightness_keyword="SKYBRIGHTNESS",
        sky_brightness_units="magdeg2",
        sky_brightness_numeric=True,
        sky_quality_keyword="SKYQUALITY",
        sky_quality_units="",
        sky_quality_numeric=True,
        sky_temperature_keyword="SKYTEMPERATURE",
        sky_temperature_units="F",
        sky_temperature_numeric=True,
        star_fwhm_keyword="STARFWHM",
        star_fwhm_units="arcsec",
        star_fwhm_numeric=True,
        temperature_keyword="TEMPERATURE",
        temperature_units="F",
        temperature_numeric=True,
        wind_direction_keyword="WINDDIRECTION",
        wind_direction_units="EofN",
        wind_direction_numeric=True,
        wind_gust_keyword="WINDGUST",
        wind_gust_units="mph",
        wind_gust_numeric=True,
        wind_speed_keyword="WINDSPEED",
        wind_speed_units="mph",
        wind_speed_numeric=True,
        last_updated_keyword="LASTUPDATED",
        last_updated_units="",
        last_updated_numeric=True,
    ):
        """
        This class provides an interface to gathering observing condition data via HTML.

        The class is designed to be used with an HTML page that contains observing conditions data,
        sensor descriptions, and time since last update.
        
        Parameters
        ----------
        url : `str`
            The URL of the HTML page that contains the observing conditions data.
        cloud_cover_keyword : `str`, default : "CLOUDCOVER", optional
            The keyword that identifies the cloud cover data.
        cloud_cover_units : `str`, default : "%", optional
            The units of the cloud cover data.
        cloud_cover_numeric : `bool`, default : `True`, optional
            Whether the cloud cover data is numeric.
        dew_point_keyword : `str`, default : "DEWPOINT", optional
            The keyword that identifies the dew point data.
        dew_point_units : `str`, default : "F", optional
            The units of the dew point data.
        dew_point_numeric : `bool`, default : `True`, optional
            Whether the dew point data is numeric.
        humidity_keyword : `str`, default : "HUMIDITY", optional
            The keyword that identifies the humidity data.
        humidity_units : `str`, default : "%", optional
            The units of the humidity data.
        humidity_numeric : `bool`, default : `True`, optional
            Whether the humidity data is numeric.
        pressure_keyword : `str`, default : "PRESSURE", optional
            The keyword that identifies the pressure data.
        pressure_units : `str`, default : "inHg", optional
            The units of the pressure data.
        pressure_numeric : `bool`, default : `True`, optional
            Whether the pressure data is numeric.
        rain_rate_keyword : `str`, default : "RAINRATE", optional
            The keyword that identifies the rain rate data.
        rain_rate_units : `str`, default : "inhr", optional
            The units of the rain rate data.
        rain_rate_numeric : `bool`, default : `True`, optional
            Whether the rain rate data is numeric.
        sky_brightness_keyword : `str`, default : "SKYBRIGHTNESS", optional
            The keyword that identifies the sky brightness data.
        sky_brightness_units : `str`, default : "magdeg2", optional
            The units of the sky brightness data.
        sky_brightness_numeric : `bool`, default : `True`, optional
            Whether the sky brightness data is numeric.
        sky_quality_keyword : `str`, default : "SKYQUALITY", optional
            The keyword that identifies the sky quality data.
        sky_quality_units : `str`, default : "", optional
            The units of the sky quality data.
        sky_quality_numeric : `bool`, default : `True`, optional
            Whether the sky quality data is numeric.
        sky_temperature_keyword : `str`, default : "SKYTEMPERATURE", optional
            The keyword that identifies the sky temperature data.
        sky_temperature_units : `str`, default : "F", optional
            The units of the sky temperature data.
        sky_temperature_numeric : `bool`, default : `True`, optional
            Whether the sky temperature data is numeric.
        star_fwhm_keyword : `str`, default : "STARFWHM", optional
            The keyword that identifies the star FWHM data.
        star_fwhm_units : `str`, default : "arcsec", optional
            The units of the star FWHM data.
        star_fwhm_numeric : `bool`, default : `True`, optional
            Whether the star FWHM data is numeric.
        temperature_keyword : `str`, default : "TEMPERATURE", optional
            The keyword that identifies the temperature data.
        temperature_units : `str`, default : "F", optional
            The units of the temperature data.
        temperature_numeric : `bool`, default : `True`, optional
            Whether the temperature data is numeric.
        wind_direction_keyword : `str`, default : "WINDDIRECTION", optional
            The keyword that identifies the wind direction data.
        wind_direction_units : `str`, default : "EofN", optional
            The units of the wind direction data.
        wind_direction_numeric : `bool`, default : `True`, optional
            Whether the wind direction data is numeric.
        wind_gust_keyword : `str`, default : "WINDGUST", optional
            The keyword that identifies the wind gust data.
        wind_gust_units : `str`, default : "mph", optional
            The units of the wind gust data.
        wind_gust_numeric : `bool`, default : `True`, optional
            Whether the wind gust data is numeric.
        wind_speed_keyword : `str`, default : "WINDSPEED", optional
            The keyword that identifies the wind speed data.
        wind_speed_units : `str`, default : "mph", optional
            The units of the wind speed data.
        wind_speed_numeric : `bool`, default : `True`, optional
            Whether the wind speed data is numeric.
        last_updated_keyword : `str`, default : "LASTUPDATED", optional
            The keyword that identifies the last updated data.
        last_updated_units : `str`, default : "", optional
            The units of the last updated data.
        last_updated_numeric : `bool`, default : `True`, optional
            Whether the last updated data is numeric.
        """
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
            cloud_cover = _get_number_from_line(
                line,
                self._cloud_cover_keyword,
                self._cloud_cover_units,
                self._cloud_cover_numeric,
            )
            dew_point = _get_number_from_line(
                line,
                self._dew_point_keyword,
                self._dew_point_units,
                self._dew_point_numeric,
            )
            humidity = _get_number_from_line(
                line,
                self._humidity_keyword,
                self._humidity_units,
                self._humidity_numeric,
            )
            pressure = _get_number_from_line(
                line,
                self._pressure_keyword,
                self._pressure_units,
                self._pressure_numeric,
            )
            rain_rate = _get_number_from_line(
                line,
                self._rain_rate_keyword,
                self._rain_rate_units,
                self._rain_rate_numeric,
            )
            sky_brightness = _get_number_from_line(
                line,
                self._sky_brightness_keyword,
                self._sky_brightness_units,
                self._sky_brightness_numeric,
            )
            sky_quality = _get_number_from_line(
                line,
                self._sky_quality_keyword,
                self._sky_quality_units,
                self._sky_quality_numeric,
            )
            sky_temperature = _get_number_from_line(
                line,
                self._sky_temperature_keyword,
                self._sky_temperature_units,
                self._sky_temperature_numeric,
            )
            star_fwhm = _get_number_from_line(
                line,
                self._star_fwhm_keyword,
                self._star_fwhm_units,
                self._star_fwhm_numeric,
            )
            temperature = _get_number_from_line(
                line,
                self._temperature_keyword,
                self._temperature_units,
                self._temperature_numeric,
            )
            wind_direction = _get_number_from_line(
                line,
                self._wind_direction_keyword,
                self._wind_direction_units,
                self._wind_direction_numeric,
            )
            wind_gust = _get_number_from_line(
                line,
                self._wind_gust_keyword,
                self._wind_gust_units,
                self._wind_gust_numeric,
            )
            wind_speed = _get_number_from_line(
                line,
                self._wind_speed_keyword,
                self._wind_speed_units,
                self._wind_speed_numeric,
            )
            last_updated = _get_number_from_line(
                line,
                self._last_updated_keyword,
                self._last_updated_units,
                self._last_updated_numeric,
            )

            if cloud_cover is not None:  # pragma: no cover
                self._cloud_cover = cloud_cover
            if dew_point is not None:  # pragma: no cover
                self._dew_point = dew_point
            if humidity is not None:  # pragma: no cover
                self._humidity = humidity
            if pressure is not None:  # pragma: no cover
                self._pressure = pressure
            if rain_rate is not None:  # pragma: no cover
                self._rain_rate = rain_rate
            if sky_brightness is not None:  # pragma: no cover
                self._sky_brightness = sky_brightness
            if sky_quality is not None:  # pragma: no cover
                self._sky_quality = sky_quality
            if sky_temperature is not None:  # pragma: no cover
                self._sky_temperature = sky_temperature
            if star_fwhm is not None:  # pragma: no cover
                self._star_fwhm = star_fwhm
            if temperature is not None:  # pragma: no cover
                self._temperature = temperature
            if wind_direction is not None:  # pragma: no cover
                self._wind_direction = wind_direction
            if wind_gust is not None:  # pragma: no cover
                self._wind_gust = wind_gust
            if wind_speed is not None:  # pragma: no cover
                self._wind_speed = wind_speed
            if last_updated is not None:  # pragma: no cover
                self._last_updated = last_updated

    def SensorDescription(self, PropertyName):
        logger.debug("HTMLObservingConditions.SensorDescription({PropertyName}) called")
        return str(eval(f"self._{PropertyName.lower()}_keyword"))

    def TimeSinceLastUpdate(self, PropertyName):
        logger.debug(
            "HTMLObservingConditions.TimeSinceLastUpdate({PropertyName}) called"
        )
        stream = urllib.request.urlopen(self._url)
        lines = stream.readlines()

        for line in lines:
            last_updated = _get_number_from_line(
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
    def Description(self):
        """Description of the driver. (`str`)"""
        logger.debug("HTMLObservingConditions.Description property called")
        return "HTML Observing Conditions Driver"

    @property
    def DriverVersion(self):
        """Version of the driver. (`str`)"""
        logger.debug("HTMLObservingConditions.DriverVersion property called")
        return None

    @property
    def DriverInfo(self):
        """Provides information about the driver. (`str`)"""
        logger.debug("HTMLObservingConditions.DriverInfo property called")
        return "HTML Observing Conditions Driver"

    @property
    def DewPoint(self):
        logger.debug("HTMLObservingConditions.DewPoint property called")
        return self._dew_point

    @property
    def Humidity(self):
        logger.debug("HTMLObservingConditions.Humidity property called")
        return self._humidity

    @property
    def InterfaceVersion(self):
        """Version of the interface supported by the driver. (`int`)"""
        logger.debug("HTMLObservingConditions.InterfaceVersion property called")
        return 1

    @property
    def Name(self):
        """Name/url of the driver. (`str`)"""
        logger.debug("HTMLObservingConditions.Name property called")
        return self._url

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

    @property
    def LastUpdated(self):
        """Time of last update of conditions. (`str`)"""
        logger.debug("HTMLObservingConditions.LastUpdated property called")
        return self._last_updated
