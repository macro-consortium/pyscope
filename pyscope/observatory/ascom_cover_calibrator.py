from .cover_calibrator import CoverCalibrator

class ASCOMCoverCalibrator(CoverCalibrator):
    def CalibratorOff(self):
        self._com_object.CalibratorOff()

    def CalibratorOn(self, Brightness):
        self._com_object.CalibratorOn(Brightness)
    
    def Choose(self, CalibratorID):
        self._com_object.Choose(CalibratorID)
    
    def CloseCover(self):
        self._com_object.CloseCover()
    
    def HaltCover(self):
        self._com_object.HaltCover()
    
    def OpenCover(self):
        self._com_object.OpenCover()
    
    @property
    def Brightness(self):
        return self._com_object.Brightness
    
    @property
    def CalibratorState(self):
        return self._com_object.CalibratorState
    
    @property
    def CoverState(self):
        return self._com_object.CoverState
    
    @property
    def MaxBrightness(self):
        return self._com_object.MaxBrightness