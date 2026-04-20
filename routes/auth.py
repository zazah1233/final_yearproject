from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, SystemUser, AuditLog
import uuid
from urllib.parse import urlparse, urljoin

auth_bp = Blueprint('auth', __name__)


def is_safe_redirect(target):
    if not target:
        return False
    host_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and host_url.netloc == test_url.netloc


def is_valid_csrf_token():
    return request.form.get('csrf_token') and request.form.get('csrf_token') == session.get('csrf_token')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('diagnosis.dashboard'))
    
    if request.method == 'POST':
        if not is_valid_csrf_token():
            flash('Invalid session token', 'danger')
            return render_template('login.html', next_page=request.form.get('next', request.args.get('next', '')))

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
        
        session.clear()
        login_user(user, remember=False)
        
        log = AuditLog(
            user_id=user.user_id,
            action_type='LOGIN',
            ip_address=request.remote_addr,
            session_id=session.get('session_id', str(uuid.uuid4()))
        )
        db.session.add(log)
        db.session.commit()
        
        session['session_id'] = log.session_id
        
        next_page = request.form.get('next') or request.args.get('next')
        if next_page and is_safe_redirect(next_page):
            return redirect(next_page)
        return redirect(url_for('diagnosis.dashboard'))
    
    return render_template('login.html', next_page=request.args.get('next', ''))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('diagnosis.dashboard'))

    if request.method == 'POST':
        if not is_valid_csrf_token():
            flash('Invalid session token', 'danger')
            return render_template('signup.html')

        username = request.form.get('username', '').strip()
        facility_id = request.form.get('facility_id', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not facility_id or not password:
            flash('Please complete all required fields', 'danger')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return render_template('signup.html')

        if SystemUser.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('signup.html')

        new_user = SystemUser(
            user_id=f"user-{uuid.uuid4().hex[:8]}",
            username=username,
            role='clinical_user',
            facility_id=facility_id,
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    if not is_valid_csrf_token():
        flash('Invalid session token', 'danger')
        return redirect(url_for('diagnosis.dashboard'))

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
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

def create_default_admin():
    """Create a bootstrap admin user only when credentials are provided."""
    import os

    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if not admin_username or not admin_password:
        return None

    admin = SystemUser.query.filter_by(username=admin_username).first()
    if admin is None:
        admin = SystemUser(
            user_id=f"admin-{uuid.uuid4().hex[:8]}",
            username=admin_username,
            role='administrator',
            facility_id='VUG-SEN-2026'
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"[AUTH] Created bootstrap admin user: {admin_username}")
    return admin