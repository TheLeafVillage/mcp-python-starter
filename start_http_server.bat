@echo off
REM Startup script for MCP Python Starter HTTP Server (Windows)
REM This allows the server to be accessed from any project

echo 🚀 Starting MCP Python Starter HTTP Server
echo.

REM Check if environment variables are set
if "%DOC_EMAIL%"=="" (
    echo ⚠️  Warning: DOC_EMAIL not set
    echo    Setting default credentials...
    set DOC_EMAIL=developer@example.com
)

if "%DOC_PASSWORD%"=="" (
    echo ⚠️  Warning: DOC_PASSWORD not set
    echo    Setting default credentials...
    set DOC_PASSWORD=devpassword123
)

echo 📧 DOC_EMAIL: %DOC_EMAIL%
echo 🔑 DOC_PASSWORD: ********
echo.

REM Check if mock documentation server is running
curl -s http://localhost:5001 >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Mock documentation server not detected on port 5001
    echo    Start it with: python mock_doc_server.py
    echo.
)

REM Start the MCP server in SSE mode
echo 🌐 Starting HTTP server on port 8000...
echo.

python server.py sse
