@echo off
setlocal
cd "%~dp0"

@ If EXIST "config.env" (
    for /f "delims== tokens=1,2" %%G in (config.env) do set %%G=%%H
)

python manage.py %*

endlocal
