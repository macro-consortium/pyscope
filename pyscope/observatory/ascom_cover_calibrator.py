import logging

from .ascom_device import ASCOMDevice
from .cover_calibrator import CoverCalibrator

logger = logging.getLogger(__name__)


class ASCOMCoverCalibrator(ASCOMDevice, CoverCalibrator):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def CalibratorOff(self):
        logger.debug(f"ASCOMCoverCalibrator.CalibratorOff() called")
        self._device.CalibratorOff()

    def CalibratorOn(self, Brightness):
        logger.debug(f"ASCOMCoverCalibrator.CalibratorOn({Brightness}) called")
        self._device.CalibratorOn(Brightness)

    def Choose(self, CalibratorID):
        logger.debug(f"ASCOMCoverCalibrator.Choose({CalibratorID}) called")
        self._device.Choose(CalibratorID)

    def CloseCover(self):
        logger.debug(f"ASCOMCoverCalibrator.CloseCover() called")
        self._device.CloseCover()

    def HaltCover(self):
        logger.debug(f"ASCOMCoverCalibrator.HaltCover() called")
        self._device.HaltCover()

    def OpenCover(self):
        logger.debug(f"ASCOMCoverCalibrator.OpenCover() called")
        self._device.OpenCover()

    @property
    def Brightness(self):
        logger.debug(f"ASCOMCoverCalibrator.Brightness property called")
        return self._device.Brightness

    @property
    def CalibratorState(self):
        logger.debug(f"ASCOMCoverCalibrator.CalibratorState property called")
        return self._device.CalibratorState

    @property
    def CoverState(self):
        logger.debug(f"ASCOMCoverCalibrator.CoverState property called")
        return self._device.CoverState

    @property
    def MaxBrightness(self):
        logger.debug(f"ASCOMCoverCalibrator.MaxBrightness property called")
        return self._device.MaxBrightness
