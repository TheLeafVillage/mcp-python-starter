#!/bin/bash

# Startup script for MCP Python Starter HTTP Server
# This allows the server to be accessed from any project

echo "🚀 Starting MCP Python Starter HTTP Server"
echo ""

# Check if environment variables are set
if [ -z "$DOC_EMAIL" ] || [ -z "$DOC_PASSWORD" ]; then
    echo "⚠️  Warning: DOC_EMAIL and/or DOC_PASSWORD not set"
    echo "   Setting default credentials..."
    export DOC_EMAIL="developer@example.com"
    export DOC_PASSWORD="devpassword123"
fi

echo "📧 DOC_EMAIL: $DOC_EMAIL"
echo "🔑 DOC_PASSWORD: ********"
echo ""

# Check if mock documentation server is running
if ! curl -s http://localhost:5001 > /dev/null 2>&1; then
    echo "⚠️  Mock documentation server not detected on port 5001"
    echo "   Start it with: python mock_doc_server.py"
    echo ""
fi

# Start the MCP server in SSE mode
echo "🌐 Starting HTTP server on port 8000..."
echo ""

python server.py sse
