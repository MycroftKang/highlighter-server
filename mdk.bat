@echo off
setlocal
cd "%~dp0"

python manage.py %*

endlocal
