import secrets
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    flash, request, redirect, make_response, Response, jsonify, url_for
)
from typing import Any
from functools import wraps

from config import Config
from database import get_db, get_user_from_session
from logger import logger

# =============================================================================
# AUTHENTICATION & USER MANAGEMENT
# =============================================================================

def hash_password(password: str) -> str:
    """Hash a password using Werkzeug's secure method"""
    return generate_password_hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return check_password_hash(hashed, password)

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)

def generate_numeric_code(length: int = 6) -> str:
    """Generate a numeric code for 2FA"""
    return ''.join(secrets.choice('0123456789') for _ in range(length))

def create_session(user_id: int, valid: bool = True) -> str:
    """Create a new session for the user"""
    try:
        # Clean up old sessions
        get_db().execute_query("DELETE FROM sessions WHERE user_id = %s", (user_id,))
        
        # Create new session
        session_token = generate_secure_token()
        query = """
            INSERT INTO sessions(user_id, session_token, valid, last_active, created_at)
            VALUES (%s, %s, %s, NOW(), NOW())
        """
        get_db().execute_query(query, (user_id, session_token, valid))
        
        logger.info(f"Session created for user {user_id}")
        return session_token
        
    except Exception as e:
        logger.error(f"Failed to create session for user {user_id}: {e}")
        raise

def logout_user(message: str = "You have been logged out") -> Response:
    """Log out the user and clear session cookie"""
    session_cookie = request.cookies.get('session_cookie')
    
    if session_cookie:
        try:
            get_db().execute_query("DELETE FROM sessions WHERE session_token = %s", (session_cookie,))
            logger.info("Session deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
    
    response = make_response(redirect("/login"))
    response.set_cookie(
        'session_cookie', 
        '', 
        max_age=0, 
        httponly=Config.SESSION_COOKIE_HTTPONLY,
        secure=Config.SESSION_COOKIE_SECURE,
        samesite=Config.SESSION_COOKIE_SAMESITE
    )
    
    flash(message, 'error')
    return response

def check_toke(token):
    """Check if API token is valid"""
    if not token:
        return False
    
    try:
        result = get_db().execute_query(
            "SELECT id FROM user_api_keys WHERE api_key = %s AND active = 1", 
            (token,), 
            True
        )
        return bool(result)
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return False
    
# =============================================================================
# MIDDLEWARE
# =============================================================================

def require_auth(f):
    """Decorator for routes requiring authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_cookie = request.cookies.get('session_cookie')
        user_data = get_user_from_session(session_cookie)  
        if not session_cookie or not user_data:
            return logout_user("Please log in to access this page.") 

        if not user_data["valid"]:
            return redirect(url_for("mfa"))

        if user_data.get('inactive_minutes', 0) > Config.MAX_COOKIE_LIFETIME // 60:
            return logout_user("Session expired. Please log in again.")
        
        return f(*args, **kwargs)
    return decorated_function

def require_auth_api(f):
    """Decorator to extract JSON params and user data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            session_cookie = request.cookies.get("session_cookie")
            user = get_user_from_session(session_cookie)

            if not user:
                return jsonify({"success": False, "error": "Authentication required"}), 401

            return f(user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {request.path}: {e}")
            return jsonify({"error": "An error occurred while processing your request."}), 500
    return decorated_function

