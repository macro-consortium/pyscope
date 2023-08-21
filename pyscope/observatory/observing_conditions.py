from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class ObservingConditions(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def Refresh(self):
        pass

    @abstractmethod
    def SensorDescription(self, PropertyName):
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
