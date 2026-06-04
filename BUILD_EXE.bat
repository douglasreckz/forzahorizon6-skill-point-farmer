@echo off
title Forza Skill Point Farmer — Build EXE
color 0A

echo ============================================================
echo   FORZA HORIZON — SKILL POINT FARMER
echo   EXE Compiler
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python not found!
    echo.
    echo Install Python 3.11+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during setup.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

:: Install dependencies
echo [1/3] Installing dependencies...
echo.
pip install pyautogui opencv-python numpy keyboard Pillow pyinstaller --quiet --upgrade
if errorlevel 1 (
    color 0C
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed!
echo.

:: Compile EXE
echo [2/3] Compiling EXE (this may take 1-2 minutes)...
echo.
pyinstaller --onefile --noconsole --name "ForzaSkillFarmer" farmer.py
if errorlevel 1 (
    echo Retrying with console window enabled (easier to debug)...
    pyinstaller --onefile --name "ForzaSkillFarmer" farmer.py
)
if errorlevel 1 (
    color 0C
    echo [ERROR] Compilation failed.
    pause
    exit /b 1
)

echo.
echo [OK] Compilation successful!
echo.

:: Move EXE to root folder
echo [3/3] Copying EXE to current folder...
if exist "dist\ForzaSkillFarmer.exe" (
    copy "dist\ForzaSkillFarmer.exe" "ForzaSkillFarmer.exe" >nul
    echo [OK] Created: ForzaSkillFarmer.exe
) else (
    echo [INFO] EXE is located at: dist\ForzaSkillFarmer.exe
)

:: Optional cleanup
echo.
set /p CLEAN="Remove temporary build files? (y/n): "
if /i "%CLEAN%"=="y" (
    rmdir /s /q build >nul 2>&1
    rmdir /s /q dist  >nul 2>&1
    del  /f /q "ForzaSkillFarmer.spec" >nul 2>&1
    echo [OK] Temporary files removed.
)

echo.
color 0A
echo ============================================================
echo   DONE!  ForzaSkillFarmer.exe is ready.
echo.
echo   IMPORTANT: Always run the EXE as Administrator!
echo   (Right-click → Run as administrator)
echo ============================================================
echo.
pause
