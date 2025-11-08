# MCP Python Starter

A minimal Model Context Protocol (MCP) server implemented in Python, matching the features and structure of the TypeScript starter.

## Features
- **Hello Tool**: Returns a greeting using the `MCP_GREETING` environment variable.
- **Markdown Resource**: Serves a static markdown file from `resources/example.md`.
- **Prompt**: Simple prompt handler example.
- **Authenticated Documentation Access**: Access API documentation behind authentication/SSO.
- **Environment-based configuration**: Reads greeting and secret from environment variables.
- **VS Code integration**: `.vscode/mcp.json` for easy server launch with input prompts.
- **Devcontainer support**: (Optional, add `.devcontainer` if needed)
- **Tests**: (Add tests as needed)

## Quickstart

1. **Install dependencies**

   ```sh
   pip install .
   ```

2. **Run the server**

   **Option A: Stdio mode (local use only)**
   ```sh
   python server.py stdio
   ```

   **Option B: HTTP mode (accessible from any project, per-developer credentials)**
   ```sh
   python server.py sse
   ```
   Server will run on `http://localhost:8000` and can be accessed from any IDE/project. Each developer provides their own credentials.

3. **Use with MCP client or VS Code**

   **For stdio mode:** Use the provided `.vscode/mcp.json` to launch the server with custom inputs.
   
   **For HTTP mode (recommended):** Each developer configures their project with their own credentials:
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
         "description": "Your password",
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

See [HTTP_SERVER_SETUP.md](HTTP_SERVER_SETUP.md) for detailed HTTP server configuration.

## Authenticated Documentation Access

This MCP server includes tools to access API documentation that is behind authentication (simulating SSO).

### Setup

1. **Start the mock documentation server** (in a separate terminal):

   ```sh
   python mock_doc_server.py
   ```

   This starts a Flask server on `http://localhost:5001` with mock API documentation.

2. **Choose your authentication method**:

   **Option A: Environment Variables (Recommended - no credentials through LLM)**
   ```sh
   export DOC_EMAIL="developer@example.com"
   export DOC_PASSWORD="devpassword123"
   python server.py stdio
   ```
   
   With this method, you can directly use documentation tools without explicit authentication:
   ```python
   get_documentation()  # Auto-authenticates using environment variables
   search_documentation("weather")  # No auth step needed
   ```

   **Option B: Manual Authentication (credentials passed as parameters)**
   ```sh
   python server.py stdio
   ```
   
   Then authenticate explicitly:
   ```python
   authenticate_docs("developer@example.com", "devpassword123")
   get_documentation()
   ```

3. **Default credentials**:
   - Email: `developer@example.com`
   - Password: `devpassword123`

### Available Tools

#### `authenticate_docs(email, password)` - Optional
Authenticate with the documentation server. **Note**: If you set `DOC_EMAIL` and `DOC_PASSWORD` environment variables, authentication happens automatically and you don't need to call this.

**Example**:
```python
authenticate_docs("developer@example.com", "devpassword123")
```

#### `check_auth_status()`
Check if you are currently authenticated and see available commands.

#### `get_documentation()`
Retrieve all API documentation from the authenticated server. Auto-authenticates using environment variables if available.

**Example**:
```python
get_documentation()  # Works automatically if DOC_EMAIL and DOC_PASSWORD are set
```

#### `search_documentation(query)`
Search the API documentation for specific endpoints or functionality. Auto-authenticates using environment variables if available.

**Example**:
```python
search_documentation("current weather")  # Auto-authenticates if env vars set
search_documentation("POST")
search_documentation("forecast")
```

#### `get_guide(title)`
Get the full content of a specific implementation guide with code examples.

**Example**:
```python
get_guide("How to Get Current Weather")
```

### Authentication Methods

**Environment Variables (Recommended)**
- Credentials never pass through the LLM/chat
- Auto-authenticates on first tool use
- Most secure for this prototype
- See [AUTHENTICATION_METHODS.md](AUTHENTICATION_METHODS.md) for details

**Manual Authentication**
- Pass credentials as tool parameters
- Useful for testing or when env vars aren't available
- Credentials may be logged in chat history

### How It Works

1. The mock documentation server (`mock_doc_server.py`) simulates an API documentation portal behind authentication
2. When you use documentation tools, the MCP server automatically authenticates using environment variables (if set)
3. Upon successful authentication, a token is stored securely (in-memory for this prototype)
4. The token is automatically included in subsequent requests to access documentation
5. Users can query documentation using `get_documentation()` or search with `search_documentation(query)`

### Security Notes

This is a **prototype implementation** for demonstration purposes:
- Tokens are stored in memory (not persisted)
- Simple password-based authentication (not OAuth2)
- No HTTPS enforcement
- For production use, implement:
  - Secure token storage (encrypted)
  - OAuth2/OIDC authentication flow
  - HTTPS for all communications
  - Token refresh mechanisms
  - Proper session management

## Project Structure

- `server.py` — Main MCP server implementation with authenticated doc access tools
- `mock_doc_server.py` — Mock documentation server with authentication
- `resources/example.md` — Example markdown resource
- `.vscode/mcp.json` — VS Code MCP server config
- `.gitignore` — Standard Python ignores

## License

MIT
