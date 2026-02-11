@echo off
REM Bench Sales Agent — Windows Install Script
echo =========================================
echo   Bench Sales Agent — Windows Installer
echo =========================================
echo.

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Download from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PY_VERSION=%%i
echo Found Python %PY_VERSION%

REM Set install directory
set INSTALL_DIR=%USERPROFILE%\.bench-sales-agent

REM Create virtual environment
if not exist "%INSTALL_DIR%\venv" (
    echo Creating virtual environment...
    python -m venv "%INSTALL_DIR%\venv"
) else (
    echo Existing installation found. Updating...
)

REM Activate and install
call "%INSTALL_DIR%\venv\Scripts\activate.bat"

echo Installing Bench Sales Agent...
pip install --upgrade pip -q
pip install "%~dp0.." -q

REM Create launcher batch file
(
echo @echo off
echo call "%INSTALL_DIR%\venv\Scripts\activate.bat"
echo bench-agent-web %%*
) > "%INSTALL_DIR%\bench-agent-web.bat"

REM Create desktop shortcut
echo Creating desktop shortcut...
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = oWS.ExpandEnvironmentStrings("%%USERPROFILE%%\Desktop\Bench Sales Agent.lnk"^)
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "%INSTALL_DIR%\bench-agent-web.bat"
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "Bench Sales Agent Web UI"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"
cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

echo.
echo =========================================
echo   Installation Complete!
echo =========================================
echo.
echo To start the agent:
echo   "%INSTALL_DIR%\bench-agent-web.bat"
echo.
echo Or double-click the "Bench Sales Agent" shortcut on your desktop.
echo.
echo Optional: Set your API key for AI features:
echo   set ANTHROPIC_API_KEY=your-key-here
echo.
pause
