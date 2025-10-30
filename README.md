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

   ```sh
   python server.py stdio
   ```

3. **Use with MCP client or VS Code**

   Use the provided `.vscode/mcp.json` to launch the server with custom inputs.

## Authenticated Documentation Access

This MCP server includes tools to access API documentation that is behind authentication (simulating SSO).

### Setup

1. **Start the mock documentation server** (in a separate terminal):

   ```sh
   python mock_doc_server.py
   ```

   This starts a Flask server on `http://localhost:5001` with mock API documentation.

2. **Default credentials**:
   - Email: `developer@example.com`
   - Password: `devpassword123`

### Available Tools

#### `authenticate_docs(email, password)`
Authenticate with the documentation server to get access to protected documentation.

**Example**:
```python
authenticate_docs("developer@example.com", "devpassword123")
```

#### `check_auth_status()`
Check if you are currently authenticated and see available commands.

#### `get_documentation()`
Retrieve all API documentation from the authenticated server.

**Example**:
```python
get_documentation()
```

#### `search_documentation(query)`
Search the API documentation for specific endpoints or functionality.

**Example**:
```python
search_documentation("users")
search_documentation("POST")
search_documentation("delete")
```

### How It Works

1. The mock documentation server (`mock_doc_server.py`) simulates an API documentation portal behind authentication
2. Users must authenticate using `authenticate_docs()` with valid credentials
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
