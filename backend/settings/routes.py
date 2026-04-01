from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from backend.db import db
from backend.utils import login_required, log_activity
from werkzeug.security import generate_password_hash

settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = db.fetch_one("SELECT * FROM users WHERE id = ?", (session.get('user_id'),))
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            email = request.form.get('email')
            db.execute_query("UPDATE users SET email = ? WHERE id = ?", (email, session['user_id']))
            flash("Profile updated successfully", "success")
            
        elif action == 'change_password':
            old = request.form.get('old_password')
            new = request.form.get('new_password')
            
            from werkzeug.security import check_password_hash
            if check_password_hash(user['password'], old):
                db.execute_query("UPDATE users SET password = ? WHERE id = ?", (generate_password_hash(new), session['user_id']))
                flash("Password secured successfully", "success")
            else:
                flash("Incorrect current password", "error")
                
        return redirect(url_for('settings_bp.settings'))
        
    return render_template('settings.html', user=user)
