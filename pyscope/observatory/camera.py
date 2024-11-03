from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class Camera(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract class for camera devices.

        The class defines the interface for camera devices, including methods for controlling
        exposures, guiding, and retrieving camera properties. Subclasses must implement
        the abstract methods defined in this class.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def AbortExposure(self):
        """
        Abort the current exposure immediately and return camera to idle.
        See `CanAbortExposure` for support and possible reasons to abort.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        pass

    @abstractmethod
    def PulseGuide(self, Direction, Duration):
        """
        Moves the scope in the given direction for the specified duration.

        Parameters
        ----------
        Direction : `int`
            The direction in which to move the scope.
            Value representations for direction are up to the camera manufacturer,
            or in case of a lack of manufacturer specification, the developer.
            See :py:meth:`ASCOMCamera.PulseGuide` for an example.
        Duration : `int`
            The duration of the guide pulse in milliseconds.

        Returns
        -------
        None
        """
        pass

    @abstractmethod
    def StartExposure(self, Duration, Light):
        """
        Starts an exposure with a given duration and light status. Check `ImageReady` for operation completion.

        Parameters
        ----------
        Duration : `float`
            The exposure duration in seconds. Can be zero if `Light` is `False`.

        Light : `bool`
            Whether the exposure is a light frame (`True`) or a dark frame (`False`).

        Returns
        -------
        None

        Notes
        -----
        `Duration` can be shorter than `ExposureMin` if used for dark frame or bias exposure.
        Bias frame also allows a `Duration` of zero.
        """
        pass

    @abstractmethod
    def StopExposure(self):
        """
        Stops the current exposure gracefully.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Readout process will initiate if stop is called during an exposure.
        Ignored if readout is already in process.
        """
        pass

    @property
    @abstractmethod
    def BayerOffsetX(self):
        """The X/column offset of the Bayer filter array matrix. (`int`)"""
        pass

    @property
    @abstractmethod
    def BayerOffsetY(self):
        """The Y/row offset of the Bayer filter array matrix. (`int`)"""
        pass

    @property
    @abstractmethod
    def BinX(self):
        """
        The binning factor in the X/column direction. (`int`)

        Default is 1 after camera connection is established.
        """
        pass

    @BinX.setter
    @abstractmethod
    def BinX(self, value):
        pass

    @property
    @abstractmethod
    def BinY(self):
        """
        The binning factor in the Y/row direction. (`int`)

        Default is 1 after camera connection is established.
        """
        pass

    @BinY.setter
    @abstractmethod
    def BinY(self, value):
        pass

    @property
    @abstractmethod
    def CameraState(self):
        """
        The current operational state of the camera. (`enum`)

        Possible values are at the discretion of the camera manufacturer specification.
        In case of a lack of one, discretion is at the developer.
        See :py:attr:`ASCOMCamera.CameraState` for an example.
        """
        pass

    @property
    @abstractmethod
    def CameraXSize(self):
        """The width of the CCD chip in unbinned pixels. (`int`)"""
        pass

    @property
    @abstractmethod
    def CameraYSize(self):
        """The height of the CCD chip in unbinned pixels. (`int`)"""
        pass

    @property
    @abstractmethod
    def CanAbortExposure(self):
        """
        Whether the camera can abort exposures imminently. (`bool`)

        Aborting is not synonymous with stopping an exposure.
        Aborting immediately stops the exposure and discards the data.
        Used for urgent situations such as errors or temperature concerns.
        See `CanStopExposure` for gracious cancellation of an exposure.
        """
        pass

    @property
    @abstractmethod
    def CanAsymmetricBin(self):
        """
        Whether the camera supports asymmetric binning such that
        `BinX` != `BinY`. (`bool`)
        """
        pass

    @property
    @abstractmethod
    def CanFastReadout(self):
        """Whether the camera supports fast readout mode. (`bool`)"""
        pass

    @property
    @abstractmethod
    def CanGetCoolerPower(self):
        """Whether the camera's cooler power setting can be read. (`bool`)"""
        pass

    @property
    @abstractmethod
    def CanPulseGuide(self):
        """Whether the camera supports pulse guiding. (`bool`)"""
        pass

    @property
    @abstractmethod
    def CanSetCCDTemperature(self):
        """
        Whether the camera's CCD temperature can be set. (`bool`)

        A false means either the camera uses an open-loop cooling system or
        does not support adjusting the CCD temperature from software.
        """
        pass

    @property
    @abstractmethod
    def CanStopExposure(self):
        """
        Whether the camera can stop exposures graciously. (`bool`)

        Stopping is not synonymous with aborting an exposure.
        Stopping allows the camera to complete the current exposure cycle, then stop.
        Image data up to the point of stopping is typically still available.
        See `CanAbortExposure` for instant cancellation of an exposure.
        """
        pass

    @property
    @abstractmethod
    def CCDTemperature(self):
        """The current CCD temperature in degrees Celsius. (`float`)"""
        pass

    @property
    @abstractmethod
    def CoolerOn(self):
        """Whether the camera's cooler is on. (`bool`)"""
        pass

    @CoolerOn.setter
    @abstractmethod
    def CoolerOn(self, value):
        pass

    @property
    @abstractmethod
    def CoolerPower(self):
        """The current cooler power level as a percentage. (`float`)"""
        pass

    @property
    @abstractmethod
    def ElectronsPerADU(self):
        """Gain of the camera in photoelectrons per analog-to-digital-unit. (`float`)"""
        pass

    @property
    @abstractmethod
    def ExposureMax(self):
        """The maximum exposure duration supported by `StartExposure` in seconds. (`float`)"""
        pass

    @property
    @abstractmethod
    def ExposureMin(self):
        """
        The minimum exposure duration supported by `StartExposure` in seconds. (`float`)

        Non-zero number, except for bias frame acquisition, where an exposure < ExposureMin
        may be possible.
        """
        pass

    @property
    @abstractmethod
    def ExposureResolution(self):
        """
        The smallest increment in exposure duration supported by `StartExposure`. (`float`)

        This property could be useful if one wants to implement a 'spin control' interface
        for fine-tuning exposure durations.

        Providing a `Duration` to `StartExposure` that is not a multiple of `ExposureResolution`
        will choose the closest available value.

        A value of 0.0 indicates no minimum resolution increment, except that imposed by the
        floating-point precision of `float` itself.
        """
        pass

    @property
    @abstractmethod
    def FastReadout(self):
        """Whether the camera is in fast readout mode. (`bool`)"""
        pass

    @FastReadout.setter
    @abstractmethod
    def FastReadout(self, value):
        pass

    @property
    @abstractmethod
    def FullWellCapacity(self):
        """
        The full well capacity of the camera in electrons with the
        current camera settings. (`float`)
        """
        pass

    @property
    @abstractmethod
    def Gain(self):
        """
        The camera's gain OR index of the selected camera gain description.
        See below for more information. (`int`)

        Represents either the camera's gain in photoelectrons per analog-to-digital-unit,
        or the 0-index of the selected camera gain description in the `Gains` array.

        Depending on a camera's capabilities, the driver can support none, one, or both
        representation modes, but only one mode will be active at a time.

        To determine operational mode, read the `GainMin`, `GainMax`, and `Gains` properties.

        `ReadoutMode` may affect the gain of the camera, so it is recommended to set
        driver behavior to ensure no conflictions occur if both `Gain` and `ReadoutMode` are used.
        """
        pass

    @Gain.setter
    @abstractmethod
    def Gain(self, value):
        pass

    @property
    @abstractmethod
    def GainMax(self):
        """The maximum gain value supported by the camera. (`int`)"""
        pass

    @property
    @abstractmethod
    def GainMin(self):
        """The minimum gain value supported by the camera. (`int`)"""
        pass

    @property
    @abstractmethod
    def Gains(self):
        """
        0-indexed array of camera gain descriptions supported by the camera. (`list` of `str`)

        Depending on implementation, the array may contain ISOs, or gain names.
        """
        pass

    @property
    @abstractmethod
    def HasShutter(self):
        """
        Whether the camera has a mechanical shutter. (`bool`)

        If `False`, i.e. the camera has no mechanical shutter, the `StartExposure`
        method will ignore the `Light` parameter.
        """
        pass

    @property
    @abstractmethod
    def HeatSinkTemperature(self):
        """
        The current heat sink temperature in degrees Celsius. (`float`)

        The readout is only valid if `CanSetCCDTemperature` is `True`.
        """
        pass

    @property
    @abstractmethod
    def ImageArray(self):
        """
        Retrieve the image data captured by the camera as a numpy array.

        The image array contains the pixel data from the camera sensor, formatted
        as a 2D or 3D numpy array depending on the camera's capabilities and settings.
        The data type and shape of the array may vary based on the camera's configuration.

        Returns
        -------
        numpy.ndarray
            The image data captured by the camera.

        Notes
        -----
        The exact format and data type of the returned array should be documented
        by the specific camera implementation. This method should handle any necessary
        data type conversions and ensure the array is in a standard orientation.
        """
        pass

    @property
    @abstractmethod
    def ImageReady(self):
        """
        Whether the camera has completed an exposure and the image is ready to be downloaded. (`bool`)

        If `False`, the `ImageArray` property will exit with an exception.
        """
        pass

    @property
    @abstractmethod
    def IsPulseGuiding(self):
        """Whether the camera is currently pulse guiding. (`bool`)"""
        pass

    @property
    @abstractmethod
    def LastExposureDuration(self):
        """
        The duration of the last exposure in seconds. (`float`)

        May differ from requested exposure time due to shutter latency, camera timing accuracy, etc.
        """
        pass

    @property
    @abstractmethod
    def LastExposureStartTime(self):
        """
        The actual last exposure start time in FITS CCYY-MM-DDThh:mm:ss[.sss...] format. (`str`)

        The date string represents UTC time.
        """
        pass

    @property
    @abstractmethod
    def MaxADU(self):
        """The maximum ADU value the camera is capable of producing. (`int`)"""
        pass

    @property
    @abstractmethod
    def MaxBinX(self):
        """
        The maximum allowed binning factor in the X/column direction. (`int`)

        Value equivalent to `MaxBinY` if `CanAsymmetricBin` is `False`.
        """
        pass

    @property
    @abstractmethod
    def MaxBinY(self):
        """
        The maximum allowed binning factor in the Y/row direction. (`int`)

        Value equivalent to `MaxBinX` if `CanAsymmetricBin` is `False`.
        """
        pass

    @property
    @abstractmethod
    def NumX(self):
        """The width of the subframe in binned pixels. (`int`)"""
        pass

    @NumX.setter
    @abstractmethod
    def NumX(self, value):
        pass

    @property
    @abstractmethod
    def NumY(self):
        """The height of the subframe in binned pixels. (`int`)"""
        pass

    @NumY.setter
    @abstractmethod
    def NumY(self, value):
        pass

    @property
    @abstractmethod
    def Offset(self):
        """
        The camera's offset OR index of the selected camera offset description.
        See below for more information. (`int`)

        Represents either the camera's offset, or the 0-index of the selected
        camera offset description in the `Offsets` array.

        Depending on a camera's capabilities, the driver can support none, one, or both
        representation modes, but only one mode will be active at a time.

        To determine operational mode, read the `OffsetMin`, `OffsetMax`, and `Offsets` properties.

        `ReadoutMode` may affect the gain of the camera, so it is recommended to set
        driver behavior to ensure no conflictions occur if both `Gain` and `ReadoutMode` are used.
        """
        pass

    @Offset.setter
    @abstractmethod
    def Offset(self, value):
        pass

    @property
    @abstractmethod
    def OffsetMax(self):
        """The maximum offset value supported by the camera. (`int`)"""
        pass

    @property
    @abstractmethod
    def OffsetMin(self):
        """The minimum offset value supported by the camera. (`int`)"""
        pass

    @property
    @abstractmethod
    def Offsets(self):
        """The array of camera offset descriptions supported by the camera. (`list` of `str`)"""
        pass

    @property
    @abstractmethod
    def PercentCompleted(self):
        """
        The percentage of completion of the current operation. (`int`)

        As opposed to `CoolerPower`, this is represented as an integer
        s.t. 0 <= PercentCompleted <= 100 instead of float.
        """
        pass

    @property
    @abstractmethod
    def PixelSizeX(self):
        """The width of the CCD chip pixels in microns. (`float`)"""
        pass

    @property
    @abstractmethod
    def PixelSizeY(self):
        """The height of the CCD chip pixels in microns. (`float`)"""
        pass

    @property
    @abstractmethod
    def ReadoutMode(self):
        """
        Current readout mode of the camera as an index. (`int`)

        The index corresponds to the `ReadoutModes` array.
        """
        pass

    @ReadoutMode.setter
    @abstractmethod
    def ReadoutMode(self, value):
        pass

    @property
    @abstractmethod
    def ReadoutModes(self):
        """The array of camera readout mode descriptions supported by the camera. (`list` of `str`)"""
        pass

    @property
    @abstractmethod
    def SensorName(self):
        """
        The name of the sensor in the camera. (`str`)

        The name is the manufacturer's data sheet part number.
        """
        pass

    @property
    @abstractmethod
    def SensorType(self):
        """
        The type of color information the camera sensor captures. (`enum`)

        Possible types and the corresponding values are at the discretion of the camera manufacturer.
        In case of a lack of specification, discretion is at the developer.
        See :py:attr:`ASCOMCamera.SensorType` for an example.
        """
        pass

    @property
    @abstractmethod
    def SetCCDTemperature(self):
        """
        The set-target CCD temperature in degrees Celsius. (`float`)

        Contrary to `CCDTemperature`, which is the current CCD temperature,
        this property is the target temperature for the cooler to reach.
        """
        pass

    @SetCCDTemperature.setter
    @abstractmethod
    def SetCCDTemperature(self, value):
        pass

    @property
    @abstractmethod
    def StartX(self):
        """The set X/column position of the start subframe in binned pixels. (`int`)"""
        pass

    @StartX.setter
    @abstractmethod
    def StartX(self, value):
        pass

    @property
    @abstractmethod
    def StartY(self):
        """The set Y/row position of the start subframe in binned pixels. (`int`)"""
        pass

    @StartY.setter
    @abstractmethod
    def StartY(self, value):
        pass

    @property
    @abstractmethod
    def SubExposureDuration(self):
        """The duration of the subframe exposure interval in seconds. (`float`)"""
        pass

    @SubExposureDuration.setter
    @abstractmethod
    def SubExposureDuration(self, value):
        pass
