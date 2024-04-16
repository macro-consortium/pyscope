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
ECHO Opening
%PWSHUTTER% open
IF %ERRORLEVEL% EQU 0 (
  ECHO Opened successfully
) ELSE (
  ECHO ERROR while opening shutters
  EXIT /B
)
