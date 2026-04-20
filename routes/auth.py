from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, SystemUser, AuditLog
from datetime import datetime
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('diagnosis.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter username and password', 'danger')
            return render_template('login.html')
        
        user = SystemUser.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated', 'danger')
            return render_template('login.html')
        
        login_user(user, remember=True)
        
        log = AuditLog(
            user_id=user.user_id,
            action_type='LOGIN',
            ip_address=request.remote_addr,
            session_id=session.get('session_id', str(uuid.uuid4()))
        )
        db.session.add(log)
        db.session.commit()
        
        session['session_id'] = log.session_id
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('diagnosis.dashboard'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    user_id = current_user.user_id
    session_id = session.get('session_id')
    
    log = AuditLog(
        user_id=user_id,
        action_type='LOGOUT',
        ip_address=request.remote_addr,
        session_id=session_id
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

def create_default_admin():
    """Create default admin user if not exists."""
    admin = SystemUser.query.filter_by(username='admin').first()
    if admin is None:
        admin = SystemUser(
            user_id='admin-001',
            username='admin',
            role='administrator',
            facility_id='VUG-SEN-2026'
        )
        admin.set_password('Admin@2026')
        db.session.add(admin)
        db.session.commit()
        print("[AUTH] Created default admin user: admin / Admin@2026")
    return admin