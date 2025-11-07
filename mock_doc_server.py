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

# Mock API documentation content - Weather API Documentation
API_DOCS = {
    "guides": [
        {
            "title": "Getting Started with the Weather API",
            "category": "quickstart",
            "description": "Learn how to make your first API request and retrieve weather data",
            "content": """
# Getting Started with the Weather API

Welcome to the Weather API! This guide will help you make your first API request.

## Authentication

All API requests require authentication using a bearer token. Include your token in the Authorization header:

```
Authorization: Bearer YOUR_API_TOKEN
```

## Base URL

```
https://api.weather-service.com/v1
```

## Your First Request

Here's how to get current weather for a location:

### Using cURL

```bash
curl -X GET "https://api.weather-service.com/v1/weather/current?city=London" \\
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Using Python

```python
import requests

url = "https://api.weather-service.com/v1/weather/current"
headers = {"Authorization": "Bearer YOUR_API_TOKEN"}
params = {"city": "London"}

response = requests.get(url, headers=headers, params=params)
weather_data = response.json()

print(f"Temperature: {weather_data['temperature']}°C")
print(f"Conditions: {weather_data['conditions']}")
```

### Using JavaScript

```javascript
const axios = require('axios');

const getWeather = async (city) => {
  const response = await axios.get(
    'https://api.weather-service.com/v1/weather/current',
    {
      headers: { 'Authorization': 'Bearer YOUR_API_TOKEN' },
      params: { city: city }
    }
  );
  
  console.log(`Temperature: ${response.data.temperature}°C`);
  console.log(`Conditions: ${response.data.conditions}`);
};

getWeather('London');
```

## Response Format

All responses are in JSON format:

```json
{
  "city": "London",
  "country": "UK",
  "temperature": 18.5,
  "conditions": "Partly Cloudy",
  "humidity": 65,
  "wind_speed": 12.3,
  "timestamp": "2024-01-15T14:30:00Z"
}
```

## Rate Limits

- Free tier: 100 requests per hour
- Pro tier: 10,000 requests per hour
- Enterprise: Unlimited

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 401: Authentication failed
- 404: Location not found
- 429: Rate limit exceeded
- 500: Server error

Example error response:

```json
{
  "error": "Location not found",
  "code": "LOCATION_NOT_FOUND",
  "message": "The specified city 'Atlantis' could not be found"
}
```
"""
        },
        {
            "title": "How to Get Current Weather",
            "category": "endpoints",
            "description": "Retrieve real-time weather data for any location worldwide",
            "content": """
# GET /weather/current - Get Current Weather

Retrieve current weather conditions for a specific location.

## Endpoint

```
GET /v1/weather/current
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| city | string | Yes* | City name (e.g., "London", "New York") |
| lat | float | Yes* | Latitude coordinate |
| lon | float | longitude | Yes* | Longitude coordinate |
| units | string | No | Temperature units: "metric" (default), "imperial", "kelvin" |
| lang | string | No | Language code for conditions (default: "en") |

*Either `city` OR `lat`/`lon` pair required

## Request Examples

### By City Name

```bash
curl -X GET "https://api.weather-service.com/v1/weather/current?city=Tokyo&units=metric" \\
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### By Coordinates

```bash
curl -X GET "https://api.weather-service.com/v1/weather/current?lat=51.5074&lon=-0.1278" \\
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Python Example

```python
import requests

def get_current_weather(city, units="metric"):
    url = "https://api.weather-service.com/v1/weather/current"
    headers = {"Authorization": "Bearer YOUR_API_TOKEN"}
    params = {
        "city": city,
        "units": units
    }
    
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
print(f"Conditions: {weather['conditions']}")
```

## Response

```json
{
  "city": "Tokyo",
  "country": "Japan",
  "coordinates": {
    "lat": 35.6762,
    "lon": 139.6503
  },
  "temperature": 22.5,
  "feels_like": 21.8,
  "conditions": "Clear Sky",
  "description": "Clear sky with excellent visibility",
  "humidity": 55,
  "pressure": 1013,
  "wind_speed": 8.5,
  "wind_direction": "NE",
  "visibility": 10000,
  "clouds": 5,
  "sunrise": "2024-01-15T06:45:00Z",
  "sunset": "2024-01-15T17:30:00Z",
  "timestamp": "2024-01-15T14:30:00Z",
  "timezone": "Asia/Tokyo"
}
```

## Field Descriptions

- **temperature**: Current temperature in specified units
- **feels_like**: Apparent temperature accounting for wind chill/heat index
- **conditions**: Brief description (e.g., "Clear Sky", "Light Rain")
- **humidity**: Humidity percentage (0-100)
- **wind_speed**: Wind speed in km/h (metric) or mph (imperial)
- **visibility**: Visibility distance in meters
- **clouds**: Cloud coverage percentage (0-100)

## Units

### Metric (default)
- Temperature: Celsius (°C)
- Wind speed: km/h
- Pressure: hPa

### Imperial
- Temperature: Fahrenheit (°F)
- Wind speed: mph
- Pressure: inHg

### Kelvin
- Temperature: Kelvin (K)
- Wind speed: m/s
- Pressure: hPa
"""
        },
        {
            "title": "How to Get Weather Forecast",
            "category": "endpoints",
            "description": "Retrieve weather forecasts up to 7 days in advance",
            "content": """
# GET /weather/forecast - Get Weather Forecast

Get weather forecast for the next 1-7 days.

## Endpoint

```
GET /v1/weather/forecast
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| city | string | Yes* | City name |
| lat | float | Yes* | Latitude |
| lon | float | Yes* | Longitude |
| days | integer | No | Number of forecast days (1-7, default: 5) |
| units | string | No | "metric" (default), "imperial", or "kelvin" |

*Either `city` OR `lat`/`lon` pair required

## Request Examples

### Get 3-Day Forecast

```bash
curl -X GET "https://api.weather-service.com/v1/weather/forecast?city=Seattle&days=3" \\
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Python Example - 7-Day Forecast

```python
import requests
from datetime import datetime

def get_weather_forecast(city, days=5):
    url = "https://api.weather-service.com/v1/weather/forecast"
    headers = {"Authorization": "Bearer YOUR_API_TOKEN"}
    params = {
        "city": city,
        "days": days,
        "units": "metric"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Forecast for {data['city']}, {data['country']}:\\n")
        
        for day in data['forecast']:
            date = datetime.fromisoformat(day['date']).strftime('%A, %B %d')
            print(f"{date}:")
            print(f"  High: {day['temp_max']}°C, Low: {day['temp_min']}°C")
            print(f"  {day['conditions']} - {day['description']}")
            print(f"  Rain chance: {day['precipitation_chance']}%")
            print()
    else:
        print(f"Error: {response.status_code}")

# Usage
get_weather_forecast("Barcelona", days=7)
```

### JavaScript Example

```javascript
const axios = require('axios');

async function getWeatherForecast(city, days = 5) {
  try {
    const response = await axios.get(
      'https://api.weather-service.com/v1/weather/forecast',
      {
        headers: { 'Authorization': 'Bearer YOUR_API_TOKEN' },
        params: { city, days, units: 'imperial' }
      }
    );
    
    const forecast = response.data.forecast;
    forecast.forEach(day => {
      console.log(`${day.date}: ${day.temp_max}°F/${day.temp_min}°F - ${day.conditions}`);
    });
  } catch (error) {
    console.error('API Error:', error.response?.status);
  }
}

getWeatherForecast('Miami', 3);
```

## Response

```json
{
  "city": "Seattle",
  "country": "USA",
  "coordinates": {
    "lat": 47.6062,
    "lon": -122.3321
  },
  "timezone": "America/Los_Angeles",
  "forecast": [
    {
      "date": "2024-01-15",
      "day_of_week": "Monday",
      "temp_max": 15.5,
      "temp_min": 8.2,
      "temp_avg": 11.8,
      "conditions": "Light Rain",
      "description": "Light rain throughout the day",
      "precipitation_chance": 75,
      "precipitation_amount": 5.2,
      "humidity": 82,
      "wind_speed": 18.5,
      "wind_direction": "SW",
      "sunrise": "2024-01-15T07:55:00-08:00",
      "sunset": "2024-01-15T16:45:00-08:00"
    },
    {
      "date": "2024-01-16",
      "day_of_week": "Tuesday",
      "temp_max": 12.3,
      "temp_min": 6.8,
      "temp_avg": 9.5,
      "conditions": "Cloudy",
      "description": "Overcast with possible light showers",
      "precipitation_chance": 45,
      "precipitation_amount": 1.5,
      "humidity": 78,
      "wind_speed": 15.2,
      "wind_direction": "W",
      "sunrise": "2024-01-16T07:54:00-08:00",
      "sunset": "2024-01-16T16:46:00-08:00"
    }
  ]
}
```

## Best Practices

1. **Cache forecast data**: Forecast data doesn't change frequently. Cache responses for at least 30 minutes.

2. **Handle missing days**: In extreme weather, some days might not be available.

3. **Use coordinates for precision**: City names can be ambiguous. Use lat/lon for exact locations.

4. **Check precipitation_chance**: Values above 50% indicate likely rain.

## Common Use Cases

### Travel Planning

```python
def is_good_weather_for_travel(city, travel_date):
    forecast = get_weather_forecast(city, days=7)
    
    for day in forecast['forecast']:
        if day['date'] == travel_date:
            if day['precipitation_chance'] < 30 and day['temp_max'] > 15:
                return True, f"Great weather! {day['conditions']}"
            else:
                return False, f"Not ideal: {day['conditions']}, {day['precipitation_chance']}% rain"
    
    return None, "Date not in forecast range"
```

### Agricultural Planning

```python
def should_water_garden(city):
    forecast = get_weather_forecast(city, days=3)
    
    total_rain = sum(day['precipitation_amount'] for day in forecast['forecast'])
    
    if total_rain > 10:  # mm
        return False, f"Expected {total_rain}mm of rain - no watering needed"
    else:
        return True, f"Only {total_rain}mm expected - watering recommended"
```
"""
        }
    ],
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
    
    # Search in implementation guides
    guide_results = []
    for guide in API_DOCS.get("guides", []):
        if (query in guide["title"].lower() or 
            query in guide["description"].lower() or 
            query in guide["category"].lower() or
            query in guide["content"].lower()):
            guide_results.append(guide)
    
    # Search in endpoint names, descriptions, and paths
    endpoint_results = []
    for endpoint in API_DOCS["endpoints"]:
        if (query in endpoint["name"].lower() or 
            query in endpoint["description"].lower() or 
            query in endpoint["path"].lower() or
            query in endpoint["method"].lower()):
            endpoint_results.append(endpoint)
    
    return jsonify({
        "query": query,
        "guides": guide_results,
        "endpoints": endpoint_results,
        "total_count": len(guide_results) + len(endpoint_results),
        "guide_count": len(guide_results),
        "endpoint_count": len(endpoint_results)
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
