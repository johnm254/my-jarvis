"""Flask backend for JARVIS dashboard with JWT authentication."""

import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from jarvis.brain.brain import Brain
from jarvis.config import load_config
from jarvis.memory.memory_system import MemorySystem, MemorySystemError
from jarvis.memory.models import ConversationExchange
from jarvis.audit_logger import get_audit_logger


# Initialize Flask app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load configuration
config = load_config()

# Initialize Brain and Memory System lazily
_brain = None
_memory_system = None


def get_brain():
    """Get or initialize the Brain instance."""
    global _brain
    if _brain is None:
        _brain = Brain(config)
    return _brain


def get_memory_system():
    """Get or initialize the Memory System instance."""
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem(config)
    return _memory_system


# Configure Flask
app.config['SECRET_KEY'] = config.jwt_secret
app.config['JWT_SECRET_KEY'] = config.jwt_secret
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_EXPIRATION_HOURS'] = 24

# Enable CORS for frontend integration
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


# JWT Token Generation
def generate_jwt_token(user_id: str) -> str:
    """
    Generate a JWT token for authenticated user.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        app.config['JWT_SECRET_KEY'],
        algorithm=app.config['JWT_ALGORITHM']
    )
    
    return token


# JWT Token Validation
def validate_jwt_token(token: str) -> Optional[dict]:
    """
    Validate a JWT token and extract payload.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            app.config['JWT_SECRET_KEY'],
            algorithms=[app.config['JWT_ALGORITHM']]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# Authentication Middleware Decorator
def require_auth(f):
    """
    Decorator to protect endpoints with JWT authentication.
    
    Usage:
        @app.route('/api/protected')
        @require_auth
        def protected_endpoint():
            return jsonify({'message': 'Access granted'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing Authorization header'}), 401
        
        # Check for Bearer token format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Invalid Authorization header format. Expected: Bearer <token>'}), 401
        
        token = parts[1]
        
        # Validate token
        payload = validate_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Attach user info to request context
        request.user_id = payload.get('user_id')
        
        return f(*args, **kwargs)
    
    return decorated_function


# Authentication Endpoints

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token.
    
    Request Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Response:
        {
            "token": "jwt_token_string",
            "user_id": "user_id",
            "expires_in": 86400
        }
    
    Status Codes:
        200: Login successful
        400: Missing username or password
        401: Invalid credentials
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # TODO: Replace with actual user authentication against database
    # For now, using simple hardcoded credentials for demonstration
    # In production, this should check against a user database with hashed passwords
    if username == 'admin' and password == 'jarvis123':
        user_id = 'admin_user'
        token = generate_jwt_token(user_id)
        
        # Log successful authentication
        try:
            memory_system = get_memory_system()
            audit_logger = get_audit_logger(memory_system)
            audit_logger.log_authentication(
                user_id=user_id,
                success=True,
                details={'username': username}
            )
        except Exception as e:
            print(f"Warning: Failed to log authentication: {e}")
        
        return jsonify({
            'token': token,
            'user_id': user_id,
            'expires_in': app.config['JWT_EXPIRATION_HOURS'] * 3600
        }), 200
    else:
        # Log failed authentication
        try:
            memory_system = get_memory_system()
            audit_logger = get_audit_logger(memory_system)
            audit_logger.log_authentication(
                user_id=username,
                success=False,
                details={'username': username, 'reason': 'invalid_credentials'}
            )
        except Exception as e:
            print(f"Warning: Failed to log failed authentication: {e}")
        
        return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_token():
    """
    Verify if the current JWT token is valid.
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
        {
            "valid": true,
            "user_id": "user_id"
        }
    
    Status Codes:
        200: Token is valid
        401: Token is invalid or expired
    """
    return jsonify({
        'valid': True,
        'user_id': request.user_id
    }), 200


# Health Check Endpoint

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    
    Response:
        {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


# Protected Example Endpoint

@app.route('/api/protected', methods=['GET'])
@require_auth
def protected_example():
    """
    Example protected endpoint requiring authentication.
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
        {
            "message": "Access granted",
            "user_id": "user_id"
        }
    """
    return jsonify({
        'message': 'Access granted',
        'user_id': request.user_id
    }), 200


# Conversation API Endpoints

@app.route('/api/conversation/history', methods=['GET'])
@require_auth
def get_conversation_history():
    """
    Retrieve conversation history for a session.
    
    Headers:
        Authorization: Bearer <token>
    
    Query Parameters:
        session_id: Optional session identifier (defaults to user_id)
        limit: Maximum number of exchanges to return (default: 20)
    
    Response:
        {
            "session_id": "session_123",
            "exchanges": [
                {
                    "timestamp": "2024-01-15T10:30:00Z",
                    "user_input": "What's the weather?",
                    "brain_response": "The weather is sunny...",
                    "confidence_score": 95,
                    "tool_calls": []
                }
            ],
            "count": 5
        }
    
    Status Codes:
        200: Success
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Get session_id from query params or use user_id
        session_id = request.args.get('session_id', request.user_id)
        limit = int(request.args.get('limit', 20))
        
        # Get conversation context from Brain
        brain = get_brain()
        exchanges = brain.get_conversation_context(session_id)
        
        # Convert exchanges to JSON-serializable format
        exchanges_data = []
        for exchange in exchanges:
            exchanges_data.append({
                'timestamp': exchange.timestamp.isoformat() + 'Z',
                'user_input': exchange.user_input,
                'brain_response': exchange.brain_response,
                'confidence_score': exchange.confidence_score,
                'tool_calls': exchange.tool_calls
            })
        
        # Limit results
        exchanges_data = exchanges_data[-limit:]
        
        return jsonify({
            'session_id': session_id,
            'exchanges': exchanges_data,
            'count': len(exchanges_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve conversation history: {str(e)}'}), 500


@app.route('/api/conversation/send', methods=['POST'])
@require_auth
def send_message():
    """
    Send a message to the Brain and get response.
    
    Headers:
        Authorization: Bearer <token>
    
    Request Body:
        {
            "message": "What's the weather in Seattle?",
            "session_id": "optional_session_id"
        }
    
    Response:
        {
            "session_id": "session_123",
            "response": "The weather in Seattle is...",
            "confidence_score": 95,
            "tool_calls": [
                {
                    "id": "call_123",
                    "name": "get_weather",
                    "input": {"location": "Seattle"}
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
    
    Status Codes:
        200: Success
        400: Missing message
        401: Unauthorized
        500: Internal server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        message = data.get('message')
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get session_id from request or use user_id
        session_id = data.get('session_id', request.user_id)
        
        # Get Brain and Memory System instances
        brain = get_brain()
        memory_system = get_memory_system()
        audit_logger = get_audit_logger(memory_system)
        
        # Get memory context for this session
        memory_context = memory_system.inject_context(session_id)
        
        # Process input through Brain
        brain_response = brain.process_input(
            user_input=message,
            session_id=session_id,
            memory_context=memory_context
        )
        
        # Log conversation to audit log
        audit_logger.log_conversation(
            user_id=request.user_id,
            session_id=session_id,
            user_input=message,
            brain_response=brain_response.text,
            confidence_score=brain_response.confidence_score,
            success=True
        )
        
        # Store conversation in memory system
        exchange = ConversationExchange(
            session_id=session_id,
            timestamp=datetime.utcnow(),
            user_input=message,
            brain_response=brain_response.text,
            confidence_score=brain_response.confidence_score,
            tool_calls=[],  # TODO: Convert brain tool_calls to ToolCall objects
            embedding=[]  # TODO: Generate embedding for semantic search
        )
        
        try:
            memory_system.store_conversation(session_id, exchange)
        except Exception as mem_error:
            # Log error but don't fail the request
            print(f"Warning: Failed to store conversation in memory: {mem_error}")
        
        # Emit WebSocket event for real-time updates
        socketio.emit('conversation_update', {
            'session_id': session_id,
            'user_input': message,
            'brain_response': brain_response.text,
            'confidence_score': brain_response.confidence_score,
            'tool_calls': brain_response.tool_calls,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }, namespace='/')
        
        return jsonify({
            'session_id': session_id,
            'response': brain_response.text,
            'confidence_score': brain_response.confidence_score,
            'tool_calls': brain_response.tool_calls,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to process message: {str(e)}'}), 500


# Memory API Endpoints

@app.route('/api/memory/search', methods=['GET'])
@require_auth
def search_memory():
    """
    Search memories by query with semantic search.
    
    Headers:
        Authorization: Bearer <token>
    
    Query Parameters:
        query: Search query string (required)
        limit: Maximum number of results to return (default: 5)
        threshold: Minimum similarity threshold 0-1 (default: 0.7)
    
    Response:
        {
            "query": "search query",
            "results": [
                {
                    "id": "uuid",
                    "session_id": "session_123",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "user_input": "What's the weather?",
                    "brain_response": "The weather is...",
                    "confidence_score": 95,
                    "similarity": 0.85
                }
            ],
            "count": 3
        }
    
    Status Codes:
        200: Success
        400: Missing query parameter
        401: Unauthorized
        500: Internal server error
    """
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        limit = int(request.args.get('limit', 5))
        threshold = float(request.args.get('threshold', 0.7))
        
        # Get Memory System instance
        memory_system = get_memory_system()
        
        # TODO: Generate embedding for query
        # For now, we'll use a placeholder empty embedding
        # In production, this should use the same embedding model as store_conversation
        query_embedding = []  # Placeholder
        
        # Perform semantic search
        results = memory_system.semantic_search(
            query_embedding=query_embedding,
            limit=limit,
            similarity_threshold=threshold
        )
        
        # Format results for JSON response
        formatted_results = []
        for result in results:
            formatted_results.append({
                'id': result.get('id'),
                'session_id': result.get('session_id'),
                'timestamp': result.get('timestamp'),
                'user_input': result.get('user_input'),
                'brain_response': result.get('brain_response'),
                'confidence_score': result.get('confidence_score'),
                'similarity': result.get('similarity', 0)
            })
        
        return jsonify({
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to search memories: {str(e)}'}), 500


@app.route('/api/memory/update', methods=['PUT'])
@require_auth
def update_memory():
    """
    Update user preferences or profile information.
    
    Headers:
        Authorization: Bearer <token>
    
    Request Body:
        {
            "user_id": "optional_user_id",
            "preference_key": "preference_name",
            "preference_value": "value"
        }
        OR
        {
            "user_id": "optional_user_id",
            "profile_updates": {
                "first_name": "John",
                "timezone": "America/Los_Angeles",
                "communication_style": "technical"
            }
        }
    
    Response:
        {
            "success": true,
            "message": "Preference updated successfully",
            "user_id": "user_id"
        }
    
    Status Codes:
        200: Success
        400: Missing required fields
        401: Unauthorized
        500: Internal server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Get user_id from request or use authenticated user
        user_id = data.get('user_id', request.user_id)
        
        # Get Memory System instance
        memory_system = get_memory_system()
        audit_logger = get_audit_logger(memory_system)
        
        # Check if updating a single preference or multiple profile fields
        if 'preference_key' in data and 'preference_value' in data:
            # Update single preference
            preference_key = data['preference_key']
            preference_value = data['preference_value']
            
            memory_system.update_preference(
                user_id=user_id,
                key=preference_key,
                value=preference_value
            )
            
            # Log memory operation
            audit_logger.log_memory_operation(
                user_id=request.user_id,
                operation="update",
                details={'preference_key': preference_key},
                success=True
            )
            
            return jsonify({
                'success': True,
                'message': f'Preference "{preference_key}" updated successfully',
                'user_id': user_id
            }), 200
            
        elif 'profile_updates' in data:
            # Update multiple profile fields
            profile_updates = data['profile_updates']
            
            if not isinstance(profile_updates, dict):
                return jsonify({'error': 'profile_updates must be a dictionary'}), 400
            
            # Get current profile
            profile = memory_system.get_personal_profile(user_id)
            
            # Update allowed fields
            allowed_fields = ['first_name', 'timezone', 'communication_style', 'work_hours', 'interests']
            update_data = {}
            
            for field, value in profile_updates.items():
                if field in allowed_fields:
                    update_data[field] = value
            
            if not update_data:
                return jsonify({'error': 'No valid profile fields to update'}), 400
            
            # Update profile in database
            result = memory_system.client.table("personal_profile").update(
                update_data
            ).eq("user_id", user_id).execute()
            
            if not result.data:
                raise MemorySystemError("Failed to update profile: no data returned")
            
            # Log memory operation
            audit_logger.log_memory_operation(
                user_id=request.user_id,
                operation="update",
                details={'updated_fields': list(update_data.keys())},
                success=True
            )
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user_id': user_id,
                'updated_fields': list(update_data.keys())
            }), 200
            
        else:
            return jsonify({
                'error': 'Request must include either preference_key/preference_value or profile_updates'
            }), 400
        
    except Exception as e:
        return jsonify({'error': f'Failed to update memory: {str(e)}'}), 500


@app.route('/api/memory/delete', methods=['DELETE'])
@require_auth
def delete_memory():
    """
    Delete specific memories or conversations.
    
    Headers:
        Authorization: Bearer <token>
    
    Request Body:
        {
            "conversation_id": "uuid"
        }
        OR
        {
            "session_id": "session_123"
        }
        OR
        {
            "delete_all": true,
            "confirm": true
        }
    
    Response:
        {
            "success": true,
            "message": "Memory deleted successfully",
            "deleted_count": 1
        }
    
    Status Codes:
        200: Success
        400: Missing required fields or invalid request
        401: Unauthorized
        403: Confirmation required for bulk delete
        500: Internal server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Get Memory System instance
        memory_system = get_memory_system()
        audit_logger = get_audit_logger(memory_system)
        
        # Delete specific conversation by ID
        if 'conversation_id' in data:
            conversation_id = data['conversation_id']
            
            result = memory_system.client.table("conversations").delete().eq(
                "id", conversation_id
            ).execute()
            
            deleted_count = len(result.data) if result.data else 0
            
            # Log memory operation
            audit_logger.log_memory_operation(
                user_id=request.user_id,
                operation="delete",
                details={'conversation_id': conversation_id, 'deleted_count': deleted_count},
                success=True
            )
            
            return jsonify({
                'success': True,
                'message': 'Conversation deleted successfully',
                'deleted_count': deleted_count
            }), 200
        
        # Delete all conversations in a session
        elif 'session_id' in data:
            session_id = data['session_id']
            
            result = memory_system.client.table("conversations").delete().eq(
                "session_id", session_id
            ).execute()
            
            deleted_count = len(result.data) if result.data else 0
            
            return jsonify({
                'success': True,
                'message': f'All conversations in session "{session_id}" deleted successfully',
                'deleted_count': deleted_count
            }), 200
        
        # Delete all memories (requires confirmation)
        elif data.get('delete_all') is True:
            if data.get('confirm') is not True:
                return jsonify({
                    'error': 'Bulk delete requires explicit confirmation',
                    'message': 'Set "confirm": true to proceed with deleting all memories'
                }), 403
            
            # Delete all conversations
            result = memory_system.client.table("conversations").delete().neq(
                "id", "00000000-0000-0000-0000-000000000000"  # Delete all except non-existent ID
            ).execute()
            
            deleted_count = len(result.data) if result.data else 0
            
            return jsonify({
                'success': True,
                'message': 'All memories deleted successfully',
                'deleted_count': deleted_count
            }), 200
        
        else:
            return jsonify({
                'error': 'Request must include conversation_id, session_id, or delete_all with confirm'
            }), 400
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete memory: {str(e)}'}), 500


# Skills and Settings API Endpoints

@app.route('/api/skills/status', methods=['GET'])
@require_auth
def get_skills_status():
    """
    Get status of all registered skills.
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
        {
            "skills": [
                {
                    "name": "web_search",
                    "description": "Search the web for information",
                    "status": "connected",
                    "last_execution": "2024-01-15T10:30:00Z",
                    "success_rate": 0.95
                }
            ],
            "count": 10
        }
    
    Status Codes:
        200: Success
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Get Brain instance to access skill registry
        brain = get_brain()
        
        # Check if brain has skill registry
        if not hasattr(brain, 'skill_registry') or brain.skill_registry is None:
            return jsonify({
                'skills': [],
                'count': 0,
                'message': 'Skill registry not initialized'
            }), 200
        
        # Get all registered skills
        skills = brain.skill_registry.list_skills()
        
        # Format skills for response
        skills_data = []
        for skill in skills:
            skill_info = {
                'name': skill.name,
                'description': skill.description,
                'status': 'connected',  # TODO: Implement actual health check
                'last_execution': None,  # TODO: Track execution times
                'success_rate': None  # TODO: Track success rates
            }
            skills_data.append(skill_info)
        
        return jsonify({
            'skills': skills_data,
            'count': len(skills_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve skills status: {str(e)}'}), 500


@app.route('/api/settings', methods=['GET'])
@require_auth
def get_settings():
    """
    Get current system settings.
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
        {
            "voice_enabled": true,
            "wake_word": "Hey Jarvis",
            "llm_model": "claude-sonnet-4-20250514",
            "dashboard_port": 3000,
            "log_level": "INFO",
            "timezone": "UTC"
        }
    
    Status Codes:
        200: Success
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Get Memory System to retrieve user profile
        memory_system = get_memory_system()
        profile = memory_system.get_personal_profile(request.user_id)
        
        # Build settings response from config and profile
        settings = {
            'voice_enabled': config.voice_enabled,
            'wake_word': config.wake_word,
            'llm_model': config.llm_model,
            'dashboard_port': config.dashboard_port,
            'log_level': config.log_level,
            'timezone': profile.timezone,
            'first_name': profile.first_name,
            'communication_style': profile.communication_style,
            'work_hours': profile.work_hours
        }
        
        return jsonify(settings), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve settings: {str(e)}'}), 500


@app.route('/api/settings', methods=['PUT'])
@require_auth
def update_settings():
    """
    Update system settings.
    
    Headers:
        Authorization: Bearer <token>
    
    Request Body:
        {
            "voice_enabled": true,
            "wake_word": "Hey Jarvis",
            "timezone": "America/Los_Angeles",
            "first_name": "John",
            "communication_style": "technical",
            "work_hours": {"start": "09:00", "end": "18:00"}
        }
    
    Response:
        {
            "success": true,
            "message": "Settings updated successfully",
            "updated_fields": ["timezone", "first_name"]
        }
    
    Status Codes:
        200: Success
        400: Invalid request body
        401: Unauthorized
        500: Internal server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Get Memory System instance
        memory_system = get_memory_system()
        
        # Separate profile fields from system config fields
        profile_fields = ['timezone', 'first_name', 'communication_style', 'work_hours', 'interests']
        profile_updates = {}
        config_updates = {}
        
        for key, value in data.items():
            if key in profile_fields:
                profile_updates[key] = value
            else:
                config_updates[key] = value
        
        updated_fields = []
        
        # Update profile fields in database
        if profile_updates:
            result = memory_system.client.table("personal_profile").update(
                profile_updates
            ).eq("user_id", request.user_id).execute()
            
            if result.data:
                updated_fields.extend(profile_updates.keys())
        
        # Note: Config updates (voice_enabled, wake_word, etc.) would require
        # restarting the application or implementing hot-reload
        # For now, we just acknowledge them
        if config_updates:
            updated_fields.extend(config_updates.keys())
        
        # Log settings update
        audit_logger = get_audit_logger(memory_system)
        audit_logger.log_settings_update(
            user_id=request.user_id,
            updated_fields=updated_fields,
            success=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully',
            'updated_fields': updated_fields
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update settings: {str(e)}'}), 500


# Audit Log API Endpoint

@app.route('/api/audit-log', methods=['GET'])
@require_auth
def get_audit_log():
    """
    Get audit log entries with pagination.
    
    Headers:
        Authorization: Bearer <token>
    
    Query Parameters:
        page: Page number (default: 1)
        limit: Entries per page (default: 50)
        action_type: Filter by action type (optional)
        success: Filter by success status (optional, true/false)
    
    Response:
        {
            "entries": [
                {
                    "id": "uuid",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "action_type": "conversation",
                    "user_id": "admin_user",
                    "details": {"message": "Hello JARVIS"},
                    "success": true
                }
            ],
            "page": 1,
            "limit": 50,
            "total": 150,
            "pages": 3
        }
    
    Status Codes:
        200: Success
        400: Invalid parameters
        401: Unauthorized
        500: Internal server error
    """
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        if page < 1:
            return jsonify({'error': 'Page must be >= 1'}), 400
        if limit < 1 or limit > 100:
            return jsonify({'error': 'Limit must be between 1 and 100'}), 400
        
        # Get filter parameters
        action_type = request.args.get('action_type')
        success_filter = request.args.get('success')
        
        # Get Memory System instance
        memory_system = get_memory_system()
        
        # Build query
        query = memory_system.client.table("audit_log").select("*")
        
        # Apply filters
        if action_type:
            query = query.eq("action_type", action_type)
        
        if success_filter is not None:
            success_bool = success_filter.lower() == 'true'
            query = query.eq("success", success_bool)
        
        # Get total count for pagination
        count_result = query.execute()
        total = len(count_result.data) if count_result.data else 0
        
        # Calculate pagination
        offset = (page - 1) * limit
        pages = (total + limit - 1) // limit  # Ceiling division
        
        # Get paginated results
        result = query.order("timestamp", desc=True).range(offset, offset + limit - 1).execute()
        
        # Format entries
        entries = []
        if result.data:
            for entry in result.data:
                entries.append({
                    'id': entry.get('id'),
                    'timestamp': entry.get('timestamp'),
                    'action_type': entry.get('action_type'),
                    'user_id': entry.get('user_id'),
                    'details': entry.get('details', {}),
                    'success': entry.get('success', True)
                })
        
        return jsonify({
            'entries': entries,
            'page': page,
            'limit': limit,
            'total': total,
            'pages': pages
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve audit log: {str(e)}'}), 500


# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    print('Client connected to WebSocket')
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    print('Client disconnected from WebSocket')


@socketio.on('join_session')
def handle_join_session(data):
    """
    Join a conversation session for real-time updates.
    
    Data:
        {
            "session_id": "session_123"
        }
    """
    session_id = data.get('session_id')
    if session_id:
        print(f'Client joined session: {session_id}')
        emit('session_joined', {'session_id': session_id})


# Error Handlers

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


# Main Entry Point

def run_server(host: str = '0.0.0.0', port: Optional[int] = None, debug: bool = False):
    """
    Start the Flask development server.
    
    Args:
        host: Host address to bind to (default: 0.0.0.0)
        port: Port number (default: from config.dashboard_port)
        debug: Enable debug mode (default: False)
    """
    if port is None:
        port = config.dashboard_port
    
    print(f"Starting JARVIS Dashboard Backend on {host}:{port}")
    print(f"Health check: http://{host}:{port}/api/health")
    print(f"Login endpoint: http://{host}:{port}/api/auth/login")
    
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_server(debug=True)
