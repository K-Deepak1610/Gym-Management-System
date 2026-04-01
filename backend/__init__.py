from flask import Flask, request, session, redirect, url_for, flash
from datetime import datetime

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = 'aurafit_enterprise_secret_v2'
    
    # Import Blueprints
    from backend.auth.routes import auth_bp
    from backend.settings.routes import settings_bp
    from backend.dashboard.routes import dashboard_bp
    from backend.members.routes import members_bp
    from backend.trainers.routes import trainers_bp
    from backend.attendance.routes import attendance_bp
    from backend.equipment.routes import equipment_bp
    from backend.payments.routes import payments_bp
    from backend.announcements.routes import announcements_bp
    from backend.reports.routes import reports_bp
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(trainers_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(announcements_bp)
    app.register_blueprint(reports_bp)
    
    @app.before_request
    def require_login():
        allowed_endpoints = ['auth_bp.login', 'static']
        if request.endpoint not in allowed_endpoints and 'user_id' not in session:
            # flash("Please sign in to access AuraFit OS.", "error")
            return redirect(url_for('auth_bp.login'))
            
    # Template Filter
    @app.template_filter('formatdate')
    def formatdate(value, fmt='%d %b, %Y'):
        if not value: return 'N/A'
        if isinstance(value, str):
            try:
                d = datetime.strptime(value.split(' ')[0], '%Y-%m-%d').date()
                return d.strftime(fmt)
            except ValueError:
                return value
        if hasattr(value, 'strftime'):
            return value.strftime(fmt)
        return value
        
    return app
