import logging

from .camera import Camera

logger = logging.getLogger(__name__)


class ASCOMCamera(Camera):
    def AbortExposure(self):
        logger.debug(f"ASCOMCamera.AbortExposure() called")
        self._com_object.AbortExposure()

    def Choose(self, cameraID):
        logger.debug(f"ASCOMCamera.Choose({cameraID}) called")
        self._com_object.Choose(cameraID)

    def PulseGuide(self, Direction, Duration):
        logger.debug(f"ASCOMCamera.PulseGuide({Direction}, {Duration}) called")
        self._com_object.PulseGuide(Direction, Duration)

    def StartExposure(self, Duration, Light):
        logger.debug(f"ASCOMCamera.StartExposure({Duration}, {Light}) called")
        self._com_object.StartExposure(Duration, Light)

    def StopExposure(self):
        logger.debug(f"ASCOMCamera.StopExposure() called")
        self._com_object.StopExposure()

    @property
    def BayerOffsetX(self):
        logger.debug(f"ASCOMCamera.BayerOffsetX property called")
        return self._com_object.BayerOffsetX

    @property
    def BayerOffsetY(self):
        logger.debug(f"ASCOMCamera.BayerOffsetY property called")
        return self._com_object.BayerOffsetY

    @property
    def BinX(self):
        logger.debug(f"ASCOMCamera.BinX property called")
        return self._com_object.BinX

    @BinX.setter
    def BinX(self, value):
        logger.debug(f"ASCOMCamera.BinX property set to {value}")
        self._com_object.BinX = value

    @property
    def BinY(self):
        logger.debug(f"ASCOMCamera.BinY property called")
        return self._com_object.BinY

    @BinY.setter
    def BinY(self, value):
        logger.debug(f"ASCOMCamera.BinY property set to {value}")
        self._com_object.BinY = value

    @property
    def CameraState(self):
        logger.debug(f"ASCOMCamera.CameraState property called")
        return self._com_object.CameraState

    @property
    def CameraXSize(self):
        logger.debug(f"ASCOMCamera.CameraXSize property called")
        return self._com_object.CameraXSize

    @property
    def CameraYSize(self):
        logger.debug(f"ASCOMCamera.CameraYSize property called")
        return self._com_object.CameraYSize

    @property
    def CanAbortExposure(self):
        logger.debug(f"ASCOMCamera.CanAbortExposure property called")
        return self._com_object.CanAbortExposure

    @property
    def CanAsymmetricBin(self):
        logger.debug(f"ASCOMCamera.CanAsymmetricBin property called")
        return self._com_object.CanAsymmetricBin

    @property
    def CanFastReadout(self):
        logger.debug(f"ASCOMCamera.CanFastReadout property called")
        return self._com_object.CanFastReadout

    @property
    def CanGetCoolerPower(self):
        logger.debug(f"ASCOMCamera.CanGetCoolerPower property called")
        return self._com_object.CanGetCoolerPower

    @property
    def CanPulseGuide(self):
        logger.debug(f"ASCOMCamera.CanPulseGuide property called")
        return self._com_object.CanPulseGuide

    @property
    def CanSetCCDTemperature(self):
        logger.debug(f"ASCOMCamera.CanSetCCDTemperature property called")
        return self._com_object.CanSetCCDTemperature

    @property
    def CanStopExposure(self):
        logger.debug(f"ASCOMCamera.CanStopExposure property called")
        return self._com_object.CanStopExposure

    @property
    def CCDTemperature(self):
        logger.debug(f"ASCOMCamera.CCDTemperature property called")
        return self._com_object.CCDTemperature

    @property
    def CoolerOn(self):
        logger.debug(f"ASCOMCamera.CoolerOn property called")
        return self._com_object.CoolerOn

    @CoolerOn.setter
    def CoolerOn(self, value):
        logger.debug(f"ASCOMCamera.CoolerOn property set to {value}")
        self._com_object.CoolerOn = value

    @property
    def CoolerPower(self):
        logger.debug(f"ASCOMCamera.CoolerPower property called")
        return self._com_object.CoolerPower

    @property
    def ElectronsPerADU(self, ADU):
        logger.debug(f"ASCOMCamera.ElectronsPerADU({ADU}) property called")
        return self._com_object.ElectronsPerADU(ADU)

    @property
    def ExposureMax(self):
        logger.debug(f"ASCOMCamera.ExposureMax property called")
        return self._com_object.ExposureMax

    @property
    def ExposureMin(self):
        logger.debug(f"ASCOMCamera.ExposureMin property called")
        return self._com_object.ExposureMin

    @property
    def ExposureResolution(self):
        logger.debug(f"ASCOMCamera.ExposureResolution property called")
        return self._com_object.ExposureResolution

    @property
    def FastReadout(self):
        logger.debug(f"ASCOMCamera.FastReadout property called")
        return self._com_object.FastReadout

    @FastReadout.setter
    def FastReadout(self, value):
        logger.debug(f"ASCOMCamera.FastReadout property set to {value}")
        self._com_object.FastReadout = value

    @property
    def FullWellCapacity(self):
        logger.debug(f"ASCOMCamera.FullWellCapacity property called")
        return self._com_object.FullWellCapacity

    @property
    def Gain(self):
        logger.debug(f"ASCOMCamera.Gain property called")
        return self._com_object.Gain

    @Gain.setter
    def Gain(self, value):
        logger.debug(f"ASCOMCamera.Gain property set to {value}")
        self._com_object.Gain = value

    @property
    def GainMax(self):
        logger.debug(f"ASCOMCamera.GainMax property called")
        return self._com_object.GainMax

    @property
    def GainMin(self):
        logger.debug(f"ASCOMCamera.GainMin property called")
        return self._com_object.GainMin

    @property
    def Gains(self):
        logger.debug(f"ASCOMCamera.Gains property called")
        return self._com_object.Gains

    @property
    def HasShutter(self):
        logger.debug(f"ASCOMCamera.HasShutter property called")
        return self._com_object.HasShutter

    @property
    def HeatSinkTemperature(self):
        logger.debug(f"ASCOMCamera.HeatSinkTemperature property called")
        return self._com_object.HeatSinkTemperature

    @property
    def ImageArray(self):
        logger.debug(f"ASCOMCamera.ImageArray property called")
        return self._com_object.ImageArray

    @property
    def ImageArrayVariant(self):
        logger.debug(f"ASCOMCamera.ImageArrayVariant property called")
        return self._com_object.ImageArrayVariant

    @property
    def ImageReady(self):
        logger.debug(f"ASCOMCamera.ImageReady property called")
        return self._com_object.ImageReady

    @property
    def IsPulseGuiding(self):
        logger.debug(f"ASCOMCamera.IsPulseGuiding property called")
        return self._com_object.IsPulseGuiding

    @property
    def LastExposureDuration(self):
        logger.debug(f"ASCOMCamera.LastExposureDuration property called")
        return self._com_object.LastExposureDuration

    @property
    def LastExposureStartTime(self):
        logger.debug(f"ASCOMCamera.LastExposureStartTime property called")
        return self._com_object.LastExposureStartTime

    @property
    def MaxADU(self):
        logger.debug(f"ASCOMCamera.MaxADU property called")
        return self._com_object.MaxADU

    @property
    def MaxBinX(self):
        logger.debug(f"ASCOMCamera.MaxBinX property called")
        return self._com_object.MaxBinX

    @property
    def MaxBinY(self):
        logger.debug(f"ASCOMCamera.MaxBinY property called")
        return self._com_object.MaxBinY

    @property
    def NumX(self):
        logger.debug(f"ASCOMCamera.NumX property called")
        return self._com_object.NumX

    @NumX.setter
    def NumX(self, value):
        logger.debug(f"ASCOMCamera.NumX property set to {value}")
        self._com_object.NumX = value

    @property
    def NumY(self):
        logger.debug(f"ASCOMCamera.NumY property called")
        return self._com_object.NumY

    @NumY.setter
    def NumY(self, value):
        logger.debug(f"ASCOMCamera.NumY property set to {value}")
        self._com_object.NumY = value

    @property
    def Offset(self):
        logger.debug(f"ASCOMCamera.Offset property called")
        return self._com_object.Offset

    @Offset.setter
    def Offset(self, value):
        logger.debug(f"ASCOMCamera.Offset property set to {value}")
        self._com_object.Offset = value

    @property
    def OffsetMax(self):
        logger.debug(f"ASCOMCamera.OffsetMax property called")
        return self._com_object.OffsetMax

    @property
    def OffsetMin(self):
        logger.debug(f"ASCOMCamera.OffsetMin property called")
        return self._com_object.OffsetMin

    @property
    def Offsets(self):
        logger.debug(f"ASCOMCamera.Offsets property called")
        return self._com_object.Offsets

    @property
    def PercentCompleted(self):
        logger.debug(f"ASCOMCamera.PercentCompleted property called")
        return self._com_object.PercentCompleted

    @property
    def PixelSizeX(self):
        logger.debug(f"ASCOMCamera.PixelSizeX property called")
        return self._com_object.PixelSizeX

    @property
    def PixelSizeY(self):
        logger.debug(f"ASCOMCamera.PixelSizeY property called")
        return self._com_object.PixelSizeY

    @property
    def ReadoutMode(self):
        logger.debug(f"ASCOMCamera.ReadoutMode property called")
        return self._com_object.ReadoutMode

    @ReadoutMode.setter
    def ReadoutMode(self, value):
        logger.debug(f"ASCOMCamera.ReadoutMode property set to {value}")
        self._com_object.ReadoutMode = value

    @property
    def ReadoutModes(self):
        logger.debug(f"ASCOMCamera.ReadoutModes property called")
        return self._com_object.ReadoutModes

    @property
    def SensorName(self):
        logger.debug(f"ASCOMCamera.SensorName property called")
        return self._com_object.SensorName

    @property
    def SensorType(self):
        logger.debug(f"ASCOMCamera.SensorType property called")
        return self._com_object.SensorType

    @property
    def SetCCDTemperature(self):
        logger.debug(f"ASCOMCamera.SetCCDTemperature property called")
        return self._com_object.SetCCDTemperature

    @SetCCDTemperature.setter
    def SetCCDTemperature(self, value):
        logger.debug(f"ASCOMCamera.SetCCDTemperature property set to {value}")
        self._com_object.SetCCDTemperature = value

    @property
    def StartX(self):
        logger.debug(f"ASCOMCamera.StartX property called")
        return self._com_object.StartX

    @StartX.setter
    def StartX(self, value):
        logger.debug(f"ASCOMCamera.StartX property set to {value}")
        self._com_object.StartX = value

    @property
    def StartY(self):
        logger.debug(f"ASCOMCamera.StartY property called")
        return self._com_object.StartY

    @StartY.setter
    def StartY(self, value):
        logger.debug(f"ASCOMCamera.StartY property set to {value}")
        self._com_object.StartY = value

    @property
    def SubExposureDuration(self):
        logger.debug(f"ASCOMCamera.SubExposureDuration property called")
        return self._com_object.SubExposureDuration

    @SubExposureDuration.setter
    def SubExposureDuration(self, value):
        logger.debug(f"ASCOMCamera.SubExposureDuration property set to {value}")
        self._com_object.SubExposureDuration = value
