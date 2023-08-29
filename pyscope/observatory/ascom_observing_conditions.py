import logging

from .ascom_device import ASCOMDevice
from .observing_conditions import ObservingConditions

logger = logging.getLogger(__name__)


class ASCOMObservingConditions(ASCOMDevice, ObservingConditions):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def Choose(self, ObservingConditionsID):
        logger.debug(f"ASCOMObservingConditions.Choose({ObservingConditionsID}) called")
        self._com_object.Choose(ObservingConditionsID)

    def Refresh(self):
        logger.debug("ASCOMObservingConditions.Refresh() called")
        self._com_object.Refresh()

    def SensorDescription(self, PropertyName):
        logger.debug(
            f"ASCOMObservingConditions.SensorDescription({PropertyName}) called"
        )
        return self._com_object.SensorDescription(PropertyName)

    def TimeSinceLastUpdate(self, PropertyName):
        logger.debug(
            f"ASCOMObservingConditions.TimeSinceLastUpdate({PropertyName}) called"
        )
        return self._com_object.TimeSinceLastUpdate(PropertyName)

    @property
    def AveragePeriod(self):
        logger.debug("ASCOMObservingConditions.AveragePeriod property called")
        return self._com_object.AveragePeriod

    @AveragePeriod.setter
    def AveragePeriod(self, value):
        logger.debug(f"ASCOMObservingConditions.AveragePeriod property set to {value}")
        self._com_object.AveragePeriod = value

    @property
    def CloudCover(self):
        logger.debug("ASCOMObservingConditions.CloudCover property called")
        return self._com_object.CloudCover

    @property
    def DewPoint(self):
        logger.debug("ASCOMObservingConditions.DewPoint property called")
        return self._com_object.DewPoint

    @property
    def Humidity(self):
        logger.debug("ASCOMObservingConditions.Humidity property called")
        return self._com_object.Humidity

    @property
    def Pressure(self):
        logger.debug("ASCOMObservingConditions.Pressure property called")
        return self._com_object.Pressure

    @property
    def RainRate(self):
        logger.debug("ASCOMObservingConditions.RainRate property called")
        return self._com_object.RainRate

    @property
    def SkyBrightness(self):
        logger.debug("ASCOMObservingConditions.SkyBrightness property called")
        return self._com_object.SkyBrightness

    @property
    def SkyQuality(self):
        logger.debug("ASCOMObservingConditions.SkyQuality property called")
        return self._com_object.SkyQuality

    @property
    def SkyTemperature(self):
        logger.debug("ASCOMObservingConditions.SkyTemperature property called")
        return self._com_object.SkyTemperature

    @property
    def StarFWHM(self):
        logger.debug("ASCOMObservingConditions.StarFWHM property called")
        return self._com_object.StarFWHM

    @property
    def Temperature(self):
        logger.debug("ASCOMObservingConditions.Temperature property called")
        return self._com_object.Temperature

    @property
    def WindDirection(self):
        logger.debug("ASCOMObservingConditions.WindDirection property called")
        return self._com_object.WindDirection

    @property
    def WindGust(self):
        logger.debug("ASCOMObservingConditions.WindGust property called")
        return self._com_object.WindGust

    @property
    def WindSpeed(self):
        logger.debug("ASCOMObservingConditions.WindSpeed property called")
        return self._com_object.WindSpeed
