from flask import Blueprint, render_template, request, redirect, url_for, flash
from backend.db import db
from backend.utils import log_activity

equipment_bp = Blueprint('equipment_bp', __name__)

@equipment_bp.route('/equipment')
def equipment():
    items = db.fetch_all("SELECT * FROM equipment ORDER BY name")
    return render_template('equipment.html', items=items)

@equipment_bp.route('/add_equipment', methods=['POST'])
def add_equipment():
    name = request.form.get('name')
    qty = request.form.get('quantity')
    cond = request.form.get('condition')
    maint = request.form.get('last_maintenance')
    
    db.execute_query("INSERT INTO equipment (name, quantity, gym_condition, last_maintenance) VALUES (?, ?, ?, ?)",
                     (name, qty, cond, maint))
    log_activity(f"Added new equipment: {name}")
    flash("Equipment added!", "success")
    return redirect(url_for('equipment_bp.equipment'))
