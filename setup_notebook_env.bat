@echo off
setlocal EnableExtensions

REM ============================================================
REM Inputs
REM ============================================================
set "BASE_ROOT=%USERPROFILE%\Phython"
set "INPUT=%~1"

if "%INPUT%"=="" (
  echo.
  echo Enter either the full project path or just the project name under "%BASE_ROOT%".
  set /p "INPUT=Project path or name: "
)

REM If only a name was provided, map to BASE_ROOT\name
if exist "%INPUT%" (
  set "PROJECT_DIR=%INPUT%"
) else (
  set "PROJECT_DIR=%BASE_ROOT%\%INPUT%"
)

for %%A in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fA"

if not exist "%PROJECT_DIR%\pyproject.toml" (
  echo.
  echo Expected pyproject.toml not found in "%PROJECT_DIR%".
  echo Check the path/name and try again.
  exit /b 1
)

echo.
echo Target project: "%PROJECT_DIR%"

REM Extract project folder name for kernel name
for %%A in ("%PROJECT_DIR%") do set "PROJ_BASENAME=%%~nA"

REM ============================================================
REM Pre-checks
REM ============================================================
where uv >nul 2>nul
if errorlevel 1 (
  echo.
  echo 'uv' not found on PATH. Please install uv first and retry.
  echo See: https://docs.astral.sh/uv/getting-started/installation/
  exit /b 1
)

pushd "%PROJECT_DIR%" || (echo Failed to enter "%PROJECT_DIR%" & exit /b 1)

REM ============================================================
REM Step 1: Virtual environment
REM ============================================================
echo.
if exist ".venv\pyvenv.cfg" (
  echo Found existing .venv
  choice /C RN /N /M "  [R]ecreate venv  or  [N] keep existing? "
  if errorlevel 2 (
    echo Keeping existing .venv
  ) else (
    echo Recreating .venv ...
    rmdir /s /q ".venv"
    if exist ".venv" (
      echo Failed to remove ".venv"
      popd & exit /b 1
    )
  )
) else (
  echo No .venv found. A new one will be created.
)

echo Ensuring .venv with: uv venv
uv venv
if errorlevel 1 (
  echo uv venv failed. Aborting.
  popd & exit /b 1
)

REM ============================================================
REM Step 2: Packages (runtime + dev)
REM ============================================================
echo.
echo Installing runtime libraries: matplotlib pandas scipy
uv add matplotlib pandas scipy
if errorlevel 1 (
  echo uv add (runtime) failed. Aborting.
  popd & exit /b 1
)

echo.
echo Installing dev tools: ipykernel pytest
uv add --dev ipykernel pytest
if errorlevel 1 (
  echo uv add (dev) failed. Aborting.
  popd & exit /b 1
)

REM ============================================================
REM Step 3: Register Jupyter kernel bound to this environment
REM ============================================================
echo.
echo Registering Jupyter kernel: Python (%PROJ_BASENAME%)
uv run python -m ipykernel install --user --name "%PROJ_BASENAME%" --display-name "Python (%PROJ_BASENAME%)" --force
if errorlevel 1 (
  echo Kernel registration failed. Aborting.
  popd & exit /b 1
)

REM ============================================================
REM Step 4 (Optional): Open in VS Code
REM ============================================================
echo.
choice /C YN /N /M "Open in VS Code now? [Y/N]: "
if errorlevel 2 (
  echo Skipping VS Code launch.
) else (
  where code >nul 2>nul
  if errorlevel 1 (
    for %%P in (
      "%LocalAppData%\Programs\Microsoft VS Code\Code.exe"
      "C:\Program Files\Microsoft VS Code\Code.exe"
      "%LocalAppData%\Programs\Microsoft VS Code Insiders\Code - Insiders.exe"
    ) do (
      if exist "%%~P" (
        echo Launching: %%~P "%PROJECT_DIR%"
        start "" "%%~P" "%PROJECT_DIR%"
        goto :launch_done
      )
    )
    echo VS Code not found. Open folder manually: "%PROJECT_DIR%"
  ) else (
    echo Launching: code "%PROJECT_DIR%"
    start "" code "%PROJECT_DIR%"
  )
)
:launch_done

popd

echo.
echo Setup complete.
echo - Environment: "%PROJECT_DIR%\.venv"
echo - Jupyter kernel: "Python (%PROJ_BASENAME%)"
endlocal