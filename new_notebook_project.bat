@echo off
setlocal enabledelayedexpansion

REM Determine roots
set "DEVROOT=%USERPROFILE%\dev"
set "KPDEV=%DEVROOT%\kp-dev"

if not exist "%DEVROOT%" mkdir "%DEVROOT%"
if not exist "%KPDEV%" mkdir "%KPDEV%"

echo.
echo Select project type:
echo   1^) Personal Project  -^> %DEVROOT%
echo   2^) KP Project        -^> %KPDEV%
choice /C 12 /N /M "Enter choice (1 or 2): "
set "CHOICE=%ERRORLEVEL%"

set "OUTPUT_DIR=%DEVROOT%"
if "%CHOICE%"=="2" set "OUTPUT_DIR=%KPDEV%"

echo.
set /p "PROJECT_NAME=Project Name: "
if "%PROJECT_NAME%"=="" (
  echo Project Name is required.
  exit /b 1
)

echo.
set /p "DESCRIPTION=Description: "

REM Path to the create script (same folder as this .bat)
set "SCRIPT=%~dp0create_notebook_project.py"

if not exist "%SCRIPT%" (
  echo Could not find script at: %SCRIPT%
  echo Make sure the repo is cloned, and this .bat resides next to create_notebook_project.py
  exit /b 1
)

echo.
echo Creating project "%PROJECT_NAME%" in "%OUTPUT_DIR%"
REM Use py launcher for Windows for more robust Python discovery
py -3 "%SCRIPT%" -n "%PROJECT_NAME%" -d "%DESCRIPTION%" -o "%OUTPUT_DIR%"

if errorlevel 1 (
  echo Project creation failed.
  exit /b 1
)

echo.
echo Done. Project created under: "%OUTPUT_DIR%\%PROJECT_NAME%"
endlocal

