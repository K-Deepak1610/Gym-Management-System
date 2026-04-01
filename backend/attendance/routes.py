from flask import Blueprint, render_template, request, jsonify
from backend.db import db
from datetime import datetime
from backend.utils import log_activity

attendance_bp = Blueprint('attendance_bp', __name__)

@attendance_bp.route('/attendance')
def attendance():
    members = db.fetch_all("SELECT id, name, membership_plan FROM members ORDER BY name")
    today = datetime.now().date()
    return render_template('attendance.html', members=members, today=today)

@attendance_bp.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    data = request.json
    attendance_list = data.get('attendance', [])
    today = datetime.now().date()
    
    for entry in attendance_list:
        member_id = entry['member_id']
        status = entry['status']
        
        existing = db.fetch_one("SELECT id FROM attendance WHERE member_id = ? AND attendance_date = ?", (member_id, today))
        if existing:
            db.execute_query("UPDATE attendance SET status = ? WHERE id = ?", (status, existing['id']))
        else:
            db.execute_query("INSERT INTO attendance (member_id, attendance_date, status) VALUES (?, ?, ?)", (member_id, today, status))
    
    log_activity(f"Marked attendance for {len(attendance_list)} members")
    return jsonify({"success": True, "message": "Attendance submitted successfully!"})
