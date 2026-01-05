@echo off
REM Hearth Writer Desktop Shortcut Creator for Windows
REM This script creates a desktop shortcut that launches Hearth Writer

echo.
echo  ========================================
echo   Hearth Writer - Desktop Shortcut Setup
echo  ========================================
echo.

set /p LICENSE_KEY="Enter your license key (HRTH_xxx): "

echo.
echo Creating desktop shortcut...

(
echo @echo off
echo title Hearth Writer
echo echo Starting Hearth Writer...
echo wsl -e bash -c "export HEARTH_LICENSE_KEY='%LICENSE_KEY%' && cd ~/hearth-writer && ./start.sh"
) > "%USERPROFILE%\Desktop\Hearth Writer.bat"

echo.
echo  ========================================
echo   SUCCESS! Shortcut created on Desktop
echo  ========================================
echo.
echo Double-click "Hearth Writer" on your desktop to start writing!
echo.
pause
