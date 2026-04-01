from flask import Blueprint, render_template, request, jsonify
from backend.db import db
from datetime import datetime
from backend.utils import log_activity, get_member_status
import traceback

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/dashboard_data')
def dashboard_data():
    try:
        today = datetime.now()
        month = today.month
        year = today.year
        
        collected_row = db.fetch_one("SELECT SUM(amount) as total FROM payments WHERE status = 'Paid' AND strftime('%m', payment_date) = ? AND strftime('%Y', payment_date) = ?", (f"{month:02d}", str(year)))
        collected = collected_row['total'] if collected_row and collected_row['total'] else 0
        
        pending_row = db.fetch_one("SELECT SUM(amount) as total FROM payments WHERE status = 'Pending' AND strftime('%m', payment_date) = ? AND strftime('%Y', payment_date) = ?", (f"{month:02d}", str(year)))
        pending = pending_row['total'] if pending_row and pending_row['total'] else 0
        
        mem_row = db.fetch_one("SELECT COUNT(*) as count FROM members")
        trn_row = db.fetch_one("SELECT COUNT(*) as count FROM trainers")
        
        stats = {
            'total_members': mem_row['count'] if mem_row else 0,
            'active_trainers': trn_row['count'] if trn_row else 0,
            'fee_collected': float(collected),
            'fee_pending': float(pending),
            'attendance_rate': 85
        }
        
        alerts = []
        members_alert = db.fetch_all("SELECT name, expiry_date FROM members")
        today_date = datetime.now().date()
        for m in members_alert:
            if m['expiry_date']:
                try:
                    exp_date = datetime.strptime(str(m['expiry_date']).split(' ')[0], '%Y-%m-%d').date()
                    days_diff = (exp_date - today_date).days
                    if days_diff < 0:
                        alerts.append({'title': 'EXPIRED RECORD', 'content': f"{m['name']}'s membership has officially expired.", 'type': 'expired'})
                    elif days_diff == 0:
                        alerts.append({'title': 'EXPIRING TODAY', 'content': f"{m['name']}'s access ends today.", 'type': 'soon'})
                    elif days_diff <= 7:
                        alerts.append({'title': f'EXPIRING IN {days_diff} DAYS', 'content': f"{m['name']}'s membership expires in {days_diff} days.", 'type': 'soon'})
                except ValueError:
                    pass
        
        if not alerts and not db.fetch_all("SELECT id FROM announcements LIMIT 1"):
            combined_announcements = []
        else:
            manual_announcements = db.fetch_all("SELECT title, content, strftime('%d %m, %H:%M', created_at) as time FROM announcements ORDER BY created_at DESC LIMIT 5")
            combined_announcements = []
            for a in alerts:
                combined_announcements.append({'title': a['title'], 'content': a['content'], 'time': 'System Alert', 'type': a['type']})
            for a in manual_announcements:
                combined_announcements.append({'title': a['title'], 'content': a['content'], 'time': a['time'], 'type': 'manual'})
        
        leaderboard = db.fetch_all("""
            SELECT m.name, COUNT(a.id) as visits 
            FROM members m 
            JOIN attendance a ON m.id = a.member_id 
            WHERE a.status = 'Present' 
            GROUP BY m.id 
            ORDER BY visits DESC LIMIT 5
        """)
        
        activities = db.fetch_all("SELECT action, strftime('%H:%M', created_at) as time FROM activity_log ORDER BY created_at DESC LIMIT 5")
        
        att_split = db.fetch_one("""
            SELECT 
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent
            FROM attendance WHERE attendance_date = date('now')
        """)
        
        return jsonify({
            "stats": stats,
            "announcements": combined_announcements,
            "leaderboard": leaderboard,
            "activities": activities,
            "att_split": {
                "present": att_split['present'] if att_split and att_split['present'] else 0,
                "absent": att_split['absent'] if att_split and att_split['absent'] else 0
            }
        })
    except Exception as e:
        return jsonify({"error": traceback.format_exc()}), 500

@dashboard_bp.route('/analytics_data')
def analytics_data():
    growth_query = "SELECT strftime('%m', join_date) as month_num, COUNT(*) as count FROM members WHERE strftime('%Y', join_date) = strftime('%Y', 'now') GROUP BY month_num"
    growth_results = db.fetch_all(growth_query)
    
    rev_query = "SELECT strftime('%m', payment_date) as month_num, SUM(amount) as total FROM payments WHERE status = 'Paid' AND strftime('%Y', payment_date) = strftime('%Y', 'now') GROUP BY month_num"
    rev_results = db.fetch_all(rev_query)
    
    att_query = "SELECT strftime('%m', attendance_date) as month_num, COUNT(*) as count FROM attendance WHERE status = 'Present' AND strftime('%Y', attendance_date) = strftime('%Y', 'now') GROUP BY month_num"
    att_results = db.fetch_all(att_query)
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    current_month = datetime.now().month
    display_months = months[:current_month]
    
    growth_map = {months[int(r['month_num'])-1]: r['count'] for r in growth_results if r['month_num']}
    rev_map = {months[int(r['month_num'])-1]: float(r['total']) for r in rev_results if r['month_num']}
    att_map = {months[int(r['month_num'])-1]: r['count'] for r in att_results if r['month_num']}
    
    return jsonify({
        "months": display_months,
        "member_growth": [growth_map.get(m, 0) for m in display_months],
        "revenue": [rev_map.get(m, 0) for m in display_months],
        "attendance": [att_map.get(m, 0) for m in display_months]
    })
