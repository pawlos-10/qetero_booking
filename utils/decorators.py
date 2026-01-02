"""
Custom decorators for route protection
"""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """
    Decorator to restrict access to admin users only
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def patient_required(f):
    """
    Decorator to restrict access to patient users only
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_admin():
            flash('Access denied. Patient access required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

