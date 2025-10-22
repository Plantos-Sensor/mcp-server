@echo off
REM Plantos MCP Installer for Windows
REM One-click installer for connecting Plantos to Claude Desktop

setlocal enabledelayedexpansion

REM API endpoint
if "%PLANTOS_API_URL%"=="" (
    set API_URL=https://api.plantos.co
) else (
    set API_URL=%PLANTOS_API_URL%
)

echo.
echo ================================ Plantos MCP Installer ================================
echo.

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not installed
    echo Please install Python 3 from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Check if pip is installed
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed
    echo Installing pip...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo Failed to install pip. Please install it manually.
        pause
        exit /b 1
    )
)

echo [OK] pip found
echo.

REM Step 1: Request authorization code
echo Requesting authorization code...
curl -s -X POST "%API_URL%/api/v1/mcp/request-code" -H "Content-Type: application/json" > %TEMP%\plantos_auth.json

if errorlevel 1 (
    echo [ERROR] Failed to connect to Plantos API
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

REM Parse the JSON response using Python
python -c "import json; data = json.load(open(r'%TEMP%\plantos_auth.json')); print(data.get('code', ''))" > %TEMP%\plantos_code.txt
set /p CODE=<%TEMP%\plantos_code.txt

python -c "import json; data = json.load(open(r'%TEMP%\plantos_auth.json')); print(data.get('verification_url', ''))" > %TEMP%\plantos_url.txt
set /p VERIFICATION_URL=<%TEMP%\plantos_url.txt

if "%CODE%"=="" (
    echo [ERROR] Failed to get authorization code
    type %TEMP%\plantos_auth.json
    echo.
    pause
    exit /b 1
)

echo.
echo ==================================================================================
echo.
echo Your authorization code:
echo.
echo          %CODE%
echo.
echo ==================================================================================
echo.
echo Opening your browser to authorize...
echo If the browser doesn't open, visit:
echo %VERIFICATION_URL%
echo.

REM Open browser
start "" "%VERIFICATION_URL%"

REM Step 2: Poll for authorization
echo Waiting for authorization...
echo (This will time out in 5 minutes if not authorized)
echo.

set ATTEMPT=0
set MAX_ATTEMPTS=60

:poll_loop
if %ATTEMPT% geq %MAX_ATTEMPTS% goto timeout

timeout /t 5 /nobreak >nul
set /a ATTEMPT+=1

curl -s "%API_URL%/api/v1/mcp/check-code?code=%CODE%" > %TEMP%\plantos_check.json

REM Check status
python -c "import json; data = json.load(open(r'%TEMP%\plantos_check.json')); print(data.get('status', ''))" > %TEMP%\plantos_status.txt
set /p STATUS=<%TEMP%\plantos_status.txt

if "%STATUS%"=="authorized" (
    python -c "import json; data = json.load(open(r'%TEMP%\plantos_check.json')); print(data.get('api_key', ''))" > %TEMP%\plantos_apikey.txt
    set /p API_KEY=<%TEMP%\plantos_apikey.txt

    if not "!API_KEY!"=="" (
        echo [OK] Authorization successful!
        echo.
        goto install
    )
)

if "%STATUS%"=="expired" (
    echo [ERROR] Authorization code expired
    echo Please run the installer again.
    echo.
    pause
    exit /b 1
)

REM Show progress every 30 seconds
set /a PROGRESS_CHECK=!ATTEMPT! %% 6
if !PROGRESS_CHECK!==0 (
    set /a ELAPSED=!ATTEMPT! * 5
    echo Still waiting... (!ELAPSED!s elapsed)
)

goto poll_loop

:timeout
echo [ERROR] Authorization timed out
echo Please run the installer again and authorize within 5 minutes.
echo.
pause
exit /b 1

:install
REM Step 3: Install plantos-mcp
echo Installing Plantos MCP server...
python -m pip install --upgrade plantos-mcp --quiet

if errorlevel 1 (
    echo [ERROR] Failed to install plantos-mcp
    echo Please check your Python installation and try again.
    echo.
    pause
    exit /b 1
)

echo [OK] Plantos MCP installed
echo.

REM Step 4: Configure Claude Desktop
echo Configuring Claude Desktop...

set CONFIG_DIR=%APPDATA%\Claude
set CONFIG_FILE=%CONFIG_DIR%\claude_desktop_config.json

REM Create config directory if it doesn't exist
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

REM Read existing config or create new one
if exist "%CONFIG_FILE%" (
    type "%CONFIG_FILE%" > %TEMP%\plantos_existing_config.json
) else (
    echo {}> %TEMP%\plantos_existing_config.json
)

REM Add Plantos MCP to config using Python
python -c "import json; config = json.load(open(r'%TEMP%\plantos_existing_config.json')); config.setdefault('mcpServers', {})['plantos'] = {'command': 'plantos-mcp', 'env': {'PLANTOS_API_KEY': '%API_KEY%'}}; json.dump(config, open(r'%CONFIG_FILE%', 'w'), indent=2)"

echo [OK] Claude Desktop configured
echo.

REM Success!
echo ==================================================================================
echo.
echo [SUCCESS] Installation Complete!
echo.
echo Next steps:
echo 1. Restart Claude Desktop (if it's running)
echo 2. Start a new conversation
echo 3. Ask Claude about weather, soil, crops, etc.
echo.
echo Example prompts:
echo   * "What's the weather like for farming in Austin, TX?"
echo   * "Analyze the soil at coordinates 30.2672, -97.7431"
echo   * "Predict corn yield for my location"
echo.
echo Need help? Visit https://plantos.co/docs
echo.
echo ==================================================================================
echo.

REM Clean up temp files
del %TEMP%\plantos_auth.json >nul 2>&1
del %TEMP%\plantos_code.txt >nul 2>&1
del %TEMP%\plantos_url.txt >nul 2>&1
del %TEMP%\plantos_check.json >nul 2>&1
del %TEMP%\plantos_status.txt >nul 2>&1
del %TEMP%\plantos_apikey.txt >nul 2>&1
del %TEMP%\plantos_existing_config.json >nul 2>&1

pause
