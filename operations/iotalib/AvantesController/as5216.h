//----------------------------------------------------------------------------
// (C) Copyright 2006, AVANTES B.V.
// Any reproduction without written permission is prohibited by law.
//----------------------------------------------------------------------------
//
// File type : C++ header
// Description : Main header file
//
//----------------------------------------------------------------------------
//
//
//----------------------------------------------------------------------------
#ifndef AS5216_DLL_H
#define AS5216_DLL_H

//----------------------------------------------------------------------------
// Export overview
//----------------------------------------------------------------------------
#ifdef DLL_EXPORTS
#define DLL_API extern "C" __declspec (dllexport)
#else
#define DLL_API extern "C" __declspec (dllimport)
#endif

typedef signed char     int8;
typedef unsigned char   uint8;
typedef signed short    int16;
typedef unsigned short  uint16;
typedef unsigned int    uint32;

uint8 const     USER_ID_LEN             = 64;
uint8 const     NR_WAVELEN_POL_COEF     = 5;
uint8 const     NR_NONLIN_POL_COEF      = 8;
uint8 const     NR_DEFECTIVE_PIXELS     = 30;
uint16 const    MAX_NR_PIXELS           = 4096;
uint8 const     NR_TEMP_POL_COEF        = 5;
uint8 const     MAX_TEMP_SENSORS        = 3;
uint8 const     ROOT_NAME_LEN           = 6;
uint8 const     AVS_SERIAL_LEN          = 10;
uint16 const    MAX_PIXEL_VALUE         = 0xFFFC;
uint8 const     MAX_VIDEO_CHANNELS      = 2;
uint16 const    MAX_LASER_WIDTH         = 0xFFFF;
uint8 const     HW_TRIGGER_MODE		    = 1;
uint8 const 	SW_TRIGGER_MODE	    	= 0;
uint8 const 	EDGE_TRIGGER_SOURCE  	= 0;
uint8 const 	LEVEL_TRIGGER_SOURCE	= 1;
uint8 const     MAX_TRIGGER_MODE        = 1;
uint8 const     MAX_TRIGGER_SOURCE      = 1;
uint8 const     MAX_TRIGGER_SOURCE_TYPE = 1;
uint32 const    MAX_INTEGRATION_TIME    = 600000;    // 600 seconds
uint8 const     SAT_DISABLE_DET         = 0;
uint8 const     SAT_ENABLE_DET          = 1;
uint8 const     SAT_PEAK_INVERSION      = 2;
uint8 const     NR_DAC_POL_COEF         = 2;
uint8 const     NTC1_ID                 = 0;
uint8 const     NTC2_ID                 = 1;
uint8 const     TEC_ID                  = 2; 

#pragma pack(push,1)

typedef enum
{
    SENS_HAMS8378_256 = 1,
    SENS_HAMS8378_1024,
    SENS_ILX554,
    SENS_HAMS9201,
    SENS_TCD1304,
    SENS_TSL1301,
    SENS_TSL1401,
    SENS_HAMS8378_512,
    SENS_HAMS9840,
    SENS_ILX511,
    SENS_HAMS10420_2048X64,
    SENS_HAMS11071_2048X64,
    SENS_HAMS7031_1024X122,
    SENS_HAMS7031_1024X58,
    SENS_HAMS11071_2048X16,
    SENS_HAMS11155,
    SENS_SU256LSB,
    SENS_SU512LDB
} SENS_TYPE;

typedef struct
{
    uint16                  m_StrobeControl;
    uint32                  m_LaserDelay;
    uint32                  m_LaserWidth;
    float                   m_LaserWaveLength;
    uint16                  m_StoreToRam;
} ControlSettingsType;

typedef struct
{
    uint8                   m_Enable;
    uint8                   m_ForgetPercentage;
} DarkCorrectionType;

typedef uint8 SensorType;

typedef struct
{
    SensorType              m_SensorType;
    uint16                  m_NrPixels;
    float                   m_aFit[NR_WAVELEN_POL_COEF];
    bool                    m_NLEnable;
    double                  m_aNLCorrect[NR_NONLIN_POL_COEF];
    double                  m_aLowNLCounts;
    double                  m_aHighNLCounts;
    float                   m_Gain[MAX_VIDEO_CHANNELS];
    float                   m_Reserved;
    float                   m_Offset[MAX_VIDEO_CHANNELS];
    float                   m_ExtOffset;
    uint16                  m_DefectivePixels[NR_DEFECTIVE_PIXELS];
} DetectorType;

typedef struct
{
    uint16                  m_SmoothPix;
    uint8                   m_SmoothModel;
} SmoothingType;

typedef struct
{
    SmoothingType           m_Smoothing;
    float                   m_CalInttime;
    float                   m_aCalibConvers[MAX_NR_PIXELS];
} SpectrumCalibrationType;

typedef struct
{
    SpectrumCalibrationType m_IntensityCalib;
    uint8                   m_CalibrationType;
    uint32                  m_FiberDiameter;
} IrradianceType;

typedef struct
{
    uint8                   m_Mode;
    uint8                   m_Source;
    uint8                   m_SourceType;
} TriggerType;

typedef struct
{
    uint16                  m_StartPixel;
    uint16                  m_StopPixel;
    float                   m_IntegrationTime;
    uint32                  m_IntegrationDelay;
    uint32                  m_NrAverages;
    DarkCorrectionType      m_CorDynDark;
    SmoothingType           m_Smoothing;
    uint8                   m_SaturationDetection;
    TriggerType             m_Trigger;
    ControlSettingsType     m_Control;
} MeasConfigType;

typedef struct
{
    uint16                  m_Date;
    uint16                  m_Time;
} TimeStampType;

typedef struct
{
    bool                    m_Enable;
    uint8                   m_SpectrumType;
    char                    m_aFileRootName[ROOT_NAME_LEN];
    TimeStampType           m_TimeStamp;
} SDCardType;

typedef struct
{
    float                   m_aSpectrumCorrect[MAX_NR_PIXELS];
} SpectrumCorrectionType;

typedef struct
{
    bool                    m_Enable;
    MeasConfigType          m_Meas;
    int16                   m_Nmsr;
    SDCardType              m_SDCard;
} StandAloneType;

typedef struct
{
    float                   m_aFit[NR_TEMP_POL_COEF];
} TempSensorType;

typedef struct
{
    bool                    m_Enable;
    float                   m_Setpoint;     // [degree Celsius]
    float                   m_aFit[NR_DAC_POL_COEF];
} TecControlType;

typedef struct
{
    float                   AnalogLow[2];
    float                   AnalogHigh[2];
    float                   DigitalLow[10];
    float                   DigitalHigh[10];
} ProcessControlType;

uint16 const    SETTINGS_RESERVED_LEN   = ((62*1024) -  sizeof(uint32) -
                                                        (sizeof(uint16) +   // m_Len
                                                         sizeof(uint16) +  // m_ConfigVersion
                                                         USER_ID_LEN +
                                                         sizeof(DetectorType) +
                                                         sizeof(IrradianceType) +
                                                         sizeof(SpectrumCalibrationType) +
                                                         sizeof(SpectrumCorrectionType) +
                                                         sizeof(StandAloneType) +
                                                        (sizeof(TempSensorType)*MAX_TEMP_SENSORS) +
                                                         sizeof(TecControlType) +
                                                         sizeof(ProcessControlType)
                                                        )
                                           );

typedef struct
{
    uint16                  m_Len;
    uint16                  m_ConfigVersion;
    char                    m_aUserFriendlyId[USER_ID_LEN];
    DetectorType            m_Detector;
    IrradianceType          m_Irradiance;
    SpectrumCalibrationType m_Reflectance;
    SpectrumCorrectionType  m_SpectrumCorrect;
    StandAloneType          m_StandAlone;
    TempSensorType          m_aTemperature[MAX_TEMP_SENSORS];
    TecControlType          m_TecControl;
    ProcessControlType      m_ProcessControl;
    uint8                   m_aReserved[SETTINGS_RESERVED_LEN];
} DeviceConfigType;

typedef long  AvsHandle;

typedef enum
{
        UNKNOWN,
        AVAILABLE,
        IN_USE_BY_APPLICATION,
        IN_USE_BY_OTHER
} DEVICE_STATUS;

// typedef
typedef struct
{
    char            SerialNumber[AVS_SERIAL_LEN];
    char            UserFriendlyName[USER_ID_LEN];
    unsigned char   Status;
} AvsIdentityType;

// Return error codes
int const ERR_SUCCESS                   = 0;
int const ERR_INVALID_PARAMETER         = -1;
int const ERR_OPERATION_NOT_SUPPORTED   = -2;
int const ERR_DEVICE_NOT_FOUND          = -3;
int const ERR_INVALID_DEVICE_ID         = -4;
int const ERR_OPERATION_PENDING         = -5;
int const ERR_TIMEOUT                   = -6;
int const ERR_INVALID_PASSWORD          = -7;
int const ERR_INVALID_MEAS_DATA         = -8;
int const ERR_INVALID_SIZE              = -9;
int const ERR_INVALID_PIXEL_RANGE       = -10;
int const ERR_INVALID_INT_TIME          = -11;
int const ERR_INVALID_COMBINATION       = -12;
int const ERR_INVALID_CONFIGURATION     = -13;
int const ERR_NO_MEAS_BUFFER_AVAIL      = -14;
int const ERR_UNKNOWN                   = -15;
int const ERR_COMMUNICATION             = -16;
int const ERR_NO_SPECTRA_IN_RAM         = -17;
int const ERR_INVALID_DLL_VERSION       = -18;
int const ERR_NO_MEMORY                 = -19;
int const ERR_DLL_INITIALISATION        = -20;
int const ERR_INVALID_STATE             = -21;

// Return error codes; DeviceData check
int const ERR_INVALID_PARAMETER_NR_PIXELS   = -100;
int const ERR_INVALID_PARAMETER_ADC_GAIN    = -101;
int const ERR_INVALID_PARAMETER_ADC_OFFSET  = -102;

// Return error codes; PrepareMeasurement check
int const ERR_INVALID_MEASPARAM_AVG_SAT2    = -110;
int const ERR_INVALID_MEASPARAM_AVG_RAM     = -111;
int const ERR_INVALID_MEASPARAM_SYNC_RAM    = -112;
int const ERR_INVALID_MEASPARAM_LEVEL_RAM   = -113;
int const ERR_INVALID_MEASPARAM_SAT2_RAM    = -114;
int const ERR_INVALID_MEASPARAM_FWVER_RAM   = -115; //StoreToRAM in 0.20.0.0 and later
int const ERR_INVALID_MEASPARAM_DYNDARK     = -116;

// Return error codes; SetSensitivityMode check
int const ERR_NOT_SUPPORTED_BY_SENSOR_TYPE  = -120;
int const ERR_NOT_SUPPORTED_BY_FW_VER       = -121;
int const ERR_NOT_SUPPORTED_BY_FPGA_VER     = -122;

int const  UNCONFIGURED_DEVICE_OFFSET    = 256;
long const INVALID_AVS_HANDLE_VALUE     = 1000L;

#define WM_MEAS_READY       (WM_APP + 1)
#define WM_DBG_INFO         (WM_APP + 2)
#define WM_DEVICE_RESET     (WM_APP + 3)


//----------------------------------------------------------------------------
//
// Name         : AVS_Init
//
// Description  : Tries to open com-port and ask spectrometer configuration
//
// Parameters   : a_COMPort   : -1, search for port to be used
//                              0, use USB port
//                              1-4, use COM port
//
// Returns      : integer     :  >0, number of attached devices
//                               <0, error occured
//
// Remark(s)    : Blocks application
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_Init
(
    short a_Port
);

//----------------------------------------------------------------------------
//
// Name         : AVS_Done
//
// Description  : Closes port and releases memory
//
// Parameters   : -
//
// Returns      : integer :  0, successfully closed
//                          -1, error occured
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_Done
(
    void
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetNrOfDevices
//
// Description  : Scans for attached devices and returns the number of devices
//                detected
//
// Parameters   : -
//
// Returns      : int (>=0)          : number of devices in list
//
// Remark(s)    : The DLL updates it's internal list if this function is called
//                So this function has to be called each time a WM_DEVICE_CHANGE
//                notification is received
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetNrOfDevices(void);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetList
//
// Description  : Returns device information for each spectrometer connected
//                to the ports indicated at AVS_Init
//
// Parameters   : a_ListSize        : number of bytes allocated by the caller to
//                                    store the a_pList data
//                a_pRequiredSize   : Number of bytes needed to store information
//                a_pList           : pointer to allocated buffer to store information
//
// Returns      : int (>=0)          : number of devices in list
//                ERROR_INVALID_SIZE : (if a_pRequiredSize > a_ListSize)
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetList
(
    unsigned int        a_ListSize,
    unsigned int*       a_pRequiredSize,
    AvsIdentityType*    a_pList
);

//----------------------------------------------------------------------------
//
// Name         : AVS_Activate
//
// Description  : Activates selected spectrometer for communication
//
// Parameters   : a_pDeviceId   : AvsIdentity of desired spectrometer
//
// Returns      : AvsHandle     : handle to be used in subsequent calls
//                INVALID_HANDLE_VALUE  : in case of error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API AvsHandle __stdcall AVS_Activate
(
    AvsIdentityType*    a_pDeviceId
);


//----------------------------------------------------------------------------
//
// Name         : AVS_Deactivate
//
// Description  : De-activates selected spectrometer for communication
//
// Parameters   : a_hHandle    : Device handle from AVS_Activate
//
// Returns      : -
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API bool  __stdcall AVS_Deactivate
(
    AvsHandle    a_hHandle
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetHandleFromSerial
//
// Description  : Searches serial number for handle id.
//
// Parameters   : a_pSerial    : serial number
//
// Returns      : AvsHandle    : INVALID_AVS_HANDLE_VALUE if not found
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API AvsHandle  __stdcall AVS_GetHandleFromSerial
(
    char*    a_pSerial
);

//----------------------------------------------------------------------------
//
// Name         : AVS_Register
//
// Description  : Installs an application windows handle to which device
//                attachment/removal messages have to be sent
//
// Parameters   : a_hWnd    : application window handle
//
// Returns      : -
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API bool  __stdcall AVS_Register
(
    long    a_hWnd
);

//----------------------------------------------------------------------------
//
// Name         : AVS_PrepareMeasure
//
// Description  : Prepares measurement on the spectrometer using the specified
//                measurement configuration.
//
// Parameters   : a_hDevice     : device handle
//                a_pMeasConfig : pointer to buffer containing a measurement
//                                configuration
//
// Returns      : SUCCESS       : parameters are set
//                ERROR_DEVICE_UNINITIALISED : no communication
//                ERROR_INVALID_DEVICE_ID    : handle unknown
//                ERROR_INVALID_PARAMETER    : measurement configuration invalid
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_PrepareMeasure
(
    AvsHandle		a_hDevice,
    MeasConfigType*	a_pMeasConfig
);

//----------------------------------------------------------------------------
//
// Name         : AVS_Measure
//
// Description  : Start measurement
//
// Parameters   : a_hDevice         : device handle
//                a_hWnd            : handle of window to which ready message
//                                    should be sent
//                a_Nmsr            : number of measurements requested
//                                    (-1 is continous)
//
// Returns      : integer : 0, successfully started
//                          error code on error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_Measure
(
    AvsHandle       a_hDevice,
    long            a_hWnd,
    short           a_Nmsr
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetLambda
//
// Description  : Returns the wavelength values corresponding to the pixels
//
// Parameters   : a_hDevice     : device handle
//                a_pWaveLength : pointer to array of doubles,
//                                array size equal to number of pixels
//
// Returns      : integer       : 0, successfully started
//                                error code on error
//
// Remark(s)    : array size not checked
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetLambda
(
    AvsHandle       a_hDevice,
    double*         a_pWaveLength
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetNumPixels
//
// Description  : Returns the number of pixels
//
// Parameters   : a_hDevice     : device handle
//                a_pNumPixels  : buffer to store number of pixels
//
// Returns      : integer       : 0, number of pixels available
//                                error code on error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetNumPixels
(
    AvsHandle       a_hDevice,
    unsigned short* a_pNumPixels
);


//----------------------------------------------------------------------------
//
// Name         : AVS_GetParameter
//
// Description  : Returns the device parameter structure
//
// Parameters   : a_hDevice     : device handle
//                a_Size        : size of a_pDeviceParm buffer
//                a_pRequiredSize: needed buffer size
//                a_pDeviceParm : pointer to allocated buffer
//
// Returns      : integer         : 0, info available
//                                  error code on error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetParameter
(
    AvsHandle           a_hDevice,
    unsigned int        a_Size,
    unsigned int*   	a_pRequiredSize,
    DeviceConfigType*   a_pDeviceParm
);

//----------------------------------------------------------------------------
//
// Name         : AVS_PollScan
//
// Description  : Poll advent of new data (e.g. for VB)
//
// Parameters   : a_hDevice : device handle
//
// Returns      : Integer, 0 when data are not ready
//                         1 when data are available
//                        <0: error code
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_PollScan
(
    AvsHandle   a_hDevice
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetScopeData
//
// Description  : Returns the values for each pixel
//
// Parameters   : a_hDevice     : device handle
//                a_pTimeLabel  : ticks count last pixel of spectrum is received
//                                by microcontroller, ticks in 10 mS units since
//                                spectrometer started
//                a_pSpectrum   : pointer to array of doubles containing dark
//                                values, array size equal to number of pixels
//
// Returns      : integer       : 0, successfully started
//                                error code on error
//
// Remark(s)    : array size not checked
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetScopeData
(
    AvsHandle       a_hDevice,
    unsigned int*   a_pTimeLabel,
    double*         a_pSpectrum
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetSaturatedPixels
//
// Description  : Returns for each pixel the number of scans (out of a total
//                of NrOfAverage scans) for which the pixel was saturated
//
// Parameters   : a_hDevice : device handle
//                a_pSaturated  : pointer to array of integers containing
//                                number of scans saturated,
//                                array size equal to number of pixels
//
// Returns      : integer       : 0, successfully started
//                                error code on error
//
// Remark(s)    : array size not checked
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetSaturatedPixels
(
    AvsHandle       a_hDevice,
    unsigned char*  a_pSaturated
);


//----------------------------------------------------------------------------
//
// Name         : AVS_GetAnalogIn
//
// Description  : Returns the status of the specified digital input
//
// Parameters   : a_hDevice : device handle
//                a_AnalogInId  : input identifier
//                a_pAnalogIn   : pointer to buffer to store result
//
// Returns      : integer       : 0, successfully started
//                                error code on error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetAnalogIn
(
    AvsHandle       a_hDevice,
    unsigned char	  a_AnalogInId,
    float*          a_pAnalogIn
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetDigIn
//
// Description  : Returns the state of the digital input
//
// Parameters   : a_hDevice : device handle
//                a_DigInId : digital input
//                a_pDigIn  : value of digital input
//
// Returns      : integer         : 0, ok
//                                  <0 on error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetDigIn
(
    AvsHandle       a_hHandle,
    unsigned char   a_DigInId,
    unsigned char*  a_pDigIn
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetVersionInfo
//
// Description  : Returns the status of the software version of the different parts.
//
// Parameters   : a_hDevice : device handle
//                a_pFPGAVersion, pointer to buffer to store version (16 chars)
//                a_pFirmwareVersion, pointer to buffer to store version (16 chars)
//            	  a_pDLLVersion pointer to buffer to store version (16 chars)
//
// Returns      : integer         : 0, ok
//                                  <0 on error
//
// Remark(s)    : Does not check the size of the buffers allocated by the caller.
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetVersionInfo
(
    AvsHandle       a_hDevice,
    char*           a_pFPGAVersion,
    char*           a_pFirmwareVersion,
    char*           a_pDLLVersion
);

//----------------------------------------------------------------------------
//
// Name         : AVS_SaveSpectraToSDCard
//
// Description  : Enables/disables writing spectra to file (if disabled the
//                other parameters are neglected)
//
// Parameters   : a_hDevice         : device handle
//                a_Enable          : enable/disable storage to SD card
//                a_SpectrumType    : 0 = Dark Spectrum
//                        			  1 = Reference Spectrum
//			                          2 = Normal Spectrum
//                        			  The spectrumtype determines the file extension (drk, ref or roh)
//                a_aFileRootName   : string used as first part of name
//                a_TimeStamp       : file time and date used to store spectrum
//
// Returns      : integer         : 0, ok
//                                  <0 on error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_SaveSpectraToSDCard
(
    AvsHandle       a_hDevice,
    bool            a_Enable,
    unsigned char   a_SpectrumType,
    char            a_aFileRootName[ROOT_NAME_LEN],
    TimeStampType	  a_TimeStamp
);

//----------------------------------------------------------------------------
//
// Name         : AVS_SetParameter
//
// Description  : Sets device parameters
//
// Parameters   : a_hDevice       : device handle
//                a_pDeviceParm   : structure containing device parameters
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : contents of structure not checked
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_SetParameter
(
    AvsHandle           a_hDevice,
    DeviceConfigType*   a_pDeviceParm
);

//----------------------------------------------------------------------------
//
// Name         : AVS_SetAnalogOut
//
// Description  : Sets analog output
//
// Parameters   : a_hDevice       : device handle
//                a_PortId        : output identifier
//                a_Value         : output value in Volts (0 - 3.3)
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_SetAnalogOut
(
	AvsHandle		a_hDevice,
	unsigned char	a_PortId,
	float			a_Value
);

//----------------------------------------------------------------------------
//
// Name         : AVS_SetDigOut
//
// Description  : Sets state of digital output
//
// Parameters   : a_hDevice : device handle
//                a_PortId  : digital output id.
//                a_Status  : new state digital output
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_SetDigOut
(
    AvsHandle       a_hHandle,
    unsigned char   a_PortId,
    unsigned char   a_Status
);

//----------------------------------------------------------------------------
//
// Name         : AVS_SetPwmOut
//
// Description  : Sets state of pwm output
//
// Parameters   : a_hDevice : device handle
//                a_PortId  : digital output id.
//                a_Freq    : desired PWM frequency (500 - 300000 Hz0
//                a_Duty    : percentage high time in single PWM period
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_SetPwmOut
(
    AvsHandle       a_hHandle,
    unsigned char   a_PortId,
    unsigned long   a_Freq,
    unsigned char   a_Duty
);

//----------------------------------------------------------------------------
//
// Name         : AVS_SetSyncMode
//
// Description  : Disables/enables support for synchronous measurement.
//                DLL takes care of dividing Nmsr request into Nmsr number
//                of single measurement requests.
//
// Parameters   : a_hDevice : device handle
//                a_Enable  : enables/disables support
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_SetSyncMode
(
	AvsHandle		a_hDevice,
	unsigned char	a_Enable
);

//----------------------------------------------------------------------------
//
// Name         : AVS_StopMeasure
//
// Description  : Stops the measurements (needed if Nmsr = infinite), can also
//                be used to stop a pending measurement with long integrationtime
//
// Parameters   : a_hDevice : device handle
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_StopMeasure
(
	AvsHandle		a_hDevice
);



//----------------------------------------------------------------------------
//
// Name         : AVS_GetFileSize
//
// Description  : Retrieves size of the file
//
// Parameters   : a_pName   : filename
//                a_pSize   : file size
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetFileSize
(
    AvsHandle       a_hDevice,
    char*           a_pName,
    unsigned int*   a_pSize
);


//----------------------------------------------------------------------------
//
// Name         : AVS_GetFile
//
// Description  : Reads the file and stores data in a_pDest
//
// Parameters   : a_pName   : filename
//                a_pDest   : destination buffer
//                a_Size    : file size
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetFile
(
    AvsHandle       a_hDevice,
    char*           a_pName,
    unsigned char*  a_pDest,
    unsigned int    a_Size
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetFirstFile
//
// Description  : Checks if files are present on SD card
//
// Parameters   : a_pName   : buffer of at least 14 characters to store filename
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetFirstFile
(
    AvsHandle       a_hDevice,
    char*           a_pName
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetNextFile
//
// Description  : Checks if another file is present on SD card
//
// Parameters   : a_pPrevName     : name returned by AVS_GetFirstFile or by AVS_GetNextFile
//                a_pNextName     : buffer of at least 14 characters to store filename
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetNextFile
(
    AvsHandle       a_hDevice,
    char*           a_pPrevName,
    char*           a_pNextName
);

//----------------------------------------------------------------------------
//
// Name         : AVS_GetNextFile
//
// Description  : Checks if another file is present on SD card
//
// Parameters   : a_pName     : name returned by AVS_GetFirstFile or by AVS_GetNextFile
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_DeleteFile
(
    AvsHandle       a_hDevice,
    char*           a_pName
);

//----------------------------------------------------------------------------
//
// Name         : AVS_SetPrescanMode
//
// Description  : Sets prescan mode (skip first measurement result),
//                at the moment only useful for the AvaSpec-3648 to switch
//                between Prescan (default) and Clear mode
//
// Parameters   : a_Prescan
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_SetPrescanMode
(
    AvsHandle       a_hDevice,
    bool            a_Prescan
);

//----------------------------------------------------------------------------
//
// Name         : AVS_UseHighResolutionADC
//
// Description  : Sets DLL in 16-bit data mode, when hardware ID >= 3.
//                Data is not longer treated as 14-bit data.
//                Will also influence gain and offset checks.
//
// Parameters   : a_hDevice : device handle
//              : a_Enable  : true = 16bit resolution, false = 14bit resolution
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_UseHighResAdc
(
    AvsHandle       a_hDevice,
    bool            a_Enable
);


//----------------------------------------------------------------------------
//
// Name       : GetFirstDirectory
//
// Description: Reads first Directoryname from SD Card
//
// Parameters : a_pName : Directory name
//
// Returns    : integer,  0, on success
//                       <0, application level error code
//
// Remark(s)  : Should be used together with GetNextDirectory
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetFirstDirectory
(
    AvsHandle       a_hDevice,
    char*           a_pName
);

//----------------------------------------------------------------------------
//
// Name       : AVS_GetNextDirectory
//
// Description: Reads next Directoryname from SD Card
//
// Parameters : a_pFirst Name : Directory name returned from GetFirstDirectory or from previous
//                              call to GetNextDirectory
//              a_pNextName   : next file name
//
// Returns    : integer,  0, on success
//                       <0, application level error code
//
// Remark(s)  : Should be used together with GetFirstFile
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_GetNextDirectory
(
    AvsHandle       a_hDevice,
    char*           a_pPrevName,
    char*           a_pNextName
);

//----------------------------------------------------------------------------
//
// Name       : AVS_DeleteDirectory
//
// Description: Deletes Directory from SD card
//
// Parameters : a_pName : Directory name
//
// Returns    : integer,  0, on success
//                       <0, application level error code
//
// Remark(s)  : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_DeleteDirectory
(
    AvsHandle       a_hDevice,
    char*           a_pName
);

//----------------------------------------------------------------------------
//
// Name       : SetDirectory
//
// Description: Sets current working to Directory from SD card
//
// Parameters : a_pName : Directory name
//
// Returns    : integer,  0, on success
//                       <0, application level error code
//
// Remark(s)  : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_SetDirectory
(
    AvsHandle       a_hDevice,
    char            a_aName[ROOT_NAME_LEN]
);

//----------------------------------------------------------------------------
//
// Name         : AVS_SetSensitivityMode
//
// Description  : Sets sensitivity mode (lownoise or high sensitivity),
//              at the moment only useful for the NIR to switch
//              between lownoise and high sensitivity mode
//
// Parameters   : a_HiSensitivity: 0 = lownoise; >0 = high sensitivity
//
// Returns      : integer         : 0, ok
//                                  error code, communication error
//
// Remark(s)    : -
//
//----------------------------------------------------------------------------
DLL_API int __stdcall AVS_SetSensitivityMode
(
    AvsHandle       a_hDevice,
    uint32          a_SensitivityMode
);

//----------------------------------------------------------------------------
// End of definitions
//----------------------------------------------------------------------------


#pragma pack(pop)
#endif  // AS5216_DLL_H



