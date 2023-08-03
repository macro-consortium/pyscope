from .camera import Camera

class ASCOMCamera(Camera):
    def AbortExposure(self):
        self._com_object.AbortExposure()

    def Choose(self, cameraID):
        self._com_object.Choose(cameraID)
    
    def PulseGuide(self, Direction, Duration):
        self._com_object.PulseGuide(Direction, Duration)

    def StartExposure(self, Duration, Light):
        self._com_object.StartExposure(Duration, Light)

    def StopExposure(self):
        self._com_object.StopExposure()
    
    @property
    def BayerOffsetX(self):
        return self._com_object.BayerOffsetX

    @property
    def BayerOffsetY(self):
        return self._com_object.BayerOffsetY

    @property
    def BinX(self):
        return self._com_object.BinX
    @BinX.setter
    def BinX(self, value):
        self._com_object.BinX = value
    
    @property
    def BinY(self):
        return self._com_object.BinY
    @BinY.setter
    def BinY(self, value):
        self._com_object.BinY = value
    
    @property
    def CameraState(self):
        return self._com_object.CameraState
    
    @property
    def CameraXSize(self):
        return self._com_object.CameraXSize
    
    @property
    def CameraYSize(self):
        return self._com_object.CameraYSize
    
    @property
    def CanAbortExposure(self):
        return self._com_object.CanAbortExposure
    
    @property
    def CanAsymmetricBin(self):
        return self._com_object.CanAsymmetricBin
    
    @property
    def CanFastReadout(self):
        return self._com_object.CanFastReadout
    
    @property
    def CanGetCoolerPower(self):
        return self._com_object.CanGetCoolerPower
    
    @property
    def CanPulseGuide(self):
        return self._com_object.CanPulseGuide
    
    @property
    def CanSetCCDTemperature(self):
        return self._com_object.CanSetCCDTemperature
    
    @property
    def CanStopExposure(self):
        return self._com_object.CanStopExposure
    
    @property
    def CCDTemperature(self):
        return self._com_object.CCDTemperature
    
    @property
    def CoolerOn(self):
        return self._com_object.CoolerOn
    @CoolerOn.setter
    def CoolerOn(self, value):
        self._com_object.CoolerOn = value
    
    @property
    def CoolerPower(self):
        return self._com_object.CoolerPower

    @property
    def ElectronsPerADU(self, ADU):
        return self._com_object.ElectronsPerADU(ADU)
    
    @property
    def ExposureMax(self):
        return self._com_object.ExposureMax
    
    @property
    def ExposureMin(self):
        return self._com_object.ExposureMin
    
    @property
    def ExposureResolution(self):
        return self._com_object.ExposureResolution
    
    @property
    def FastReadout(self):
        return self._com_object.FastReadout
    @FastReadout.setter
    def FastReadout(self, value):
        self._com_object.FastReadout = value
    
    @property
    def FullWellCapacity(self):
        return self._com_object.FullWellCapacity
    
    @property
    def Gain(self):
        return self._com_object.Gain
    @Gain.setter
    def Gain(self, value):
        self._com_object.Gain = value

    @property
    def GainMax(self):
        return self._com_object.GainMax
    
    @property
    def GainMin(self):
        return self._com_object.GainMin
    
    @property
    def Gains(self):
        return self._com_object.Gains
    
    @property
    def HasShutter(self):
        return self._com_object.HasShutter
    
    @property
    def HeatSinkTemperature(self):
        return self._com_object.HeatSinkTemperature
    
    @property
    def ImageArray(self):
        return self._com_object.ImageArray
    
    @property
    def ImageArrayVariant(self):
        return self._com_object.ImageArrayVariant
    
    @property
    def ImageReady(self):
        return self._com_object.ImageReady

    @property
    def IsPulseGuiding(self):
        return self._com_object.IsPulseGuiding

    @property
    def LastExposureDuration(self):
        return self._com_object.LastExposureDuration

    @property
    def LastExposureStartTime(self):
        return self._com_object.LastExposureStartTime

    @property
    def MaxADU(self):
        return self._com_object.MaxADU
    
    @property
    def MaxBinX(self):
        return self._com_object.MaxBinX

    @property
    def MaxBinY(self):
        return self._com_object.MaxBinY

    @property
    def NumX(self):
        return self._com_object.NumX
    @NumX.setter
    def NumX(self, value):
        self._com_object.NumX = value

    @property
    def NumY(self):
        return self._com_object.NumY
    @NumY.setter
    def NumY(self, value):
        self._com_object.NumY = value

    @property
    def Offset(self):
        return self._com_object.Offset
    @Offset.setter
    def Offset(self, value):
        self._com_object.Offset = value

    @property
    def OffsetMax(self):
        return self._com_object.OffsetMax
    
    @property
    def OffsetMin(self):
        return self._com_object.OffsetMin

    @property
    def Offsets(self):
        return self._com_object.Offsets
    
    @property
    def PercentCompleted(self):
        return self._com_object.PercentCompleted
    
    @property
    def PixelSizeX(self):
        return self._com_object.PixelSizeX
    
    @property
    def PixelSizeY(self):
        return self._com_object.PixelSizeY

    @property
    def ReadoutMode(self):
        return self._com_object.ReadoutMode
    @ReadoutMode.setter
    def ReadoutMode(self, value):
        self._com_object.ReadoutMode = value

    @property
    def ReadoutModes(self):
        return self._com_object.ReadoutModes

    @property
    def SensorName(self):
        return self._com_object.SensorName
    
    @property
    def SensorType(self):
        return self._com_object.SensorType
    
    @property
    def SetCCDTemperature(self):
        return self._com_object.SetCCDTemperature
    @SetCCDTemperature.setter
    def SetCCDTemperature(self, value):
        self._com_object.SetCCDTemperature = value

    @property
    def StartX(self):
        return self._com_object.StartX
    @StartX.setter
    def StartX(self, value):
        self._com_object.StartX = value
    
    @property
    def StartY(self):
        return self._com_object.StartY
    @StartY.setter
    def StartY(self, value):
        self._com_object.StartY = value
    
    @property
    def SubExposureDuration(self):
        return self._com_object.SubExposureDuration
    @SubExposureDuration.setter
    def SubExposureDuration(self, value):
        self._com_object.SubExposureDuration = value