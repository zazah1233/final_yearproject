from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from models import db, PatientRecord, DiagnosticResult, KnowledgeRule, AuditLog
from engine import HybridModule
import uuid
import json
from datetime import datetime

diagnosis_bp = Blueprint('diagnosis', __name__)

hybrid_engine = None

def get_hybrid_engine():
    global hybrid_engine
    if hybrid_engine is None:
        rules = KnowledgeRule.query.filter_by(is_active=True).all()
        rules_data = [{'rule_id': r.rule_id, 'condition_json': r.condition_json, 
                     'outcome': r.outcome, 'confidence_wt': r.confidence_wt,
                     'category': r.category, 'is_active': r.is_active,
                     'condition_text': r.condition_text} for r in rules]
        hybrid_engine = HybridModule(rules=rules_data)
    return hybrid_engine

def refresh_hybrid_engine():
    global hybrid_engine
    hybrid_engine = None
    return get_hybrid_engine()

@diagnosis_bp.route('/')
@login_required
def index():
    return redirect(url_for('diagnosis.dashboard'))

@diagnosis_bp.route('/dashboard')
@login_required
def dashboard():
    engine = get_hybrid_engine()
    model_ready = engine.is_ready()
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    today_results = DiagnosticResult.query.filter(DiagnosticResult.result_timestamp >= today_start).all()
    today_count = len(today_results)
    today_positive = sum(1 for r in today_results if r.diagnosis == 'Typhoid Positive')
    today_positive_rate = (today_positive / today_count * 100) if today_count > 0 else 0
    
    recent = DiagnosticResult.query.order_by(DiagnosticResult.result_timestamp.desc()).limit(10).all()
    
    metrics_data = {}
    metrics_path = hybrid_engine.preprocessor.model_path.parent / 'metrics.json'
    if metrics_path.exists():
        with open(metrics_path) as f:
            metrics_data = json.load(f)
    
    model_accuracy = metrics_data.get('rf', {}).get('accuracy', 0) * 100 if metrics_data else 0
    model_auc = metrics_data.get('rf', {}).get('auc', 0) * 100 if metrics_data else 0
    
    return render_template('dashboard.html',
                     model_ready=model_ready,
                     today_count=today_count,
                     today_positive_rate=today_positive_rate,
                     model_accuracy=model_accuracy,
                     model_auc=model_auc,
                     recent_diagnoses=recent)

@diagnosis_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_diagnosis():
    if request.method == 'POST':
        case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        
        patient_data = {
            'case_id': case_id,
            'age': request.form.get('age'),
            'sex': request.form.get('sex'),
            'fever_duration': request.form.get('fever_duration'),
            'fever_pattern': request.form.get('fever_pattern'),
            'headache_severity': request.form.get('headache_severity'),
            'abdominal_pain': request.form.get('abdominal_pain'),
            'relative_bradycardia': request.form.get('relative_bradycardia'),
            'hepatosplenomegaly': request.form.get('hepatosplenomegaly'),
            'leukocyte_count': request.form.get('leukocyte_count'),
            'platelet_count': request.form.get('platelet_count'),
            'neutrophil_pct': request.form.get('neutrophil_pct'),
            'widal_titre': request.form.get('widal_titre'),
            'esr': request.form.get('esr'),
            'haemoglobin': request.form.get('haemoglobin'),
            'lymphocyte_pct': request.form.get('lymphocyte_pct'),
            'monocyte_pct': request.form.get('monocyte_pct'),
            'temperature': request.form.get('temperature'),
            'diarrhoea': request.form.get('diarrhoea'),
            'vomiting': request.form.get('vomiting'),
            'rose_spots': request.form.get('rose_spots'),
            'nausea': request.form.get('nausea'),
            'constipation': request.form.get('constipation'),
            'created_by': current_user.user_id
        }
        
        record = PatientRecord(**{k: v for k, v in patient_data.items() if v is not None})
        db.session.add(record)
        db.session.commit()
        
        engine = get_hybrid_engine()
        result = engine.diagnose(patient_data)
        
        db_result = DiagnosticResult(
            case_id=case_id,
            diagnosis=result.diagnosis,
            confidence_score=result.confidence_score,
            es_score=result.es_score,
            rf_probability=result.rf_probability,
            route_used=result.route,
            reasoning_trace=json.dumps(result.fired_rules)
        )
        db.session.add(db_result)
        
        log = AuditLog(
            result_id=db_result.result_id,
            user_id=current_user.user_id,
            action_type='DIAGNOSIS',
            ip_address=request.remote_addr,
            session_id=session.get('session_id')
        )
        db.session.add(log)
        db.session.commit()
        
        return redirect(url_for('diagnosis.result', result_id=db_result.result_id))
    
    return render_template('diagnosis/new.html')

@diagnosis_bp.route('/<int:result_id>')
@login_required
def result(result_id):
    result = DiagnosticResult.query.get_or_404(result_id)
    patient = PatientRecord.query.get(result.case_id)
    
    reasoning_trace = json.loads(result.reasoning_trace) if result.reasoning_trace else []
    
    feature_importances = {}
    engine = get_hybrid_engine()
    if engine.rf_classifier.is_loaded():
        feature_importances = engine.rf_classifier.get_feature_importances()
        top_10 = dict(list(feature_importances.items())[:10])
        feature_importances = top_10
    
    return render_template('diagnosis/result.html',
                     result=result,
                     patient=patient,
                     reasoning_trace=reasoning_trace,
                     feature_importances=feature_importances)