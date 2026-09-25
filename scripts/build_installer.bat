@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo  Endocare Endoscopy Management System - Build Pipeline
echo ========================================================
echo.

:: 1. Verify Python & PyInstaller
echo [1/3] Compiling Application with PyInstaller...
python -m PyInstaller --clean -y endocare.spec
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller compilation failed!
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Verifying Output Bundle...
if not exist "dist\Endocare\Endocare.exe" (
    echo [ERROR] dist\Endocare\Endocare.exe was not created!
    exit /b 1
)
echo [SUCCESS] Binary bundle generated in dist\Endocare\

echo.
echo [3/3] Compiling Windows Setup Installer with Inno Setup...

:: Locate ISCC.exe
set "ISCC_PATH="
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    for /f "delims=" %%I in ('where iscc 2^>nul') do set "ISCC_PATH=%%I"
)

if "!ISCC_PATH!"=="" (
    echo [WARNING] Inno Setup compiler (ISCC.exe) not found on PATH.
    echo The portable build in 'dist\Endocare\' is ready to use!
    echo To create the installer EXE, please install Inno Setup 6 and run this script again.
    exit /b 0
)

echo Using Inno Setup: "!ISCC_PATH!"
"!ISCC_PATH!" installer\endocare_setup.iss
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Inno Setup failed to compile the installer.
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo  BUILD COMPLETE!
echo  Installer location: installer_output\Endocare_Setup_v2.42.exe
echo ========================================================
pause
