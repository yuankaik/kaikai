@echo off
chcp 65001 > nul
cd /d "%~dp0"
"C:\Program Files\Python312\python.exe" -u scripts\start_tutor_site.py --host 127.0.0.1 --port 8000 1>server_runtime.out.log 2>server_runtime.err.log
pause
