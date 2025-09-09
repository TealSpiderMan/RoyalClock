@echo off
echo Building Royal Clock...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the application
pyinstaller --onefile --windowed --add-data "alert.png;." --add-data "alert.mp3;." --add-data "icon.png;." --add-data "icon.ico;." --icon="icon.ico" --name "RoyalClock" royalclock_safe.py

REM Copy assets to dist folder
copy "alert.png" "dist\"
copy "alert.mp3" "dist\"
copy "icon.png" "dist\"
copy "icon.ico" "dist\"

echo.
echo Build complete! Check the 'dist' folder for RoyalClock.exe
pause
