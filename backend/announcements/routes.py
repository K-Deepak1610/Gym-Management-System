from flask import Blueprint, render_template, request, flash, redirect, url_for
from backend.db import db
from backend.utils import log_activity

announcements_bp = Blueprint('announcements_bp', __name__)

@announcements_bp.route('/announcements')
def announcements():
    all_announcements = db.fetch_all("SELECT * FROM announcements ORDER BY created_at DESC")
    return render_template('announcements.html', announcements=all_announcements)

@announcements_bp.route('/add_announcement', methods=['POST'])
def add_announcement():
    title = request.form.get('title')
    content = request.form.get('content')
    
    db.execute_query("INSERT INTO announcements (title, content) VALUES (?, ?)", (title, content))
    log_activity(f"Posted announcement: {title}")
    flash("Announcement posted!", "success")
    return redirect(url_for('announcements_bp.announcements'))
