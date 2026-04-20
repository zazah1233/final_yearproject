from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import db, DiagnosticResult, PatientRecord
from sqlalchemy import desc

history_bp = Blueprint('history', __name__)

@history_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = DiagnosticResult.query.join(PatientRecord).filter(
        PatientRecord.created_by == current_user.user_id
    ).order_by(desc(DiagnosticResult.result_timestamp))
    
    results = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('history.html',
                     diagnoses=results.items,
                     pagination=results)

@history_bp.route('/<int:result_id>')
@login_required
def view(result_id):
    result = DiagnosticResult.query.get_or_404(result_id)
    
    if result.patient.created_by != current_user.user_id and not current_user.is_administrator():
        from flask import abort
        abort(403)
    
    return render_template('diagnosis/result.html', result=result)