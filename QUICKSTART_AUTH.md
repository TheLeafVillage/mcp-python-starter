# Quick Start: Authenticated Documentation Access

This guide will help you get started with the authenticated documentation MCP server in under 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip

## Step 1: Install Dependencies

```bash
pip install .
```

Or install manually:

```bash
pip install mcp>=1.9.4 requests>=2.31.0 flask>=3.0.0
```

## Step 2: Start the Mock Documentation Server

Open a terminal and run:

```bash
python mock_doc_server.py
```

You should see:

```
Starting Mock Documentation Server on http://localhost:5001
Default credentials: developer@example.com / devpassword123
 * Running on http://127.0.0.1:5001
```

**Keep this terminal open.**

## Step 3: Start the MCP Server

Open a **new terminal** and run:

```bash
python server.py stdio
```

## Step 4: Use the Tools

You can now use the following MCP tools to access authenticated documentation:

### 1. Check if authenticated

```python
check_auth_status()
```

### 2. Authenticate

```python
authenticate_docs("developer@example.com", "devpassword123")
```

### 3. Get all documentation

```python
get_documentation()
```

### 4. Search documentation

```python
search_documentation("users")
search_documentation("POST")
search_documentation("delete")
```

## Example Session

```
> check_auth_status()
❌ Not authenticated.

> authenticate_docs("developer@example.com", "devpassword123")
✅ Authentication successful! User: developer@example.com

> search_documentation("users")
🔍 Search Results for 'users' (5 found):

▶ GET /api/users
  Description: Retrieve a list of all users
  
▶ POST /api/users
  Description: Create a new user
  Parameters:
    - name (string) - required
    - email (string) - required
...
```

## Default Credentials

- **Email:** `developer@example.com`
- **Password:** `devpassword123`

## Troubleshooting

### Server won't connect?

Make sure the mock documentation server is running:

```bash
curl http://localhost:5001/
```

Should return:

```json
{
  "message": "Mock API Documentation Server",
  "version": "1.0"
}
```

### Authentication fails?

Double-check the credentials:
- Email: `developer@example.com`
- Password: `devpassword123`

### Need to reset authentication?

Restart the mock documentation server:

1. Press `Ctrl+C` in the terminal running `mock_doc_server.py`
2. Run `python mock_doc_server.py` again

## What's Next?

- Read [AUTHENTICATED_DOCS_EXAMPLE.md](AUTHENTICATED_DOCS_EXAMPLE.md) for detailed usage examples
- Read [README.md](README.md) for the complete documentation
- Customize the mock server in `mock_doc_server.py` to add your own documentation

## Architecture Overview

```
┌───────────────┐
│  AI Assistant │
└───────┬───────┘
        │
        │ Uses MCP tools
        ▼
┌───────────────┐
│  MCP Server   │
│  (server.py)  │
└───────┬───────┘
        │
        │ Authenticates & fetches docs
        ▼
┌─────────────────────┐
│ Mock Doc Server     │
│ (mock_doc_server.py)│
│                     │
│ 🔒 Protected Docs   │
└─────────────────────┘
```

The MCP server acts as a bridge between your AI assistant and the authenticated documentation server, handling authentication and formatting the responses.
