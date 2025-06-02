# Third-party libraries
from flask import (
    Flask, request, redirect, url_for
)

# from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO, emit, disconnect

from config import Config
from database import create_database_connection, get_user_from_session
from logger import logger

# =============================================================================
# FLASK APPLICATION SETUP
# =============================================================================

def create_app() -> tuple[Flask, SocketIO]:
    """Application factory pattern"""
    global db_connection
    
    # Validate configuration
    Config.validate()
    
    # Create Flask app
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)
    
    # Initialize extensions
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        async_mode='eventlet', 
        transports=['websocket'],
        logger=True,
        engineio_logger=True
    )
    
    # Initialize database
    try:
        db_connection = create_database_connection(Config)
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}")
        raise
    
    return app, socketio

def create_app_with_middleware():
    """Create app with middleware"""
    app, socketio = create_app()
    
    @app.before_request
    def check_session():
        """Check session validity before processing requests"""
        
        public_endpoints = {
            "login_or_register", "reset_password", 
            "forgot_password", "quarantine", "verify_email", "static"
        }
        
        session_cookie = request.cookies.get('session_cookie')
        user = get_user_from_session(session_cookie)    

        if session_cookie and request.endpoint in public_endpoints and request.endpoint !="static":
            if user:
                return redirect(url_for("index"))

        # Skip check for static files and WebSocket connections
        if (request.path.startswith('/static/') or 
            request.path.startswith('/ws/') or
            request.endpoint in public_endpoints):
            return None

    return app, socketio
