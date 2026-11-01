@echo off
setlocal
python "%~dp0easygit.py" --install
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to execute Python. Please make sure Python is installed and added to PATH.
)
echo.

