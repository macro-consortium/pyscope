"""
Wraps the SBIG Universal Driver Library using the ctypes Python module
Developed by Kevin Ivarsen at PlaneWave Instruments

SBIG Driver Documentation: 
http://archive.sbig.com/pdffiles/SBIGUDrv.pdf

For special notes on the ST-i camera, refer to section 5.11 of the driver doc.

SBIG development kit (includes sbigudrv.h, which describes structures and constants)
ftp://ftp.sbig.com/pub/devsw/WinDevKit.zip
"""

import ctypes
import time

### Utility classes ###############################

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
        for k,v in list(self._namesToValues.items()):
            self._valuesToNames[v] = k

    def getName(self, value):
        return self._valuesToNames.get(value, "UNKNOWN(%r)" % value)
    
    def __getattr__(self, name):
        return self._namesToValues[name]

### Exception to be used for SBIG commands ##############
class SbigException(Exception):
    def __init__(self, sbigErrorCode, message=None):
        self.sbigErrorCode = sbigErrorCode
        if message is None:
            message = "SBIG ERROR %d (%s)" % (self.sbigErrorCode, self.getErrorName())

        super(SbigException, self).__init__(message)

    def getErrorName(self):
        return PAR_ERROR.getName(self.sbigErrorCode)

### Struct wrappers #####################################
class GetDriverInfoParams(ctypes.Structure):
    _fields_ = [("request", ctypes.c_int)]

class GetDriverInfoResults(ctypes.Structure):
    _fields_ = [
            ("version", ctypes.c_ushort),
            ("name", ctypes.c_char*512),
            ("maxRequest", ctypes.c_ushort)
        ]

class QueryUSBInfo(ctypes.Structure):
    _fields_ = [
            ("cameraFound", ctypes.c_short),
            ("cameraType", ctypes.c_ushort),
            ("name", ctypes.c_char*64),
            ("serialNumber", ctypes.c_char*10)
        ]

class QueryUSBResults(ctypes.Structure):
    _fields_ = [
            ("camerasFound", ctypes.c_ushort),
            ("usbInfo", QueryUSBInfo*4)
        ]

class OpenDeviceParams(ctypes.Structure):
    _fields_ = [
            ("deviceType", ctypes.c_ushort),
            ("lptBaseAddress", ctypes.c_ushort),
            ("ipAddress", ctypes.c_ulong)
        ]

class EstablishLinkParams(ctypes.Structure):
    _fields_ = [
            ("sbigUseOnly", ctypes.c_ushort)
        ]

class EstablishLinkResults(ctypes.Structure):
    _fields_ = [
            ("cameraType", ctypes.c_ushort)
        ]


class StartExposureParams2(ctypes.Structure):
    _fields_ = [
            ("ccd", ctypes.c_ushort),
            ("exposureTime", ctypes.c_ulong),
            ("abgState", ctypes.c_ushort),
            ("openShutter", ctypes.c_ushort),
            ("readoutMode", ctypes.c_ushort),
            ("top", ctypes.c_ushort),
            ("left", ctypes.c_ushort),
            ("height", ctypes.c_ushort),
            ("width", ctypes.c_ushort)
        ]

class EndExposureParams(ctypes.Structure):
    _fields_ = [
            ("ccd", ctypes.c_ushort)
        ]

class StartReadoutParams(ctypes.Structure):
    _fields_ = [
            ("ccd", ctypes.c_ushort),
            ("readoutMode", ctypes.c_ushort),
            ("top", ctypes.c_ushort),
            ("left", ctypes.c_ushort),
            ("height", ctypes.c_ushort),
            ("width", ctypes.c_ushort)
        ]

class EndReadoutParams(ctypes.Structure):
    _fields_ = [
            ("ccd", ctypes.c_ushort)
        ]

class ReadoutLineParams(ctypes.Structure):
    _fields_ = [
            ("ccd", ctypes.c_ushort),
            ("readoutMode", ctypes.c_ushort),
            ("pixelStart", ctypes.c_ushort),
            ("pixelLength", ctypes.c_ushort),
        ]

class SetTemperatureRegulationParams2(ctypes.Structure):
    _fields_ = [
            ("regulation", ctypes.c_ushort),
            ("ccdSetpoint", ctypes.c_double),
        ]

class QueryTemperatureStatusParams(ctypes.Structure):
    _fields_ = [
            ("request", ctypes.c_ushort)
        ]

class QueryTemperatureStatusResults2(ctypes.Structure):
    _fields_ = [
            ("coolingEnabled", ctypes.c_ushort),
            ("fanEnabled", ctypes.c_ushort),
            ("ccdSetpoint", ctypes.c_double),
            ("imagingCCDTemperature", ctypes.c_double),
            ("trackingCCDTemperature", ctypes.c_double),
            ("externalTrackingCCDTemperature", ctypes.c_double),
            ("ambientTemperature", ctypes.c_double),
            ("imagingCCDPower", ctypes.c_double),
            ("trackingCCDPower", ctypes.c_double),
            ("externalTrackingCCDPower", ctypes.c_double),
            ("heatsinkTemperature", ctypes.c_double),
            ("fanPower", ctypes.c_double),
            ("fanSpeed", ctypes.c_double),
            ("trackingCCDSetpoint", ctypes.c_double),
        ]

class GetCCDInfoParams(ctypes.Structure):
    _fields_ = [
            ("request", ctypes.c_ushort)
        ]

class READOUT_INFO(ctypes.Structure):
    _fields_ = [
            ("mode", ctypes.c_ushort),
            ("width", ctypes.c_ushort),
            ("height", ctypes.c_ushort),
            ("gain", ctypes.c_ushort),
            ("pixelWidth", ctypes.c_ulong),
            ("pixelHeight", ctypes.c_ulong),
        ]

class GetCCDInfoResults0(ctypes.Structure):
    _fields_ = [
            ("firmwareVersion", ctypes.c_ushort),
            ("cameraType", ctypes.c_ushort),
            ("name", ctypes.c_char*64),
            ("readoutModes", ctypes.c_ushort),
            ("readoutInfo", READOUT_INFO*20)
        ]

class QueryCommandStatusParams(ctypes.Structure):
    _fields_ = [
            ("command", ctypes.c_ushort)
        ]

class QueryCommandStatusResults(ctypes.Structure):
    _fields_ = [
            ("status", ctypes.c_ushort)
        ]


### PAR_COMMAND constants #####################################
# Refer to sbigudrv.h from the SBIG Development Kit and add
# more values as needed

# 1 - 10
CC_START_EXPOSURE = 1
CC_END_EXPOSURE = 2
CC_READOUT_LINE = 3
CC_DUMP_LINES = 4
CC_SET_TEMPERATURE_REGULATION = 5
CC_QUERY_TEMPERATURE_STATUS = 6
CC_ACTIVATE_RELAY = 7
CC_PULSE_OUT = 8
CC_ESTABLISH_LINK = 9
CC_GET_DRIVER_INFO = 10

# 11 - 20 
CC_GET_CCD_INFO = 11
CC_QUERY_COMMAND_STATUS = 12
CC_MISCELLANEOUS_CONTROL = 13
CC_READ_SUBTRACT_LINE = 14
CC_UPDATE_CLOCK = 15
CC_READ_OFFSET = 16
CC_OPEN_DRIVER = 17
CC_CLOSE_DRIVER = 18
CC_TX_SERIAL_BYTES = 19 
CC_GET_SERIAL_STATUS = 20

# 21 - 30 
CC_AO_TIP_TILT = 21
CC_AO_SET_FOCUS = 22
CC_AO_DELAY = 23
CC_GET_TURBO_STATUS = 24
CC_END_READOUT = 25
CC_GET_US_TIMER = 26
CC_OPEN_DEVICE = 27
CC_CLOSE_DEVICE = 28
CC_SET_IRQL = 29
CC_GET_IRQL = 30

# 31 - 40 
CC_GET_LINE = 31
CC_GET_LINK_STATUS = 32
CC_GET_DRIVER_HANDLE = 33
CC_SET_DRIVER_HANDLE = 34
CC_START_READOUT = 35
CC_GET_ERROR_STRING = 36 
CC_SET_DRIVER_CONTROL = 37
CC_GET_DRIVER_CONTROL = 38
CC_USB_AD_CONTROL = 39
CC_QUERY_USB = 40

# 41 - 50 
CC_GET_PENTIUM_CYCLE_COUNT = 41
CC_RW_USB_I2C = 42
CC_CFW = 43
CC_BIT_IO = 44 
CC_USER_EEPROM = 45
CC_AO_CENTER = 46
CC_BTDI_SETUP = 47
CC_MOTOR_FOCUS = 48
CC_QUERY_ETHERNET = 49 
CC_START_EXPOSURE2 = 50

# 51 - 60
CC_SET_TEMPERATURE_REGULATION2 = 51
CC_READ_OFFSET2 = 52
CC_DIFF_GUIDER = 53
CC_COLUMN_EEPROM = 54
CC_CUSTOMER_OPTIONS = 55
CC_DEBUG_LOG = 56
CC_QUERY_USB2 = 57
CC_QUERY_ETHERNET2 = 58
CC_GET_AO_MODEL = 59

# SBIG Use Only Commands

# 90 - 99
CC_SEND_BLOCK = 90 
CC_SEND_BYTE = 91
CC_GET_BYTE = 92
CC_SEND_AD = 93
CC_GET_AD = 94
CC_CLOCK_AD = 95
CC_SYSTEM_TEST = 96
CC_GET_DRIVER_OPTIONS = 97
CC_SET_DRIVER_OPTIONS = 98
CC_FIRMWARE = 99

# 100 - 109
CC_BULK_IO = 100
CC_RIPPLE_CORRECTION = 101
CC_EZUSB_RESET = 102
CC_BREAKPOINT = 103
CC_QUERY_EXPOSURE_TICKS = 104
CC_SET_ACTIVE_CCD_AREA = 105

### PAR_ERROR Constants ############################

# Instantiate a dictionary using keyword arguments so that we
# can look up 
PAR_ERROR = Enum(
    # 0 - 10
    NO_ERROR = 0,
    CAMERA_NOT_FOUND = 1,
    #ERROR_BASE = 1,
    EXPOSURE_IN_PROGRESS = 2,
    NO_EXPOSURE_IN_PROGRESS = 3,
    UNKNOWN_COMMAND = 4,
    BAD_CAMERA_COMMAND = 5,
    BAD_PARAMETER = 6,
    TX_TIMEOUT = 7,
    RX_TIMEOUT = 8,
    NAK_RECEIVED = 9,
    CAN_RECEIVED = 10,

    # 11 - 20,
    UNKNOWN_RESPONSE = 11,
    BAD_LENGTH = 12,
    AD_TIMEOUT = 13,
    KBD_ESC = 14,
    CHECKSUM_ERROR = 15,
    EEPROM_ERROR = 16,
    SHUTTER_ERROR = 17,
    UNKNOWN_CAMERA = 18,
    DRIVER_NOT_FOUND = 19,
    DRIVER_NOT_OPEN = 20,

    # 21 - 30,
    DRIVER_NOT_CLOSED = 21,
    SHARE_ERROR = 22,
    TCE_NOT_FOUND = 23,
    AO_ERROR = 24,
    ECP_ERROR = 25,
    MEMORY_ERROR = 26,
    DEVICE_NOT_FOUND = 27,
    DEVICE_NOT_OPEN = 28,
    DEVICE_NOT_CLOSED = 29,
    DEVICE_NOT_IMPLEMENTED = 30,

    # 31 - 40 ,
    DEVICE_DISABLED = 31,
    OS_ERROR = 32,
    SOCK_ERROR = 33,
    SERVER_NOT_FOUND = 34,
    CFW_ERROR = 35,
    MF_ERROR = 36,
    FIRMWARE_ERROR = 37,
    DIFF_GUIDER_ERROR = 38,
    RIPPLE_CORRECTION_ERROR = 39,
    EZUSB_RESET = 40,

    # 41 - 50,
    NEXT_ERROR = 41
)

### SBIG_DEVICE_TYPE Constants ################################
DEV_NONE = 0
DEV_LPT1 = 1
DEV_LPT2 = 2
DEV_LPT3 = 3
DEV_USB = 0x7F00
DEV_ETH = 0x7F01
DEV_USB1 = 0x7F02
DEV_USB2 = 0x7F03
DEV_USB3 = 0x7F04
DEV_USB4 = 0x7F05
DEV_USB5 = 0x7F06
DEV_USB6 = 0x7F07
DEV_USB7 = 0x7F08
DEV_USB8 = 0x7F09

### CCD_INFO_REQUEST Constants ################################

CCD_INFO_IMAGING = 0
CCD_INFO_TRACKING = 1
CCD_INFO_EXTENDED = 2
CCD_INFO_EXTENDED_5C = 3
CCD_INFO_EXTENDED2_IMAGING = 4
CCD_INFO_EXTENDED2_TRACKING = 5
CCD_INFO_EXTENDED3 = 6

### TEMPERATURE_REGULATION Constants ##########################

REGULATION_OFF = 0
REGULATION_ON = 1
REGULATION_OVERRIDE = 2
REGULATION_FREEZE = 3
REGULATION_UNFREEZE = 4
REGULATION_ENABLE_AUTOFREEZE = 5
REGULATION_DISABLE_AUTOFREEZE = 6

### QUERY_TEMP_STATUS_REQUEST Constants #######################

TEMP_STATUS_STANDARD = 0
TEMP_STATUS_ADVANCED = 1
TEMP_STATUS_ADVANCED2 = 2

### READOUT_BINNING_MODE Constants ############################

RM_1X1 = 0
RM_2X2 = 1
RM_3X3 = 2
RM_NX1 = 3
RM_NX2 = 4
RM_NX3 = 5
RM_1X1_VOFFCHIP = 6
RM_2X2_VOFFCHIP = 7
RM_3X3_VOFFCHIP = 8
RM_9X9 = 9
RM_NXN = 10

### Low-level SBIG control function ###########################

# Wrapper around SBIGUnivDrvCommand(). Parameters are optionally
# passed in (use None if the command takes no params) and results
# are optionally passed out (use None if command produces no
# results)
def sbigCtrl(command, params, results):
    sbigCmd = ctypes.windll.sbigudrv.SBIGUnivDrvCommand
    sbigCmd.restype = ctypes.c_short

    if params != None:
        params = ctypes.byref(params)
    if results != None:
        results = ctypes.byref(results)

    errorCode = sbigCmd(command, params, results)

    if errorCode != PAR_ERROR.NO_ERROR:
        raise SbigException(errorCode)

### Higher-level wrappers around SBIG control function ########

def openDriver():
    sbigCtrl(CC_OPEN_DRIVER, None, None)

def closeDriver():
    sbigCtrl(CC_CLOSE_DRIVER, None, None)

def openDevice(sbigDeviceType):
    """
    sbigDeviceType = DEV_USB1, DEV_USB2, etc.
    """

    params = OpenDeviceParams()
    params.deviceType = sbigDeviceType
    params.lptBaseAddress = 0
    params.ipAddress = 0x00000000

    results = None

    sbigCtrl(CC_OPEN_DEVICE, params, results)

def closeDevice():
    sbigCtrl(CC_CLOSE_DEVICE, None, None);

def establishLink():
    params = EstablishLinkParams()
    params.sbigUseOnly = 0

    results = EstablishLinkResults()

    sbigCtrl(CC_ESTABLISH_LINK, params, results)

    return results

def queryUsb():
    params = None
    results = QueryUSBResults()

    sbigCtrl(CC_QUERY_USB, params, results)

    return results

def getDriverInfo():
    params = GetDriverInfoParams()
    params.request = 0
    results = GetDriverInfoResults()

    sbigCtrl(CC_GET_DRIVER_INFO, params, results)

    return results

def getCcdInfo():
    params = GetCCDInfoParams()
    params.request = CCD_INFO_IMAGING
    results = GetCCDInfoResults0()

    sbigCtrl(CC_GET_CCD_INFO, params, results)

    return results

def coolerOff():
    params = SetTemperatureRegulationParams2()
    params.regulation = REGULATION_OFF
    params.ccdCetpoint = 99

    sbigCtrl(CC_SET_TEMPERATURE_REGULATION2, params, None)

def coolerOn(setpointDegsC):
    params = SetTemperatureRegulationParams2()
    params.regulation = REGULATION_ON
    params.ccdSetpoint = setpointDegsC

    sbigCtrl(CC_SET_TEMPERATURE_REGULATION2, params, None)

def getTemperatureStatus():
    params = QueryTemperatureStatusParams()
    params.request = TEMP_STATUS_ADVANCED2

    results = QueryTemperatureStatusResults2()

    sbigCtrl(CC_QUERY_TEMPERATURE_STATUS, params, results)

    return results

def startExposure(expLengthSeconds, openShutter, top, left, width, height):
    params = StartExposureParams2()
    params.ccd = 0
    params.exposureTime = int(expLengthSeconds*100)
    params.abgState = 0
    if openShutter:
        params.openShutter = 1
    else:
        params.openShutter = 2
    params.readoutMode = RM_1X1
    params.top = top
    params.left = left
    params.width = width
    params.height = height

    sbigCtrl(CC_START_EXPOSURE2, params, None)

def endExposure():
    params = EndExposureParams()
    params.ccd = 0

    sbigCtrl(CC_END_EXPOSURE, params, None)

def startReadout(top, left, width, height):
    params = StartReadoutParams()
    params.ccd = 0
    params.readoutMode = RM_1X1
    params.top = top
    params.left = left
    params.width = width
    params.height = height

    sbigCtrl(CC_START_READOUT, params, None)

def endReadout():
    params = EndReadoutParams()
    params.ccd = 0

    sbigCtrl(CC_END_READOUT, params, None)

def readoutLine(pixelStart, pixelLength):
    params = ReadoutLineParams()
    params.ccd = 0
    params.readoutMode = RM_1X1
    params.pixelStart = pixelStart
    params.pixelLength = pixelLength

    # Create array of unsigned shorts, of length "pixelLength"
    line = (ctypes.c_ushort*pixelLength)()

    sbigCtrl(CC_READOUT_LINE, params, line)

    return line


def isExposureComplete():
    commandStatus = queryCommandStatus(CC_START_EXPOSURE2)
    if (commandStatus & 0x03) == 0x03:
        return True
    else:
        return False

def waitForExposure():
    while not isExposureComplete():
        time.sleep(0.1)

def queryCommandStatus(command):
    params = QueryCommandStatusParams()
    params.command = command

    results = QueryCommandStatusResults()

    sbigCtrl(CC_QUERY_COMMAND_STATUS, params, results)

    return results.status

def expose(expLengthSeconds, openShutter, top, left, width, height):
    """
    High-level wrapper for taking an exposure, waiting until finished, and
    reading out the pixel data. Returned data is a list of rows of pixel values. 
    Values should be indexed as image[y][x], where y = row number and x = column
    number.
    """

    image = []

    startExposure(expLengthSeconds, openShutter, top, left, width, height)
    waitForExposure()
    endExposure()
    startReadout(top, left, width, height)
    for i in range(height):
        line = readoutLine(left, width)
        image.append(list(line))

    endReadout()

    return image

def main():
    """ 
    Tests and examples for the SBIG wrapper functions
    """

    openDriver()

    driverInfo = getDriverInfo()
    print("DRIVER INFO:")
    print("  Version:", driverInfo.version)
    print("  Name:", driverInfo.name)
    print("  Max request:", driverInfo.maxRequest)
    print()

    usbInfo = queryUsb()
    print("Found %d cameras" % usbInfo.camerasFound)
    for i in range(usbInfo.camerasFound):
        info = usbInfo.usbInfo[i]
        print("Camera", i)
        print("  Detected:", info.cameraFound)
        print("  Camera type:", info.cameraType)
        print("  Camera name:", info.name)
        print("  Serial number:", info.serialNumber)

    print()
    print("Opening device...")
    openDevice(DEV_USB1)

    print("Establishing link...")
    estLinkResult = establishLink()
    print("  Camera type:", estLinkResult.cameraType)

    print()
    print("CCD Info:")
    ccdInfo = getCcdInfo()
    print("  Firmware version:", ccdInfo.firmwareVersion)
    print("  Camera type:", ccdInfo.cameraType)
    print("  Name:", ccdInfo.name)
    print("  Number of readout modes:", ccdInfo.readoutModes)
    for i in range(ccdInfo.readoutModes):
        print("    Mode", i)
        print("      Width:", ccdInfo.readoutInfo[i].width)
        print("      Height:", ccdInfo.readoutInfo[i].height)
        print("      Gain:", ccdInfo.readoutInfo[i].gain/100.0)
        print("      Pixel width (microns):", ccdInfo.readoutInfo[i].pixelWidth/100.0)
        print("      Pixel height (microns):", ccdInfo.readoutInfo[i].pixelHeight/100.0)


    print()
    print("Temperature Info:")
    tempInfo = getTemperatureStatus()
    print("  Cooling enabled:", tempInfo.coolingEnabled)
    print("  Fan enabled:", tempInfo.fanEnabled)
    print("  CCD setpoint:", tempInfo.ccdSetpoint)
    print("  CCD temperature:", tempInfo.imagingCCDTemperature)
    print()

    input("Press Enter to take an exposure")


    top = 0
    left = 0
    width = 10
    height = 10
    expLength = 0.1

    print("Exposing using low-level control functions (subframed)...")
    startExposure(expLength, True, top, left, width, height)

    while not isExposureComplete():
        print(".")
        time.sleep(1)

    print("Ending exposure...")
    endExposure()

    print("Starting readout...")
    startReadout(top, left, width, height)

    for i in range(height):
        line = readoutLine(left, width)
        print(list(line))

    endReadout()

    print("Exposure finished!")

    # High-level version of expose()
    print("Taking subframed exposure...")
    image = expose(0.1, True, 0, 0, 10, 10)
    for row in image:
        print(row)

    print("Taking full-frame exposure...")
    width = ccdInfo.readoutInfo[RM_1X1].width
    height = ccdInfo.readoutInfo[RM_1X1].height
    image = expose(0.1, True, 0, 0, width, height)
    print("First row:")
    print(image[0])
    print("Last row:")
    print(image[-1])
    
    response = input("Test the cooler? (y/n): ")
    if response.strip() == "y":
        input("Press Enter to turn cooler on")

        coolerOn(-10)
        print("Cooler on; reporting status for 10 seconcds...")
        for i in range(10):
            tempInfo = getTemperatureStatus()
            print("  Cooler on:", tempInfo.coolingEnabled, " Setpoint:", tempInfo.ccdSetpoint, " Temp:", tempInfo.imagingCCDTemperature)

            time.sleep(1)

        input("Press Enter to turn cooler off")
        coolerOff()
        print("Cooler off; reporting status for 10 seconds...")
        for i in range(10):
            tempInfo = getTemperatureStatus()
            print("  Cooler on:", tempInfo.coolingEnabled, " Setpoint:", tempInfo.ccdSetpoint, " Temp:", tempInfo.imagingCCDTemperature)

            time.sleep(1)

    print("Closing device...")
    closeDevice()

    print("Closing driver...")
    closeDriver()

    print("Testing exception handling...")

    # Try doing something after driver is closed and make sure
    # an exception with the right error code (DRIVER_NOT_OPEN)
    # is thrown
    try:
        queryUsb() 
    except SbigException as ex:
        print("Expected exception occurred:", str(ex))

if __name__ == "__main__":
    main()
