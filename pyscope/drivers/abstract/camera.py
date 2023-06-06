from abc import ABC, abstractmethod

from abstract import DocstringInheritee

class Camera(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def AbortExposure(self):
        pass

    @abstractmethod
    def PulseGuide(self, Direction, Duration):
        pass

    @abstractmethod
    def StartExposure(self, Duration, Light):
        pass

    @abstractmethod
    def StopExposure(self):
        pass

    @property
    @abstractmethod
    def BayerOffsetX(self):
        pass

    @property
    @abstractmethod
    def BayerOffsetY(self):
        pass

    @property
    @abstractmethod
    def BinX(self):
        pass

    @property
    @abstractmethod
    def BinY(self):
        pass

    @property
    @abstractmethod
    def CameraState(self):
        pass

    @property
    @abstractmethod
    def CameraXSize(self):
        pass

    @property
    @abstractmethod
    def CameraYSize(self):
        pass

    @property
    @abstractmethod
    def CanAbortExposure(self):
        pass

    @property
    @abstractmethod
    def CanAsymmetricBin(self):
        pass

    @property
    @abstractmethod
    def CanFastReadout(self):
        pass

    @property
    @abstractmethod
    def CanGetCoolerPower(self):
        pass

    @property
    @abstractmethod
    def CanPulseGuide(self):
        pass

    @property
    @abstractmethod
    def CanSetCCDTemperature(self):
        pass

    @property
    @abstractmethod
    def CanStopExposure(self):
        pass

    @property
    @abstractmethod
    def CCDTemperature(self):
        pass

    @property
    @abstractmethod
    def CoolerOn(self):
        pass
    @CoolerOn.setter
    @abstractmethod
    def CoolerOn(self, value):
        pass

    @property
    @abstractmethod
    def CoolerPower(self):
        pass

    @property
    @abstractmethod
    def ElectronsPerADU(self):
        pass

    @property
    @abstractmethod
    def ExposureMax(self):
        pass

    @property
    @abstractmethod
    def ExposureMin(self):
        pass

    @property
    @abstractmethod
    def ExposureResolution(self):
        pass

    @property
    @abstractmethod
    def FastReadout(self):
        pass
    @FastReadout.setter
    @abstractmethod
    def FastReadout(self, value):
        pass

    @property
    @abstractmethod
    def FullWellCapacity(self):
        pass

    @property
    @abstractmethod
    def Gain(self):
        pass
    @Gain.setter
    @abstractmethod
    def Gain(self, value):
        pass

    @property
    @abstractmethod
    def GainMax(self):
        pass

    @property
    @abstractmethod
    def GainMin(self):
        pass

    @property
    @abstractmethod
    def Gains(self):
        pass

    @property
    @abstractmethod
    def HasShutter(self):
        pass

    @property
    @abstractmethod
    def HeatSinkTemperature(self):
        pass

    @property
    @abstractmethod
    def ImageArray(self):
        pass

    @property
    @abstractmethod
    def ImageArrayVariant(self):
        pass

    @property
    @abstractmethod
    def ImageReady(self):
        pass

    @property
    @abstractmethod
    def IsPulseGuiding(self):
        pass

    @property
    @abstractmethod
    def LastExposureDuration(self):
        pass

    @property
    @abstractmethod
    def LastExposureStartTime(self):
        pass

    @property
    @abstractmethod
    def MaxADU(self):
        pass

    @property
    @abstractmethod
    def MaxBinX(self):
        pass

    @property
    @abstractmethod
    def MaxBinY(self):
        pass

    @property
    @abstractmethod
    def NumX(self):
        pass
    @NumX.setter
    @abstractmethod
    def NumX(self, value):
        pass

    @property
    @abstractmethod
    def NumY(self):
        pass
    @NumY.setter
    @abstractmethod
    def NumY(self, value):
        pass

    @property
    @abstractmethod
    def Offset(self):
        pass
    @Offset.setter
    @abstractmethod
    def Offset(self, value):
        pass

    @property
    @abstractmethod
    def OffsetMax(self):
        pass

    @property
    @abstractmethod
    def OffsetMin(self):
        pass

    @property
    @abstractmethod
    def Offsets(self):
        pass

    @property
    @abstractmethod
    def PercentCompleted(self):
        pass

    @property
    @abstractmethod
    def PixelSizeX(self):
        pass

    @property
    @abstractmethod
    def PixelSizeY(self):
        pass

    @property
    @abstractmethod
    def ReadoutMode(self):
        pass
    @ReadoutMode.setter
    @abstractmethod
    def ReadoutMode(self, value):
        pass

    @property
    @abstractmethod
    def ReadoutModes(self):
        pass

    @property
    @abstractmethod
    def SensorName(self):
        pass

    @property
    @abstractmethod
    def SensorType(self):
        pass

    @property
    @abstractmethod
    def SetCCDTemperature(self):
        pass
    @SetCCDTemperature.setter
    @abstractmethod
    def SetCCDTemperature(self, value):
        pass

    @property
    @abstractmethod
    def StartX(self):
        pass
    @StartX.setter
    @abstractmethod
    def StartX(self, value):
        pass

    @property
    @abstractmethod
    def StartY(self):
        pass
    @StartY.setter
    @abstractmethod
    def StartY(self, value):
        pass

    @property
    @abstractmethod
    def SubExposureDuration(self):
        pass
    @SubExposureDuration.setter
    @abstractmethod
    def SubExposureDuration(self, value):
        pass