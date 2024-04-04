@ECHO OFF
SET PWSHUTTER="C:\Program Files (x86)\PlaneWave Instruments\PlaneWave Shutter Control\PWShutter.exe"

ECHO Checking connection
%PWSHUTTER% isconnected
IF %ERRORLEVEL% EQU 0 (
  ECHO Shutter is connected
) ELSE (
  ECHO Shutter is NOT connected
)

ECHO Trying to connect
%PWSHUTTER% connect
IF %ERRORLEVEL% EQU 0 (
  ECHO Connected successfully
) ELSE (
  ECHO ERROR: Connection failed
  EXIT /B
)

%PWSHUTTER% shutterstate
echo Return code: %ERRORLEVEL%
IF %ERRORLEVEL% EQU 0 (
  ECHO Shutters: Open
) ELSE IF %ERRORLEVEL% EQU 1 (
  ECHO Shutters: Closed
) ELSE IF %ERRORLEVEL% EQU 2 (
  ECHO Shutters: Opening
) ELSE IF %ERRORLEVEL% EQU 3 (
  ECHO Shutters: Closing
) ELSE IF %ERRORLEVEL% EQU 4 (
  ECHO Shutters: Error
) ELSE IF %ERRORLEVEL% EQU 5 (
  ECHO Shutters: PartlyOpen
) ELSE (
  ECHO Shutters: UNKNOWN STATE
)
