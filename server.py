import json
import sys
from typing import Any, Optional
import requests

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from mcp.types import (
    CreateMessageResult,
    SamplingMessage,
    TextContent,
    TextResourceContents,
)
import os

mcp = FastMCP("MCP Python Starter")

# Configuration for authenticated documentation server
DOC_SERVER_URL = os.environ.get("DOC_SERVER_URL", "http://localhost:5001")
REQUEST_TIMEOUT = 10  # seconds

# Optional: Credentials from environment variables (avoids passing through LLM)
DOC_EMAIL = os.environ.get("DOC_EMAIL")
DOC_PASSWORD = os.environ.get("DOC_PASSWORD")

# PROTOTYPE: In-memory token storage
# Production requirements:
# - Store tokens securely per session/user context
# - Use encrypted storage
# - Implement token expiration and refresh
_auth_token: Optional[str] = None

# Tool: hello
@mcp.tool()
def say_hello(name: str) -> str:
    """Say hello to a user with a configurable greeting."""
    greeting = os.environ.get("MCP_GREETING", "Hello")
    return f"{greeting}, {name}!"

# Resource: example markdown
@mcp.resource("example://md")
def example_md() -> str:
    """Serve the example markdown file as a resource."""
    with open("resources/example.md", "r", encoding="utf-8") as f:
        return f.read()

# Prompt: greeting
@mcp.prompt()
def greeting_prompt(name: str = "friend") -> str:
    return f"Say hello to {name}!"

# Tool: hello sampling
@mcp.tool()
async def say_hello_sampling(name: str,  ctx: Context) -> str:
    """Say hello to a user with a configurable greeting - with sampling to improve the response."""
    greeting = os.environ.get("MCP_GREETING", "Hello")
    await ctx.info(f"Requesting sampling for greeting: {greeting}")

    result = await ctx.session.create_message(
        messages=[SamplingMessage(role="user", content=TextContent(type="text", text=f"write a letter with the greeting: {greeting} addressed to: {name}!"))],
        max_tokens=800,
        temperature=0.7,
    )
    return result.content.text


# ===== Authenticated Documentation Access Tools =====

def _auto_authenticate() -> bool:
    """
    Auto-authenticate using environment variables if available.
    Returns True if authenticated, False otherwise.
    """
    global _auth_token
    
    # Already authenticated
    if _auth_token is not None:
        return True
    
    # Try to authenticate with env vars
    if DOC_EMAIL and DOC_PASSWORD:
        try:
            response = requests.post(
                f"{DOC_SERVER_URL}/auth/login",
                json={"email": DOC_EMAIL, "password": DOC_PASSWORD},
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                _auth_token = data.get("token")
                return _auth_token is not None
        except:
            pass  # Silent fail, user will see error from calling function
    
    return False

@mcp.tool()
def authenticate_docs(email: str, password: str) -> str:
    """
    Authenticate with the documentation server to access protected API documentation.
    
    Note: You can also set DOC_EMAIL and DOC_PASSWORD environment variables to avoid
    passing credentials through the LLM. The server will auto-authenticate on first use.
    
    Args:
        email: User email (default: developer@example.com)
        password: User password (default: devpassword123)
    
    Returns:
        Authentication status and instructions
    """
    global _auth_token
    
    try:
        response = requests.post(
            f"{DOC_SERVER_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            _auth_token = data.get("token")
            return f"✅ Authentication successful! User: {data.get('user')}\nYou can now access the documentation using get_documentation or search_documentation tools."
        elif response.status_code == 401:
            return "❌ Authentication failed: Invalid credentials. Please check your email and password."
        else:
            return f"❌ Authentication failed: {response.json().get('error', 'Unknown error')}"
    except requests.exceptions.ConnectionError:
        return f"❌ Cannot connect to documentation server at {DOC_SERVER_URL}. Please ensure the mock server is running (python mock_doc_server.py)."
    except Exception as e:
        return f"❌ Authentication error: {str(e)}"


@mcp.tool()
def get_documentation() -> str:
    """
    Retrieve all API documentation from the authenticated documentation server.
    Automatically authenticates using environment variables (DOC_EMAIL, DOC_PASSWORD) if available.
    Otherwise, call authenticate_docs first.
    
    Returns:
        Complete API documentation in JSON format
    """
    global _auth_token
    
    if not _auto_authenticate():
        return "❌ Not authenticated. Please either:\n1. Set DOC_EMAIL and DOC_PASSWORD environment variables, or\n2. Call authenticate_docs(email, password)\n\nDefault credentials: developer@example.com / devpassword123"
    
    try:
        response = requests.get(
            f"{DOC_SERVER_URL}/docs",
            headers={"Authorization": f"Bearer {_auth_token}"},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            docs = response.json()
            # Format the documentation nicely
            formatted = "📚 API Documentation\n\n"
            formatted += f"Base URL: {docs.get('base_url')}\n"
            formatted += f"Version: {docs.get('version')}\n\n"
            formatted += "Authentication:\n"
            formatted += f"  Type: {docs.get('authentication', {}).get('type')}\n"
            formatted += f"  Description: {docs.get('authentication', {}).get('description')}\n\n"
            
            # Add implementation guides
            guides = docs.get('guides', [])
            if guides:
                formatted += "📖 Implementation Guides:\n\n"
                for guide in guides:
                    formatted += f"▶ {guide['title']}\n"
                    formatted += f"  Category: {guide['category']}\n"
                    formatted += f"  {guide['description']}\n\n"
            
            formatted += "Available Endpoints:\n\n"
            
            for endpoint in docs.get('endpoints', []):
                formatted += f"▶ {endpoint['method']} {endpoint['path']}\n"
                formatted += f"  Description: {endpoint['description']}\n"
                if endpoint.get('parameters'):
                    formatted += "  Parameters:\n"
                    for param in endpoint['parameters']:
                        required = "required" if param.get('required') else "optional"
                        location = f" ({param.get('location', 'body')})" if param.get('location') else ""
                        formatted += f"    - {param['name']} ({param['type']}) - {required}{location}\n"
                formatted += "  Responses:\n"
                for code, resp in endpoint.get('response', {}).items():
                    formatted += f"    {code}: {resp.get('description')}\n"
                    if resp.get('example'):
                        formatted += f"      Example: {resp.get('example')}\n"
                formatted += "\n"
            
            return formatted
        elif response.status_code == 401:
            _auth_token = None  # Clear invalid token
            return "❌ Authentication token expired or invalid. Please authenticate again using authenticate_docs."
        else:
            return f"❌ Error fetching documentation: {response.json().get('error', 'Unknown error')}"
    except requests.exceptions.ConnectionError:
        return f"❌ Cannot connect to documentation server at {DOC_SERVER_URL}. Please ensure the mock server is running."
    except Exception as e:
        return f"❌ Error: {str(e)}"


@mcp.tool()
def search_documentation(query: str) -> str:
    """
    Search the API documentation for specific endpoints, guides, or functionality.
    Automatically authenticates using environment variables (DOC_EMAIL, DOC_PASSWORD) if available.
    Otherwise, call authenticate_docs first.
    
    Args:
        query: Search term (e.g., "GET method", "POST", "delete", "implement", etc.)
    
    Returns:
        Search results with matching guides and endpoints
    """
    global _auth_token
    
    if not _auto_authenticate():
        return "❌ Not authenticated. Please either:\n1. Set DOC_EMAIL and DOC_PASSWORD environment variables, or\n2. Call authenticate_docs(email, password)\n\nDefault credentials: developer@example.com / devpassword123"
    
    if not query:
        return "❌ Please provide a search query."
    
    try:
        response = requests.get(
            f"{DOC_SERVER_URL}/docs/search",
            params={"q": query},
            headers={"Authorization": f"Bearer {_auth_token}"},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            guides = data.get('guides', [])
            endpoints = data.get('endpoints', [])
            total_count = data.get('total_count', 0)
            
            if total_count == 0:
                return f"🔍 No results found for query: '{query}'"
            
            formatted = f"🔍 Search Results for '{query}' ({total_count} found):\n\n"
            
            # Show implementation guides first
            if guides:
                formatted += "📖 Implementation Guides:\n\n"
                for guide in guides:
                    formatted += f"▶ {guide['title']}\n"
                    formatted += f"  Category: {guide['category']}\n"
                    formatted += f"  {guide['description']}\n"
                    formatted += f"  Use get_guide(\"{guide['title']}\") for full content\n\n"
            
            # Show endpoints
            if endpoints:
                formatted += "API Endpoints:\n\n"
                for endpoint in endpoints:
                    formatted += f"▶ {endpoint['method']} {endpoint['path']}\n"
                    formatted += f"  Description: {endpoint['description']}\n"
                    if endpoint.get('parameters'):
                        formatted += "  Parameters:\n"
                        for param in endpoint['parameters']:
                            required = "required" if param.get('required') else "optional"
                            formatted += f"    - {param['name']} ({param['type']}) - {required}\n"
                    formatted += "\n"
            
            return formatted
        elif response.status_code == 401:
            _auth_token = None  # Clear invalid token
            return "❌ Authentication token expired or invalid. Please authenticate again using authenticate_docs."
        else:
            return f"❌ Error searching documentation: {response.json().get('error', 'Unknown error')}"
    except requests.exceptions.ConnectionError:
        return f"❌ Cannot connect to documentation server at {DOC_SERVER_URL}. Please ensure the mock server is running."
    except Exception as e:
        return f"❌ Error: {str(e)}"


@mcp.tool()
def get_guide(guide_title: str) -> str:
    """
    Get the full content of an implementation guide.
    Automatically authenticates using environment variables (DOC_EMAIL, DOC_PASSWORD) if available.
    Otherwise, call authenticate_docs first.
    
    Args:
        guide_title: Title of the guide (e.g., "How to Get Current Weather")
    
    Returns:
        Full guide content with code examples
    """
    global _auth_token
    
    if not _auto_authenticate():
        return "❌ Not authenticated. Please either:\n1. Set DOC_EMAIL and DOC_PASSWORD environment variables, or\n2. Call authenticate_docs(email, password)\n\nDefault credentials: developer@example.com / devpassword123"
    
    if not guide_title:
        return "❌ Please provide a guide title."
    
    try:
        response = requests.get(
            f"{DOC_SERVER_URL}/docs",
            headers={"Authorization": f"Bearer {_auth_token}"},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            docs = response.json()
            guides = docs.get('guides', [])
            
            # Find the guide by title (case-insensitive)
            guide = None
            for g in guides:
                if g['title'].lower() == guide_title.lower():
                    guide = g
                    break
            
            if not guide:
                available = [g['title'] for g in guides]
                return f"❌ Guide not found: '{guide_title}'\n\nAvailable guides:\n" + "\n".join(f"  - {t}" for t in available)
            
            # Format the guide content
            formatted = f"📖 {guide['title']}\n\n"
            formatted += f"Category: {guide['category']}\n"
            formatted += f"Description: {guide['description']}\n\n"
            formatted += "=" * 70 + "\n\n"
            formatted += guide['content']
            
            return formatted
        elif response.status_code == 401:
            _auth_token = None
            return "❌ Authentication token expired or invalid. Please authenticate again using authenticate_docs."
        else:
            return f"❌ Error fetching guide: {response.json().get('error', 'Unknown error')}"
    except requests.exceptions.ConnectionError:
        return f"❌ Cannot connect to documentation server at {DOC_SERVER_URL}. Please ensure the mock server is running."
    except Exception as e:
        return f"❌ Error: {str(e)}"


@mcp.tool()
def check_auth_status() -> str:
    """
    Check if you are currently authenticated with the documentation server.
    
    Returns:
        Authentication status
    """
    global _auth_token
    
    if not _auth_token:
        return "❌ Not authenticated.\n\nTo access the documentation, please:\n1. Start the mock documentation server: python mock_doc_server.py\n2. Authenticate using: authenticate_docs(email, password)\n   Default credentials: developer@example.com / devpassword123"
    
    try:
        response = requests.get(
            f"{DOC_SERVER_URL}/auth/validate",
            headers={"Authorization": f"Bearer {_auth_token}"},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            return f"✅ Authenticated as: {data.get('user')}\n\nYou can now use:\n- get_documentation() to retrieve all API docs\n- search_documentation(query) to search for specific endpoints"
        else:
            _auth_token = None
            return "❌ Authentication token is invalid or expired. Please authenticate again using authenticate_docs."
    except requests.exceptions.ConnectionError:
        return f"❌ Cannot connect to documentation server at {DOC_SERVER_URL}. Please ensure the mock server is running."
    except Exception as e:
        return f"❌ Error checking auth status: {str(e)}"


if __name__ == "__main__":
    # Support both stdio (default) and HTTP transports
    # Usage:
    #   python server.py              # stdio transport (default, for local use)
    #   python server.py stdio        # stdio transport explicitly
    #   python server.py sse          # SSE HTTP server on port 8000
    #   python server.py streamable-http  # Streamable HTTP on port 8000
    
    transport = "stdio"  # default
    
    if len(sys.argv) > 1:
        transport = sys.argv[1].lower()
    
    if transport in ["sse", "streamable-http"]:
        print(f"🚀 Starting MCP server with {transport.upper()} transport")
        print(f"📡 Server running at: http://localhost:8000")
        print(f"\n📝 Configure your MCP client with:")
        print(f'   {{')
        print(f'     "mcpServers": {{')
        print(f'       "mcp-python-starter": {{')
        print(f'         "url": "http://localhost:8000"')
        print(f'       }}')
        print(f'     }}')
        print(f'   }}')
        print(f"\n💡 Set environment variables for authentication:")
        print(f'   export DOC_EMAIL="developer@example.com"')
        print(f'   export DOC_PASSWORD="devpassword123"')
        print(f"\n🛑 Press Ctrl+C to stop the server\n")
        
        # Run with HTTP transport (FastMCP handles everything)
        mcp.run(transport=transport)
        
    else:  # stdio (default)
        # Run with stdio transport (default behavior)
        mcp.run()



