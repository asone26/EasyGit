@echo off
setlocal
if exist "%~dp0easygit.exe" (
    "%~dp0easygit.exe" --install
) else (
    python "%~dp0easygit.py" --install
)
if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed.
)
echo.
pause
