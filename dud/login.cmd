@echo off
rem Sign the HaShamran publisher in to Substack again (only when the status file says so).
"%LOCALAPPDATA%\HaShamran\venv\Scripts\python.exe" "%LOCALAPPDATA%\HaShamran\app\publisher.py" login
pause
