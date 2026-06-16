@echo off
REM ====================================================================
REM  VECTRA-X dashboard launcher
REM  Serves the landing page, dashboard, and local assessment API, then
REM  opens the landing page in your browser. A server is required because
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

REM Prefer common per-user Python installs used on this machine, then PATH python.
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
  echo       Install Python 3.10+ and double-click this file again.
  echo.
  pause
  exit /b 1
)

set "VENV_DIR=%~dp0.dashboard-venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

if not exist "%VENV_PY%" (
  echo.
  echo   Creating local dashboard environment...
  "%PY_EXE%" %PY_ARGS% -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo.
    echo   [!] Could not create .dashboard-venv.
    echo       Try running: "%PY_EXE%" -m venv .dashboard-venv
    echo.
    pause
    exit /b 1
  )
)

"%VENV_PY%" -c "import joblib, sklearn, pandas, numpy" >nul 2>nul
if errorlevel 1 (
  echo.
  echo   Installing local dashboard dependencies...
  "%VENV_PY%" -m pip install --upgrade pip >nul
  "%VENV_PY%" -m pip install -r web\requirements.txt
  if errorlevel 1 (
    echo.
    echo   [!] Dependency install failed.
    echo       Check the messages above, then run this file again.
    echo.
    pause
    exit /b 1
  )
)

set "PORT="
for %%P in (4173 4174 4175 4176 4177) do (
  if not defined PORT (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 'http://127.0.0.1:%%P/api/health'; if ($r.StatusCode -eq 200) { exit 2 } else { exit 1 } } catch { try { $tcp = New-Object Net.Sockets.TcpClient; $iar = $tcp.BeginConnect('127.0.0.1', %%P, $null, $null); if ($iar.AsyncWaitHandle.WaitOne(250)) { $tcp.EndConnect($iar); $tcp.Close(); exit 1 } else { $tcp.Close(); exit 0 } } catch { exit 0 } }" >nul 2>nul
    if errorlevel 2 (
      set "PORT=%%P"
      set "SERVER_ALREADY_RUNNING=1"
    ) else if not errorlevel 1 (
      set "PORT=%%P"
    )
  )
)

if not defined PORT (
  echo.
  echo   [!] Ports 4173-4177 are already in use.
  echo       Close the old server window and run this launcher again.
  echo.
  pause
  exit /b 1
)

set "URL=http://127.0.0.1:%PORT%/index.html"
echo.
echo   VECTRA-X landing page  -  %URL%
echo   Serving with: "%VENV_PY%" web\serve_live.py --port %PORT%
echo   Close the "VECTRA-X server" window to stop the server.
echo.

if defined VECTRA_X_DRY_RUN (
  echo   Dry run only: launcher resolved successfully.
  exit /b 0
)

if not defined SERVER_ALREADY_RUNNING (
  start "VECTRA-X server" cmd /k ""%VENV_PY%" web\serve_live.py --port %PORT%"
)

echo   Waiting for local server...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$url='http://127.0.0.1:%PORT%/api/health'; for ($i=0; $i -lt 40; $i++) { try { $r=Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 $url; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 500 }; exit 1"
if errorlevel 1 (
  echo.
  echo   [!] Server did not become ready.
  echo       Check the "VECTRA-X server" window for details.
  echo.
  pause
  exit /b 1
)

start "" "%URL%"

endlocal
