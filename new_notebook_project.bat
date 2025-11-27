@echo off
setlocal EnableExtensions

REM ---- Root folder for all projects ----
set "BASE_ROOT=%USERPROFILE%\Phython"

REM Optional override: new_notebook_project.bat "D:\Projects"
if not "%~1"=="" set "BASE_ROOT=%~1"

for %%A in ("%BASE_ROOT%") do set "BASE_ROOT=%%~fA"
if not exist "%BASE_ROOT%" (
  mkdir "%BASE_ROOT%" || (echo Failed to create project root "%BASE_ROOT%" & exit /b 1)
)

echo.
echo Project root: "%BASE_ROOT%"

REM ---- Prompt for name/description (no validation beyond non-empty) ----
:ask_name
set "PROJECT_NAME="
set /p "PROJECT_NAME=Project Name: "
if "%PROJECT_NAME%"=="" (
  echo Project Name is required.
  goto ask_name
)

echo.
set "DESCRIPTION="
set /p "DESCRIPTION=Description: "

REM ---- Locate helper and create the project skeleton only ----
set "SCRIPT=%~dp0create_notebook_project.py"
if not exist "%SCRIPT%" (
  echo Could not find script at: %SCRIPT%
  echo Ensure this .bat resides next to create_notebook_project.py
  exit /b 1
)

echo.
echo Creating project "%PROJECT_NAME%" in "%BASE_ROOT%"
py -3 "%SCRIPT%" -n "%PROJECT_NAME%" -d "%DESCRIPTION%" -o "%BASE_ROOT%"
if errorlevel 1 (
  echo Project creation failed.
  exit /b 1
)

echo.
echo Done. Project created under: "%BASE_ROOT%\%PROJECT_NAME%"
echo (Next step) Run setup_notebook_env.bat to configure the environment.
endlocal