# ZAZAH — AGENT CODING GUIDE
## How to Build This Project: Step-by-Step Instructions for Your AI Coding Agent

---

## READ THIS FIRST

This is the **master instruction guide** for building the ZAZAH typhoid diagnosis expert system.  
All other files in this directory are supporting artefacts you will use.

**Files in this artefacts package:**
- `00_PROJECT_OVERVIEW.md` — Full requirements, architecture, DB schema, algorithms
- `AGENT_CODING_GUIDE.md` — THIS FILE — step-by-step build instructions
- `requirements.txt` — Python dependencies
- `ml_train.py` — ML training script (copy to `ml/train.py`)
- `seed_rules.py` — 47 knowledge base rules (copy to `data/seed_rules.py`)
- `inference_engine.py` — Expert system engine (copy to `engine/inference_engine.py`)
- `hybrid_module.py` — Hybrid decision module (copy to `engine/hybrid_module.py`)
- `UI_SPEC.md` — UI design spec

---

## STEP 1 — SET UP THE PROJECT STRUCTURE

Create this exact directory tree:

```
zazah/
├── app.py
├── config.py
├── requirements.txt          ← copy from artefacts
├── .env
├── models/
│   ├── __init__.py
│   ├── patient_record.py
│   ├── diagnostic_result.py
│   ├── knowledge_rule.py
│   ├── audit_log.py
│   └── system_user.py
├── engine/
│   ├── __init__.py
│   ├── preprocessor.py
│   ├── inference_engine.py   ← copy from artefacts
│   ├── rf_classifier.py
│   └── hybrid_module.py      ← copy from artefacts
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── diagnosis.py
│   ├── history.py
│   └── admin.py
├── ml/
│   └── train.py              ← copy ml_train.py from artefacts
├── data/
│   └── seed_rules.py         ← copy from artefacts
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── diagnosis/
    │   ├── new.html
    │   └── result.html
    ├── history.html
    └── admin/
        ├── panel.html
        ├── rules.html
        └── users.html
```

---

## STEP 2 — CONFIG AND APP SETUP

### `.env`
```
SECRET_KEY=zazah-dev-secret-2026-change-in-production
DATABASE_URL=sqlite:///zazah.db
FLASK_DEBUG=True
THRESHOLD_HIGH=0.65
THRESHOLD_LOW=0.45
```

### `config.py`
```python
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///zazah.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    THRESHOLD_HIGH = float(os.environ.get('THRESHOLD_HIGH', 0.65))
    THRESHOLD_LOW = float(os.environ.get('THRESHOLD_LOW', 0.45))
    RF_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'data', 'rf_model.joblib')
    DT_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'data', 'dt_model.joblib')
    PREPROCESSOR_PATH = os.path.join(os.path.dirname(__file__), 'data', 'preprocessor.joblib')
    FEATURE_IMPORTANCES_PATH = os.path.join(os.path.dirname(__file__), 'data', 'feature_importances.joblib')
    EVAL_METRICS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'eval_metrics.joblib')
```

### `app.py` (key parts)
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import joblib, os

db = SQLAlchemy()
login_manager = LoginManager()

# Global model objects (loaded once at startup)
rf_model = None
dt_model = None
preprocessor_artefact = None
feature_importances = None
eval_metrics = None

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        # Import models
        from models.system_user import SystemUser
        from models.patient_record import PatientRecord
        from models.diagnostic_result import DiagnosticResult
        from models.knowledge_rule import KnowledgeRule
        from models.audit_log import AuditLog

        # Create tables
        db.create_all()

        # Seed rules if empty
        from data.seed_rules import seed_rules
        seed_rules(db.session, KnowledgeRule)

        # Seed admin user if empty
        _seed_admin_user(SystemUser)

        # Load ML models
        _load_models(app)

        # Register blueprints
        from routes.auth import auth_bp
        from routes.diagnosis import diagnosis_bp
        from routes.history import history_bp
        from routes.admin import admin_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(diagnosis_bp)
        app.register_blueprint(history_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app


def _seed_admin_user(SystemUser):
    from werkzeug.security import generate_password_hash
    from datetime import date
    if SystemUser.query.count() == 0:
        admin = SystemUser(
            user_id='admin-001',
            username='admin',
            password_hash=generate_password_hash('Admin@2026'),
            role='administrator',
            facility_id='VERITAS-001',
            created_date=date.today(),
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("[SEED] Default admin user created: admin / Admin@2026")


def _load_models(app):
    global rf_model, dt_model, preprocessor_artefact, feature_importances, eval_metrics
    try:
        rf_model = joblib.load(app.config['RF_MODEL_PATH'])
        dt_model = joblib.load(app.config['DT_MODEL_PATH'])
        preprocessor_artefact = joblib.load(app.config['PREPROCESSOR_PATH'])
        feature_importances = joblib.load(app.config['FEATURE_IMPORTANCES_PATH'])
        eval_metrics = joblib.load(app.config['EVAL_METRICS_PATH'])
        print("[OK] ML models loaded successfully")
    except FileNotFoundError:
        print("[WARNING] ML model files not found. Run: python ml/train.py")
        rf_model = None


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
```

---

## STEP 3 — SQLALCHEMY MODELS

Build all 5 models matching the schema in `00_PROJECT_OVERVIEW.md` Section 7.

Key notes:
- `system_users.user_id` is a VARCHAR (not auto-increment), generate with `str(uuid.uuid4())[:8]`
- `patient_records.case_id` is a VARCHAR like `CASE-20260420-001`
- `diagnostic_results.result_id` is auto-increment INTEGER
- `diagnostic_results.reasoning_trace` is stored as TEXT (JSON string)
- All timestamps use `datetime.utcnow`

### `models/system_user.py`
Must implement `flask_login.UserMixin` for Flask-Login.

---

## STEP 4 — ENGINE MODULES

### `engine/preprocessor.py`
```python
"""
Loads the preprocessor artefact and transforms a patient dict into
a numpy array ready for the RF model.
"""
import numpy as np
import json

WIDAL_ORDER = ['Negative', '1:20', '1:40', '1:80', '1:160', '1:320', '>=1:640']
FEVER_PATTERN_CATS = ['Step-ladder', 'Continuous', 'Remittent', 'Intermittent']
SEX_CATS = ['Male', 'Female', 'Other']
CONTINUOUS_COLS = ['age', 'fever_duration', 'leukocyte_count', 'platelet_count',
                   'neutrophil_pct', 'esr', 'haemoglobin', 'lymphocyte_pct',
                   'monocyte_pct', 'temperature']
BINARY_COLS = ['abdominal_pain', 'relative_bradycardia', 'hepatosplenomegaly',
               'diarrhoea', 'vomiting', 'rose_spots', 'nausea', 'constipation']


def transform_patient(patient_dict: dict, preprocessor_artefact: dict) -> np.ndarray:
    """
    Transforms a single patient dict into a scaled numpy array.
    Uses the fitted scaler from preprocessor_artefact.
    """
    scaler = preprocessor_artefact['scaler']

    # Build raw feature vector in same order as training
    features = []

    # Continuous
    for col in CONTINUOUS_COLS:
        features.append(float(patient_dict.get(col, 0) or 0))

    # Binary
    for col in BINARY_COLS:
        features.append(int(patient_dict.get(col, 0) or 0))

    # Widal titre (ordinal)
    widal_raw = patient_dict.get('widal_titre', 'Negative')
    features.append(WIDAL_ORDER.index(widal_raw) if widal_raw in WIDAL_ORDER else 0)

    # Headache severity (shift to 0-4)
    features.append(int(patient_dict.get('headache_severity', 1) or 1) - 1)

    # Sex one-hot
    sex_val = patient_dict.get('sex', 'Male')
    for cat in SEX_CATS:
        features.append(1 if sex_val == cat else 0)

    # Fever pattern one-hot
    fp_val = patient_dict.get('fever_pattern', 'Continuous')
    for cat in FEVER_PATTERN_CATS:
        features.append(1 if fp_val == cat else 0)

    X = np.array(features, dtype=float).reshape(1, -1)
    X_scaled = scaler.transform(X)
    return X_scaled
```

### `engine/rf_classifier.py`
```python
"""Thin wrapper around the RF model."""
import numpy as np

def get_rf_prediction(rf_model, X: np.ndarray) -> float:
    """Returns probability of positive class (class index 1)."""
    proba = rf_model.predict_proba(X)
    return float(proba[0][1])

def get_feature_importances(rf_model, feature_names: list) -> dict:
    """Returns sorted dict of feature: importance."""
    importances = dict(zip(feature_names, rf_model.feature_importances_))
    return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
```

Copy `inference_engine.py` and `hybrid_module.py` from artefacts.

---

## STEP 5 — ROUTES / BLUEPRINTS

### `routes/auth.py`
- GET `/login` → render login form
- POST `/login` → validate credentials, create session, log to audit_log, redirect to dashboard
- GET `/logout` → clear session, log to audit_log

### `routes/diagnosis.py`
**GET `/diagnosis/new`** → render the patient data entry form (22 fields)

**POST `/diagnosis/new`**:
1. Parse form data into patient_dict
2. Run `validate_patient_dict(patient_dict)` → if invalid, flash error and re-render
3. Create PatientRecord, save to DB
4. Load active rules from DB
5. Run `run_hybrid_diagnosis(patient_dict, rules, rf_model, preprocessor_artefact, feature_importances)`
6. Create DiagnosticResult, save to DB
7. Create AuditLog entry
8. Redirect to GET `/diagnosis/<result_id>`

**GET `/diagnosis/<result_id>`**:
- Load DiagnosticResult + PatientRecord from DB
- Render result.html

### `routes/history.py`
- GET `/history` → paginated list of this user's diagnoses (or all if admin)

### `routes/admin.py`
All routes require `role == 'administrator'`.
- GET `/admin` → panel with stats
- GET `/admin/rules` → list all rules, with toggle buttons
- GET/POST `/admin/rules/new` → add rule form
- GET/POST `/admin/rules/<rule_id>/edit` → edit rule
- POST `/admin/rules/<rule_id>/toggle` → activate/deactivate
- GET `/admin/users` → user list
- GET/POST `/admin/users/new` → create user
- POST `/admin/retrain` → accept CSV, retrain (call ml/train.py logic inline)
- GET `/admin/reports` → performance stats from eval_metrics.joblib

---

## STEP 6 — TEMPLATES (HTML/CSS)

See `UI_SPEC.md` for detailed design requirements.

Key template guidelines:
- `base.html`: sidebar nav, top bar with user name + logout, flash messages, main content block
- All pages use the same CSS design system (dark clinical theme)
- `diagnosis/new.html`: grouped form with sections for Demographics, Clinical Symptoms, Lab Values
- `diagnosis/result.html`: result card (POSITIVE/NEGATIVE badge), confidence meter, fired rules accordion, feature importance bar chart (Chart.js)
- `admin/rules.html`: table with all 47 rules, active toggle switch per row, edit/add buttons

---

## STEP 7 — TRAIN THE MODELS

After setting up the project, run:
```bash
cd zazah
python ml/train.py
```

This will:
1. Generate synthetic data matching the paper's statistics
2. Train Decision Tree and Random Forest
3. Save to `data/rf_model.joblib`, `data/dt_model.joblib`, `data/preprocessor.joblib`,
   `data/feature_importances.joblib`, `data/eval_metrics.joblib`

The app won't work without these files.

---

## STEP 8 — RUN AND TEST

```bash
cd zazah
pip install -r requirements.txt
python ml/train.py       # generates models
python app.py            # starts Flask on http://localhost:5000
```

**Default login:** `admin` / `Admin@2026`

**Smoke tests to perform:**
1. Login works
2. Navigate to New Diagnosis, fill in all fields, submit → see result
3. Fill in an obvious positive case (fever 12 days, WBC 2.8, platelets 80, relative bradycardia, hepatosplenomegaly) → should show POSITIVE via ExpertSystem
4. Fill in an obvious negative case (fever 1 day, WBC 14, neutrophils 82%) → should show NEGATIVE via ExpertSystem
5. Fill in an ambiguous case → should route to RandomForest
6. Check history page shows past diagnoses
7. Admin panel: view rules, toggle a rule inactive, confirm it no longer fires

---

## CRITICAL RULES FOR THE AGENT

1. **Never use `<form>` with Flask without CSRF** — use Flask-WTF or add `{{ form.hidden_tag() }}` / include `csrf_token` in POST forms.

2. **The inference engine uses RAW values** (not normalized). The RF classifier uses the NORMALIZED numpy array. Do NOT mix these up.

3. **The `reasoning_trace` column in diagnostic_results** stores JSON string of fired_rules list. Serialize before saving, deserialize before displaying.

4. **The disclaimer** "⚠️ This system is a clinical decision SUPPORT tool. All diagnoses must be reviewed by a qualified clinician." must appear on every result page.

5. **Protect all routes** with `@login_required`. Admin routes also check `current_user.role == 'administrator'`.

6. **Load models globally once** at app startup, not on every request. Use `app.config` or a global `g`-like store.

7. **The patient form's numeric fields** should accept empty input (for optional fields). Empty → None → handled by preprocessor as 0.

8. **Flash messages** should be categorized: `flash('message', 'success')` / `flash('message', 'danger')` / `flash('message', 'warning')`.

9. **Widal titre** is a dropdown, not a free-text field. Options: Negative, 1:20, 1:40, 1:80, 1:160, 1:320, >=1:640.

10. **Run `python ml/train.py` before `python app.py`** — document this clearly in README.md.

---

## DELIVERABLES CHECKLIST

When the build is complete, verify:
- [ ] `python ml/train.py` runs without error and produces 5 joblib files
- [ ] `python app.py` starts without error
- [ ] Login/logout works
- [ ] New diagnosis form submits and produces a result
- [ ] Result page shows: diagnosis, confidence %, route used, fired rules, feature chart
- [ ] History page shows past diagnoses
- [ ] Admin panel shows rules (all 47)
- [ ] Admin can toggle a rule active/inactive
- [ ] Admin can add a new rule
- [ ] Admin user management works
- [ ] Performance report page shows accuracy/F1/AUC from last training
- [ ] Disclaimer appears on result page
- [ ] Audit log is populated after each action
- [ ] No unhandled exceptions on happy path
