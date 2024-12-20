import ctypes
import pathlib
from ctypes import *
from enum import Enum

import cv2
import numpy as np

lib_path = pathlib.Path(
    r"C:\Users\MACRO\Downloads\ASI_Camera_SDK\ASI_Camera_SDK\ASI_Windows_SDK_V1.37\ASI SDK\lib\x64\ASICamera2.dll"
)
print(lib_path)
asi = CDLL(lib_path)  # 调用SDK lib
cameraID = 0  # 初始化相关全局变量
width = 0
height = 0
bufferSize = 0


class ASI_IMG_TYPE(Enum):  # 定义相关枚举量
    ASI_IMG_RAW8 = 0
    ASI_IMG_RGB24 = 1
    ASI_IMG_RAW16 = 2
    ASI_IMG_Y8 = 3
    ASI_IMG_END = -1


class ASI_BOOL(Enum):
    ASI_FALSE = 0
    ASI_TRUE = 1


class ASI_BAYER_PATTERN(Enum):
    ASI_BAYER_RG = 0
    ASI_BAYER_BG = 1
    ASI_BAYER_GR = 2
    ASI_BAYER_GB = 3


class ASI_EXPOSURE_STATUS(Enum):
    ASI_EXP_IDLE = 0  # idle states, you can start exposure now
    ASI_EXP_WORKING = 1  # exposing
    ASI_EXP_SUCCESS = 2  # exposure finished and waiting for download
    ASI_EXP_FAILED = 3  # exposure failed, you need to start exposure again


class ASI_ERROR_CODE(Enum):
    ASI_SUCCESS = 0
    ASI_ERROR_INVALID_INDEX = 1  # no camera connected or index value out of boundary
    ASI_ERROR_INVALID_ID = 2  # invalid ID
    ASI_ERROR_INVALID_CONTROL_TYPE = 3  # invalid control type
    ASI_ERROR_CAMERA_CLOSED = 4  # camera didn't open
    ASI_ERROR_CAMERA_REMOVED = (
        5  # failed to find the camera, maybe the camera has been removed
    )
    ASI_ERROR_INVALID_PATH = 6  # cannot find the path of the file
    ASI_ERROR_INVALID_FILEFORMAT = 7
    ASI_ERROR_INVALID_SIZE = 8  # wrong video format size
    ASI_ERROR_INVALID_IMGTYPE = 9  # unsupported image formate
    ASI_ERROR_OUTOF_BOUNDARY = 10  # the startpos is out of boundary
    ASI_ERROR_TIMEOUT = 11  # timeout
    ASI_ERROR_INVALID_SEQUENCE = 12  # stop capture first
    ASI_ERROR_BUFFER_TOO_SMALL = 13  # buffer size is not big enough
    ASI_ERROR_VIDEO_MODE_ACTIVE = 14
    ASI_ERROR_EXPOSURE_IN_PROGRESS = 15
    ASI_ERROR_GENERAL_ERROR = 16  # general error, eg: value is out of valid range
    ASI_ERROR_INVALID_MODE = 17  # the current mode is wrong
    ASI_ERROR_END = 18


class ASI_CAMERA_INFO(Structure):  # 定义ASI_CAMERA_INFO 结构体
    _fields_ = [
        ("Name", c_char * 64),
        ("CameraID", c_int),
        ("MaxHeight", c_long),
        ("MaxWidth", c_long),
        ("IsColorCam", c_int),
        ("BayerPattern", c_int),
        ("SupportedBins", c_int * 16),
        ("SupportedVideoFormat", c_int * 8),
        ("PixelSize", c_double),
        ("MechanicalShutter", c_int),
        ("ST4Port", c_int),
        ("IsCoolerCam", c_int),
        ("IsUSB3Host", c_int),
        ("IsUSB3Camera", c_int),
        ("ElecPerADU", c_float),
        ("BitDepth", c_int),
        ("IsTriggerCam", c_int),
        ("Unused", c_char * 16),
    ]


class ASI_CONTROL_TYPE(Enum):  # Control type 定义 ASI_CONTROL_TYPE 结构体
    ASI_GAIN = 0
    ASI_EXPOSURE = 1
    ASI_GAMMA = 2
    ASI_WB_R = 3
    ASI_WB_B = 4
    ASI_OFFSET = 5
    ASI_BANDWIDTHOVERLOAD = 6
    ASI_OVERCLOCK = 7
    ASI_TEMPERATURE = 8  # return 10*temperature
    ASI_FLIP = 9
    ASI_AUTO_MAX_GAIN = 10
    ASI_AUTO_MAX_EXP = 11  # micro second
    ASI_AUTO_TARGET_BRIGHTNESS = 12  # target brightness
    ASI_HARDWARE_BIN = 13
    ASI_HIGH_SPEED_MODE = 14
    ASI_COOLER_POWER_PERC = 15
    ASI_TARGET_TEMP = 16  # not need *10
    ASI_COOLER_ON = 17
    ASI_MONO_BIN = 18  # lead to less grid at software bin mode for color camera
    ASI_FAN_ON = 19
    ASI_PATTERN_ADJUST = 20
    ASI_ANTI_DEW_HEATER = 21


def init():  # 相机初始化
    global width
    global height
    global cameraID

    num = asi.ASIGetNumOfConnectedCameras()  # 获取连接相机数
    if num == 0:
        print("No camera connection!")
        return
    print("Number of connected cameras: ", num)

    camInfo = ASI_CAMERA_INFO()
    getCameraProperty = asi.ASIGetCameraProperty
    getCameraProperty.argtypes = [POINTER(ASI_CAMERA_INFO), c_int]
    getCameraProperty.restype = c_int

    for i in range(0, num):
        asi.ASIGetCameraProperty(camInfo, i)  # 以index获取相机属性

    cameraID = camInfo.CameraID

    err = asi.ASIOpenCamera(cameraID)  # 打开相机
    if err != 0:
        return
    print("Open Camera Success")

    err = asi.ASIInitCamera(cameraID)  # 初始化相机
    if err != 0:
        return
    print("Init Camera Success")

    width = camInfo.MaxWidth
    height = camInfo.MaxHeight
    _bin = 1
    startx = 0
    starty = 0
    imageType = ASI_IMG_TYPE.ASI_IMG_RAW16

    err = asi.ASISetROIFormat(
        cameraID, width, height, _bin, imageType.value
    )  # SetROIFormat
    if err != 0:
        print("Set ROI Format Fail")
        return
    print("Set ROI Format Success")

    asi.ASISetStartPos(cameraID, startx, starty)  # SetStartPos


def getFrame():  # 获取图像帧
    global bufferSize
    buffersize = width * height

    buffer = (c_ubyte * 2 * buffersize)()

    err = asi.ASIStartExposure(cameraID, 0)  # 开始曝光
    if err != 0:
        print("Start Exposure Fail")
        return
    print("Start Exposure Success")

    getExpStatus = asi.ASIGetExpStatus
    getExpStatus.argtypes = [c_int, POINTER(c_int)]
    getExpStatus.restype = c_int
    expStatus = c_int()

    getDataAfterExp = asi.ASIGetDataAfterExp
    getDataAfterExp.argtypes = [c_int, POINTER(c_ubyte) * 2, c_int]
    getDataAfterExp.restype = c_int
    buffer = (c_ubyte * 2 * buffersize)()

    getExpStatus(cameraID, expStatus)
    print("status: ", expStatus)

    # c_int转int
    sts = expStatus.value
    while sts == ASI_EXPOSURE_STATUS.ASI_EXP_WORKING.value:  # 获取曝光状态
        getExpStatus(cameraID, expStatus)
        sts = expStatus.value

    if sts != ASI_EXPOSURE_STATUS.ASI_EXP_SUCCESS.value:
        print("Exposure Fail")
        return

    err = getDataAfterExp(cameraID, buffer, buffersize)  # 曝光成功，获取buffer
    if err != 0:
        print("GetDataAfterExp Fail")
        return
    print("getDataAfterExp Success")

    return buffer


def closeCamera():  # 关闭相机
    err = asi.ASIStopVideoCapture(cameraID)
    if err != 0:
        print("Stop Capture Fail")
        return
    print("Stop Capture Success")

    err = asi.ASICloseCamera(cameraID)
    if err != 0:
        print("Close Camera Fail")
        return
    print("Close Camera Success")


def setExpValue(val):  # 设置曝光时间
    # setControlValue = asi.ASISetControlValue
    # setControlValue.argtypes = [c_int, ASI_CONTROL_TYPE, c_long, ASI_BOOL]
    # setControlValue.restype = c_int
    err = asi.ASISetControlValue(
        cameraID, ASI_CONTROL_TYPE.ASI_EXPOSURE.value, val, ASI_BOOL.ASI_FALSE.value
    )


def setGainValue(val):  # 设置增益
    err = asi.ASISetControlValue(
        cameraID, ASI_CONTROL_TYPE.ASI_GAIN.value, val, ASI_BOOL.ASI_FALSE.value
    )


def setBiasValue(val):
    err = asi.ASISetControlValue(
        cameraID, ASI_CONTROL_TYPE.ASI_OFFSET.value, val, ASI_BOOL.ASI_FALSE.value
    )
