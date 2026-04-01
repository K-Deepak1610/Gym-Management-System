from flask import Blueprint, render_template, request, flash, redirect, url_for
from backend.db import db
from backend.utils import log_activity

trainers_bp = Blueprint('trainers_bp', __name__)

@trainers_bp.route('/trainers')
def trainers():
    all_trainers = db.fetch_all("SELECT * FROM trainers ORDER BY id DESC")
    for trainer in all_trainers:
        trainer['assigned_members'] = db.fetch_all("SELECT name FROM members WHERE trainer_id = ?", (trainer['id'],))
        trainer['experience'] = trainer.get('experience', 0) or 0
        trainer['salary'] = float(trainer.get('salary', 0) or 0)
    return render_template('trainers.html', trainers=all_trainers)

@trainers_bp.route('/add_trainer', methods=['POST'])
def add_trainer():
    name = request.form.get('name')
    spec = request.form.get('specialization')
    phone = request.form.get('phone')
    experience = request.form.get('experience', 0)
    salary = request.form.get('salary', 0)
    
    if not name:
        flash("Trainer Name is required!", "danger")
        return redirect(url_for('trainers_bp.trainers'))
        
    db.execute_query(
        "INSERT INTO trainers (name, specialization, phone, experience, salary) VALUES (?, ?, ?, ?, ?)",
        (name, spec, phone, experience, salary)
    )
    log_activity(f"Added new trainer: {name}")
    flash("Trainer added successfully!", "success")
    return redirect(url_for('trainers_bp.trainers'))

@trainers_bp.route('/edit_trainer/<int:id>', methods=['POST'])
def edit_trainer(id):
    name = request.form.get('name')
    spec = request.form.get('specialization')
    phone = request.form.get('phone')
    experience = request.form.get('experience', 0)
    salary = request.form.get('salary', 0)
    
    db.execute_query(
        "UPDATE trainers SET name=?, specialization=?, phone=?, experience=?, salary=? WHERE id=?",
        (name, spec, phone, experience, salary, id)
    )
    flash("Trainer updated successfully!", "success")
    return redirect(url_for('trainers_bp.trainers'))

@trainers_bp.route('/delete_trainer/<int:id>')
def delete_trainer(id):
    trainer = db.fetch_one("SELECT name FROM trainers WHERE id = ?", (id,))
    db.execute_query("DELETE FROM trainers WHERE id=?", (id,))
    if trainer:
        log_activity(f"Removed trainer: {trainer['name']}")
    flash("Trainer deleted successfully!", "success")
    return redirect(url_for('trainers_bp.trainers'))
