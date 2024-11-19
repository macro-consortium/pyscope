from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class ObservingConditions(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for observing conditions.

        This class defines the interface for observing conditions, including methods
        for refreshing data, getting sensor descriptions, and checking time since last
        update for a given property, and properties for various environmental conditions.
        Subclasses must implement the abstract methods and properties in this class.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def Refresh(self):
        """Forces an immediate query to the hardware to refresh sensor values."""
        pass

    @abstractmethod
    def SensorDescription(self, PropertyName):
        """
        Provides the description of the sensor of the specified property. (`str`)

        The property whose name is supplied must be one of the properties specified
        in the `ObservingConditions` interface, else the method should throw an exception.

        Even if the driver to the sensor isn't connected, if the sensor itself is implemented, this method must
        return a valid string, for example in case an application wants to determine what sensors are available.
        
        Parameters
        ----------
        PropertyName : `str`
            The name of the property for which the sensor description is required.
        
        Returns
        -------
        `str`
            The sensor description.
        """
        pass

    @abstractmethod
    def TimeSinceLastUpdate(self, PropertyName):
        """
        Time since the sensor value was last updated. (`float`)

        The property whose name is supplied must be one of the properties specified in the `ObservingConditions` interface,
        else the method should throw an exception. There should be a return of a negative value if no valid value has
        ever been received from the hardware.
        The driver should return the time since the most recent value update of any sensor if an empty string is supplied.

        Parameters
        ----------
        PropertyName : `str`
            The name of the property for which time since last update is required.
        """
        pass

    @property
    @abstractmethod
    def AveragePeriod(self):
        """
        The time period over which observations will be averaged. (`float`)

        This is the time period in hours over which the driver will average sensor readings.
        If the driver delivers instantaneous values, then this value should be 0.0.
        """
        pass

    @AveragePeriod.setter
    @abstractmethod
    def AveragePeriod(self, value):
        pass

    @property
    @abstractmethod
    def CloudCover(self):
        """
        Amount of sky obscured by cloud. (`float`)

        Returns a value between 0 and 100 representing the percentage of the sky covered by cloud.
        """
        pass

    @property
    @abstractmethod
    def DewPoint(self):
        """
        Atmospheric dew point at the observatory. (`float`)

        Dew point given in degrees Celsius.
        """
        pass

    @property
    @abstractmethod
    def Humidity(self):
        """
        Atmospheric humidity at the observatory. (`float`)

        Humidity given as a percentage, ranging from no humidity at 0 to full humidity at 100.
        """
        pass

    @property
    @abstractmethod
    def Pressure(self):
        """
        Atmospheric pressure at the observatory. (`float`)

        Pressure in hectopascals (hPa), should be at the observatory altitude and not sea level altitude.
        If your pressure sensor measures sea level pressure, adjust to the observatory altitude before returning the value.
        """
        pass

    @property
    @abstractmethod
    def RainRate(self):
        """
        Rate of rain at the observatory. (`float`)

        Rain rate in millimeters per hour.
        Rainfall intensity is classified according to the rate of precipitation:
        - Light rain: 0.1 - 2.5 mm/hr
        - Moderate rain: 2.5 - 7.6 mm/hr
        - Heavy rain: 7.6 - 50 mm/hr
        - Violent rain: > 50 mm/hr
        """
        pass

    @property
    @abstractmethod
    def SkyBrightness(self):
        """
        Sky brightness at the observatory. (`float`)

        Sky brightness in Lux.
        For a scale of sky brightness, see `ASCOM <https://ascom-standards.org/Help/Developer/html/P_ASCOM_DriverAccess_ObservingConditions_SkyBrightness.htm>`_.
        """
        pass

    @property
    @abstractmethod
    def SkyQuality(self):
        """
        Sky quality at the observatory. (`float`)

        Sky quality in magnitudes per square arcsecond.
        """
        pass

    @property
    @abstractmethod
    def SkyTemperature(self):
        """
        Sky temperature at the observatory. (`float`)

        Sky temperature in degrees Celsius, expected to be read by an infra-red sensor pointing at the sky.
        Lower temperatures are indicative of clearer skies.
        """
        pass

    @property
    @abstractmethod
    def StarFWHM(self):
        """
        Seeing at the observatory. (`float`)

        Measured as the average star full width at half maximum (FWHM) in arcseconds within a star field.
        """
        pass

    @property
    @abstractmethod
    def Temperature(self):
        """
        Temperature at the observatory. (`float`)

        Ambient temperature at the observatory in degrees Celsius.
        """
        pass

    @property
    @abstractmethod
    def WindDirection(self):
        """
        Wind direction at the observatory. (`float`)

        Wind direction in degrees from North, increasing clockwise, where a value of 0.0 should be interpreted
        as wind speed being 0.0.
        """
        pass

    @property
    @abstractmethod
    def WindGust(self):
        """
        Peak 3 second wind gust at the observatory over the last 2 minutes. (`float`)

        Wind gust in meters per second.
        """
        pass

    @property
    @abstractmethod
    def WindSpeed(self):
        """
        Wind speed at the observatory. (`float`)

        Wind speed in meters per second.
        """
        pass
