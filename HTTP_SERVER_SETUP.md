# MCP Server HTTP Configuration

This document explains how to run the MCP server as an HTTP server that can be accessed from different projects.

## Running as HTTP Server

The MCP server supports multiple transport modes:

### 1. Stdio Mode (Default - Local Use Only)
```bash
python server.py stdio
# or just
python server.py
```
This mode runs the server via stdio and can only be accessed from the same process/IDE.

### 2. SSE Mode (HTTP - Remote Access)
```bash
python server.py sse
```
Starts an HTTP server using Server-Sent Events on `http://localhost:8000`

### 3. Streamable HTTP Mode (HTTP - Remote Access)
```bash
python server.py streamable-http
```
Starts an HTTP server using streamable HTTP on `http://localhost:8000`

## Configuration for Different Projects

Once the server is running in HTTP mode, you can access it from any project:

### VS Code MCP Configuration (.vscode/mcp.json)

**In Project A (where server runs):**
```bash
# Terminal 1: Start the HTTP server
cd /path/to/mcp-python-starter
export DOC_EMAIL="developer@example.com"
export DOC_PASSWORD="devpassword123"
python server.py sse
```

**In Project B (different project):**
```json
{
  "mcpServers": {
    "mcp-python-starter": {
      "url": "http://localhost:8000"
    }
  }
}
```

### With Environment Variables

Set authentication credentials as environment variables before starting the server:

```bash
export DOC_EMAIL="developer@example.com"
export DOC_PASSWORD="devpassword123"
export DOC_SERVER_URL="http://localhost:5001"  # if using different port for mock server
python server.py sse
```

The server will automatically use these credentials for documentation access.

### Example: Multi-Project Setup

**Terminal 1: Start mock documentation server**
```bash
cd /path/to/mcp-python-starter
python mock_doc_server.py
```

**Terminal 2: Start MCP HTTP server**
```bash
cd /path/to/mcp-python-starter
export DOC_EMAIL="developer@example.com"
export DOC_PASSWORD="devpassword123"
python server.py sse
```

**Any VS Code project can now connect:**
```json
{
  "mcpServers": {
    "weather-api-docs": {
      "url": "http://localhost:8000"
    }
  }
}
```

## Port Configuration

By default, the HTTP server runs on port 8000. This is configured in the FastMCP library settings.

To use a different port, you would need to modify the server initialization or set environment variables (check FastMCP documentation for details).

## Security Considerations

When running as an HTTP server:

1. **Network exposure**: The server binds to `0.0.0.0`, making it accessible from your local network
2. **No authentication on MCP endpoint**: The MCP protocol itself doesn't have built-in auth
3. **Environment variables**: Use environment variables for credentials instead of config files
4. **Production use**: For production, implement proper authentication, use HTTPS, and restrict network access

## Advantages of HTTP Mode

✅ **Access from any project**: Connect from different IDE instances or projects
✅ **Centralized server**: Run one instance, use from multiple places
✅ **Easy testing**: Can test with curl or Postman
✅ **Language agnostic**: Any MCP client can connect via HTTP
✅ **No stdio limitations**: Not tied to process lifecycle

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Try a different transport: `streamable-http` instead of `sse`

### Can't connect from other project
- Verify server is running: `curl http://localhost:8000`
- Check firewall settings
- Ensure correct URL in mcp.json configuration

### Authentication not working
- Verify environment variables are set in the terminal where server runs
- Check: `echo $DOC_EMAIL` and `echo $DOC_PASSWORD`
- Restart server after setting environment variables

## Example Session

```bash
# Terminal 1: Start mock doc server
$ python mock_doc_server.py
Starting Mock Documentation Server on http://localhost:5001
Default credentials: developer@example.com / devpassword123

# Terminal 2: Start MCP HTTP server
$ export DOC_EMAIL="developer@example.com"
$ export DOC_PASSWORD="devpassword123"
$ python server.py sse

🚀 Starting MCP server with SSE transport
📡 Server running at: http://localhost:8000

📝 Configure your MCP client with:
   {
     "mcpServers": {
       "mcp-python-starter": {
         "url": "http://localhost:8000"
       }
     }
   }

💡 Set environment variables for authentication:
   export DOC_EMAIL="developer@example.com"
   export DOC_PASSWORD="devpassword123"

🛑 Press Ctrl+C to stop the server

# Now any project can connect via http://localhost:8000
```
