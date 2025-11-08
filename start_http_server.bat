@echo off
REM Startup script for MCP Python Starter HTTP Server (Windows)
REM This allows the server to be accessed from any project with per-developer credentials

echo 🚀 Starting MCP Python Starter HTTP Server
echo.
echo ℹ️  HTTP Mode: Each developer provides their own credentials through MCP client
echo    Server does not need credentials at startup
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
echo 📝 Developers should configure their projects with:
echo    See .vscode/mcp-http.json for example configuration
echo    Each developer will be prompted for their credentials
echo.

python server.py sse
