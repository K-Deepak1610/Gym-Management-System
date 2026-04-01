from functools import wraps
from flask import session, redirect, url_for, flash
from backend.db import db
from datetime import datetime

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(action, admin="System"):
    db.execute_query("INSERT INTO activity_log (action, admin_name) VALUES (?, ?)", (action, admin))

def get_member_status(expiry_date_str):
    if not expiry_date_str: return "Expired"
    today = datetime.now().date()
    
    try:
        expiry_date = datetime.strptime(str(expiry_date_str).split(' ')[0], '%Y-%m-%d').date()
    except ValueError:
        return "Expired"
        
    days_left = (expiry_date - today).days
    if days_left < 0: return "Expired"
    if days_left <= 7: return "Expiring Soon"
    return "Active"
