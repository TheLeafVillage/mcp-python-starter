# Authenticated Documentation Access - Usage Example

This document demonstrates how to use the MCP server to access API documentation that is behind authentication.

## Setup

### 1. Start the Mock Documentation Server

In one terminal, run:

```bash
python mock_doc_server.py
```

This will start a Flask server on `http://localhost:5001` that simulates an API documentation portal with authentication.

**Output:**
```
Starting Mock Documentation Server on http://localhost:5001
Default credentials: developer@example.com / devpassword123
 * Running on http://127.0.0.1:5001
```

### 2. Start the MCP Server

In another terminal, run:

```bash
python server.py stdio
```

This starts the MCP server that you can interact with.

## Usage Flow

### Step 1: Check Authentication Status

Before accessing documentation, check if you're authenticated:

```python
check_auth_status()
```

**Expected Response (not authenticated):**
```
❌ Not authenticated.

To access the documentation, please:
1. Start the mock documentation server: python mock_doc_server.py
2. Authenticate using: authenticate_docs(email, password)
   Default credentials: developer@example.com / devpassword123
```

### Step 2: Authenticate

Use the default credentials to authenticate:

```python
authenticate_docs("developer@example.com", "devpassword123")
```

**Expected Response (success):**
```
✅ Authentication successful! User: developer@example.com
You can now access the documentation using get_documentation or search_documentation tools.
```

**Expected Response (failure):**
```
❌ Authentication failed: Invalid credentials. Please check your email and password.
```

### Step 3: Verify Authentication

Check that authentication was successful:

```python
check_auth_status()
```

**Expected Response:**
```
✅ Authenticated as: developer@example.com

You can now use:
- get_documentation() to retrieve all API docs
- search_documentation(query) to search for specific endpoints
```

### Step 4: Retrieve Complete Documentation

Get all available API documentation:

```python
get_documentation()
```

**Expected Response:**
```
📚 API Documentation

Base URL: https://api.example.com
Version: v1

Authentication:
  Type: Bearer Token
  Description: All API requests require a valid bearer token in the Authorization header

Available Endpoints:

▶ GET /api/users
  Description: Retrieve a list of all users
  Responses:
    200: List of users
      Example: {"users": [{"id": 1, "name": "John"}]}

▶ POST /api/users
  Description: Create a new user
  Parameters:
    - name (string) - required
    - email (string) - required
  Responses:
    201: User created successfully
      Example: {"id": 1, "name": "John", "email": "john@example.com"}

▶ GET /api/users/{id}
  Description: Get a specific user by ID
  Parameters:
    - id (integer) - required (path)
  Responses:
    200: User details
      Example: {"id": 1, "name": "John", "email": "john@example.com"}
    404: User not found

▶ PUT /api/users/{id}
  Description: Update an existing user
  Parameters:
    - id (integer) - required (path)
    - name (string) - optional
    - email (string) - optional
  Responses:
    200: User updated successfully
      Example: {"id": 1, "name": "John Updated", "email": "john.updated@example.com"}

▶ DELETE /api/users/{id}
  Description: Delete a user
  Parameters:
    - id (integer) - required (path)
  Responses:
    204: User deleted successfully
```

### Step 5: Search Documentation

Search for specific endpoints or functionality:

**Example 1: Search for "users"**
```python
search_documentation("users")
```

**Response:**
```
🔍 Search Results for 'users' (5 found):

▶ GET /api/users
  Description: Retrieve a list of all users

▶ POST /api/users
  Description: Create a new user
  Parameters:
    - name (string) - required
    - email (string) - required

▶ GET /api/users/{id}
  Description: Get a specific user by ID
  Parameters:
    - id (integer) - required

▶ PUT /api/users/{id}
  Description: Update an existing user
  Parameters:
    - id (integer) - required
    - name (string) - optional
    - email (string) - optional

▶ DELETE /api/users/{id}
  Description: Delete a user
  Parameters:
    - id (integer) - required
```

**Example 2: Search for specific HTTP methods**
```python
search_documentation("POST")
```

**Response:**
```
🔍 Search Results for 'POST' (1 found):

▶ POST /api/users
  Description: Create a new user
  Parameters:
    - name (string) - required
    - email (string) - required
```

**Example 3: Search for specific actions**
```python
search_documentation("delete")
```

**Response:**
```
🔍 Search Results for 'delete' (1 found):

▶ DELETE /api/users/{id}
  Description: Delete a user
  Parameters:
    - id (integer) - required
```

## Example Conversation with AI Assistant

**User:** "Can you help me understand how to create a new user in this API?"

**Assistant:** Let me authenticate and search the documentation for you.

```python
authenticate_docs("developer@example.com", "devpassword123")
search_documentation("POST users")
```

**Response:**
```
✅ Authentication successful! User: developer@example.com

🔍 Search Results for 'POST users' (1 found):

▶ POST /api/users
  Description: Create a new user
  Parameters:
    - name (string) - required
    - email (string) - required
  Responses:
    201: User created successfully
      Example: {"id": 1, "name": "John", "email": "john@example.com"}
```

**Assistant:** To create a new user, you need to make a POST request to `/api/users` with the following required parameters:
- `name` (string) - The user's name
- `email` (string) - The user's email address

Upon success, you'll receive a 201 response with the created user's details including their ID.

## Architecture

### Components

1. **Mock Documentation Server** (`mock_doc_server.py`)
   - Flask-based server simulating an API documentation portal
   - Implements token-based authentication (simulating SSO)
   - Provides endpoints for login, token validation, doc retrieval, and search

2. **MCP Server** (`server.py`)
   - Provides MCP tools for authentication and documentation access
   - Manages authentication tokens securely (in-memory for prototype)
   - Formats documentation responses for easy reading

### Authentication Flow

```
┌─────────────┐          ┌──────────────────┐          ┌──────────────────┐
│             │          │                  │          │                  │
│  AI Client  │────────> │   MCP Server     │────────> │  Mock Doc Server │
│             │          │                  │          │                  │
└─────────────┘          └──────────────────┘          └──────────────────┘
       │                         │                              │
       │  1. authenticate_docs   │                              │
       │────────────────────────>│                              │
       │                         │  2. POST /auth/login         │
       │                         │─────────────────────────────>│
       │                         │                              │
       │                         │  3. Return token             │
       │                         │<─────────────────────────────│
       │  4. Success message     │                              │
       │<────────────────────────│                              │
       │                         │                              │
       │  5. get_documentation   │                              │
       │────────────────────────>│                              │
       │                         │  6. GET /docs (with token)   │
       │                         │─────────────────────────────>│
       │                         │                              │
       │                         │  7. Return documentation     │
       │                         │<─────────────────────────────│
       │  8. Formatted docs      │                              │
       │<────────────────────────│                              │
```

## Configuration

### Environment Variables

- `DOC_SERVER_URL`: URL of the documentation server (default: `http://localhost:5001`)

### Default Credentials

- Email: `developer@example.com`
- Password: `devpassword123`

You can modify these in `mock_doc_server.py`:

```python
USERS = {
    "developer@example.com": "devpassword123",
    "another@example.com": "anotherpassword"
}
```

## Security Considerations

This is a **prototype implementation** for demonstration purposes. For production use:

### Current Implementation (Prototype)
- ✅ Token-based authentication
- ✅ Authorization checks on protected endpoints
- ✅ Clear error messages for authentication failures
- ⚠️ In-memory token storage (not persistent)
- ⚠️ Simple password authentication (not OAuth2/OIDC)
- ⚠️ HTTP only (no HTTPS)
- ⚠️ No token expiration
- ⚠️ No token refresh mechanism

### Production Requirements
- 🔒 Use OAuth2/OIDC for authentication
- 🔒 Implement HTTPS for all communications
- 🔒 Store tokens securely (encrypted at rest)
- 🔒 Implement token expiration and refresh
- 🔒 Add rate limiting
- 🔒 Implement proper session management
- 🔒 Add audit logging
- 🔒 Use environment variables for all sensitive configuration
- 🔒 Implement proper password hashing (bcrypt/argon2)

## Troubleshooting

### "Cannot connect to documentation server"

**Problem:** The MCP server can't reach the documentation server.

**Solution:**
1. Ensure the mock documentation server is running: `python mock_doc_server.py`
2. Check that it's running on `http://localhost:5001`
3. If using a different URL, set the `DOC_SERVER_URL` environment variable

### "Authentication token expired or invalid"

**Problem:** The token is no longer valid.

**Solution:**
1. Re-authenticate using `authenticate_docs(email, password)`
2. Note: In this prototype, tokens are stored in memory and cleared when the mock server restarts

### "Invalid credentials"

**Problem:** Wrong email or password.

**Solution:**
1. Use the default credentials: `developer@example.com` / `devpassword123`
2. Check `mock_doc_server.py` for the list of valid credentials

## Extending the System

### Adding More Documentation

Edit the `API_DOCS` dictionary in `mock_doc_server.py`:

```python
API_DOCS = {
    "endpoints": [
        {
            "name": "GET /api/products",
            "description": "Retrieve all products",
            "method": "GET",
            "path": "/api/products",
            # ... more fields
        }
    ]
}
```

### Adding More Users

Edit the `USERS` dictionary in `mock_doc_server.py`:

```python
USERS = {
    "developer@example.com": "devpassword123",
    "admin@example.com": "adminpass456",
    "tester@example.com": "testpass789"
}
```

### Implementing OAuth2

For a production system, replace the token-based authentication with OAuth2:

1. Use a library like `authlib` or `python-oauth2`
2. Implement authorization code flow
3. Handle token refresh
4. Store tokens securely

Example OAuth2 flow integration:

```python
from authlib.integrations.requests_client import OAuth2Session

def authenticate_docs_oauth2(ctx: Context):
    """Authenticate using OAuth2."""
    client = OAuth2Session(
        client_id=os.environ['OAUTH_CLIENT_ID'],
        client_secret=os.environ['OAUTH_CLIENT_SECRET'],
        redirect_uri='http://localhost:8080/callback'
    )
    
    # Get authorization URL
    authorization_url, state = client.create_authorization_url(
        'https://auth.example.com/authorize'
    )
    
    # Prompt user to visit URL and authorize
    await ctx.info(f"Please visit: {authorization_url}")
    
    # ... handle callback and token exchange
```

## Testing

Run the test script to verify all functionality:

```bash
python /tmp/test_auth_tools.py
```

This will test:
1. ✅ Authentication status check (before auth)
2. ✅ Authentication with valid credentials
3. ✅ Authentication status check (after auth)
4. ✅ Retrieving full documentation
5. ✅ Searching documentation
6. ✅ Authentication with invalid credentials
