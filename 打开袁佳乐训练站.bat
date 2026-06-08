@echo off
chcp 65001 > nul
cd /d "%~dp0"
if exist "C:\Program Files\Python312\python.exe" (
  set "PYTHON=C:\Program Files\Python312\python.exe"
) else (
  set "PYTHON=python"
)
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
  taskkill /PID %%p /F > nul 2> nul
)
start "YJL Tutor Server 8000" /D "%~dp0" run_tutor_server_8000.cmd
ping 127.0.0.1 -n 5 > nul
start "" "http://127.0.0.1:8000/captain/today"
