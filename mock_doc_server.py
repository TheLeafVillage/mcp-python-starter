"""
Mock documentation server with simple token-based authentication.
This simulates an API documentation server behind SSO/authentication.

PROTOTYPE IMPLEMENTATION - NOT FOR PRODUCTION USE
This is a demonstration/testing server with intentional simplifications:
- Passwords stored in plain text (use bcrypt/argon2 in production)
- Tokens without expiration (implement expiration in production)
- In-memory storage (use database in production)
- No rate limiting (add in production)
"""
from flask import Flask, request, jsonify
import secrets
import json

app = Flask(__name__)

# Simple in-memory token store (for prototype purposes)
TOKENS = {}
# Mock user credentials (PROTOTYPE: plain text passwords)
# Production: Use proper password hashing (bcrypt, argon2, etc.)
USERS = {
    "developer@example.com": "devpassword123"
}

# Mock API documentation content
API_DOCS = {
    "endpoints": [
        {
            "name": "GET /api/users",
            "description": "Retrieve a list of all users",
            "method": "GET",
            "path": "/api/users",
            "parameters": [],
            "response": {
                "200": {
                    "description": "List of users",
                    "example": '{"users": [{"id": 1, "name": "John"}]}'
                }
            }
        },
        {
            "name": "POST /api/users",
            "description": "Create a new user",
            "method": "POST",
            "path": "/api/users",
            "parameters": [
                {"name": "name", "type": "string", "required": True},
                {"name": "email", "type": "string", "required": True}
            ],
            "response": {
                "201": {
                    "description": "User created successfully",
                    "example": '{"id": 1, "name": "John", "email": "john@example.com"}'
                }
            }
        },
        {
            "name": "GET /api/users/{id}",
            "description": "Get a specific user by ID",
            "method": "GET",
            "path": "/api/users/{id}",
            "parameters": [
                {"name": "id", "type": "integer", "required": True, "location": "path"}
            ],
            "response": {
                "200": {
                    "description": "User details",
                    "example": '{"id": 1, "name": "John", "email": "john@example.com"}'
                },
                "404": {
                    "description": "User not found"
                }
            }
        },
        {
            "name": "PUT /api/users/{id}",
            "description": "Update an existing user",
            "method": "PUT",
            "path": "/api/users/{id}",
            "parameters": [
                {"name": "id", "type": "integer", "required": True, "location": "path"},
                {"name": "name", "type": "string", "required": False},
                {"name": "email", "type": "string", "required": False}
            ],
            "response": {
                "200": {
                    "description": "User updated successfully",
                    "example": '{"id": 1, "name": "John Updated", "email": "john.updated@example.com"}'
                }
            }
        },
        {
            "name": "DELETE /api/users/{id}",
            "description": "Delete a user",
            "method": "DELETE",
            "path": "/api/users/{id}",
            "parameters": [
                {"name": "id", "type": "integer", "required": True, "location": "path"}
            ],
            "response": {
                "204": {
                    "description": "User deleted successfully"
                }
            }
        }
    ],
    "authentication": {
        "type": "Bearer Token",
        "description": "All API requests require a valid bearer token in the Authorization header"
    },
    "base_url": "https://api.example.com",
    "version": "v1"
}

@app.route("/auth/login", methods=["POST"])
def login():
    """Authenticate user and return a token."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if email in USERS and USERS[email] == password:
        # Generate a token
        token = secrets.token_urlsafe(32)
        TOKENS[token] = email
        return jsonify({
            "token": token,
            "message": "Authentication successful",
            "user": email
        }), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/auth/validate", methods=["GET"])
def validate():
    """Validate a token."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    
    token = auth_header.split(" ")[1]
    
    if token in TOKENS:
        return jsonify({
            "valid": True,
            "user": TOKENS[token]
        }), 200
    
    return jsonify({"error": "Invalid token"}), 401

@app.route("/docs", methods=["GET"])
def get_docs():
    """Get all API documentation (requires authentication)."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authentication required. Please provide a valid Bearer token."}), 401
    
    token = auth_header.split(" ")[1]
    
    if token not in TOKENS:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    return jsonify(API_DOCS), 200

@app.route("/docs/search", methods=["GET"])
def search_docs():
    """Search API documentation (requires authentication)."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authentication required"}), 401
    
    token = auth_header.split(" ")[1]
    
    if token not in TOKENS:
        return jsonify({"error": "Invalid token"}), 401
    
    query = request.args.get("q", "").lower()
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    # Search in endpoint names, descriptions, and paths
    results = []
    for endpoint in API_DOCS["endpoints"]:
        if (query in endpoint["name"].lower() or 
            query in endpoint["description"].lower() or 
            query in endpoint["path"].lower() or
            query in endpoint["method"].lower()):
            results.append(endpoint)
    
    return jsonify({
        "query": query,
        "results": results,
        "count": len(results)
    }), 200

@app.route("/", methods=["GET"])
def index():
    """Root endpoint."""
    return jsonify({
        "message": "Mock API Documentation Server",
        "version": "1.0",
        "endpoints": {
            "login": "POST /auth/login",
            "validate": "GET /auth/validate",
            "docs": "GET /docs (authenticated)",
            "search": "GET /docs/search?q=<query> (authenticated)"
        }
    }), 200

if __name__ == "__main__":
    print("Starting Mock Documentation Server on http://localhost:5001")
    print("Default credentials: developer@example.com / devpassword123")
    # Security: debug=False to prevent arbitrary code execution via debugger
    # For development, set FLASK_DEBUG=1 environment variable instead
    app.run(host="0.0.0.0", port=5001, debug=False)
