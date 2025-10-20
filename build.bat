@echo off
REM Build Plantos MCP Installer for Windows

echo Building Plantos MCP Installer...

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the installer
echo Building installer...
pyinstaller installer.spec

echo.
echo Build complete!
echo.
echo Windows Executable: dist\plantos-mcp-installer.exe
echo.
echo To test locally:
echo   dist\plantos-mcp-installer.exe
echo.
echo To distribute:
echo   1. Zip the exe: cd dist ^&^& tar -a -c -f plantos-mcp-installer-windows.zip plantos-mcp-installer.exe
echo   2. Upload to GitHub Releases
