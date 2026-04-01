import csv
import io
from flask import Blueprint, render_template, Response
from backend.db import db
from datetime import datetime

reports_bp = Blueprint('reports_bp', __name__)

@reports_bp.route('/reports')
def reports():
    stats = {
        'total_members': db.fetch_one("SELECT COUNT(*) as count FROM members")['count'],
        'total_revenue': db.fetch_one("SELECT SUM(amount) as total FROM payments")['total'] or 0,
        'total_trainers': db.fetch_one("SELECT COUNT(*) as count FROM trainers")['count']
    }
    return render_template('reports.html', stats=stats)

@reports_bp.route('/export/<type>')
def export_csv(type):
    output = io.StringIO()
    writer = csv.writer(output)
    
    filename = f"aurafit_{type}_{datetime.now().strftime('%Y%m%d')}.csv"
    
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
