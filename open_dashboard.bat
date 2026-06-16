@echo off
REM ====================================================================
REM  VECTRA-X dashboard launcher
REM  Serves the dashboard and local assessment API, then opens the
REM  evidence dashboard in your browser. A server is required because
REM  browsers block fetch() of local JSON over file://.
REM
REM  Prereq (run once after training / release refresh):
REM     py run_pipeline.py
REM     py scripts\validate_web_bundle.py
REM  Then just double-click this file.
REM ====================================================================
setlocal
cd /d "%~dp0"

if not exist "web\data\manifest.json" (
  echo.
  echo   [!] web\data\manifest.json not found.
  echo       Run first:   py run_pipeline.py
  echo.
  pause
  exit /b 1
)

if not exist "web\data\evidence.json" (
  echo.
  echo   [!] web\data\evidence.json not found.
  echo       Run first:   py run_pipeline.py
  echo.
  pause
  exit /b 1
)

if not exist "web\serve_live.py" (
  echo.
  echo   [!] web\serve_live.py not found.
  echo       This launcher must be run from the VECTRA-X repo root.
  echo.
  pause
  exit /b 1
)

REM Prefer common per-user Python installs used on this machine, then a
REM working Windows py launcher, then PATH python.
set "PY_EXE="
set "PY_ARGS="

for %%P in (
  "%LocalAppData%\Programs\Python\Python312\python.exe"
  "%LocalAppData%\Programs\Python\Python311\python.exe"
  "%LocalAppData%\Programs\Python\Python310\python.exe"
  "%~dp0.venv\Scripts\python.exe"
) do (
  if not defined PY_EXE if exist "%%~P" (
    "%%~P" -c "import sys" >nul 2>nul && set "PY_EXE=%%~P"
  )
)

where py >nul 2>nul
if %ERRORLEVEL%==0 if not defined PY_EXE (
  py -3 -c "import sys" >nul 2>nul
  if %ERRORLEVEL%==0 (
    set "PY_EXE=py"
    set "PY_ARGS=-3"
  )
)

where python >nul 2>nul
if %ERRORLEVEL%==0 if not defined PY_EXE (
  python -c "import sys" >nul 2>nul
  if %ERRORLEVEL%==0 (
    set "PY_EXE=python"
  )
)

if not defined PY_EXE (
  echo.
  echo   [!] Python was not found.
  echo       Install Python or run the dashboard with a known interpreter:
  echo       C:\Users\rapha\AppData\Local\Programs\Python\Python312\python.exe web\serve_live.py --port 4173
  echo.
  pause
  exit /b 1
)

set "PORT=4173"
set "URL=http://127.0.0.1:%PORT%/dashboard.html"
echo.
echo   VECTRA-X dashboard  -  %URL%
echo   Serving with: "%PY_EXE%" %PY_ARGS% web\serve_live.py --port %PORT%
echo   Close the "VECTRA-X server" window to stop the server.
echo.

if defined VECTRA_X_DRY_RUN (
  echo   Dry run only: launcher resolved successfully.
  exit /b 0
)

REM Start the live server in its own window, give it a moment, then open the dashboard.
start "VECTRA-X server" "%PY_EXE%" %PY_ARGS% web\serve_live.py --port %PORT%
timeout /t 1 >nul
start "" "%URL%"

endlocal
