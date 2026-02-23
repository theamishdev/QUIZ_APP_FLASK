"""
Utility functions for the Quizify application
"""

import re
from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_username(username):
    """Validate username format (alphanumeric, underscore, hyphen)"""
    if len(username) < 3 or len(username) > 20:
        return False
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, username))

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

def role_required(role):
    """Decorator to require a specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def teacher_required(f):
    """Decorator to require teacher role"""
    return role_required('teacher')(f)

def student_required(f):
    """Decorator to require student role"""
    return role_required('student')(f)

def sanitize_string(text, max_length=1000):
    """Sanitize string input"""
    if not text:
        return ""
    # Remove leading/trailing whitespace
    text = text.strip()
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    return text
