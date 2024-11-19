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
        pass

    @property
    @abstractmethod
    def AveragePeriod(self):
        pass

    @AveragePeriod.setter
    @abstractmethod
    def AveragePeriod(self, value):
        pass

    @property
    @abstractmethod
    def CloudCover(self):
        pass

    @property
    @abstractmethod
    def DewPoint(self):
        pass

    @property
    @abstractmethod
    def Humidity(self):
        pass

    @property
    @abstractmethod
    def Pressure(self):
        pass

    @property
    @abstractmethod
    def RainRate(self):
        pass

    @property
    @abstractmethod
    def SkyBrightness(self):
        pass

    @property
    @abstractmethod
    def SkyQuality(self):
        pass

    @property
    @abstractmethod
    def SkyTemperature(self):
        pass

    @property
    @abstractmethod
    def StarFWHM(self):
        pass

    @property
    @abstractmethod
    def Temperature(self):
        pass

    @property
    @abstractmethod
    def WindDirection(self):
        pass

    @property
    @abstractmethod
    def WindGust(self):
        pass

    @property
    @abstractmethod
    def WindSpeed(self):
        pass
