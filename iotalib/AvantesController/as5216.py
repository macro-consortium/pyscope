"""
as5216 Avantes Driver Wrapper
Bryan Prather-Huff
"""

import ctypes as C
import atexit
import os
import time

"""
The following code was lifted from work done by
Kevin Ivarsen at PlaneWave Instruments and is used with permission.
"""

### Utility Classes ###


class Enum:

    """
    Similar to a C# enum. Name can be converted to value,
    and value and be converted to string name. Useful for
    defining constants where you might want to look up
    the name of a given numeric value.

    Example:

    commands = Enum(
        GET_TEMP = 0x01,
        GET_RATE = 0x02,
        SET_RATE = 0x03
        )

    sendCommand(commands.GET_TEMP)
    print commands.getName(0x01) # GET_TEMP
    """

    def __init__(self, **kwargs):
        # Use keyword args to map names to values
        self._namesToValues = kwargs
        self._valuesToNames = dict()
        for k, v in list(self._namesToValues.items()):
            self._valuesToNames[v] = k

    def getName(self, value):
        return self._valuesToNames.get(value, "UNKNOWN(%r)" % value)

    def __getattr__(self, name):
        return self._namesToValues[name]

"""
Types, Structures, and Enumerators
Refrence Avantes 64x driver documentation and Avantes the as5216x64 header (as5216.h)
"""

"""
Enumerators
"""
SensorType = Enum(
    RESERVED=0,
    SENS_HAMS8378_256=1,
    SENS_HAMS8378_1024=2,
    SENS_ILX554=3,
    SENS_HAMS9201=4,
    SENS_TCD1304=5,
    SENS_TSL1301=6,
    SENS_TSL1401=7,
    SENS_HAMS8378_512=8,
    SENS_HAMS9840=9,
    SENS_ILX511=10,
    SENS_HAMS10420_2048X64=11,
    SENS_HAMS11071_2048X64=12,
    SENS_HAMS7031_1024X122=13,
    SENS_HAMS7031_1024X58=14,
    SENS_HAMS11071_2048X16=15,
    SENS_HAMS11155=16,
    SENS_SU256LSB=17,
    SENS_SU512LDB=18
)

"""
SensorType = C.c_char
RESERVED = SensorType(0)
SENS_HAMS8378_256 = SensorType(1)
SENS_HAMS8378_1024 = SensorType(2)
SENS_ILX554 = SensorType(3)
SENS_HAMS9201 = SensorType(4)
SENS_TCD1304 = SensorType(5)
SENS_TSL1301 = SensorType(6)
SENS_TSL1401 = SensorType(7)
SENS_HAMS8378_512 = SensorType(8)
SENS_HAMS9840 = SensorType(9)
SENS_ILX511 = SensorType(10)
SENS_HAMS10420_2048X64 = SensorType(11)
SENS_HAMS11071_2048X64 = SensorType(12)
SENS_HAMS7031_1024X122 = SensorType(13)
SENS_HAMS7031_1024X58 = SensorType(14)
SENS_HAMS11071_2048X16 = SensorType(15)
SENS_HAMS11155 = SensorType(16)
SENS_SU256LSB = SensorType(17)
SENS_SU512LDB = SensorType(18)
"""

DeviceStatus = Enum(
    UNKNOWN=0,
    AVALIBLE=1,
    IN_USE_BY_APPLICATION=2,
    IN_USE_BY_OTHER=3
)

"""
DeviceStatus = C.c_char
UNKNOWN = DeviceStatus(0)
AVALIBLE = DeviceStatus(1)
IN_USE_BY_APPLICATION = DeviceStatus(2)
IN_USE_BY_OTHER = DeviceStatus(3)
"""

PAR_ERROR = Enum(

    DEV_SUCCESS=1,
    ERR_SUCCESS=0,
    ERR_INVALID_PARAMETER=-1,
    ERR_OPERATION_NOT_SUPPORTED=-2,
    ERR_DEVICE_NOT_FOUND=-3,
    ERR_INVALID_DEVICE_ID=-4,
    ERR_OPERATION_PENDING=-5,
    ERR_TIMEOUT=-6,
    ERR_INVALID_PASSWORD=-7,
    ERR_INVALID_MEAS_DATA=-8,
    ERR_INVALID_SIZE=-9,
    ERR_INVALID_PIXEL_RANGE=-10,
    ERR_INVALID_INT_TIME=-11,
    ERR_INVALID_COMBINATION=-12,
    ERR_INVALID_CONFIGURATION=-13,
    ERR_NO_MEAS_BUFFER_AVAIL=-14,
    ERR_UNKNOWN=-15,
    ERR_COMMUNICATION=-16,
    ERR_NO_SPECTRA_IN_RAM=-17,
    ERR_INVALID_DLL_VERSION=-18,
    ERR_NO_MEMORY=-19,
    ERR_DLL_INITIALISATION=-20,
    ERR_INVALID_STATE=-21,


    ERR_INVALID_PARAMETER_NR_PIXELS=-100,
    ERR_INVALID_PARAMETER_ADC_GAIN=-101,
    ERR_INVALID_PARAMETER_ADC_OFFSET=-102,


    ERR_INVALID_MEASPARAM_AVG_SAT2=-110,
    ERR_INVALID_MEASPARAM_AVG_RAM=-111,
    ERR_INVALID_MEASPARAM_SYNC_RAM=-112,
    ERR_INVALID_MEASPARAM_LEVEL_RAM=-113,
    ERR_INVALID_MEASPARAM_SAT2_RAM=-114,
    ERR_INVALID_MEASPARAM_FWVER_RAM=-115,
    ERR_INVALID_MEASPARAM_DYNDARK=-116,


    ERR_NOT_SUPPORTED_BY_SENSOR_TYPE=-120,
    ERR_NOT_SUPPORTED_BY_FW_VER=-121,
    ERR_NOT_SUPPORTED_BY_FPGA_VER=-122,

    UNCONFIGURED_DEVICE_OFFSET=256,
    INVALID_AVS_HANDLE_VALUE=1000
)


"""
Structures & Types
"""

AvsHandle = C.c_long
Spectrum = (C.c_double*3648)


class AvsIdentityType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("SerialID", C.c_char * 10),
        ("UserFriendlyID", C.c_char * 64),
        ("DeviceStatus", C.c_ubyte)
    ]


class ControlSettingsType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("StrobeControl", C.c_ushort),
        ("LaserDelay", C.c_uint),
        ("LaserWidth", C.c_uint),
        ("LaserWaveLength", C.c_float),
        ("StoreToRam", C.c_ushort)
    ]


class DarkCorrectionType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("Enable", C.c_ubyte),
        ("ForgetPercentage", C.c_ubyte)
    ]


class TriggerType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("Mode", C.c_ubyte),
        ("Source", C.c_ubyte),
        ("SourceType", C.c_ubyte)
    ]


class DetectorType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("SensorType", C.c_ubyte),
        ("NrPixels", C.c_ushort),
        ("aFit", C.c_float * 5),
        ("NLEnable", C.c_bool),
        ("aNLCorrect", C.c_double * 8),
        ("aLowNLCounts", C.c_double),
        ("aHighNLCounts", C.c_double),
        ("Gain", C.c_float * 2),
        ("Reserved", C.c_float),
        ("Offset", C.c_float * 2),
        ("ExtOffset", C.c_float),
        ("DefectivePixels", C.c_ushort)
    ]


class ProcessControlType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("AnalogLow", C.c_float * 2),
        ("AnalogHigh", C.c_float * 2),
        ("DigitalLow", C.c_float * 10),
        ("DigitalHigh", C.c_float * 10)
    ]


class SmoothingType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("SmoothPix", C.c_ushort),
        ("SmoothModel", C.c_ubyte)
    ]


class SpectrumCalibrationType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("Smoothing", SmoothingType),
        ("CalInttime", C.c_float),
        ("aCalibConvers", C.c_float * 3648)
    ]


class SpectrumCorrectionType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("aSpectrumCorrect", C.c_float * 3648)
    ]


class MeasConfigType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("StartPixel", C.c_ushort),
        ("StopPixel", C.c_ushort),
        ("IntegrationTime", C.c_float),
        ("IntegrationDelay", C.c_uint),
        ("NrAverages", C.c_uint),
        ("CorDynDark", DarkCorrectionType),
        ("Smoothing", SmoothingType),
        ("SaturationDetection", C.c_ubyte),
        ("Trigger", TriggerType),
        ("Control", ControlSettingsType)
    ]


class TimeStampType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("Date", C.c_ushort),
        ("Time", C.c_ushort)
    ]


class SDCardType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("Enable", C.c_bool),
        ("SpectrumType", C.c_char),
        ("aFileRootName", C.c_char * 6),
        ("TimeStamp", TimeStampType)
    ]


class StandaloneType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("Enable", C.c_bool),
        ("Meas", MeasConfigType),
        ("Nmsr", C.c_short),
        ("SDCard", SDCardType)
    ]


class TecControlType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("Enable", C.c_bool),
        ("Setpoint", C.c_float),
        ("aFit", C.c_float * 2)
    ]


class TempSensorType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("aFit", C.c_float * 5)
    ]


class IrradianceType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("IntensityCalib", SpectrumCalibrationType),
        ("CalibrationType", C.c_char),
        ("FiberDiameter", C.c_uint)
    ]


class DeviceConfigType(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("Len", C.c_ushort),
        ("ConfigVersion", C.c_ushort),
        ("UserFriendlyID", C.c_char * 64),
        ("Detector", DetectorType),
        ("Irradiance", IrradianceType),
        ("Reflectance", SpectrumCalibrationType),
        ("SpectrumCorrect", SpectrumCorrectionType),
        ("StandAlone", StandaloneType),
        ("aTemperature", TempSensorType * 3),
        ("TecControl", TecControlType),
        ("ProcessControl", ProcessControlType),
        ("aReserved", C.c_ubyte * 13832)
    ]

"""
Begin external interface definition
"""


class AvantesException(Exception):

    def __init__(self, avsErrorCode, message=None):
        self.avsErrorCode = avsErrorCode
        if message is None:
            message = "Avantes ERROR %d (%s)" % (
                self.avsErrorCode, self.getErrorName())

        super(AvantesException, self).__init__(message)

    def getErrorName(self):
        return PAR_ERROR.getName(self.avsErrorCode)


class AvantesDriver(object):

    def __init__(self):
        # Load required libraries
        os.environ['PATH'] = os.path.dirname(__file__) + ';' + os.environ['PATH']
        #self.qtcore = C.windll.LoadLibrary("QtCore4.dll")
        self.avsdrvr = C.WinDLL("AS5216.dll")

        # Device Identifiers / Information
        self.deviceID = AvsIdentityType()
        self.devicehandle = AvsHandle()
        self.lambdaWave = Spectrum()
        self.numPixels = C.c_ushort()
        self.devConfig = DeviceConfigType()
        self.lastMeasurement = Spectrum()
        self.lastSaturated = Spectrum()
        self.FPGAVersion = C.c_ubyte * 16
        self.FirmwareVersion = C.c_ubyte * 16
        self.DLLVersion = C.c_ubyte * 16

        # Dark Correction
        self.darkCorr = DarkCorrectionType()
        self.darkCorr.Enable = 0
        self.darkCorr.ForgetPercentage = 0

        # Smoothing Model
        self.smooth = SmoothingType()
        self.smooth.SmoothPix = 2
        self.smooth.SmoothModel = 0

        # Trigger Setup
        self.triggerSet = TriggerType()
        self.triggerSet.Mode = 0
        self.triggerSet.Source = 0
        self.triggerSet.SourceType = 0

        # Control Settings
        self.controlSet = ControlSettingsType()
        self.controlSet.StrobeControl = 0
        self.controlSet.LaserDelay = 0
        self.controlSet.LaserWidth = 0
        self.controlSet.LaserWaveLength = 0
        self.controlSet.StoreToRam = 0

        # Measurement Config
        self.config = MeasConfigType()
        self.config.StartPixel = 0
        self.config.StopPixel = 3647
        self.config.IntegrationTime = 500
        self.config.IntegrationDelay = 0
        self.config.NrAverages = 1
        self.config.CorDynDark = self.darkCorr
        self.config.Smoothing = self.smooth
        self.config.SaturationDetection = 1
        self.config.Trigger = self.triggerSet
        self.config.Control = self.controlSet

    def __enter__(self):
        atexit.register(self.AVS_Done)
        return self

    def AVS_Init(self):
        errorCode = self.avsdrvr.AVS_Init(0)

        if errorCode != PAR_ERROR.DEV_SUCCESS:
            raise AvantesException(errorCode)

    def AVS_Done(self):
        errorCode = self.avsdrvr.AVS_Done()

        return errorCode

    def AVS_GetNrOfDevices(self):
        errorCode = self.avsdrvr.AVS_GetNrOfDevices(None)
        
        # NOTE FROM KEVIN:
        # Return code is:
        #  0 = No devices found
        #  > 0 = Number of devices found
        # This code technically works if exactly one device is found,
        # but AvantesException won't report a valid error type if
        # more than one device is connected.
        # Instead, just return the result of AVS_GetNrOfDevices directly.
        
        if errorCode != PAR_ERROR.DEV_SUCCESS:
            raise AvantesException(errorCode)
        return errorCode

    def AVS_GetList(self):
        deviceList = (AvsIdentityType*4)() # create array that can contain up to 4 AVS devices
        listSize = C.c_uint(C.sizeof(deviceList)) # get size of our array, in bytes
        #listSize = C.c_uint(75)
        reqSize = C.c_uint()

        errorCode = self.avsdrvr.AVS_GetList(
            listSize, C.byref(reqSize), C.byref(deviceList)) # C.byref(self.deviceID))
        print("GetList reqSize =", reqSize)

        if errorCode == PAR_ERROR.ERR_INVALID_SIZE:
            listSize = C.c_uint(reqSize.value)
            reqSize = C.c_uint()

            errorCode = self.avsdrvr.AVS_GetList(
                listSize, C.byref(reqSize), C.byref(self.deviceID))

        print("Number of devices =", errorCode)
        for device in deviceList:
            print(device.SerialID, device.UserFriendlyID, device.DeviceStatus)
                
        if errorCode == PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(0, "Avantes ERROR NULL (No Devices Found)")

        if errorCode < PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)
           
        self.deviceID = deviceList[0]
        print('Listed')
        return

    def AVS_Activate(self):
        errorCode = self.avsdrvr.AVS_Activate(C.byref(self.deviceID))
        self.devicehandle = C.c_long(errorCode)

        if errorCode == 1000:
            raise AvantesException(1000)
        print('Activated')
        return

    def AVS_Deactivate(self):
        errorCode = self.avsdrvr.AVS_Deactivate(self.devicehandle)

        if not C.c_bool(errorCode).value:
            raise AvantesException(
                0, "Avantes ERROR NULL (Failed to disconnect)")

    def AVS_PrepareMeasure(self):
        errorCode = self.avsdrvr.AVS_PrepareMeasure(
            self.devicehandle, C.byref(self.config))

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

    def AVS_Measure(self):
        errorCode = self.avsdrvr.AVS_Measure(
            self.devicehandle, None, C.c_short(10))

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

    def AVS_GetLambda(self):
        self.lambdaWave = Spectrum()
        errorCode = self.avsdrvr.AVS_GetLambda(
            self.devicehandle, C.byref(self.lambdaWave))

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

        return list(self.lambdaWave)

    def AVS_GetNumPixels(self):
        errorCode = self.avsdrvr.AVS_GetNumPixels(
            self.devicehandle, C.byref(self.numPixels))

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

        self.config.StopPixel = C.c_ushort(self.numPixels.value - 1)

        return self.numPixels.value

    def AVS_GetParameter(self):
        listSize = C.c_uint(63484)
        reqSize = C.c_uint()
        errorCode = self.avsdrvr.AVS_GetParameter(
            self.devicehandle, listSize, C.byref(reqSize), C.byref(self.devConfig))

        if errorCode == PAR_ERROR.ERR_INVALID_SIZE:
            listSize = C.c_uint(reqSize.value)
            reqSize = C.c_uint()

            errorCode = self.avsdrvr.AVS_GetParameter(
                self.devicehandle, listSize, C.byref(reqSize), C.byref(self.devConfig))

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

    def AVS_PollScan(self):
        errorCode = self.avsdrvr.AVS_PollScan(self.devicehandle)

        if errorCode == 1:
            return True
        elif errorCode == 0:
            return False
        else:
            raise AvantesException(errorCode)

    def AVS_GetScopeData(self):
        timeLabel = C.c_uint()
        self.lastMeasurement = Spectrum()
        errorCode = self.avsdrvr.AVS_GetScopeData(
            self.devicehandle, C.byref(timeLabel), C.byref(self.lastMeasurement))

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

        return list(self.lastMeasurement)

    def AVS_GetSaturatedPixels(self):
        self.lastSaturated = Spectrum()
        errorCode = self.avsdrvr.AVS_GetSaturatedPixels(
            self.devicehandle, C.byref(self.lastSaturated))

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

        return list(self.lastSaturated)

    def AVS_StopMeasure(self):
        errorCode = self.avsdrvr.AVS_StopMeasure(self.devicehandle)

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

    def AVS_SetPrescanMode(self):
        errorCode = self.avsdrvr.AVS_SetPrescanMode(
            self.devicehandle, C.c_bool(True))

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

    def AVS_GetVersionInfo(self):
        self.FPGAVersion = self.FPGAVersion()
        self.FirmwareVersion = self.FirmwareVersion()
        self.DLLVersion = self.DLLVersion()

        errorCode = self.avsdrvr.AVS_GetVersionInfo(self.devicehandle, C.byref(
            self.FPGAVersion), C.byref(self.FirmwareVersion), C.byref(self.DLLVersion))

        if errorCode != PAR_ERROR.ERR_SUCCESS:
            raise AvantesException(errorCode)

    def expose(self, intTime):
        self.config.IntegrationTime = C.c_float(intTime)
        self.AVS_PrepareMeasure()
        self.AVS_Measure()
        print("Measuring")
        while True:
            if self.AVS_PollScan():
                break
            else:
                time.sleep(0.1)
            print('Polling')
        print('Stopping Measure') 
        self.AVS_StopMeasure()
        print('Storing Spec')
        spec = self.AVS_GetScopeData()
        print('Stored Spec')
        return spec

    def close(self):
        self.AVS_StopMeasure()
        self.AVS_Deactivate()
        return self.AVS_Done()

    def __exit__(self, exct_type, exce_value, traceback):
        self.close()