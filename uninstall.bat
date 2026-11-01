@echo off
setlocal
if exist "%~dp0easygit.exe" (
    "%~dp0easygit.exe" --uninstall
) else (
    python "%~dp0easygit.py" --uninstall
)
if errorlevel 1 (
    echo.
    echo [ERROR] Uninstallation failed.
)
echo.
pause
