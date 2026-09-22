@echo off
cd /d "%~dp0"
for /f "skip=1 tokens=1" %%p in ('wmic process where "name='python.exe'" get ProcessId 2^>nul') do (
    if not "%%p"=="" (
        taskkill /PID %%p /F >nul 2>&1
    )
)
exit /b 0
