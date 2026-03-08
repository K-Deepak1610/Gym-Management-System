import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, Response
import csv
import io
from backend.db import db

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'titanfit_enterprise_secret'

# --- HELPERS ---
def log_activity(action, admin="Admin"):
    db.execute_query("INSERT INTO activity_log (action, admin_name) VALUES (%s, %s)", (action, admin))

def get_member_status(expiry_date):
    if not expiry_date: return "Expired"
    today = datetime.now().date()
    days_left = (expiry_date - today).days
    if days_left < 0: return "Expired"
    if days_left <= 7: return "Expiring Soon"
    return "Active"

# --- DASHBOARD ---
@app.route('/')
@app.route('/dashboard')
def dashboard():
    # Only pass constant or initial view data here. 
    # Real data will be fetched via AJAX for performance.
    return render_template('dashboard.html')

@app.route('/dashboard_data')
def dashboard_data():
    today = datetime.now()
    month = today.month
    year = today.year
    
    collected = db.fetch_one("SELECT SUM(amount) as total FROM payments WHERE status = 'Paid' AND MONTH(payment_date) = %s AND YEAR(payment_date) = %s", (month, year))['total'] or 0
    pending = db.fetch_one("SELECT SUM(amount) as total FROM payments WHERE status = 'Pending' AND MONTH(payment_date) = %s AND YEAR(payment_date) = %s", (month, year))['total'] or 0
    
    stats = {
        'total_members': db.fetch_one("SELECT COUNT(*) as count FROM members")['count'],
        'active_trainers': db.fetch_one("SELECT COUNT(*) as count FROM trainers")['count'],
        'fee_collected': float(collected),
        'fee_pending': float(pending),
        'attendance_rate': 85 # Simulated for now
    }
    
    # Automated Business Intelligence Alerts
    alerts = []
    members_alert = db.fetch_all("SELECT name, expiry_date FROM members")
    today_date = datetime.now().date()
    for m in members_alert:
        if m['expiry_date']:
            days_diff = (m['expiry_date'] - today_date).days
            if days_diff < 0:
                alerts.append({'title': 'EXPIRED RECORD', 'content': f"{m['name']}'s membership has officially expired.", 'type': 'expired'})
            elif days_diff == 0:
                alerts.append({'title': 'EXPIRING TODAY', 'content': f"{m['name']}'s access ends today.", 'type': 'soon'})
            elif days_diff <= 7:
                alerts.append({'title': f'EXPIRING IN {days_diff} DAYS', 'content': f"{m['name']}'s membership expires in {days_diff} days.", 'type': 'soon'})
    
    if not alerts and not db.fetch_all("SELECT id FROM announcements LIMIT 1"):
        combined_announcements = [] # Will show "No announcements today" in frontend
    else:
        manual_announcements = db.fetch_all("SELECT title, content, DATE_FORMAT(created_at, '%%d %%b, %%H:%%i') as time FROM announcements ORDER BY created_at DESC LIMIT 5")
        combined_announcements = []
        for a in alerts:
            combined_announcements.append({'title': a['title'], 'content': a['content'], 'time': 'System Alert', 'type': a['type']})
        for a in manual_announcements:
            combined_announcements.append({'title': a['title'], 'content': a['content'], 'time': a['time'], 'type': 'manual'})
    
    # Leaderboard: Members with most attendance
    leaderboard = db.fetch_all("""
        SELECT m.name, COUNT(a.id) as visits 
        FROM members m 
        JOIN attendance a ON m.id = a.member_id 
        WHERE a.status = 'Present' 
        GROUP BY m.id 
        ORDER BY visits DESC LIMIT 5
    """)
    
    # Today's Activity Log
    activities = db.fetch_all("SELECT action, DATE_FORMAT(created_at, '%%H:%%i') as time FROM activity_log ORDER BY created_at DESC LIMIT 5")
    
    # Today's attendance split
    att_split = db.fetch_one("""
        SELECT 
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
            SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent
        FROM attendance WHERE attendance_date = CURRENT_DATE
    """)
    
    return jsonify({
        "stats": stats,
        "announcements": combined_announcements,
        "leaderboard": leaderboard,
        "activities": activities,
        "att_split": {
            "present": att_split['present'] or 0,
            "absent": att_split['absent'] or 0
        }
    })

@app.route('/analytics_data')
def analytics_data():
    # 1. Member Growth (Monthly)
    growth_query = "SELECT DATE_FORMAT(join_date, '%%b') as month, COUNT(*) as count FROM members WHERE YEAR(join_date) = YEAR(CURRENT_DATE) GROUP BY MONTH(join_date), month ORDER BY MONTH(join_date)"
    growth_results = db.fetch_all(growth_query)
    
    # 2. Revenue (Monthly)
    rev_query = "SELECT DATE_FORMAT(payment_date, '%%b') as month, SUM(amount) as total FROM payments WHERE status = 'Paid' AND YEAR(payment_date) = YEAR(CURRENT_DATE) GROUP BY MONTH(payment_date), month ORDER BY MONTH(payment_date)"
    rev_results = db.fetch_all(rev_query)
    
    # 3. Attendance (Monthly)
    att_query = "SELECT DATE_FORMAT(attendance_date, '%%b') as month, COUNT(*) as count FROM attendance WHERE status = 'Present' AND YEAR(attendance_date) = YEAR(CURRENT_DATE) GROUP BY MONTH(attendance_date), month ORDER BY MONTH(attendance_date)"
    att_results = db.fetch_all(att_query)
    
    # Syncing all to a standard month list
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    current_month = datetime.now().month
    display_months = months[:current_month]
    
    growth_map = {r['month']: r['count'] for r in growth_results}
    rev_map = {r['month']: float(r['total']) for r in rev_results}
    att_map = {r['month']: r['count'] for r in att_results}
    
    return jsonify({
        "months": display_months,
        "member_growth": [growth_map.get(m, 0) for m in display_months],
        "revenue": [rev_map.get(m, 0) for m in display_months],
        "attendance": [att_map.get(m, 0) for m in display_months]
    })

# --- MEMBER MANAGEMENT ---
@app.route('/members')
def members():
    all_members = db.fetch_all("SELECT m.*, t.name as trainer_name FROM members m LEFT JOIN trainers t ON m.trainer_id = t.id ORDER BY m.id DESC")
    # Refresh statuses on load
    for m in all_members:
        new_status = get_member_status(m['expiry_date'])
        if m['status'] != new_status:
            db.execute_query("UPDATE members SET status = %s WHERE id = %s", (new_status, m['id']))
            m['status'] = new_status
            
    trainers_list = db.fetch_all("SELECT id, name FROM trainers")
    return render_template('members.html', members=all_members, trainers=trainers_list)

@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form.get('name')
    age = request.form.get('age')
    phone = request.form.get('phone')
    plan = request.form.get('membership_plan')
    join_date = request.form.get('join_date')
    expiry_date = request.form.get('expiry_date')
    trainer_id = request.form.get('trainer_id')
    
    # Simple validation for trainer_id
    trainer_id = int(trainer_id) if trainer_id and trainer_id != 'None' else None
    
    db.execute_query(
        "INSERT INTO members (name, age, phone, membership_plan, join_date, expiry_date, trainer_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (name, age, phone, plan, join_date, expiry_date, trainer_id)
    )
    log_activity(f"Registered new member: {name}")
    flash("Member registered successfully!", "success")
    return redirect(url_for('members'))

@app.route('/renew_member', methods=['POST'])
def renew_member():
    member_id = request.form.get('member_id')
    plan = request.form.get('plan')
    amount = float(request.form.get('amount'))
    method = request.form.get('method')
    
    # Calculate new expiry
    member = db.fetch_one("SELECT name, expiry_date FROM members WHERE id = %s", (member_id,))
    current_expiry = member['expiry_date'] if member['expiry_date'] > datetime.now().date() else datetime.now().date()
    
    from datetime import timedelta
    if "Monthly" in plan: days = 30
    elif "Quarterly" in plan: days = 90
    elif "Yearly" in plan: days = 365
    else: days = 30
    
    new_expiry = current_expiry + timedelta(days=days)
    
    db.execute_query("UPDATE members SET expiry_date = %s, membership_plan = %s, status = 'Active' WHERE id = %s", 
                     (new_expiry, plan, member_id))
    
    # Log payment
    db.execute_query("INSERT INTO payments (member_id, amount, payment_method, notes, status) VALUES (%s, %s, %s, %s, %s)",
                     (member_id, amount, method, f"Renewal: {plan}", "Paid"))
    
    log_activity(f"Renewed membership for {member['name']} ({plan})")
    flash(f"Successfully renewed {member['name']} until {new_expiry}", "success")
    return redirect(url_for('members'))

@app.route('/member_profile/<int:id>')
def member_profile(id):
    member = db.fetch_one("SELECT m.*, t.name as trainer_name FROM members m LEFT JOIN trainers t ON m.trainer_id = t.id WHERE m.id = %s", (id,))
    payments = db.fetch_all("SELECT * FROM payments WHERE member_id = %s ORDER BY payment_date DESC", (id,))
    attendance = db.fetch_all("SELECT * FROM attendance WHERE member_id = %s ORDER BY attendance_date DESC LIMIT 30", (id,))
    return render_template('member_profile.html', member=member, payments=payments, attendance=attendance)

@app.route('/edit_member/<int:id>', methods=['POST'])
def edit_member(id):
    name = request.form.get('name')
    age = request.form.get('age')
    phone = request.form.get('phone')
    plan = request.form.get('membership_plan')
    join_date = request.form.get('join_date')
    expiry_date = request.form.get('expiry_date')
    trainer_id = request.form.get('trainer_id')
    
    trainer_id = int(trainer_id) if trainer_id and trainer_id != 'None' else None
    
    db.execute_query(
        "UPDATE members SET name=%s, age=%s, phone=%s, membership_plan=%s, join_date=%s, expiry_date=%s, trainer_id=%s WHERE id=%s",
        (name, age, phone, plan, join_date, expiry_date, trainer_id, id)
    )
    flash("Member profile synchronized!", "success")
    return redirect(url_for('members'))

@app.route('/delete_member/<int:id>')
def delete_member(id):
    db.execute_query("DELETE FROM members WHERE id=%s", (id,))
    flash("Member deleted successfully!", "success")
    return redirect(url_for('members'))

# --- TRAINER MANAGEMENT ---
@app.route('/trainers')
def trainers():
    all_trainers = db.fetch_all("SELECT * FROM trainers ORDER BY id DESC")
    # Fetch assigned members for each trainer
    for trainer in all_trainers:
        trainer['assigned_members'] = db.fetch_all("SELECT name FROM members WHERE trainer_id = %s", (trainer['id'],))
        # Ensure salary and experience are present (db.py handles schema but might be None for old records)
        trainer['experience'] = trainer.get('experience', 0) or 0
        trainer['salary'] = float(trainer.get('salary', 0) or 0)
    return render_template('trainers.html', trainers=all_trainers)

@app.route('/add_trainer', methods=['POST'])
def add_trainer():
    name = request.form.get('name')
    spec = request.form.get('specialization')
    phone = request.form.get('phone')
    experience = request.form.get('experience', 0)
    salary = request.form.get('salary', 0)
    
    if not name:
        flash("Trainer Name is required!", "danger")
        return redirect(url_for('trainers'))
        
    db.execute_query(
        "INSERT INTO trainers (name, specialization, phone, experience, salary) VALUES (%s, %s, %s, %s, %s)",
        (name, spec, phone, experience, salary)
    )
    log_activity(f"Added new trainer: {name}")
    flash("Trainer added successfully!", "success")
    return redirect(url_for('trainers'))

@app.route('/edit_trainer/<int:id>', methods=['POST'])
def edit_trainer(id):
    name = request.form.get('name')
    spec = request.form.get('specialization')
    phone = request.form.get('phone')
    experience = request.form.get('experience', 0)
    salary = request.form.get('salary', 0)
    
    db.execute_query(
        "UPDATE trainers SET name=%s, specialization=%s, phone=%s, experience=%s, salary=%s WHERE id=%s",
        (name, spec, phone, experience, salary, id)
    )
    flash("Trainer updated successfully!", "success")
    return redirect(url_for('trainers'))

@app.route('/delete_trainer/<int:id>')
def delete_trainer(id):
    trainer = db.fetch_one("SELECT name FROM trainers WHERE id = %s", (id,))
    db.execute_query("DELETE FROM trainers WHERE id=%s", (id,))
    if trainer:
        log_activity(f"Removed trainer: {trainer['name']}")
    flash("Trainer deleted successfully!", "success")
    return redirect(url_for('trainers'))

# --- ATTENDANCE SYSTEM ---
@app.route('/attendance')
def attendance():
    # Fetch all members to mark attendance for today
    members = db.fetch_all("SELECT id, name, membership_plan FROM members ORDER BY name")
    today = datetime.now().date()
    return render_template('attendance.html', members=members, today=today)

@app.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    data = request.json
    attendance_list = data.get('attendance', [])
    today = datetime.now().date()
    
    for entry in attendance_list:
        member_id = entry['member_id']
        status = entry['status']
        
        # Avoid duplicates for same member on same date
        existing = db.fetch_one("SELECT id FROM attendance WHERE member_id = %s AND attendance_date = %s", (member_id, today))
        if existing:
            db.execute_query("UPDATE attendance SET status = %s WHERE id = %s", (status, existing['id']))
        else:
            db.execute_query("INSERT INTO attendance (member_id, attendance_date, status) VALUES (%s, %s, %s)", (member_id, today, status))
    
    log_activity(f"Marked attendance for {len(attendance_list)} members")
    return jsonify({"success": True, "message": "Attendance submitted successfully!"})

# --- EQUIPMENT MANAGEMENT ---
@app.route('/equipment')
def equipment():
    items = db.fetch_all("SELECT * FROM equipment ORDER BY name")
    return render_template('equipment.html', items=items)

@app.route('/add_equipment', methods=['POST'])
def add_equipment():
    name = request.form.get('name')
    qty = request.form.get('quantity')
    cond = request.form.get('condition')
    maint = request.form.get('last_maintenance')
    
    db.execute_query("INSERT INTO equipment (name, quantity, gym_condition, last_maintenance) VALUES (%s, %s, %s, %s)",
                     (name, qty, cond, maint))
    log_activity(f"Added new equipment: {name}")
    flash("Equipment added!", "success")
    return redirect(url_for('equipment'))

# --- REPORTS ---
@app.route('/reports')
def reports():
    # Fetch some summary data for the reports page
    stats = {
        'total_members': db.fetch_one("SELECT COUNT(*) as count FROM members")['count'],
        'total_revenue': db.fetch_one("SELECT SUM(amount) as total FROM payments")['total'] or 0,
        'total_trainers': db.fetch_one("SELECT COUNT(*) as count FROM trainers")['count']
    }
    return render_template('reports.html', stats=stats)

# --- EXPORT REPORTS ---
@app.route('/export/<type>')
def export_csv(type):
    output = io.StringIO()
    writer = csv.writer(output)
    
    filename = f"titanfit_{type}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    if type == 'members':
        data = db.fetch_all("SELECT name, phone, membership_plan, status, expiry_date FROM members")
        writer.writerow(['Name', 'Phone', 'Plan', 'Status', 'Expiry Date'])
        for row in data:
            writer.writerow([row['name'], row['phone'], row['membership_plan'], row['status'], row['expiry_date']])
    elif type == 'payments':
        data = db.fetch_all("SELECT m.name, p.amount, p.payment_method, p.payment_date FROM payments p JOIN members m ON p.member_id = m.id")
        writer.writerow(['Member', 'Amount', 'Method', 'Date'])
        for row in data:
            writer.writerow([row['name'], row['amount'], row['payment_method'], row['payment_date']])
    elif type == 'attendance':
        data = db.fetch_all("SELECT m.name, a.attendance_date, a.status FROM attendance a JOIN members m ON a.member_id = m.id ORDER BY a.attendance_date DESC")
        writer.writerow(['Member', 'Date', 'Status'])
        for row in data:
            writer.writerow([row['name'], row['attendance_date'], row['status']])
            
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

# --- PAYMENTS ---
@app.route('/payments')
def payments():
    query = """
        SELECT p.*, m.name as member_name 
        FROM payments p 
        JOIN members m ON p.member_id = m.id 
        ORDER BY p.payment_date DESC
    """
    all_payments = db.fetch_all(query)
    
    paid_total = db.fetch_one("SELECT SUM(amount) as total FROM payments WHERE status = 'Paid'")['total'] or 0
    pending_total = db.fetch_one("SELECT SUM(amount) as total FROM payments WHERE status = 'Pending'")['total'] or 0
    
    return render_template('payments.html', 
                          payments=all_payments, 
                          paid_total=float(paid_total), 
                          pending_total=float(pending_total),
                          members=db.fetch_all("SELECT id, name FROM members"))

@app.route('/add_payment', methods=['POST'])
def add_payment():
    member_id = request.form.get('member_id')
    amount = request.form.get('amount')
    notes = request.form.get('notes')
    status = request.form.get('status', 'Paid')
    
    db.execute_query("INSERT INTO payments (member_id, amount, notes, status) VALUES (%s, %s, %s, %s)", (member_id, amount, notes, status))
    flash("Payment recorded!", "success")
    return redirect(url_for('payments'))

# --- ANNOUNCEMENTS ---
@app.route('/announcements')
def announcements():
    all_announcements = db.fetch_all("SELECT * FROM announcements ORDER BY created_at DESC")
    return render_template('announcements.html', announcements=all_announcements)

@app.route('/add_announcement', methods=['POST'])
def add_announcement():
    title = request.form.get('title')
    content = request.form.get('content')
    
    db.execute_query("INSERT INTO announcements (title, content) VALUES (%s, %s)", (title, content))
    log_activity(f"Posted announcement: {title}")
    flash("Announcement posted!", "success")
    return redirect(url_for('announcements'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
