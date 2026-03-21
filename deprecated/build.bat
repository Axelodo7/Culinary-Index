@echo off
title The Culinary Index - Build Script
echo ============================================
echo   The Culinary Index - Build Script
echo ============================================
echo.

echo [1/4] Installing dependencies...
pip install customtkinter requests beautifulsoup4 ddgs Pillow pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo       Done.
echo.

echo [2/4] Generating icon assets...
python generate_assets.py
if errorlevel 1 (
    echo ERROR: Failed to generate assets
    pause
    exit /b 1
)
echo       Done.
echo.

echo [3/4] Building executable with PyInstaller...
pyinstaller CulinaryIndex.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo       Done.
echo.

echo [4/4] Copying assets to distribution folder...
if exist "dist\CulinaryIndex\assets" (
    echo       Assets already included by PyInstaller.
) else (
    mkdir "dist\CulinaryIndex\assets" 2>nul
    copy "assets\*" "dist\CulinaryIndex\assets\" >nul
    echo       Assets copied.
)
echo.

echo ============================================
echo   BUILD COMPLETE!
echo ============================================
echo.
echo   Executable: dist\CulinaryIndex\CulinaryIndex.exe
echo.
echo   To create a Windows installer, install Inno Setup
echo   and run: iscc installer.iss
echo.
pause
