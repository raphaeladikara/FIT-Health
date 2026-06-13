@echo off
setlocal EnableExtensions

REM VECTRA-X Next.js Outbreak Triage Command Center launcher.
REM Double-click this file, or run: open_dashboard.bat --hostname 0.0.0.0

cd /d "%~dp0"
title VECTRA-X Command Center

if not exist "web\package.json" (
    echo.
    echo [ERROR] web\package.json was not found.
    echo Run this launcher from the VECTRA-X project folder.
    echo.
    pause
    exit /b 1
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] npm was not found.
    echo Install Node.js 20 or newer, then reopen this launcher.
    echo.
    pause
    exit /b 1
)

if /I "%VECTRA_X_LAUNCHER_TEST%"=="1" (
    echo VECTRA_X_LAUNCHER_OK
    exit /b 0
)

if not exist "web\node_modules" (
    echo [SETUP] Installing web dependencies...
    pushd "web"
    call npm.cmd install
    set "INSTALL_EXIT=%ERRORLEVEL%"
    popd
    if not "%INSTALL_EXIT%"=="0" (
        echo.
        echo [ERROR] npm install failed with exit code %INSTALL_EXIT%.
        pause
        exit /b %INSTALL_EXIT%
    )
)

if not exist "web\public\data\manifest.json" (
    echo [DATA] Exporting privacy-safe dashboard artifacts...
    set "PYTHON_CMD="
    where python.exe >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python.exe"
    if not defined PYTHON_CMD if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    if not defined PYTHON_CMD (
        where py.exe >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=py.exe -3.12"
    )
    if not defined PYTHON_CMD (
        echo.
        echo [ERROR] Public web data is missing and Python could not be found.
        echo Run scripts\export_web_data.py with Python 3.10 or newer.
        pause
        exit /b 1
    )
    %PYTHON_CMD% scripts\export_web_data.py
    if errorlevel 1 (
        echo.
        echo [ERROR] Web data export failed.
        pause
        exit /b 1
    )
)

echo.
echo ================================================================
echo   VECTRA-X Outbreak Triage Command Center
echo ================================================================
echo   Project : %CD%
echo   URL     : http://localhost:3000
echo   Stop    : Press Ctrl+C in this window
echo ================================================================
echo.

start "" powershell.exe -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://localhost:3000'"

pushd "web"
call npm.cmd run dev -- %*
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] The VECTRA-X command center stopped with exit code %EXIT_CODE%.
    echo Run npm.cmd install inside the web folder, then try again.
    echo.
    pause
)

exit /b %EXIT_CODE%
