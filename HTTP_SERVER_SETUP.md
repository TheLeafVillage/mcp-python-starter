# MCP Server HTTP Configuration

This document explains how to run the MCP server as an HTTP server that can be accessed from different projects, with each developer providing their own credentials.

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

## Per-Developer Credentials (Recommended for HTTP Mode)

When running in HTTP mode, **each developer provides their own credentials** through their MCP client configuration. This allows multiple developers to connect to the same server with different credentials.

### Setup

**Step 1: Start the HTTP server (no credentials needed at server level)**
```bash
# Terminal: Start the HTTP server without credentials
cd /path/to/mcp-python-starter
python server.py sse
```

The server starts without any baked-in credentials and accepts connections on `http://localhost:8000`.

**Step 2: Each developer configures their own project**

Each developer adds the server to their project's `.vscode/mcp.json` with **their own credentials**:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "DOC_EMAIL",
      "description": "Your email for documentation access",
      "default": "developer@example.com"
    },
    {
      "type": "promptString",
      "id": "DOC_PASSWORD",
      "description": "Your password for documentation access",
      "password": true
    }
  ],
  "mcpServers": {
    "weather-api-docs": {
      "url": "http://localhost:8000",
      "env": {
        "DOC_EMAIL": "${input:DOC_EMAIL}",
        "DOC_PASSWORD": "${input:DOC_PASSWORD}"
      }
    }
  }
}
```

**Step 3: VS Code prompts for credentials**

When the developer opens VS Code or connects to the MCP server:
1. VS Code prompts: "Your email for documentation access"
2. Developer enters: `alice@company.com`
3. VS Code prompts: "Your password for documentation access" (hidden input)
4. Developer enters their password
5. MCP client passes these credentials to the server

### Benefits

✅ **Multi-user support**: Different developers use different credentials  
✅ **No shared secrets**: Server doesn't need credentials at startup  
✅ **Secure**: Each developer manages their own credentials  
✅ **Audit trail**: Different users can be tracked (in production)

### Example: Team Setup

**Scenario**: 3 developers connecting to the same server

**Server (starts once, no credentials):**
```bash
$ cd ~/mcp-python-starter
$ python server.py sse
🚀 Starting MCP server with SSE transport
📡 Server running at: http://localhost:8000
```

**Developer 1 (Alice):**
```json
{
  "mcpServers": {
    "api-docs": {
      "url": "http://localhost:8000",
      "env": {
        "DOC_EMAIL": "alice@company.com",
        "DOC_PASSWORD": "alice-secret-password"
      }
    }
  }
}
```

**Developer 2 (Bob):**
```json
{
  "mcpServers": {
    "api-docs": {
      "url": "http://localhost:8000",
      "env": {
        "DOC_EMAIL": "bob@company.com",
        "DOC_PASSWORD": "bob-secret-password"
      }
    }
  }
}
```

**Developer 3 (Carol):**
```json
{
  "mcpServers": {
    "api-docs": {
      "url": "http://localhost:8000",
      "env": {
        "DOC_EMAIL": "carol@company.com",
        "DOC_PASSWORD": "carol-secret-password"
      }
    }
  }
}
```

Each developer authenticates with their own credentials when using the MCP tools!

## Alternative: Server-Level Credentials (Single User)

If you want the server to use a single set of credentials for all clients (not recommended for production):

```bash
export DOC_EMAIL="developer@example.com"
export DOC_PASSWORD="devpassword123"
python server.py sse
```

Client configuration:
```json
{
  "mcpServers": {
    "mcp-python-starter": {
      "url": "http://localhost:8000"
    }
  }
}
```

⚠️ **Note**: All developers would use the same credentials. Not recommended for production.

## Configuration for Different Projects

Once the server is running in HTTP mode, any project can connect:
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

## Advantages of HTTP Mode with Per-Developer Credentials

✅ **Multi-user support**: Each developer uses their own credentials  
✅ **Access from any project**: Connect from different IDE instances or projects  
✅ **Centralized server**: Run one instance, multiple developers can use it  
✅ **Easy testing**: Can test with curl or Postman  
✅ **Language agnostic**: Any MCP client can connect via HTTP  
✅ **No stdio limitations**: Not tied to process lifecycle  
✅ **Secure**: No shared secrets, credentials managed per-developer  

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Try a different transport: `streamable-http` instead of `sse`

### Can't connect from other project
- Verify server is running: `curl http://localhost:8000`
- Check firewall settings
- Ensure correct URL in mcp.json configuration

### Authentication not working
- **Per-developer credentials**: Verify the `env` section in your mcp.json includes DOC_EMAIL and DOC_PASSWORD
- **VS Code inputs**: Check that VS Code is prompting for credentials
- **Server-level credentials** (if using): Verify environment variables in the terminal where server runs
- Check: `echo $DOC_EMAIL` and `echo $DOC_PASSWORD`
- Restart server after setting environment variables

### Credentials not being prompted
- Ensure `inputs` section is defined in mcp.json
- Check that the input IDs match the env variable references
- Restart VS Code after modifying mcp.json

## Example Session (Per-Developer Credentials)

```bash
# Terminal 1: Start mock doc server
$ python mock_doc_server.py
Starting Mock Documentation Server on http://localhost:5001
Default credentials: 
  - developer@example.com / devpassword123
  - alice@company.com / alice-password
  - bob@company.com / bob-password

# Terminal 2: Start MCP HTTP server (no credentials needed)
$ python server.py sse

🚀 Starting MCP server with SSE transport
📡 Server running at: http://localhost:8000

📝 Configure your MCP client with per-developer credentials:
   See .vscode/mcp-http.json for example configuration

# Developer Alice in her project:
# Creates .vscode/mcp.json with:
{
  "inputs": [
    {
      "type": "promptString",
      "id": "DOC_EMAIL",
      "description": "Your email for documentation access"
    },
    {
      "type": "promptString",
      "id": "DOC_PASSWORD",
      "description": "Your password",
      "password": true
    }
  ],
  "mcpServers": {
    "api-docs": {
      "url": "http://localhost:8000",
      "env": {
        "DOC_EMAIL": "${input:DOC_EMAIL}",
        "DOC_PASSWORD": "${input:DOC_PASSWORD}"
      }
    }
  }
}

# When Alice opens VS Code:
# VS Code prompts: "Your email for documentation access"
# Alice enters: alice@company.com
# VS Code prompts: "Your password" (hidden)
# Alice enters: alice-password
# Alice can now use the documentation tools with her credentials

# Developer Bob in his project does the same with bob@company.com
# Each developer authenticates with their own credentials!
     }
   }

💡 Set environment variables for authentication:
   export DOC_EMAIL="developer@example.com"
   export DOC_PASSWORD="devpassword123"

🛑 Press Ctrl+C to stop the server

# Now any project can connect via http://localhost:8000
```
