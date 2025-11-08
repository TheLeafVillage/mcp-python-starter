# Alternative Authentication Methods for MCP Documentation Access

## Current Implementation (Prototype)

Currently, the MCP server uses a simple `authenticate_docs(email, password)` tool where credentials are passed as parameters. While this works for a prototype, there are better approaches for production use.

## Better Authentication Approaches

### 1. Environment Variables (Recommended for this prototype)

**How it works:**
- Store credentials in environment variables
- MCP server reads them automatically on startup
- No credentials pass through the LLM/chat

**Implementation:**

```python
# In server.py
DOC_EMAIL = os.environ.get("DOC_EMAIL")
DOC_PASSWORD = os.environ.get("DOC_PASSWORD")

@mcp.tool()
def authenticate_docs() -> str:
    """Authenticate using credentials from environment variables."""
    if not DOC_EMAIL or not DOC_PASSWORD:
        return "❌ Please set DOC_EMAIL and DOC_PASSWORD environment variables"
    
    response = requests.post(
        f"{DOC_SERVER_URL}/auth/login",
        json={"email": DOC_EMAIL, "password": DOC_PASSWORD},
        timeout=REQUEST_TIMEOUT
    )
    # ... handle response
```

**Usage:**
```bash
# Set environment variables
export DOC_EMAIL="developer@example.com"
export DOC_PASSWORD="devpassword123"

# Run MCP server
python server.py stdio
```

**Pros:**
- ✅ No credentials in chat/LLM
- ✅ Simple to implement
- ✅ Works well for prototypes
- ✅ Can be configured per deployment

**Cons:**
- ⚠️ Requires setting env vars before starting
- ⚠️ Credentials stored in plain text on system

---

### 2. OAuth2 / OIDC Flow (Production-ready)

**How it works:**
- User opens browser to authenticate
- Redirects back with authorization code
- MCP server exchanges code for token
- No credentials pass through LLM

**Implementation Flow:**

```python
@mcp.tool()
def authenticate_docs_oauth() -> str:
    """Start OAuth2 authentication flow."""
    # Generate auth URL
    auth_url = f"{DOC_SERVER_URL}/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    
    return f"Please visit this URL to authenticate:\n{auth_url}\n\nAfter authentication, you'll be redirected back."

# Separate endpoint handles OAuth callback
def handle_oauth_callback(code):
    # Exchange code for token
    response = requests.post(
        f"{DOC_SERVER_URL}/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    # Store token
    token = response.json()["access_token"]
```

**Pros:**
- ✅ Industry standard
- ✅ No credentials through LLM
- ✅ Supports SSO (Google, Microsoft, etc.)
- ✅ Secure token refresh
- ✅ User controls permissions

**Cons:**
- ⚠️ More complex to implement
- ⚠️ Requires OAuth2 provider setup
- ⚠️ Requires browser interaction

---

### 3. API Key from Environment (Simplest)

**How it works:**
- Pre-generate API key/token
- Store in environment variable
- MCP server uses it directly

**Implementation:**

```python
# In server.py
DOC_API_KEY = os.environ.get("DOC_API_KEY")

# Auto-authenticate on first use
def ensure_authenticated():
    global _auth_token
    if not _auth_token and DOC_API_KEY:
        _auth_token = DOC_API_KEY

@mcp.tool()
def get_documentation() -> str:
    """Get documentation (authenticates automatically)."""
    ensure_authenticated()
    
    if not _auth_token:
        return "❌ Please set DOC_API_KEY environment variable"
    
    # Use token directly
    response = requests.get(
        f"{DOC_SERVER_URL}/docs",
        headers={"Authorization": f"Bearer {_auth_token}"}
    )
```

**Usage:**
```bash
export DOC_API_KEY="your-api-key-here"
python server.py stdio
```

**Pros:**
- ✅ Simplest implementation
- ✅ No credentials in LLM
- ✅ No interactive auth needed
- ✅ Perfect for service accounts

**Cons:**
- ⚠️ API key must be generated beforehand
- ⚠️ Less secure than OAuth2

---

### 4. VS Code Secret Storage (Best for VS Code integration)

**How it works:**
- VS Code has built-in secure secret storage
- Prompt user once for credentials
- Store in VS Code's encrypted storage
- Never pass through LLM

**Implementation (pseudo-code):**

```python
# VS Code extension handles this
async def get_credentials():
    # Check if credentials exist in VS Code secret storage
    stored_creds = await vscode.secrets.get("doc_credentials")
    
    if not stored_creds:
        # Prompt user once
        email = await vscode.window.showInputBox("Enter email")
        password = await vscode.window.showInputBox("Enter password", password=True)
        
        # Store securely
        await vscode.secrets.store("doc_credentials", {email, password})
    
    return stored_creds
```

**Pros:**
- ✅ Most secure for VS Code
- ✅ Native integration
- ✅ Encrypted storage
- ✅ No credentials in LLM
- ✅ Prompt only once

**Cons:**
- ⚠️ Requires VS Code extension development
- ⚠️ Not portable to other MCP clients

---

### 5. Interactive CLI Prompt (Current alternative)

**How it works:**
- MCP server prompts for credentials on startup
- Uses getpass for secure password input
- Never logged or sent through LLM

**Implementation:**

```python
import getpass

def get_credentials_from_user():
    """Prompt user for credentials on startup."""
    print("Documentation Authentication Required")
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    return email, password

# On startup
if not os.environ.get("DOC_EMAIL"):
    DOC_EMAIL, DOC_PASSWORD = get_credentials_from_user()
    # Authenticate immediately
    authenticate_with_credentials(DOC_EMAIL, DOC_PASSWORD)
```

**Pros:**
- ✅ No credentials in LLM
- ✅ Secure password input (hidden)
- ✅ Simple to implement

**Cons:**
- ⚠️ Must restart server to change credentials
- ⚠️ Interrupts startup flow

---

## Recommended Approach for This Prototype

**Use Environment Variables + Optional Auto-authentication**

This provides a good balance:

1. **Set credentials in environment variables** (not in chat)
2. **Auto-authenticate on first tool use** (no explicit auth needed)
3. **Falls back to manual auth** if env vars not set

### Implementation:

```python
# server.py
DOC_EMAIL = os.environ.get("DOC_EMAIL")
DOC_PASSWORD = os.environ.get("DOC_PASSWORD")

def auto_authenticate():
    """Auto-authenticate if credentials are in environment."""
    global _auth_token
    if _auth_token:
        return True  # Already authenticated
    
    if DOC_EMAIL and DOC_PASSWORD:
        # Auto-authenticate silently
        response = requests.post(
            f"{DOC_SERVER_URL}/auth/login",
            json={"email": DOC_EMAIL, "password": DOC_PASSWORD},
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            _auth_token = response.json().get("token")
            return True
    
    return False

@mcp.tool()
def get_documentation() -> str:
    """Get documentation (auto-authenticates if credentials available)."""
    if not auto_authenticate():
        return "❌ Not authenticated. Please set DOC_EMAIL and DOC_PASSWORD environment variables, or call authenticate_docs(email, password)"
    
    # ... rest of implementation
```

### Usage:

**With environment variables (recommended):**
```bash
export DOC_EMAIL="developer@example.com"
export DOC_PASSWORD="devpassword123"
python server.py stdio
# Now just use: get_documentation() - no explicit auth needed!
```

**Without environment variables (fallback):**
```bash
python server.py stdio
# Use: authenticate_docs("email", "password") first
```

---

## Security Comparison

| Method | Security Level | Complexity | LLM Exposure | Best For |
|--------|---------------|------------|--------------|----------|
| Current (params) | ⭐⭐ | Low | ❌ Yes | Quick demos |
| Environment vars | ⭐⭐⭐ | Low | ✅ No | Prototypes |
| API Key | ⭐⭐⭐ | Low | ✅ No | Service accounts |
| OAuth2/OIDC | ⭐⭐⭐⭐⭐ | High | ✅ No | Production |
| VS Code Secrets | ⭐⭐⭐⭐⭐ | Medium | ✅ No | VS Code integration |
| CLI Prompt | ⭐⭐⭐⭐ | Low | ✅ No | Interactive use |

---

## For Production Deployment

For a real production system accessing enterprise documentation:

1. **Use OAuth2/OIDC** with your SSO provider (Okta, Azure AD, etc.)
2. **Implement token refresh** to avoid re-authentication
3. **Use HTTPS** for all communication
4. **Store tokens securely** (encrypted, per-user)
5. **Add token expiration** and automatic refresh
6. **Implement proper session management**
7. **Add audit logging** of authentication events
8. **Use environment-specific credentials** (dev/staging/prod)

---

## Summary

**For this prototype, I recommend:**

✅ **Implement environment variable authentication** (no credentials through LLM)
✅ **Add auto-authentication** on first tool use
✅ **Keep the current manual method** as fallback

This gives users flexibility while avoiding credential exposure in the chat.
