from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, SystemUser, KnowledgeRule, AuditLog
from werkzeug.security import generate_password_hash
from functools import wraps
import json
import uuid

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator():
            flash('Administrator access required', 'danger')
            return redirect(url_for('diagnosis.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    user_count = SystemUser.query.count()
    active_users = SystemUser.query.filter_by(is_active=True).count()
    rule_count = KnowledgeRule.query.count()
    active_rules = KnowledgeRule.query.filter_by(is_active=True).count()
    
    recent_logs = AuditLog.query.order_by(AuditLog.log_timestamp.desc()).limit(20).all()
    
    return render_template('admin/panel.html',
                     user_count=user_count,
                     active_users=active_users,
                     rule_count=rule_count,
                     active_rules=active_rules,
                     recent_logs=recent_logs)

@admin_bp.route('/rules')
@login_required
@admin_required
def rules():
    all_rules = KnowledgeRule.query.all()
    return render_template('admin/rules.html', rules=all_rules)

@admin_bp.route('/rules/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_rule():
    if request.method == 'POST':
        rule_id = request.form.get('rule_id')
        condition_text = request.form.get('condition_text')
        condition_json = request.form.get('condition_json')
        outcome = request.form.get('outcome')
        confidence_wt = float(request.form.get('confidence_wt', 0.5))
        category = request.form.get('category')
        
        if KnowledgeRule.query.get(rule_id):
            flash(f'Rule {rule_id} already exists', 'danger')
            return redirect(url_for('admin.new_rule'))
        
        try:
            json.loads(condition_json)
        except json.JSONDecodeError:
            flash('Invalid JSON in conditions', 'danger')
            return redirect(url_for('admin.new_rule'))
        
        rule = KnowledgeRule(
            rule_id=rule_id,
            condition_text=condition_text,
            condition_json=condition_json,
            outcome=outcome,
            confidence_wt=confidence_wt,
            category=category,
            updated_by=current_user.user_id
        )
        db.session.add(rule)
        db.session.commit()
        
        flash(f'Rule {rule_id} created successfully', 'success')
        return redirect(url_for('admin.rules'))
    
    return render_template('admin/rules_new.html')

@admin_bp.route('/rules/<rule_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_rule(rule_id):
    rule = KnowledgeRule.query.get_or_404(rule_id)
    
    if request.method == 'POST':
        rule.condition_text = request.form.get('condition_text')
        rule.condition_json = request.form.get('condition_json')
        rule.outcome = request.form.get('outcome')
        rule.confidence_wt = float(request.form.get('confidence_wt', 0.5))
        rule.category = request.form.get('category')
        rule.updated_by = current_user.user_id
        
        try:
            json.loads(rule.condition_json)
        except json.JSONDecodeError:
            flash('Invalid JSON in conditions', 'danger')
            return redirect(url_for('admin.edit_rule', rule_id=rule_id))
        
        db.session.commit()
        
        from routes.diagnosis import refresh_hybrid_engine
        refresh_hybrid_engine()
        
        flash(f'Rule {rule_id} updated successfully', 'success')
        return redirect(url_for('admin.rules'))
    
    return render_template('admin/rules_edit.html', rule=rule)

@admin_bp.route('/rules/<rule_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_rule(rule_id):
    rule = KnowledgeRule.query.get_or_404(rule_id)
    rule.is_active = not rule.is_active
    rule.updated_by = current_user.user_id
    db.session.commit()
    
    from routes.diagnosis import refresh_hybrid_engine
    refresh_hybrid_engine()
    
    status = 'activated' if rule.is_active else 'deactivated'
    flash(f'Rule {rule_id} {status}', 'success')
    return redirect(url_for('admin.rules'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = SystemUser.query.all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        facility_id = request.form.get('facility_id')
        password = request.form.get('password')
        
        if SystemUser.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.new_user'))
        
        user = SystemUser(
            user_id=f"user-{uuid.uuid4().hex[:6]}",
            username=username,
            role=role,
            facility_id=facility_id
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {username} created successfully', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/users_new.html')

@admin_bp.route('/users/<user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = SystemUser.query.get_or_404(user_id)
    
    if user.user_id == current_user.user_id:
        flash('Cannot deactivate your own account', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} {status}', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/retrain', methods=['GET', 'POST'])
@login_required
@admin_required
def retrain():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(url_for('admin.retrain'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('admin.retrain'))
        
        if file and file.filename.endswith('.csv'):
            try:
                csv_path = '/tmp/zazah_retrain.csv'
                file.save(csv_path)
                flash('File uploaded. Retraining will be implemented.', 'success')
            except Exception as e:
                flash(f'Error processing file: {e}', 'danger')
        else:
            flash('Please upload a CSV file', 'danger')
        
        return redirect(url_for('admin.retrain'))
    
    return render_template('admin/retrain.html')

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    metrics_data = {}
    metrics_path = None
    
    from pathlib import Path
    data_dir = Path(__file__).parent.parent / 'data'
    metrics_path = data_dir / 'metrics.json'
    
    if metrics_path.exists():
        with open(metrics_path) as f:
            metrics_data = json.load(f)
    
    return render_template('admin/reports.html', metrics=metrics_data)