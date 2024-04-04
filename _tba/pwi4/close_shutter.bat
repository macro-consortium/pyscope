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
ECHO Closing
%PWSHUTTER% close
IF %ERRORLEVEL% EQU 0 (
  ECHO Closed successfully
) ELSE (
  ECHO ERROR while closing shutters
  EXIT /B
)
