@echo off
setlocal
python "%~dp0easygit.py" %*
set "EXITCODE=%ERRORLEVEL%"

for %%I in (%CMDCMDLINE%) do if /i "%%~I"=="%~f0" (
    echo.
    pause
)

exit /b %EXITCODE%
