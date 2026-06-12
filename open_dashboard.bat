@echo off
REM ====================================================================
REM  VECTRA-X dashboard launcher
REM  Serves the static web/ folder over a local HTTP server and opens it
REM  in your browser. A server is required because browsers block
REM  fetch() of local JSON over file:// .
REM
REM  Prereq (run once after training):
REM     py run_pipeline.py
REM     py export_web_data.py
REM  Then just double-click this file.
REM ====================================================================
setlocal
cd /d "%~dp0web"

if not exist "data\dashboard.json" (
  echo.
  echo   [!] web\data\dashboard.json not found.
  echo       Run first:   py run_pipeline.py   then   py export_web_data.py
  echo.
  pause
  exit /b 1
)

REM prefer the Windows py launcher, fall back to python
where py >nul 2>nul && (set "PY=py") || (set "PY=python")

set "PORT=8765"
echo.
echo   VECTRA-X dashboard  -  http://localhost:%PORT%
echo   Serving with: %PY% -m http.server %PORT%
echo   Close the "VECTRA-X server" window to stop the server.
echo.

REM start the server in its own window, give it a moment, then open the browser
start "VECTRA-X server" %PY% -m http.server %PORT%
timeout /t 1 >nul
start "" "http://localhost:%PORT%/"

endlocal
