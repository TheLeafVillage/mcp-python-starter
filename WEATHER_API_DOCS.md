# Weather API Documentation - MCP Server Implementation

## Overview

This implementation provides a realistic example of using an MCP server to access API documentation that is behind authentication. The mock documentation website hosts **Weather API** documentation with comprehensive implementation guides.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Developer in VS Code with Copilot                              │
│  Asks: "How do I get current weather in Python?"               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Natural Language Query
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCP Server (server.py)                                         │
│  - authenticate_docs()      - Handles login                     │
│  - search_documentation()   - Searches using natural language   │
│  - get_guide()              - Retrieves full guide content      │
│  - get_documentation()      - Gets all available docs           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP + Bearer Token Auth
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Mock Documentation Website (mock_doc_server.py)                │
│  Port: 5001                                                     │
│  🔒 Requires Authentication (Token-based SSO simulation)        │
│                                                                 │
│  📚 Weather API Documentation:                                  │
│  - Getting Started Guide                                        │
│  - How to Get Current Weather                                   │
│  - How to Get Weather Forecast                                  │
│                                                                 │
│  Each guide includes:                                           │
│  ✓ Python code examples                                         │
│  ✓ cURL commands                                                │
│  ✓ JavaScript examples                                          │
│  ✓ Response formats                                             │
│  ✓ Best practices                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Documentation Content

### 1. Getting Started with the Weather API
**Category**: Quickstart  
**Content**:
- Authentication setup
- Base URL configuration
- First API request examples in Python, cURL, and JavaScript
- Response format explanation
- Error handling
- Rate limits

### 2. How to Get Current Weather
**Category**: Endpoints  
**Content**:
- Complete endpoint documentation for `/v1/weather/current`
- Parameters: city, lat/lon, units, lang
- Python implementation with error handling
- cURL examples for quick testing
- Response field descriptions
- Unit conversion information

### 3. How to Get Weather Forecast
**Category**: Endpoints  
**Content**:
- 7-day forecast endpoint documentation
- Parameters: city, lat/lon, days, units
- Python implementation with date formatting
- JavaScript async/await example
- Use cases: travel planning, agriculture
- Best practices for caching

## Example Usage in VS Code

### Scenario 1: Getting Started
```
Developer: "How do I get started with this Weather API?"

Copilot: Let me search the documentation...

[MCP server authenticates and searches]

Here's the getting started guide:

# Authentication
All requests require a bearer token:
Authorization: Bearer YOUR_API_TOKEN

# Python Example:
import requests

url = "https://api.weather-service.com/v1/weather/current"
headers = {"Authorization": "Bearer YOUR_API_TOKEN"}
params = {"city": "London"}

response = requests.get(url, headers=headers, params=params)
weather_data = response.json()
print(f"Temperature: {weather_data['temperature']}°C")
```

### Scenario 2: Implementation Question
```
Developer: "Show me how to get current weather in Python"

Copilot: Here's a complete Python implementation:

def get_current_weather(city, units="metric"):
    url = "https://api.weather-service.com/v1/weather/current"
    headers = {"Authorization": "Bearer YOUR_API_TOKEN"}
    params = {"city": city, "units": units}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["temperature"],
            "conditions": data["conditions"],
            "humidity": data["humidity"],
            "wind_speed": data["wind_speed"]
        }
    else:
        raise Exception(f"API Error: {response.status_code}")

# Usage
weather = get_current_weather("Paris")
print(f"It's {weather['temperature']}°C in Paris")
```

### Scenario 3: Advanced Feature
```
Developer: "How do I get a 7-day forecast?"

Copilot: Here's how to get weather forecasts:

def get_weather_forecast(city, days=7):
    url = "https://api.weather-service.com/v1/weather/forecast"
    headers = {"Authorization": "Bearer YOUR_API_TOKEN"}
    params = {"city": city, "days": days}
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    for day in data['forecast']:
        print(f"{day['date']}: {day['temp_max']}°C/{day['temp_min']}°C")
        print(f"  {day['conditions']} - {day['precipitation_chance']}% rain")
```

## MCP Tools Available

### 1. `authenticate_docs(email, password)`
Authenticates with the documentation server.
```python
authenticate_docs("developer@example.com", "devpassword123")
# Returns: ✅ Authentication successful!
```

### 2. `search_documentation(query)`
Search using natural language.
```python
search_documentation("how to get current weather")
# Returns: List of matching guides with descriptions
```

### 3. `get_guide(title)`
Retrieve full guide content.
```python
get_guide("How to Get Current Weather")
# Returns: Complete guide with code examples
```

### 4. `get_documentation()`
Get all available documentation.
```python
get_documentation()
# Returns: List of all guides and endpoints
```

### 5. `check_auth_status()`
Check authentication status.
```python
check_auth_status()
# Returns: Current auth state and available actions
```

## Key Features

✅ **Natural Language Queries**: Ask questions naturally, get relevant documentation  
✅ **Code Examples**: Every guide includes working Python, cURL, and JavaScript examples  
✅ **Authentication Handling**: Seamlessly manages SSO/authentication to protected docs  
✅ **Search Across Content**: Searches guide titles, descriptions, and content  
✅ **Realistic API Documentation**: Weather API docs represent real-world API documentation  

## Testing

Run the test script to see it in action:
```bash
python /tmp/test_weather_api_docs.py
```

This demonstrates:
- Authenticating with the doc server
- Searching for guides using natural language
- Retrieving full guide content with code examples
- How developers would interact with it through VS Code Copilot

## Production Considerations

This is a prototype. For production:
- Replace token-based auth with OAuth2/OIDC
- Use HTTPS for all communication
- Implement token expiration and refresh
- Add rate limiting
- Use a production database
- Deploy with proper WSGI server (Gunicorn)
- Add monitoring and logging
- Implement proper error handling and retries

## Extending the System

To add more API documentation:
1. Edit `API_DOCS` in `mock_doc_server.py`
2. Add new guides to the `"guides"` array
3. Include code examples in Python, cURL, JavaScript
4. Test with natural language queries
5. Guides are automatically searchable and retrievable
