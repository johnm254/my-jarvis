"""Dashboard module - Web interface for monitoring and control."""

from jarvis.dashboard.app import (
    app,
    generate_jwt_token,
    require_auth,
    run_server,
    socketio,
    validate_jwt_token,
)

__all__ = [
    'app',
    'socketio',
    'run_server',
    'generate_jwt_token',
    'validate_jwt_token',
    'require_auth',
]
