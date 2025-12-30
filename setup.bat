@echo off
REM DaVinci Resolve Automation Setup Script for Windows

echo ==========================================
echo DaVinci Resolve Automation Setup
echo ==========================================
echo.

echo Detected platform: Windows
echo.

REM Set Windows paths
set "RESOLVE_SCRIPT_API=C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
set "RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
set "LUT_DIR=C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT"

echo ==========================================
echo Step 1: Checking DaVinci Resolve installation
echo ==========================================

REM Check if DaVinci Resolve is installed
if not exist "%RESOLVE_SCRIPT_API%" (
    echo [ERROR] DaVinci Resolve API not found at:
    echo    %RESOLVE_SCRIPT_API%
    echo.
    echo Please install DaVinci Resolve Studio before running this script.
    echo Note: Free version has limited API access.
    pause
    exit /b 1
)

echo [OK] DaVinci Resolve installation found
echo.

echo ==========================================
echo Step 2: Setting up environment variables
echo ==========================================

REM Set user environment variables permanently
setx RESOLVE_SCRIPT_API "%RESOLVE_SCRIPT_API%"
setx RESOLVE_SCRIPT_LIB "%RESOLVE_SCRIPT_LIB%"

REM Set for current session
set "RESOLVE_SCRIPT_API=%RESOLVE_SCRIPT_API%"
set "RESOLVE_SCRIPT_LIB=%RESOLVE_SCRIPT_LIB%"
set "PYTHONPATH=%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules"

echo [OK] Environment variables configured
echo.

echo ==========================================
echo Step 3: Installing sample LUTs
echo ==========================================

REM Create LUT directory if it doesn't exist
if not exist "%LUT_DIR%" (
    echo Creating LUT directory: %LUT_DIR%
    mkdir "%LUT_DIR%"
)

REM Copy sample LUTs
if exist "Examples\LUT" (
    echo Copying sample LUTs to %LUT_DIR%...

    for %%f in (Examples\LUT\*.cube) do (
        copy /Y "%%f" "%LUT_DIR%\" >nul
        echo   [OK] %%~nxf
    )

    echo.
    echo [OK] Sample LUTs installed successfully
) else (
    echo [WARNING] Examples\LUT directory not found
)

echo.

echo ==========================================
echo Step 4: Verifying Python installation
echo ==========================================

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python 3.6 or later from https://www.python.org/
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%v in ('python --version') do set PYTHON_VERSION=%%v
    echo [OK] !PYTHON_VERSION! found
)

echo.

echo ==========================================
echo Step 5: Testing DaVinci Resolve API connection
echo ==========================================

REM Test API connection
python -c "import sys; import os; sys.path.append(os.environ['RESOLVE_SCRIPT_API'] + '\\Modules'); import DaVinciResolveScript as dvr; resolve = dvr.scriptapp('Resolve'); print('[OK] Successfully connected to DaVinci Resolve' if resolve else '[ERROR] Could not connect'); pm = resolve.GetProjectManager() if resolve else None; project = pm.GetCurrentProject() if pm else None; print(f'[OK] Current project: {project.GetName()}' if project else '[INFO] No project currently open')" 2>nul

if errorlevel 1 (
    echo [WARNING] API connection test failed
    echo.
    echo Troubleshooting:
    echo 1. Make sure DaVinci Resolve is running
    echo 2. Make sure you have DaVinci Resolve Studio (not free version^)
    echo 3. Try restarting DaVinci Resolve
    echo 4. Restart this command prompt and try again
    echo.
    pause
    exit /b 1
)

echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Summary:
echo   * Platform: Windows
echo   * Environment variables: Configured
echo   * Sample LUTs: Installed
echo   * API connection: Working
echo.
echo Next steps:
echo.
echo 1. RESTART this command prompt for environment variables to take effect
echo.
echo 2. Open a project in DaVinci Resolve
echo.
echo 3. Try running a sample script:
echo    python Scripts\ColorGrading\lut_comparison.py
echo.
echo 4. Read the documentation:
echo    type README.md
echo    type Docs\Best_Practices.md
echo.
echo ==========================================

pause
