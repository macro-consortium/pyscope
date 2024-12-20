import logging

from .ascom_device import ASCOMDevice
from .observing_conditions import ObservingConditions

logger = logging.getLogger(__name__)


class ASCOMObservingConditions(ASCOMDevice, ObservingConditions):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        """
        ASCOM implementation of the base class.

        The class provides an interface to access a set of values useful for astronomical purposes such as
        determining if it is safe to operate the observing system, recording data, or determining
        refraction corrections.

        Parameters
        ----------
        identifier : `str`
            The device identifier.
        alpaca : `bool`, default : `False`, optional
            Whether the device is an Alpaca device.
        device_number : `int`, default : 0, optional
            The device number.
        protocol : `str`, default : "http", optional
            The protocol to use for communication with the device.
        """
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def Refresh(self):
        logger.debug("ASCOMObservingConditions.Refresh() called")
        self._device.Refresh()

    def SensorDescription(self, PropertyName):
        logger.debug(
            f"ASCOMObservingConditions.SensorDescription({PropertyName}) called"
        )
        return self._device.SensorDescription(PropertyName)

    def TimeSinceLastUpdate(self, PropertyName):
        logger.debug(
            f"ASCOMObservingConditions.TimeSinceLastUpdate({PropertyName}) called"
        )
        return self._device.TimeSinceLastUpdate(PropertyName)

    @property
    def AveragePeriod(self):
        logger.debug("ASCOMObservingConditions.AveragePeriod property called")
        return self._device.AveragePeriod

    @AveragePeriod.setter
    def AveragePeriod(self, value):
        logger.debug(f"ASCOMObservingConditions.AveragePeriod property set to {value}")
        self._device.AveragePeriod = value

    @property
    def CloudCover(self):
        logger.debug("ASCOMObservingConditions.CloudCover property called")
        return self._device.CloudCover

    @property
    def DewPoint(self):
        logger.debug("ASCOMObservingConditions.DewPoint property called")
        return self._device.DewPoint

    @property
    def Humidity(self):
        logger.debug("ASCOMObservingConditions.Humidity property called")
        return self._device.Humidity

    @property
    def Pressure(self):
        logger.debug("ASCOMObservingConditions.Pressure property called")
        return self._device.Pressure

    @property
    def RainRate(self):
        logger.debug("ASCOMObservingConditions.RainRate property called")
        return self._device.RainRate

    @property
    def SkyBrightness(self):
        logger.debug("ASCOMObservingConditions.SkyBrightness property called")
        return self._device.SkyBrightness

    @property
    def SkyQuality(self):
        logger.debug("ASCOMObservingConditions.SkyQuality property called")
        return self._device.SkyQuality

    @property
    def SkyTemperature(self):
        logger.debug("ASCOMObservingConditions.SkyTemperature property called")
        return self._device.SkyTemperature

    @property
    def StarFWHM(self):
        logger.debug("ASCOMObservingConditions.StarFWHM property called")
        return self._device.StarFWHM

    @property
    def Temperature(self):
        logger.debug("ASCOMObservingConditions.Temperature property called")
        return self._device.Temperature

    @property
    def WindDirection(self):
        logger.debug("ASCOMObservingConditions.WindDirection property called")
        return self._device.WindDirection

    @property
    def WindGust(self):
        logger.debug("ASCOMObservingConditions.WindGust property called")
        return self._device.WindGust

    @property
    def WindSpeed(self):
        logger.debug("ASCOMObservingConditions.WindSpeed property called")
        return self._device.WindSpeed
