import logging

from .ascom_device import ASCOMDevice
from .camera import Camera

logger = logging.getLogger(__name__)


class ASCOMCamera(ASCOMDevice, Camera):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def AbortExposure(self):
        logger.debug(f"ASCOMCamera.AbortExposure() called")
        self._device.AbortExposure()

    def PulseGuide(self, Direction, Duration):
        logger.debug(f"ASCOMCamera.PulseGuide({Direction}, {Duration}) called")
        self._device.PulseGuide(Direction, Duration)

    def StartExposure(self, Duration, Light):
        logger.debug(f"ASCOMCamera.StartExposure({Duration}, {Light}) called")
        self._device.StartExposure(Duration, Light)

    def StopExposure(self):
        logger.debug(f"ASCOMCamera.StopExposure() called")
        self._device.StopExposure()

    @property
    def BayerOffsetX(self):  # pragma: no cover
        """
        .. warning::
            This property is not implemented in the ASCOM Alpaca protocol.
        """
        logger.debug(f"ASCOMCamera.BayerOffsetX property called")
        return self._device.BayerOffsetX

    @property
    def BayerOffsetY(self):  # pragma: no cover
        """
        .. warning::
            This property is not implemented in the ASCOM Alpaca protocol.
        """
        logger.debug(f"ASCOMCamera.BayerOffsetY property called")
        return self._device.BayerOffsetY

    @property
    def BinX(self):
        logger.debug(f"ASCOMCamera.BinX property called")
        return self._device.BinX

    @BinX.setter
    def BinX(self, value):
        logger.debug(f"ASCOMCamera.BinX property set to {value}")
        self._device.BinX = value

    @property
    def BinY(self):
        logger.debug(f"ASCOMCamera.BinY property called")
        return self._device.BinY

    @BinY.setter
    def BinY(self, value):
        logger.debug(f"ASCOMCamera.BinY property set to {value}")
        self._device.BinY = value

    @property
    def CameraState(self):
        logger.debug(f"ASCOMCamera.CameraState property called")
        return self._device.CameraState

    @property
    def CameraXSize(self):
        logger.debug(f"ASCOMCamera.CameraXSize property called")
        return self._device.CameraXSize

    @property
    def CameraYSize(self):
        logger.debug(f"ASCOMCamera.CameraYSize property called")
        return self._device.CameraYSize

    @property
    def CanAbortExposure(self):
        logger.debug(f"ASCOMCamera.CanAbortExposure property called")
        return self._device.CanAbortExposure

    @property
    def CanAsymmetricBin(self):
        logger.debug(f"ASCOMCamera.CanAsymmetricBin property called")
        return self._device.CanAsymmetricBin

    @property
    def CanFastReadout(self):
        logger.debug(f"ASCOMCamera.CanFastReadout property called")
        return self._device.CanFastReadout

    @property
    def CanGetCoolerPower(self):
        logger.debug(f"ASCOMCamera.CanGetCoolerPower property called")
        return self._device.CanGetCoolerPower

    @property
    def CanPulseGuide(self):
        logger.debug(f"ASCOMCamera.CanPulseGuide property called")
        return self._device.CanPulseGuide

    @property
    def CanSetCCDTemperature(self):
        logger.debug(f"ASCOMCamera.CanSetCCDTemperature property called")
        return self._device.CanSetCCDTemperature

    @property
    def CanStopExposure(self):
        logger.debug(f"ASCOMCamera.CanStopExposure property called")
        return self._device.CanStopExposure

    @property
    def CCDTemperature(self):
        logger.debug(f"ASCOMCamera.CCDTemperature property called")
        return self._device.CCDTemperature

    @property
    def CoolerOn(self):
        logger.debug(f"ASCOMCamera.CoolerOn property called")
        return self._device.CoolerOn

    @CoolerOn.setter
    def CoolerOn(self, value):
        logger.debug(f"ASCOMCamera.CoolerOn property set to {value}")
        self._device.CoolerOn = value

    @property
    def CoolerPower(self):
        logger.debug(f"ASCOMCamera.CoolerPower property called")
        return self._device.CoolerPower

    @property
    def ElectronsPerADU(self):
        logger.debug(f"ASCOMCamera.ElectronsPerADU() property called")
        return self._device.ElectronsPerADU

    @property
    def ExposureMax(self):
        logger.debug(f"ASCOMCamera.ExposureMax property called")
        return self._device.ExposureMax

    @property
    def ExposureMin(self):
        logger.debug(f"ASCOMCamera.ExposureMin property called")
        return self._device.ExposureMin

    @property
    def ExposureResolution(self):
        logger.debug(f"ASCOMCamera.ExposureResolution property called")
        return self._device.ExposureResolution

    @property
    def FastReadout(self):
        logger.debug(f"ASCOMCamera.FastReadout property called")
        return self._device.FastReadout

    @FastReadout.setter
    def FastReadout(self, value):
        logger.debug(f"ASCOMCamera.FastReadout property set to {value}")
        self._device.FastReadout = value

    @property
    def FullWellCapacity(self):
        logger.debug(f"ASCOMCamera.FullWellCapacity property called")
        return self._device.FullWellCapacity

    @property
    def Gain(self):
        logger.debug(f"ASCOMCamera.Gain property called")
        return self._device.Gain

    @Gain.setter
    def Gain(self, value):
        logger.debug(f"ASCOMCamera.Gain property set to {value}")
        self._device.Gain = value

    @property
    def GainMax(self):
        logger.debug(f"ASCOMCamera.GainMax property called")
        return self._device.GainMax

    @property
    def GainMin(self):
        logger.debug(f"ASCOMCamera.GainMin property called")
        return self._device.GainMin

    @property
    def Gains(self):
        logger.debug(f"ASCOMCamera.Gains property called")
        return self._device.Gains

    @property
    def HasShutter(self):
        logger.debug(f"ASCOMCamera.HasShutter property called")
        return self._device.HasShutter

    @property
    def HeatSinkTemperature(self):
        logger.debug(f"ASCOMCamera.HeatSinkTemperature property called")
        return self._device.HeatSinkTemperature

    @property
    def ImageArray(self):
        logger.debug(f"ASCOMCamera.ImageArray property called")
        return self._device.ImageArray

    @property
    def ImageReady(self):
        logger.debug(f"ASCOMCamera.ImageReady property called")
        return self._device.ImageReady

    @property
    def IsPulseGuiding(self):
        logger.debug(f"ASCOMCamera.IsPulseGuiding property called")
        return self._device.IsPulseGuiding

    @property
    def LastExposureDuration(self):
        logger.debug(f"ASCOMCamera.LastExposureDuration property called")
        return self._device.LastExposureDuration

    @property
    def LastExposureStartTime(self):
        logger.debug(f"ASCOMCamera.LastExposureStartTime property called")
        return self._device.LastExposureStartTime

    @property
    def MaxADU(self):
        logger.debug(f"ASCOMCamera.MaxADU property called")
        return self._device.MaxADU

    @property
    def MaxBinX(self):
        logger.debug(f"ASCOMCamera.MaxBinX property called")
        return self._device.MaxBinX

    @property
    def MaxBinY(self):
        logger.debug(f"ASCOMCamera.MaxBinY property called")
        return self._device.MaxBinY

    @property
    def NumX(self):
        logger.debug(f"ASCOMCamera.NumX property called")
        return self._device.NumX

    @NumX.setter
    def NumX(self, value):
        logger.debug(f"ASCOMCamera.NumX property set to {value}")
        self._device.NumX = value

    @property
    def NumY(self):
        logger.debug(f"ASCOMCamera.NumY property called")
        return self._device.NumY

    @NumY.setter
    def NumY(self, value):
        logger.debug(f"ASCOMCamera.NumY property set to {value}")
        self._device.NumY = value

    @property
    def Offset(self):
        logger.debug(f"ASCOMCamera.Offset property called")
        return self._device.Offset

    @Offset.setter
    def Offset(self, value):
        logger.debug(f"ASCOMCamera.Offset property set to {value}")
        self._device.Offset = value

    @property
    def OffsetMax(self):
        logger.debug(f"ASCOMCamera.OffsetMax property called")
        return self._device.OffsetMax

    @property
    def OffsetMin(self):
        logger.debug(f"ASCOMCamera.OffsetMin property called")
        return self._device.OffsetMin

    @property
    def Offsets(self):
        logger.debug(f"ASCOMCamera.Offsets property called")
        return self._device.Offsets

    @property
    def PercentCompleted(self):
        logger.debug(f"ASCOMCamera.PercentCompleted property called")
        return self._device.PercentCompleted

    @property
    def PixelSizeX(self):
        logger.debug(f"ASCOMCamera.PixelSizeX property called")
        return self._device.PixelSizeX

    @property
    def PixelSizeY(self):
        logger.debug(f"ASCOMCamera.PixelSizeY property called")
        return self._device.PixelSizeY

    @property
    def ReadoutMode(self):
        logger.debug(f"ASCOMCamera.ReadoutMode property called")
        return self._device.ReadoutMode

    @ReadoutMode.setter
    def ReadoutMode(self, value):
        logger.debug(f"ASCOMCamera.ReadoutMode property set to {value}")
        self._device.ReadoutMode = value

    @property
    def ReadoutModes(self):
        logger.debug(f"ASCOMCamera.ReadoutModes property called")
        return self._device.ReadoutModes

    @property
    def SensorName(self):
        logger.debug(f"ASCOMCamera.SensorName property called")
        return self._device.SensorName

    @property
    def SensorType(self):
        logger.debug(f"ASCOMCamera.SensorType property called")
        return self._device.SensorType

    @property
    def SetCCDTemperature(self):
        logger.debug(f"ASCOMCamera.SetCCDTemperature property called")
        return self._device.SetCCDTemperature

    @SetCCDTemperature.setter
    def SetCCDTemperature(self, value):
        logger.debug(f"ASCOMCamera.SetCCDTemperature property set to {value}")
        self._device.SetCCDTemperature = value

    @property
    def StartX(self):
        logger.debug(f"ASCOMCamera.StartX property called")
        return self._device.StartX

    @StartX.setter
    def StartX(self, value):
        logger.debug(f"ASCOMCamera.StartX property set to {value}")
        self._device.StartX = value

    @property
    def StartY(self):
        logger.debug(f"ASCOMCamera.StartY property called")
        return self._device.StartY

    @StartY.setter
    def StartY(self, value):
        logger.debug(f"ASCOMCamera.StartY property set to {value}")
        self._device.StartY = value

    @property
    def SubExposureDuration(self):
        logger.debug(f"ASCOMCamera.SubExposureDuration property called")
        return self._device.SubExposureDuration

    @SubExposureDuration.setter
    def SubExposureDuration(self, value):
        logger.debug(f"ASCOMCamera.SubExposureDuration property set to {value}")
        self._device.SubExposureDuration = value
