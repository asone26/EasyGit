@echo off
setlocal
python "%~dp0easygit.py" --uninstall
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to execute Python.
)
echo.
pause

