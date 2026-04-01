from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from backend.db import db

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard_bp.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash("Authentication successful. Welcome to AuraFit OS.", "success")
            return redirect(url_for('dashboard_bp.dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "error")
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out of your session securely.", "success")
    return redirect(url_for('auth_bp.login'))
