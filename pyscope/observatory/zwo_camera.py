import logging
import pathlib

import numpy as np
import zwoasi as asi
from astropy.time import Time

from .camera import Camera

logger = logging.getLogger(__name__)

lib_path = pathlib.Path(
    r"C:\Users\MACRO\Downloads\ASI_Camera_SDK\ASI_Camera_SDK\ASI_Windows_SDK_V1.37\ASI SDK\lib\x64\ASICamera2.dll"
)
print(lib_path)

asi.init(lib_path)


class ZWOCamera(Camera):
    def __init__(self, device_number=0):
        logger.debug(f"ZWOCamera.__init__({device_number})")

        self._device = asi.Camera(device_number)
        self._camera_info = self._device.get_camera_property()
        # Use minimum USB bandwidth permitted
        self._device.set_control_value(
            asi.ASI_BANDWIDTHOVERLOAD,
            self._device.get_controls()["BandWidth"]["MinValue"],
        )
        self._controls = self._device.get_controls()
        self._last_exposure_duration = None
        self._last_exposure_start_time = None
        self._image_data_type = None
        self._DoTranspose = True
        self._camera_time = True
        self._binX = 1
        self._NumX = self._camera_info["MaxWidth"]
        self._NumY = self._camera_info["MaxHeight"]
        self._StartX = 0
        self._StartY = 0

    def AbortExposure(self):
        logger.debug(f"ASICamera.AbortExposure() called")
        self._device.stop_exposure()

    def SetImageDataType(self):
        """Determine the data type of the image array based on the MaxADU property.

        This method is called automatically when the ImageArray property is called
        if it has not already been set (initializes to `None`).
        It will choose from the following data types based on the MaxADU property:

        - numpy.uint8 : (if MaxADU <= 255)
        - numpy.uint16 : (default if MaxADU is not defined, or if MaxADU <= 65535)
        - numpy.uint32 : (if MaxADU > 65535)

        See Also
        --------
        numpy.uint8
        numpy.uint16
        numpy.uint32
        MaxADU : ASCOM Camera interface property `ASCOM Documentation <https://ascom-standards.org/Help/Developer/html/P_ASCOM_DriverAccess_Camera_MaxADU.htm>`_
        """
        logger.debug(f"ASCOMCamera.SetImageDataType() called")
        try:
            max_adu = self.MaxADU
            if max_adu <= 255:
                self._image_data_type = np.uint8
            elif max_adu <= 65535:
                self._image_data_type = np.uint16
            else:
                self._image_data_type = np.uint32
        except:
            self._image_data_type = np.uint16

    def PulseGuide(self, Direction, Duration):
        logger.debug(f"ASCOMCamera.PulseGuide({Direction}, {Duration}) called")
        pass

    def StartExposure(self, Duration, Light):
        logger.debug(f"ASCOMCamera.StartExposure({Duration}, {Light}) called")

        # Set up ROI and binning
        bins = self.BinX
        startX = self.StartX
        startY = self.StartY

        max_bin_width = int(self.CameraXSize / bins)
        max_bin_height = int(self.CameraYSize / bins)
        # Fix using lines 479+ in zwoasi init
        if self.NumX > max_bin_width:
            self.NumX = max_bin_width
        if self.NumY > max_bin_height:
            self.NumY = max_bin_height

        width = self.NumX
        height = self.NumY

        image_type = asi.ASI_IMG_RAW16
        whbi_old = self._device.get_roi_format()
        whbi_new = [width, height, bins, image_type]
        if whbi_old != whbi_new:
            self._device.set_roi(startX, startY, width, height, bins, image_type)

        self._last_exposure_duration = Duration
        self._last_exposure_start_time = str(Time.now())
        self.Exposure = Duration
        dark = not Light
        print(f"Dark: {dark}")
        self._device.start_exposure(dark)

    def StopExposure(self):
        logger.debug(f"ASCOMCamera.StopExposure() called")
        self._device.stop_exposure()

    @property
    def BayerOffsetX(self):  # pragma: no cover
        """
        .. warning::
            This property is not implemented in the ASCOM Alpaca protocol.
        """
        logger.debug(f"ASCOMCamera.BayerOffsetX property called")
        pass

    @property
    def BayerOffsetY(self):  # pragma: no cover
        """
        .. warning::
            This property is not implemented in the ASCOM Alpaca protocol.
        """
        logger.debug(f"ASCOMCamera.BayerOffsetY property called")
        pass

    @property
    def BinX(self):
        logger.debug(f"ASCOMCamera.BinX property called")
        return self._BinX

    @BinX.setter
    def BinX(self, value):
        logger.debug(f"ASCOMCamera.BinX property set to {value}")
        self._BinX = value

    @property
    def BinY(self):
        logger.debug(
            f"ASCOMCamera.BinY property called - Symmetric binning only - use BinX property"
        )
        return self.BinX

    @BinY.setter
    def BinY(self, value):
        logger.debug(
            f"ASCOMCamera.BinY setter called - Symmetric binning only - use BinX property"
        )
        pass

    @property
    def CameraState(self):
        logger.debug(f"ASCOMCamera.CameraState property called")
        return self._device.get_exposure_status()

    @property
    def CameraXSize(self):
        logger.debug(f"ASCOMCamera.CameraXSize property called")
        return self._camera_info["MaxWidth"]

    @property
    def CameraYSize(self):
        logger.debug(f"ASCOMCamera.CameraYSize property called")
        return self._camera_info["MaxHeight"]

    @property
    def CameraTime(self):
        logger.debug(f"ASCOMCamera.CameraTime property called")
        return self._camera_time

    @property
    def CanAbortExposure(self):
        logger.debug(f"ASCOMCamera.CanAbortExposure property called")
        return False

    @property
    def CanAsymmetricBin(self):
        logger.debug(f"ASCOMCamera.CanAsymmetricBin property called")
        return False

    @property
    def CanFastReadout(self):
        logger.debug(f"ASCOMCamera.CanFastReadout property called")
        return False

    @property
    def CanGetCoolerPower(self):
        logger.debug(f"ASCOMCamera.CanGetCoolerPower property called")
        return False

    @property
    def CanPulseGuide(self):
        logger.debug(f"ASCOMCamera.CanPulseGuide property called")
        return False

    @property
    def CanSetCCDTemperature(self):
        logger.debug(f"ASCOMCamera.CanSetCCDTemperature property called")
        return self._camera_info["IsCoolerCam"]

    @property
    def CanStopExposure(self):
        logger.debug(f"ASCOMCamera.CanStopExposure property called")
        return True

    @property
    def CCDTemperature(self):
        logger.debug(f"ASCOMCamera.CCDTemperature property called")
        return self._device.get_control_value(asi.ASI_TEMPERATURE)[0] / 10

    @property
    def CoolerOn(self):
        logger.debug(f"ASCOMCamera.CoolerOn property called")
        return self._device.get_control_value(asi.ASI_COOLER_ON)[0]

    @CoolerOn.setter
    def CoolerOn(self, value):
        logger.debug(f"ASCOMCamera.CoolerOn property set to {value}")
        self._device.set_control_value(asi.ASI_COOLER_ON, value)

    @property
    def CoolerPower(self):
        logger.debug(f"ASCOMCamera.CoolerPower property called")
        return self._device.get_control_value(asi.ASI_COOLER_POWER)[0]

    @property
    def DriverVersion(self):
        logger.debug(f"ASCOMCamera.DriverVersion property called")
        return "Custom Driver"

    @property
    def DriverInfo(self):
        logger.debug(f"ASCOMCamera.DriverInfo property called")
        return ["Custom Driver for ZWO ASI Cameras", 1]

    @property
    def Description(self):
        logger.debug(f"ASCOMCamera.Description property called")
        return self._camera_info["Name"]

    @property
    def ElectronsPerADU(self):
        logger.debug(f"ASCOMCamera.ElectronsPerADU() property called")
        return self._device.get_camera_property()["ElecPerADU"] * self.BinX * self.BinY

    @property
    def Exposure(self):
        """
        Get the exposure time in seconds. The exposure time is the time that the camera will be collecting light from the sky. The exposure time must be greater than or equal to the minimum exposure time and less than or equal to the maximum exposure time. The exposure time is specified in seconds.

        Returns
        -------
        float
            The exposure time in seconds.
        """
        logger.debug(f"ZWOASI.Exposure property called")
        # Convert to seconds
        return self._device.get_control_value(asi.ASI_EXPOSURE)[0] / 1e6

    @Exposure.setter
    def Exposure(self, value):
        """
        Set the exposure time in seconds. The exposure time is the time that the camera will be collecting light from the sky. The exposure time must be greater than or equal to the minimum exposure time and less than or equal to the maximum exposure time. The exposure time is specified in seconds.

        Parameters
        ----------
        value : float
            The exposure time in seconds.
        """
        logger.debug(f"ZWOASI.Exposure property set to {value}")
        # Convert to microseconds
        value = int(value * 1e6)
        self._device.set_control_value(asi.ASI_EXPOSURE, value)

    @property
    def ExposureMax(self):
        logger.debug(f"ASCOMCamera.ExposureMax property called")
        exp_max = self._controls["Exposure"]["MaxValue"]
        exp_max /= 1e6
        return exp_max

    @property
    def ExposureMin(self):
        logger.debug(f"ASCOMCamera.ExposureMin property called")
        exp_min = self._controls["Exposure"]["MinValue"]
        exp_min /= 1e6
        return exp_min

    @property
    def ExposureResolution(self):
        logger.debug(f"ASCOMCamera.ExposureResolution property called")
        return False

    @property
    def FastReadout(self):
        logger.debug(f"ASCOMCamera.FastReadout property called")
        return False

    @FastReadout.setter
    def FastReadout(self, value):
        logger.debug(f"ASCOMCamera.FastReadout property set to {value}")
        self._device.FastReadout = value

    @property
    def FullWellCapacity(self):
        logger.debug(f"Not implemented in ZWO ASI")
        pass

    @property
    def Gain(self):
        logger.debug(f"ASCOMCamera.Gain property called")
        return self._device.get_control_value(asi.ASI_GAIN)[0]

    @Gain.setter
    def Gain(self, value):
        logger.debug(f"ZWO ASI Gain set to {value}")
        self._device.set_control_value(asi.ASI_GAIN, value)
        self._device.Gain = value
        # Add in ElecPerADU updater here and remove in ElectronsPerADU
        # property for speed up.

    @property
    def GainMax(self):
        logger.debug(f"ASCOMCamera.GainMax property called")
        return self._controls["Gain"]["MaxValue"]

    @property
    def GainMin(self):
        logger.debug(f"ASCOMCamera.GainMin property called")
        return self._controls["Gain"]["MinValue"]

    @property
    def Gains(self):
        logger.debug(f"No Gains property in ZWO ASI")
        pass

    @property
    def HasShutter(self):
        logger.debug(f"ZWOASI.HasShutter property called")
        return False

    @property
    def HeatSinkTemperature(self):
        logger.debug(f"ASCOMCamera.HeatSinkTemperature property called")
        return False

    @property
    def ImageArray(self):
        """Return the image array as a numpy array of the correct data type and in
        standard FITS orientation. \b

        Return the image array as a numpy array of the correct data type. The
        data type is determined by the MaxADU property. If the MaxADU property
        is not defined, or if it is less than or equal to 65535, the data type
        will be numpy.uint16. If the MaxADU property is greater than 65535, the
        data type will be numpy.uint32.

        .. Note::
            The image array is returned in the standard FITS orientation, which
            deviates from the ASCOM standard (see below).

        The image array is returned in the standard FITS orientation, with the
        rows and columns transposed (if `_DoTranspose` is `True`). This is the same orientation as the
        astropy.io.fits package. This is done because the ASCOM standard
        specifies that the image array should be returned with the first index
        being the column and the second index being the row. This is the
        opposite of the FITS standard, which specifies that the first index
        should be the row and the second index should be the column. The
        astropy.io.fits package follows the FITS standard, so the image array
        returned by the pyscope ASCOM driver is transposed to match the FITS
        standard.

        Parameters
        ----------
        None

        Returns
        -------
        numpy.ndarray
            The image array as a numpy array of the correct data type.
            Rows and columns are transposed to match the FITS standard.

        """
        logger.debug(f"ASCOMCamera.ImageArray property called")

        data = self._device.get_data_after_exposure(None)
        whbi = self._device.get_roi_format()
        shape = [whbi[1], whbi[0]]
        if whbi[3] == asi.ASI_IMG_RAW8 or whbi[3] == asi.ASI_IMG_Y8:
            img = np.frombuffer(data, dtype=np.uint8)
        elif whbi[3] == asi.ASI_IMG_RAW16:
            img = np.frombuffer(data, dtype=np.uint16)
        elif whbi[3] == asi.ASI_IMG_RGB24:
            img = np.frombuffer(data, dtype=np.uint8)
            shape.append(3)
        else:
            raise ValueError("Unsupported image type")
        img = img.reshape(shape)
        # Done by default in zwoasi
        # if self._DoTranspose:
        #     img_array = np.transpose(img_array)
        return img

    @property
    def ImageReady(self):
        logger.debug(f"ASCOMCamera.ImageReady property called")
        status = self._device.get_exposure_status()
        image_ready = False
        if status == asi.ASI_EXP_SUCCESS:
            image_ready = True
        return image_ready

    @property
    def IsPulseGuiding(self):
        logger.debug(f"ASCOMCamera.IsPulseGuiding property called")
        return False

    @property
    def LastExposureDuration(self):
        logger.debug(f"ASCOMCamera.LastExposureDuration property called")
        return self.LastInputExposureDuration

    @property
    def LastExposureStartTime(self):
        logger.debug(f"ASCOMCamera.LastExposureStartTime property called")
        last_time = self._device.LastExposureStartTime
        """ This code is needed to handle the case of the ASCOM ZWO driver
        which returns an empty string instead of None if the camera does not
        support the property """
        return (
            last_time
            if last_time != "" and last_time != None
            else self._last_exposure_start_time
        )

    @property
    def LastInputExposureDuration(self):
        logger.debug(f"ASCOMCamera.LastInputExposureDuration property called")
        return self._last_exposure_duration

    @LastInputExposureDuration.setter
    def LastInputExposureDuration(self, value):
        logger.debug(f"ASCOMCamera.LastInputExposureDuration property set to {value}")
        self._last_exposure_duration = value

    @property
    def MaxADU(self):
        logger.debug(f"ASCOMCamera.MaxADU property called")
        return 65535

    @property
    def MaxBinX(self):
        logger.debug(f"ASCOMCamera.MaxBinX property called")
        return self._camera_info["SupportedBins"][-1]

    @property
    def MaxBinY(self):
        logger.debug(f"ASCOMCamera.MaxBinY property called")
        return self._camera_info["SupportedBins"][-1]

    @property
    def NumX(self):
        logger.debug(f"ASCOMCamera.NumX property called")
        return self._NumX

    @NumX.setter
    def NumX(self, value):
        logger.debug(f"ASCOMCamera.NumX property set to {value}")
        width = value
        if width % 8 != 0:
            width -= width % 8  # Make width a multiple of 8
        self._NumX = width

    @property
    def NumY(self):
        logger.debug(f"ASCOMCamera.NumY property called")
        return self._NumY

    @NumY.setter
    def NumY(self, value):
        logger.debug(f"ASCOMCamera.NumY property set to {value}")
        # Set height to next multiple of 2
        height = value
        if height % 2 != 0:
            height -= 1  # Make height even
        self._NumY = height

    @property
    def Offset(self):
        logger.debug(f"ASCOMCamera.Offset property called")
        return self._device.get_control_value(asi.ASI_OFFSET)[0]

    @Offset.setter
    def Offset(self, value):
        logger.debug(f"ASCOMCamera.Offset property set to {value}")
        self._device.set_control_value(asi.ASI_OFFSET, value)

    @property
    def OffsetMax(self):
        logger.debug(f"ASCOMCamera.OffsetMax property called")
        return self._controls["Offset"]["MaxValue"]

    @property
    def OffsetMin(self):
        logger.debug(f"ASCOMCamera.OffsetMin property called")
        return self._controls["Offset"]["MinValue"]

    @property
    def Offsets(self):
        logger.debug(f"ASCOMCamera.Offsets property called")
        pass

    @property
    def PercentCompleted(self):
        logger.debug(f"ASCOMCamera.PercentCompleted property called")
        pass

    @property
    def PixelSizeX(self):
        logger.debug(f"ASCOMCamera.PixelSizeX property called")
        return self._camera_info["PixelSize"] * self.BinX

    @property
    def PixelSizeY(self):
        logger.debug(f"ASCOMCamera.PixelSizeY property called")
        return self._camera_info["PixelSize"] * self.BinY

    @property
    def ReadoutMode(self):
        logger.debug(f"ASCOMCamera.ReadoutMode property called")
        return False

    @ReadoutMode.setter
    def ReadoutMode(self, value):
        logger.debug(f"ASCOMCamera.ReadoutMode property set to {value}")
        pass

    @property
    def ReadoutModes(self):
        logger.debug(f"ASCOMCamera.ReadoutModes property called")
        return None

    @property
    def SensorName(self):
        logger.debug(f"ASCOMCamera.SensorName property called")
        return self._camera_info["Name"]

    @property
    def Name(self):
        logger.debug(f"ASCOMCamera.Name property called")
        return self._camera_info["Name"]

    @property
    def SensorType(self):
        logger.debug(f"ASCOMCamera.SensorType property called")
        return "CMOS"

    @property
    def SetCCDTemperature(self):
        logger.debug(f"ASCOMCamera.SetCCDTemperature property called")
        return self._device.get_control_value(asi.ASI_TARGET_TEMP)[0]

    @SetCCDTemperature.setter
    def SetCCDTemperature(self, value):
        logger.debug(f"ASCOMCamera.SetCCDTemperature property set to {value}")
        self._device.set_control_value(asi.ASI_TARGET_TEMP, value)

    @property
    def StartX(self):
        logger.debug(f"ASCOMCamera.StartX property called")
        return self._StartX

    @StartX.setter
    def StartX(self, value):
        logger.debug(f"ASCOMCamera.StartX property set to {value}")
        self._StartX = value

    @property
    def StartY(self):
        logger.debug(f"ASCOMCamera.StartY property called")
        return self._StartY

    @StartY.setter
    def StartY(self, value):
        logger.debug(f"ASCOMCamera.StartY property set to {value}")
        self._StartY = value

    @property
    def SubExposureDuration(self):
        logger.debug(f"ASCOMCamera.SubExposureDuration property called")
        pass

    @SubExposureDuration.setter
    def SubExposureDuration(self, value):
        logger.debug(f"ASCOMCamera.SubExposureDuration property set to {value}")
        pass
