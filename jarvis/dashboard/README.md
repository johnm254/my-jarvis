# JARVIS Dashboard Backend

Flask-based REST API backend for the JARVIS web dashboard with JWT authentication.

## Features

- **JWT Authentication**: Secure token-based authentication for API endpoints
- **CORS Support**: Configured for frontend integration
- **WebSocket Support**: Real-time communication via Flask-SocketIO
- **Health Monitoring**: Health check endpoint for system monitoring
- **Middleware Protection**: Easy-to-use `@require_auth` decorator for protected endpoints

## Quick Start

### Running the Server

```bash
# Run with default settings (port from config)
python -m jarvis.dashboard

# Run on custom port
python -m jarvis.dashboard --port 5000

# Run in debug mode
python -m jarvis.dashboard --debug

# Run on specific host and port
python -m jarvis.dashboard --host 127.0.0.1 --port 8080
```

### Programmatic Usage

```python
from jarvis.dashboard import run_server

# Start server with default settings
run_server()

# Start with custom configuration
run_server(host='0.0.0.0', port=5000, debug=True)
```

## API Endpoints

### Authentication

#### POST /api/auth/login

Authenticate user and receive JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "jarvis123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "admin_user",
  "expires_in": 86400
}
```

**Error Responses:**
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials

#### GET /api/auth/verify

Verify if JWT token is valid.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "valid": true,
  "user_id": "admin_user"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token

### Health Check

#### GET /api/health

Check server health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Protected Endpoints

All protected endpoints require the `Authorization` header with a valid JWT token:

```
Authorization: Bearer <token>
```

Example protected endpoint:

#### GET /api/protected

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Access granted",
  "user_id": "admin_user"
}
```

## JWT Authentication

### Token Generation

```python
from jarvis.dashboard import generate_jwt_token

token = generate_jwt_token(user_id='user123')
```

### Token Validation

```python
from jarvis.dashboard import validate_jwt_token

payload = validate_jwt_token(token)
if payload:
    user_id = payload['user_id']
    print(f"Valid token for user: {user_id}")
else:
    print("Invalid or expired token")
```

### Protecting Endpoints

Use the `@require_auth` decorator to protect endpoints:

```python
from flask import jsonify
from jarvis.dashboard import app, require_auth

@app.route('/api/my-endpoint', methods=['GET'])
@require_auth
def my_protected_endpoint():
    # Access user_id from request context
    user_id = request.user_id
    return jsonify({'message': f'Hello {user_id}'})
```

## Configuration

The dashboard backend uses configuration from `jarvis.config`:

- `JWT_SECRET`: Secret key for JWT token signing (from environment variable)
- `DASHBOARD_PORT`: Port number for the server (default: 3000)

### Environment Variables

Required in `.env` file:

```env
JWT_SECRET=your_jwt_secret_here_change_in_production
DASHBOARD_PORT=3000
```

## Security Notes

### Current Implementation

- **Hardcoded Credentials**: The current implementation uses hardcoded credentials (`admin`/`jarvis123`) for demonstration purposes
- **Production Warning**: This MUST be replaced with proper user authentication before production use

### Production Recommendations

1. **User Database**: Implement user authentication against a database
2. **Password Hashing**: Use bcrypt or argon2 for password hashing
3. **Rate Limiting**: Add rate limiting to prevent brute force attacks
4. **HTTPS**: Always use HTTPS in production
5. **Token Refresh**: Implement token refresh mechanism for long-lived sessions
6. **Audit Logging**: Log all authentication attempts

### Example Production Authentication

```python
from werkzeug.security import check_password_hash
from jarvis.memory import MemorySystem

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Query user from database
    memory = MemorySystem()
    user = memory.get_user_by_username(username)
    
    if user and check_password_hash(user.password_hash, password):
        token = generate_jwt_token(user.id)
        return jsonify({'token': token, 'user_id': user.id}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
```

## Testing

### Manual Testing with curl

```bash
# Login and get token
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "jarvis123"}'

# Use token to access protected endpoint
TOKEN="<token_from_login>"
curl -X GET http://localhost:3000/api/protected \
  -H "Authorization: Bearer $TOKEN"

# Verify token
curl -X GET http://localhost:3000/api/auth/verify \
  -H "Authorization: Bearer $TOKEN"
```

### Testing with Python

```python
import requests

# Login
response = requests.post('http://localhost:3000/api/auth/login', json={
    'username': 'admin',
    'password': 'jarvis123'
})
token = response.json()['token']

# Access protected endpoint
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:3000/api/protected', headers=headers)
print(response.json())
```

## Architecture

```
jarvis/dashboard/
├── __init__.py          # Module exports
├── __main__.py          # CLI entry point
├── app.py               # Flask application with JWT auth
└── README.md            # This file
```

## Dependencies

- `flask`: Web framework
- `flask-cors`: CORS support
- `flask-socketio`: WebSocket support
- `pyjwt`: JWT token generation and validation
- `python-socketio`: Socket.IO server

## Future Enhancements

- [ ] User registration endpoint
- [ ] Password reset functionality
- [ ] Token refresh mechanism
- [ ] Role-based access control (RBAC)
- [ ] OAuth2 integration
- [ ] Multi-factor authentication (MFA)
- [ ] Session management
- [ ] API rate limiting
