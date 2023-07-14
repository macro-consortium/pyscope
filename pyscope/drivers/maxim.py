import platform
import time

from . import abstract, ascom

class Maxim(abstract.Driver):
    def __init__(self):
        if platform.system() != 'Windows':
            raise Exception('This class is only available on Windows.')
        else:
            from win32com.client import Dispatch
            self._app = Dispatch('MaxIm.Application')
            self._app.LockApp = True

            self._camera = _MaximCamera()
            self._camera.Connected = True

            self._filter_wheel = None
            self._autofocus = None
            if self._camera.HasFilterWheel:
                self._filter_wheel = _MaximFilterWheel(self.camera)
            if self._app.FocuserConnected:
                self._autofocus = _MaximAutofocus(self.app)

            self._wcs = _MaximPinpointWCS(self.camera)
    
    @property
    def Connected(self):
        return self.camera.Connected
    @Connected.setter
    def Connected(self, value):
        self.camera.Connected = value
    
    @property
    def Name(self):
        return 'MaxIm DL'
    
    @property
    def app(self):
        return self._app

    @property
    def autofocus(self):
        return self._autofocus
    
    @property
    def camera(self):
        return self._camera

    @property
    def filter_wheel(self):
        return self._filter_wheel
    
    @property
    def wcs(self):
        return self._wcs

class _MaximAutofocus(abstract.Autofocus):
    def __init__(self, maxim):
        self.maxim = maxim

    def Run(self, exposure=10):
        self.maxim.Autofocus(exposure)

        while self.maxim.AutofocusStatus == -1:
            time.sleep(1)
        
        if self.maxim.AutofocusStatus == 1:
            return True
        else:
            return False

    def Abort(self):
        raise NotImplementedError

class _MaximCamera(abstract.Camera):
    def __init__(self):
        self._com_object = Dispatch('MaxIm.CCDCamera')
        self._com_object.DisableAutoShutdown = True

        self._last_exposure_duration = None
        self._last_exposure_start_time = None

    @property
    def Connected(self):
        return self._com_object is not None and self._com_object.LinkEnabled
    @Connected.setter
    def Connected(self, value):
        self._com_object.LinkEnabled = value
    
    @property
    def Name(self):
        self._com_object.CameraName
    
    def AbortExposure(self):
        self._com_object.AbortExposure()

    def PulseGuide(self, Direction, Duration):
        raise NotImplementedError

    def StartExposure(self, Duration, Light):
        self._last_exposure_duration = Duration
        self._last_exposure_start_time = time.time()
        self._com_object.Expose(Duration, Light)

    def StopExposure(self):
        self._com_object.AbortExposure()

    @property
    def BayerOffsetX(self):
        raise NotImplementedError

    @property
    def BayerOffsetY(self):
        raise NotImplementedError

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
        return self._com_object.CameraStatus

    @property
    def CameraXSize(self):
        return self._com_object.CameraXSize

    @property
    def CameraYSize(self):
        return self._com_object.CameraYSize

    @property
    def CanAbortExposure(self):
        return True

    @property
    def CanAsymmetricBin(self):
        return self._com_object.XYBinning

    @property
    def CanFastReadout(self):
        raise NotImplementedError

    @property
    def CanGetCoolerPower(self):
        return True

    @property
    def CanPulseGuide(self):
        return False

    @property
    def CanSetCCDTemperature(self):
        return self._com_object.CanSetTemperature

    @property
    def CanStopExposure(self):
        return True

    @property
    def CCDTemperature(self):
        return self._com_object.Temperature

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
    def ElectronsPerADU(self):
        raise NotImplementedError

    @property
    def ExposureMax(self):
        raise NotImplementedError

    @property
    def ExposureMin(self):
        raise NotImplementedError

    @property
    def ExposureResolution(self):
        raise NotImplementedError

    @property
    def FastReadout(self):
        raise DeprecationWarning
    @FastReadout.setter
    def FastReadout(self, value):
        raise DeprecationWarning

    @property
    def FullWellCapacity(self):
        raise NotImplementedError

    @property
    def Gain(self):
        return self._com_object.Speed
    @Gain.setter
    def Gain(self, value):
        self._com_object.Speed = value

    @property
    def GainMax(self):
        raise NotImplementedError

    @property
    def GainMin(self):
        raise NotImplementedError

    @property
    def Gains(self):
        return self._com_object.Speeds

    @property
    def HasShutter(self):
        return self._com_object.HasShutter

    @property
    def HeatSinkTemperature(self):
        return self._com_object.AmbientTemperature

    @property
    def ImageArray(self):
        return self._com_object.ImageArray

    @property
    def ImageArrayVariant(self):
        return float(self._com_object.ImageArray)

    @property
    def ImageReady(self):
        return self._com_object.ImageReady

    @property
    def IsPulseGuiding(self):
        raise NotImplementedError

    @property
    def LastExposureDuration(self):
        return self._last_exposure_duration

    @property
    def LastExposureStartTime(self):
        return self._last_exposure_start_time

    @property
    def MaxADU(self):
        raise NotImplementedError

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
        raise NotImplementedError
    @Offset.setter
    def Offset(self, value):
        raise NotImplementedError

    @property
    def OffsetMax(self):
        raise NotImplementedError

    @property
    def OffsetMin(self):
        raise NotImplementedError

    @property
    def Offsets(self):
        raise NotImplementedError

    @property
    def PercentCompleted(self):
        raise NotImplementedError

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
        raise NotImplementedError

    @property
    def SensorType(self):
        raise NotImplementedError

    @property
    def SetCCDTemperature(self):
        return self._com_object.TemperatureSetpoint
    @SetCCDTemperature.setter
    def SetCCDTemperature(self, value):
        self._com_object.TemperatureSetpoint = value

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
        raise NotImplementedError
    @SubExposureDuration.setter
    def SubExposureDuration(self, value):
        raise NotImplementedError

class _MaximFilterWheel(abstract.FilterWheel):
    def __init__(self, maxim_camera):
        self.maxim_camera = maxim_camera

    @property
    def Connected(self):
        return self.maxim_camera.Connected and self.maxim_camera.HasFilterWheel
    @Connected.setter
    def Connected(self, value):
        self.maxim_camera.Connected = value
    
    @property
    def Name(self):
        self.maxim_camera.FilterWheelName

    @property
    def FocusOffsets(self):
        raise NotImplementedError

    @property
    def Names(self):
        return self.maxim_camera.FilterNames

    @property
    def Position(self):
        return self.maxim_camera.Filter
    @Position.setter
    def Position(self, value):
        self.maxim_camera.Filter = value

class _MaximPinpointWCS(abstract.WCS):
    def __init__(self, maxim_camera):
        self.maxim_camera = maxim_camera

    def Solve(self, ra=None, dec=None, scale_est=None, *args, **kwargs):
        self.maxim_camera.document.PinpointSolve(ra, dec, scale_est, scale_est)

        while self.maxim_camera.document.PinpointStatus == 3:
            time.sleep(1)
        
        if self.maxim_camera.document.PinpointStatus == 2:
            return True
        else:
            return False