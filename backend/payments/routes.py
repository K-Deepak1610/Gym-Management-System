from flask import Blueprint, render_template, request, redirect, url_for, flash
from backend.db import db
from backend.utils import log_activity

payments_bp = Blueprint('payments_bp', __name__)

@payments_bp.route('/payments')
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

@payments_bp.route('/add_payment', methods=['POST'])
def add_payment():
    member_id = request.form.get('member_id')
    amount = request.form.get('amount')
    notes = request.form.get('notes')
    status = request.form.get('status', 'Paid')
    
    db.execute_query("INSERT INTO payments (member_id, amount, notes, status) VALUES (?, ?, ?, ?)", (member_id, amount, notes, status))
    flash("Payment recorded!", "success")
    return redirect(url_for('payments_bp.payments'))
