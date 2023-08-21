import logging
from .cover_calibrator import CoverCalibrator

logger = logging.getLogger(__name__)


class ASCOMCoverCalibrator(CoverCalibrator):
    def CalibratorOff(self):
        logger.debug(f"ASCOMCoverCalibrator.CalibratorOff() called")
        self._com_object.CalibratorOff()

    def CalibratorOn(self, Brightness):
        logger.debug(f"ASCOMCoverCalibrator.CalibratorOn({Brightness}) called")
        self._com_object.CalibratorOn(Brightness)

    def Choose(self, CalibratorID):
        logger.debug(f"ASCOMCoverCalibrator.Choose({CalibratorID}) called")
        self._com_object.Choose(CalibratorID)

    def CloseCover(self):
        logger.debug(f"ASCOMCoverCalibrator.CloseCover() called")
        self._com_object.CloseCover()

    def HaltCover(self):
        logger.debug(f"ASCOMCoverCalibrator.HaltCover() called")
        self._com_object.HaltCover()

    def OpenCover(self):
        logger.debug(f"ASCOMCoverCalibrator.OpenCover() called")
        self._com_object.OpenCover()

    @property
    def Brightness(self):
        logger.debug(f"ASCOMCoverCalibrator.Brightness property called")
        return self._com_object.Brightness

    @property
    def CalibratorState(self):
        logger.debug(f"ASCOMCoverCalibrator.CalibratorState property called")
        return self._com_object.CalibratorState

    @property
    def CoverState(self):
        logger.debug(f"ASCOMCoverCalibrator.CoverState property called")
        return self._com_object.CoverState

    @property
    def MaxBrightness(self):
        logger.debug(f"ASCOMCoverCalibrator.MaxBrightness property called")
        return self._com_object.MaxBrightness
