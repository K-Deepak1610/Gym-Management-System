import csv
import io
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, Response
from backend.db import db
from datetime import datetime, timedelta
from backend.utils import log_activity, get_member_status

members_bp = Blueprint('members_bp', __name__)

@members_bp.route('/members')
def members():
    all_members = db.fetch_all("SELECT m.*, t.name as trainer_name FROM members m LEFT JOIN trainers t ON m.trainer_id = t.id ORDER BY m.id DESC")
    for m in all_members:
        new_status = get_member_status(m['expiry_date'])
        if m['status'] != new_status:
            db.execute_query("UPDATE members SET status = ? WHERE id = ?", (new_status, m['id']))
            m['status'] = new_status
            
    trainers_list = db.fetch_all("SELECT id, name FROM trainers")
    return render_template('members.html', members=all_members, trainers=trainers_list)

@members_bp.route('/add_member', methods=['POST'])
def add_member():
    name = request.form.get('name')
    age = request.form.get('age')
    phone = request.form.get('phone')
    plan = request.form.get('membership_plan')
    join_date = request.form.get('join_date')
    expiry_date = request.form.get('expiry_date')
    trainer_id = request.form.get('trainer_id')
    
    trainer_id = int(trainer_id) if trainer_id and trainer_id != 'None' else None
    
    db.execute_query(
        "INSERT INTO members (name, age, phone, membership_plan, join_date, expiry_date, trainer_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, age, phone, plan, join_date, expiry_date, trainer_id)
    )
    log_activity(f"Registered new member: {name}")
    flash("Member registered successfully!", "success")
    return redirect(url_for('members_bp.members'))

@members_bp.route('/renew_member', methods=['POST'])
def renew_member():
    member_id = request.form.get('member_id')
    plan = request.form.get('plan')
    amount = float(request.form.get('amount'))
    method = request.form.get('method')
    
    member = db.fetch_one("SELECT name, expiry_date FROM members WHERE id = ?", (member_id,))
    current_expiry_str = member['expiry_date']
    
    try:
        if current_expiry_str:
            current_expiry = datetime.strptime(str(current_expiry_str).split(' ')[0], '%Y-%m-%d').date()
        else:
            current_expiry = datetime.now().date()
    except ValueError:
        current_expiry = datetime.now().date()
        
    if current_expiry < datetime.now().date():
        current_expiry = datetime.now().date()
    
    if "Monthly" in plan: days = 30
    elif "Quarterly" in plan: days = 90
    elif "Yearly" in plan: days = 365
    else: days = 30
    
    new_expiry = current_expiry + timedelta(days=days)
    
    db.execute_query("UPDATE members SET expiry_date = ?, membership_plan = ?, status = 'Active' WHERE id = ?", 
                     (new_expiry, plan, member_id))
    
    db.execute_query("INSERT INTO payments (member_id, amount, payment_method, notes, status) VALUES (?, ?, ?, ?, ?)",
                     (member_id, amount, method, f"Renewal: {plan}", "Paid"))
    
    log_activity(f"Renewed membership for {member['name']} ({plan})")
    flash(f"Successfully renewed {member['name']} until {new_expiry}", "success")
    return redirect(url_for('members_bp.members'))

@members_bp.route('/member_profile/<int:id>')
def member_profile(id):
    member = db.fetch_one("SELECT m.*, t.name as trainer_name FROM members m LEFT JOIN trainers t ON m.trainer_id = t.id WHERE m.id = ?", (id,))
    payments = db.fetch_all("SELECT * FROM payments WHERE member_id = ? ORDER BY payment_date DESC", (id,))
    attendance = db.fetch_all("SELECT * FROM attendance WHERE member_id = ? ORDER BY attendance_date DESC LIMIT 30", (id,))
    return render_template('member_profile.html', member=member, payments=payments, attendance=attendance)

@members_bp.route('/edit_member/<int:id>', methods=['POST'])
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
        "UPDATE members SET name=?, age=?, phone=?, membership_plan=?, join_date=?, expiry_date=?, trainer_id=? WHERE id=?",
        (name, age, phone, plan, join_date, expiry_date, trainer_id, id)
    )
    flash("Member profile synchronized!", "success")
    return redirect(url_for('members_bp.members'))

@members_bp.route('/delete_member/<int:id>')
def delete_member(id):
    db.execute_query("DELETE FROM members WHERE id=?", (id,))
    flash("Member deleted successfully!", "success")
    return redirect(url_for('members_bp.members'))
