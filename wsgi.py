#!/usr/bin/env python3
"""
WSGI Entry Point for Flask Application

This module serves as the production entry point for the Flask application.
It properly handles application initialization, error handling, and graceful shutdown.
"""

import os
import sys
import signal
from typing import Optional

# Add the application directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import create_app_with_middleware
from database import get_db
from views import register_error_handlers, register_auth_handlers, register_user_handlers
from api import register_api_handlers
import eventlet
import eventlet.wsgi
from logger import logger

# Global variables for application state
application: Optional[object] = None
socketio_app: Optional[object] = None

def create_application():
    """Create and configure the Flask application"""
    global application, socketio_app
    
    try:
        app, socketio = create_app_with_middleware()
        register_auth_handlers(app)
        register_user_handlers(app)
        register_api_handlers(app)
        # register_error_handlers(app)
        
        # Store references for cleanup
        application = app
        socketio_app = socketio
        
        logger.info("Application created successfully")
        return app, socketio
        
    except Exception as e:
        logger.critical(f"Failed to create application: {e}")
        raise

def cleanup_resources():
    """Clean up application resources"""
    try:
        if get_db():
            # Close database connections if applicable
            logger.info("Cleaning up database connections")
            get_db().close()
            
        logger.info("Resource cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    cleanup_resources()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Create the application for WSGI server
try:
    app, socketio = create_application()
    
    # Make the Flask app available to WSGI server
    application = app
    
except Exception as e:
    logger.critical(f"Failed to initialize WSGI application: {e}")
    sys.exit(1)

def run_development_server():
    """Run the development server"""
    try:
        logger.info("Starting development server...")
        socketio.run(
            app, 
            debug=True, 
            host="127.0.0.1", 
            port=5000,
            use_reloader=False  # Disable reloader in WSGI context
        )
    except Exception as e:
        logger.error(f"Development server error: {e}")
        cleanup_resources()
        raise

def run_production_server():
    """Run the production server with eventlet"""
    try:
        logger.info("Starting production server with eventlet...")
        # Patch eventlet for better performance
        eventlet.monkey_patch()
        
        # Create eventlet WSGI server
        listener = eventlet.listen(('0.0.0.0', int(os.getenv('PORT', 5000))))
        eventlet.wsgi.server(listener, app, log=logger)
        
    except Exception as e:
        logger.error(f"Production server error: {e}")
        cleanup_resources()
        raise

if __name__ == "__main__":
    try:
        # Determine environment
        env = os.getenv('FLASK_ENV', 'production')
        
        if env == 'development':
            run_development_server()
        else:
            run_production_server()
            
    except KeyboardInterrupt:
        logger.info("Server shutting down due to keyboard interrupt...")
        cleanup_resources()
    except Exception as e:
        logger.critical(f"Server startup failed: {e}")
        cleanup_resources()
        sys.exit(1)