import json
import multiprocessing
import socket
import time
from collections.abc import Generator
from typing import Any, Optional
from unittest import result
import uvicorn
from pydantic import AnyUrl
from starlette.applications import Starlette
from starlette.requests import Request
import requests

import mcp.types as types
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources import FunctionResource
from mcp.shared.context import RequestContext
from mcp.server.fastmcp import Context
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    GetPromptResult,
    InitializeResult,
    ReadResourceResult,
    SamplingMessage,
    TextContent,
    TextResourceContents,
)
import os

mcp = FastMCP("MCP Python Starter")

# Configuration for authenticated documentation server
DOC_SERVER_URL = os.environ.get("DOC_SERVER_URL", "http://localhost:5001")

# In-memory token storage (in production, use secure storage)
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

@mcp.tool()
def authenticate_docs(email: str, password: str) -> str:
    """
    Authenticate with the documentation server to access protected API documentation.
    
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
            timeout=10
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
    Requires authentication - call authenticate_docs first if not authenticated.
    
    Returns:
        Complete API documentation in JSON format
    """
    global _auth_token
    
    if not _auth_token:
        return "❌ Not authenticated. Please call authenticate_docs with your credentials first.\nDefault credentials: developer@example.com / devpassword123"
    
    try:
        response = requests.get(
            f"{DOC_SERVER_URL}/docs",
            headers={"Authorization": f"Bearer {_auth_token}"},
            timeout=10
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
    Search the API documentation for specific endpoints or functionality.
    Requires authentication - call authenticate_docs first if not authenticated.
    
    Args:
        query: Search term (e.g., "users", "POST", "delete", etc.)
    
    Returns:
        Search results with matching endpoints
    """
    global _auth_token
    
    if not _auth_token:
        return "❌ Not authenticated. Please call authenticate_docs with your credentials first.\nDefault credentials: developer@example.com / devpassword123"
    
    if not query:
        return "❌ Please provide a search query."
    
    try:
        response = requests.get(
            f"{DOC_SERVER_URL}/docs/search",
            params={"q": query},
            headers={"Authorization": f"Bearer {_auth_token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            count = data.get('count', 0)
            
            if count == 0:
                return f"🔍 No results found for query: '{query}'"
            
            formatted = f"🔍 Search Results for '{query}' ({count} found):\n\n"
            
            for endpoint in results:
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
            timeout=10
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
    mcp.run()

