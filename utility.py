from functools import wraps
from flask import (
    Flask, request, redirect, make_response, jsonify, send_file
)
from typing import List, Dict, Any

from logger import logger
from database import get_user_from_session, get_db
from config import Config
import smtplib
from email.message import EmailMessage



def update_user_field(user_id: int, field: str, value: Any) -> bool:
    """Generic function to update user fields"""
    try:
        allowed_fields = ['username', 'email', 'password', 'is_mfa_enabled']
        if field not in allowed_fields:
            raise ValueError(f"Field {field} is not allowed to be updated")
        
        query = f"UPDATE users SET {field} = %s WHERE id = %s"
        result = get_db().execute_query(query, (value, user_id))
        
        if result:
            logger.info(f"Updated {field} for user {user_id}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Failed to update {field} for user {user_id}: {e}")
        return False


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def extract_params(f):
    """Decorator to extract JSON params and user data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = request.get_json(force=True) if request.is_json else {}
            return f(data, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {request.path}: {e}")
            return jsonify({"error": "An error occurred while processing your request."}), 500
    return decorated_function

def validate_input(data: Dict, required_fields: List[str]) -> tuple[bool, str]:
    """Validate required input fields"""
    if not isinstance(data, dict):
        return False, "Invalid data format"
    
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, ""

def sanitize_input(value: str, max_length: int = 255) -> str:
    """Sanitize user input"""
    if not isinstance(value, str):
        return str(value)
    return value.strip()[:max_length]

# =============================================================================
# EMAIL UTILITY 
# =============================================================================

def send_email(subject: str, body: str, to_email: str) -> bool:
    """Send an email using SMTP with proper error handling"""
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = Config.SMTP_EMAIL
        msg['To'] = to_email

        # Set content
        msg.set_content("This email requires an HTML-compatible client.")
        msg.add_alternative(body, subtype='html')

        # Choose connection method based on configuration
        if Config.SMTP_USE_TLS:
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_EMAIL, Config.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.login(Config.SMTP_EMAIL, Config.SMTP_PASSWORD)
                server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

