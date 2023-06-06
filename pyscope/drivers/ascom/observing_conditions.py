from .driver import Driver
from .. import abstract

class ObservingConditions(Driver, abstract.ObservingConditions):
    def Choose(self, ObservingConditionsID):
        self._com_object.Choose(ObservingConditionsID)
    
    def Refresh(self):
        self._com_object.Refresh()
    
    def SensorDescription(self, PropertyName):
        return self._com_object.SensorDescription(PropertyName)

    def TimeSinceLastUpdate(self, PropertyName):
        return self._com_object.TimeSinceLastUpdate(PropertyName)
    
    @property
    def AveragePeriod(self):
        return self._com_object.AveragePeriod
    @AveragePeriod.setter
    def AveragePeriod(self, value):
        self._com_object.AveragePeriod = value
    
    @property
    def CloudCover(self):
        return self._com_object.CloudCover
    
    @property
    def DewPoint(self):
        return self._com_object.DewPoint
    
    @property
    def Humidity(self):
        return self._com_object.Humidity
    
    @property
    def Pressure(self):
        return self._com_object.Pressure

    @property
    def RainRate(self):
        return self._com_object.RainRate
    
    @property
    def SkyBrightness(self):
        return self._com_object.SkyBrightness

    @property
    def SkyQuality(self):
        return self._com_object.SkyQuality

    @property
    def SkyTemperature(self):
        return self._com_object.SkyTemperature
    
    @property
    def StarFWHM(self):
        return self._com_object.StarFWHM
    
    @property
    def Temperature(self):
        return self._com_object.Temperature
    
    @property
    def WindDirection(self):
        return self._com_object.WindDirection
    
    @property
    def WindGust(self):
        return self._com_object.WindGust

    @property
    def WindSpeed(self):
        return self._com_object.WindSpeed