# ZAZAH — AI-Enhanced Expert System for Typhoid Fever Diagnosis
## Master Project Specification for Agent Coding

> Source: BSc Software Engineering Final Year Project by Victor Hassan (VUG/SEN/22/7856), Veritas University, March 2026.
> This document is the authoritative spec. Build exactly what is described here — no extras, no shortcuts.

---

## 1. What We Are Building

A **web-based clinical decision support system** that helps Nigerian healthcare workers (doctors, nurses, clinical officers) diagnose typhoid fever. It combines:

1. A **rule-based expert system** (47 IF-THEN rules, forward chaining)
2. A **Random Forest ML classifier** (200 trees, trained on 487 patient records)
3. A **hybrid decision module** — expert system runs first; uncertain cases are escalated to ML

The system is NOT a replacement for clinical judgment. It is a decision *support* tool.

---

## 2. Actors / Users

| Actor | Role | Key Actions |
|---|---|---|
| **Clinical User** | Doctor, nurse, or clinical officer | Enter patient data, request diagnosis, view results, view feature importance |
| **System Administrator** | IT admin or research lead | Manage knowledge base rules, retrain model, generate performance reports, manage users |

---

## 3. Core Functional Requirements

### 3.1 Patient Data Entry
- Form accepts 22 clinical/lab features per patient (see Feature List below)
- Validates completeness — rejects if >4 features missing
- Validates physiological ranges for numeric fields
- Saves to SQLite database with anonymous case_id

### 3.2 Hybrid Diagnostic Engine
- **Step 1:** Preprocess input (encode categoricals, normalize numerics to [0,1])
- **Step 2:** Run forward-chaining expert system inference (47 rules, sum confidence weights)
  - Score > 0.65 → Typhoid POSITIVE (expert system)
  - Score < 0.45 → Typhoid NEGATIVE (expert system)
  - Score 0.45–0.65 → uncertain → escalate to Random Forest
- **Step 3 (if uncertain):** Random Forest predict_proba() ≥ 0.50 → POSITIVE, else NEGATIVE
- **Output:** diagnosis, confidence score, reasoning trace (which rules fired), feature importances, route used (ExpertSystem or RandomForest)

### 3.3 Results Display
- Diagnosis (POSITIVE / NEGATIVE)
- Confidence score (0–100%)
- Which rules fired (reasoning trace)
- Top 10 feature importances (bar chart)
- Route used
- Timestamp, patient case ID

### 3.4 Audit & Logging
- Every diagnostic action logged with user_id, result_id, timestamp, IP, session_id
- Logs accessible to administrator only

### 3.5 Administrator Panel
- CRUD on knowledge base rules (add, edit, deactivate rules)
- Trigger model retraining (on new data upload)
- View system performance stats (accuracy, F1, AUC from last evaluation)
- Export performance reports
- User management (create/deactivate clinical users)

### 3.6 User Authentication
- Login/logout with role-based access (clinical_user, administrator)
- Session management
- Audit trail of all logins

---

## 4. Feature List (22 Input Variables)

| # | Feature | Type | Encoding | Validation Range |
|---|---|---|---|---|
| 1 | Age | Continuous (int) | Min-Max normalize | 0–120 |
| 2 | Sex | Categorical | One-hot (Male/Female/Other) | Required |
| 3 | Fever Duration (days) | Continuous (float) | Min-Max normalize | 0–60 |
| 4 | Fever Pattern | Categorical | One-hot (Continuous/Step-ladder/Remittent/Intermittent) | Required |
| 5 | Headache Severity | Ordinal (1–5) | Label encode 1–5 | 1–5 |
| 6 | Abdominal Pain | Binary | 0/1 | 0 or 1 |
| 7 | Relative Bradycardia | Binary | 0/1 | 0 or 1 |
| 8 | Hepatosplenomegaly | Binary | 0/1 | 0 or 1 |
| 9 | Total Leukocyte Count (×10⁹/L) | Continuous (float) | Min-Max normalize | 0.5–50 |
| 10 | Platelet Count (×10⁹/L) | Continuous (float) | Min-Max normalize | 10–1000 |
| 11 | Neutrophil Percentage (%) | Continuous (float) | Min-Max normalize | 0–100 |
| 12 | Widal O-Antigen Titre | Ordinal | Label encode (Negative/1:20/1:40/1:80/1:160/1:320/≥1:640) | Required |
| 13 | ESR (mm/hr) | Continuous (float) | Min-Max normalize | 0–150 |
| 14 | Haemoglobin (g/dL) | Continuous (float) | Min-Max normalize | 3–25 |
| 15 | Lymphocyte Percentage (%) | Continuous (float) | Min-Max normalize | 0–100 |
| 16 | Monocyte Percentage (%) | Continuous (float) | Min-Max normalize | 0–30 |
| 17 | Temperature at Presentation (°C) | Continuous (float) | Min-Max normalize | 35–42 |
| 18 | Diarrhoea | Binary | 0/1 | 0 or 1 |
| 19 | Vomiting | Binary | 0/1 | 0 or 1 |
| 20 | Rose Spots | Binary | 0/1 | 0 or 1 |
| 21 | Nausea | Binary | 0/1 | 0 or 1 |
| 22 | Constipation | Binary | 0/1 | 0 or 1 |

---

## 5. Expert System Knowledge Base (47 Rules)

### Typhoid POSITIVE Rules (18)
| Rule ID | Conditions | Outcome | Confidence |
|---|---|---|---|
| R-001 | Fever Duration > 7 AND Leukocyte Count < 4.5 | POSITIVE | 0.82 |
| R-002 | Relative Bradycardia = 1 AND Hepatosplenomegaly = 1 | POSITIVE | 0.78 |
| R-003 (sic, should be positive) | Fever Duration > 7 AND Fever Pattern = Step-ladder | POSITIVE | 0.76 |
| R-004 | Leukocyte Count < 4.0 AND Neutrophil % < 40 | POSITIVE | 0.75 |
| R-005 | Platelet Count < 100 AND Leukocyte Count < 5.0 | POSITIVE | 0.74 |
| R-006 | Widal O-titre ≥ 1:160 AND Fever Duration > 5 | POSITIVE | 0.71 |
| R-007 | Hepatosplenomegaly = 1 AND Fever Duration > 7 | POSITIVE | 0.70 |
| R-008 | Rose Spots = 1 AND Fever Duration > 5 | POSITIVE | 0.85 |
| R-009 | Relative Bradycardia = 1 AND Fever Duration > 7 | POSITIVE | 0.79 |
| R-010 | Leukocyte Count < 3.5 AND Platelet Count < 120 | POSITIVE | 0.80 |
| R-011 | Temperature > 39.5 AND Fever Duration > 7 AND Leukocyte Count < 5 | POSITIVE | 0.77 |
| R-012 | Hepatosplenomegaly = 1 AND Abdominal Pain = 1 AND Fever Duration > 5 | POSITIVE | 0.73 |
| R-013 | Neutrophil % < 35 AND Lymphocyte % > 40 | POSITIVE | 0.69 |
| R-014 | Widal O-titre ≥ 1:320 AND Fever Duration > 3 | POSITIVE | 0.74 |
| R-015 | Fever Pattern = Step-ladder AND Relative Bradycardia = 1 | POSITIVE | 0.76 |
| R-016 | Platelet Count < 80 AND Haemoglobin < 11 | POSITIVE | 0.72 |
| R-017 | Abdominal Pain = 1 AND Constipation = 1 AND Fever Duration > 5 | POSITIVE | 0.68 |
| R-018 | ESR > 50 AND Leukocyte Count < 5 AND Fever Duration > 7 | POSITIVE | 0.71 |

### Typhoid NEGATIVE Rules (15)
| Rule ID | Conditions | Outcome | Confidence |
|---|---|---|---|
| R-019 | Fever Duration < 4 AND Leukocyte Count > 11 | NEGATIVE | 0.80 |
| R-020 | Leukocyte Count > 12 AND Neutrophil % > 75 | NEGATIVE | 0.82 |
| R-021 | Fever Duration < 3 AND Temperature < 38.5 | NEGATIVE | 0.78 |
| R-022 | Widal O-titre = Negative AND Leukocyte Count > 10 | NEGATIVE | 0.75 |
| R-023 | Platelet Count > 300 AND Leukocyte Count > 10 | NEGATIVE | 0.76 |
| R-024 | Fever Duration < 4 AND Hepatosplenomegaly = 0 AND Relative Bradycardia = 0 | NEGATIVE | 0.72 |
| R-025 | Neutrophil % > 80 AND Fever Duration < 5 | NEGATIVE | 0.77 |
| R-026 | Leukocyte Count > 15 | NEGATIVE | 0.83 |
| R-027 | Rose Spots = 0 AND Relative Bradycardia = 0 AND Widal O-titre = Negative | NEGATIVE | 0.65 |
| R-028 | Fever Duration < 2 AND Vomiting = 1 AND Diarrhoea = 1 | NEGATIVE | 0.70 |
| R-029 | Temperature < 37.5 AND Fever Duration < 3 | NEGATIVE | 0.79 |
| R-030 | Leukocyte Count > 11 AND Platelet Count > 250 AND Neutrophil % > 70 | NEGATIVE | 0.81 |
| R-031 | Headache Severity < 2 AND Fever Duration < 3 AND Leukocyte Count > 9 | NEGATIVE | 0.68 |
| R-032 | Widal O-titre ≤ 1:40 AND Leukocyte Count > 9 AND Fever Duration < 5 | NEGATIVE | 0.69 |
| R-033 | Diarrhoea = 1 AND Vomiting = 1 AND Fever Duration < 3 AND Leukocyte Count > 10 | NEGATIVE | 0.71 |

### Intermediate State Rules (14)
| Rule ID | Conditions | Outcome | Confidence |
|---|---|---|---|
| R-034 | Platelet Count < 100 AND Neutrophil % < 40 | Haematological Suppression | 0.74 |
| R-035 | Abdominal Pain = 1 AND Hepatosplenomegaly = 1 | Enteric Fever Syndrome | 0.71 |
| R-036 | Leukocyte Count < 4.5 AND ESR > 40 | Haematological Suppression | 0.72 |
| R-037 | Fever Duration > 5 AND Abdominal Pain = 1 AND Nausea = 1 | Enteric Fever Syndrome | 0.69 |
| R-038 | Temperature > 39 AND Relative Bradycardia = 1 | Faget Sign Present | 0.80 |
| R-039 | Haemoglobin < 10 AND Platelet Count < 120 | Haematological Suppression | 0.73 |
| R-040 | Fever Pattern = Step-ladder AND Temperature > 38.5 | Enteric Fever Syndrome | 0.70 |
| R-041 | Hepatosplenomegaly = 1 AND ESR > 50 | Systemic Inflammatory Response | 0.68 |
| R-042 | Neutrophil % < 40 AND Lymphocyte % > 45 | Atypical Differential | 0.71 |
| R-043 | Widal O-titre ≥ 1:160 AND Widal H not specified | Seropositive Suspicious | 0.67 |
| R-044 | Rose Spots = 1 | Rose Spot Present | 0.88 |
| R-045 | Constipation = 1 AND Fever Duration > 5 | Enteric Fever Syndrome | 0.66 |
| R-046 | Relative Bradycardia = 1 | Faget Sign Present | 0.75 |
| R-047 | Leukocyte Count < 4.5 AND Platelet Count < 150 AND Haemoglobin < 12 | Haematological Suppression | 0.76 |

> **Intermediate rules:** If "Haematological Suppression" fires → add 0.12 to confidence. If "Enteric Fever Syndrome" fires → add 0.10. If "Faget Sign Present" fires → add 0.15. If "Rose Spot Present" fires → add 0.20. These feed into the positive confidence accumulation.

---

## 6. Architecture

### 6.1 Stack
| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web Framework | Flask 2.3 |
| ML Library | Scikit-learn 1.3 |
| Data | Pandas 2.0, NumPy 1.24 |
| Visualisation (backend charts) | Matplotlib 3.7, Seaborn 0.12 |
| Database | SQLite via SQLAlchemy 2.0 |
| Model Persistence | Joblib |
| Frontend | Jinja2 templates + HTML/CSS/Vanilla JS (or minimal Bootstrap 5) |
| Charts (frontend) | Chart.js (CDN) |
| Auth | Flask-Login + Werkzeug password hashing |
| Config | python-dotenv |

### 6.2 Three-Tier Architecture
```
PRESENTATION TIER
  Flask HTML/CSS/JS templates
  Pages: Login, Dashboard, New Diagnosis, Results, History, Admin Panel

APPLICATION TIER
  Preprocessing Module (encoder + scaler)
  Inference Engine (47 rules, forward chaining)
  Random Forest Classifier (200 trees, joblib-serialized)
  Hybrid Decision Module

DATA TIER
  SQLite DB (patient_records, diagnostic_results, knowledge_rules, audit_log, system_users)
  Serialized RF model file (rf_model.joblib)
  Serialized preprocessor file (preprocessor.joblib)
```

### 6.3 Directory Structure
```
zazah/
├── app.py                  # Flask entry point
├── config.py               # Configuration (DB URI, secret key, thresholds)
├── requirements.txt
├── .env                    # Secrets (not committed)
│
├── models/                 # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── patient_record.py
│   ├── diagnostic_result.py
│   ├── knowledge_rule.py
│   ├── audit_log.py
│   └── system_user.py
│
├── engine/                 # Core diagnostic logic
│   ├── __init__.py
│   ├── preprocessor.py     # Encoding + scaling pipeline
│   ├── inference_engine.py # Forward chaining expert system
│   ├── rf_classifier.py    # Random Forest wrapper
│   └── hybrid_module.py    # Combines ES + RF outputs
│
├── routes/                 # Flask blueprints
│   ├── __init__.py
│   ├── auth.py             # Login/logout
│   ├── diagnosis.py        # New diagnosis, results
│   ├── history.py          # Case history
│   └── admin.py            # Admin panel
│
├── ml/                     # ML training scripts (not served, run offline)
│   ├── train.py            # Train DT + RF, save joblib artefacts
│   ├── evaluate.py         # Evaluation metrics
│   └── feature_importance.py
│
├── data/
│   ├── rf_model.joblib     # Trained RF model
│   ├── preprocessor.joblib # Fitted encoder + scaler
│   └── seed_rules.py       # Seeds the 47 rules into DB on first run
│
├── static/
│   ├── css/style.css
│   └── js/main.js
│
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── diagnosis/
    │   ├── new.html        # Patient data entry form
    │   └── result.html     # Diagnosis results
    ├── history.html
    └── admin/
        ├── panel.html
        ├── rules.html
        └── users.html
```

---

## 7. Database Schema (SQLite / SQLAlchemy)

### system_users
```sql
user_id       VARCHAR PK
username      VARCHAR UNIQUE NOT NULL
password_hash VARCHAR NOT NULL
role          VARCHAR NOT NULL  -- 'clinical_user' or 'administrator'
facility_id   VARCHAR
created_date  DATE
is_active     BOOLEAN DEFAULT TRUE
```

### patient_records
```sql
case_id           VARCHAR PK  -- auto-generated anonymous ID
age               INTEGER
sex               VARCHAR
fever_duration    FLOAT
fever_pattern     VARCHAR
headache_severity INTEGER
abdominal_pain    BOOLEAN
relative_bradycardia BOOLEAN
hepatosplenomegaly BOOLEAN
leukocyte_count   FLOAT
platelet_count    FLOAT
neutrophil_pct    FLOAT
widal_titre       VARCHAR
esr               FLOAT
haemoglobin       FLOAT
lymphocyte_pct    FLOAT
monocyte_pct      FLOAT
temperature       FLOAT
diarrhoea         BOOLEAN
vomiting          BOOLEAN
rose_spots        BOOLEAN
nausea            BOOLEAN
constipation      BOOLEAN
record_date       DATE
created_by        VARCHAR FK → system_users.user_id
```

### diagnostic_results
```sql
result_id         INTEGER PK AUTOINCREMENT
case_id           VARCHAR FK → patient_records.case_id
diagnosis         VARCHAR  -- 'Typhoid Positive' or 'Typhoid Negative'
confidence_score  FLOAT
es_score          FLOAT    -- raw expert system score
rf_probability    FLOAT    -- null if ES was definitive
route_used        VARCHAR  -- 'ExpertSystem' or 'RandomForest'
reasoning_trace   TEXT     -- JSON list of fired rules
result_timestamp  DATETIME
```

### knowledge_rules
```sql
rule_id           VARCHAR PK  -- e.g. 'R-001'
condition_text    TEXT        -- human-readable condition
condition_json    TEXT        -- JSON for programmatic evaluation
outcome           VARCHAR     -- 'POSITIVE', 'NEGATIVE', or intermediate label
confidence_wt     FLOAT
category          VARCHAR     -- 'positive', 'negative', 'intermediate'
last_updated      DATE
updated_by        VARCHAR FK → system_users.user_id
is_active         BOOLEAN DEFAULT TRUE
```

### audit_log
```sql
log_id        INTEGER PK AUTOINCREMENT
result_id     INTEGER FK → diagnostic_results.result_id  -- nullable
user_id       VARCHAR FK → system_users.user_id
action_type   VARCHAR  -- 'DIAGNOSIS', 'LOGIN', 'LOGOUT', 'RULE_UPDATE', 'MODEL_RETRAIN'
ip_address    VARCHAR
session_id    VARCHAR
log_timestamp DATETIME
```

---

## 8. Key Algorithms (Pseudocode as Implementation Guide)

### 8.1 Preprocessing Pipeline
```python
# preprocessor.py
# Fitted on training data (n=341), saved as preprocessor.joblib

ORDINAL_MAP_WIDAL = {
    'Negative': 0, '1:20': 1, '1:40': 2, '1:80': 3,
    '1:160': 4, '1:320': 5, '>=1:640': 6
}

ONE_HOT_FEATURES = ['sex', 'fever_pattern']
ORDINAL_FEATURES = ['headache_severity', 'widal_titre']  # label encode with order
BINARY_FEATURES  = ['abdominal_pain', 'relative_bradycardia', 'hepatosplenomegaly',
                     'diarrhoea', 'vomiting', 'rose_spots', 'nausea', 'constipation']
CONTINUOUS_FEATURES = ['age', 'fever_duration', 'leukocyte_count', 'platelet_count',
                        'neutrophil_pct', 'esr', 'haemoglobin', 'lymphocyte_pct',
                        'monocyte_pct', 'temperature']

def transform(patient_dict):
    # 1. Apply one-hot to sex and fever_pattern
    # 2. Label-encode ordinals preserving order
    # 3. Min-Max normalize all continuous features using fitted scaler
    # Returns: np.array of shape (1, n_features)
```

### 8.2 Inference Engine (Forward Chaining)
```python
# inference_engine.py

def evaluate(patient_dict, rules_from_db):
    confidence_score = 0.0
    fired_rules = []

    for rule in rules_from_db:
        if rule.is_active and evaluate_conditions(rule.condition_json, patient_dict):
            if rule.category == 'positive':
                confidence_score += rule.confidence_wt
            elif rule.category == 'negative':
                confidence_score -= rule.confidence_wt
            elif rule.category == 'intermediate':
                # Apply intermediate additive weights
                confidence_score += INTERMEDIATE_WEIGHTS.get(rule.outcome, 0)
            fired_rules.append({'rule_id': rule.rule_id, 'outcome': rule.outcome, 'weight': rule.confidence_wt})

    return confidence_score, fired_rules
```

### 8.3 Hybrid Decision Module
```python
# hybrid_module.py

THRESHOLD_HIGH = 0.65
THRESHOLD_LOW  = 0.45

def decide(patient_dict, preprocessed_vector, rules_from_db, rf_model):
    es_score, fired_rules = inference_engine.evaluate(patient_dict, rules_from_db)

    if es_score > THRESHOLD_HIGH:
        return DiagnosticResult(
            diagnosis='Typhoid Positive',
            confidence_score=min(es_score, 1.0),
            route='ExpertSystem',
            fired_rules=fired_rules,
            rf_probability=None
        )
    elif es_score < THRESHOLD_LOW:
        return DiagnosticResult(
            diagnosis='Typhoid Negative',
            confidence_score=1.0 - max(es_score, 0),
            route='ExpertSystem',
            fired_rules=fired_rules,
            rf_probability=None
        )
    else:
        rf_proba = rf_model.predict_proba(preprocessed_vector)[0][1]
        diagnosis = 'Typhoid Positive' if rf_proba >= 0.50 else 'Typhoid Negative'
        return DiagnosticResult(
            diagnosis=diagnosis,
            confidence_score=rf_proba,
            route='RandomForest',
            fired_rules=fired_rules,
            rf_probability=rf_proba
        )
```

---

## 9. ML Model Specification

### Random Forest (Primary Classifier)
- Algorithm: `sklearn.ensemble.RandomForestClassifier`
- Hyperparameters (from grid search):
  - n_estimators: 200
  - max_depth: 10
  - max_features: 'sqrt'
  - min_samples_split: 2
  - bootstrap: True
  - criterion: 'gini'
  - random_state: 42
- Training: 341 records, stratified 70/30 split
- Cross-val F1: 0.903 (SD 0.018)

### Decision Tree (Secondary / Explainability)
- Algorithm: `sklearn.tree.DecisionTreeClassifier`
- Hyperparameters:
  - max_depth: 7
  - min_samples_split: 5
  - min_samples_leaf: 2
  - criterion: 'gini'
  - random_state: 42
- Cross-val F1: 0.847 (SD 0.031)

### Test Set Performance (n=146)
| Metric | DT | RF |
|---|---|---|
| Accuracy | 86.3% | 91.8% |
| Precision | 84.7% | 90.3% |
| Recall | 88.6% | 93.9% |
| Specificity | 84.2% | 90.0% |
| F1-Score | 0.866 | 0.921 |
| ROC-AUC | 0.891 | 0.963 |

### Hybrid System: 92.5% accuracy (test set, n=146)

### Feature Importance (Top 10, RF Gini)
1. Fever Duration: 0.187
2. Total Leukocyte Count: 0.164
3. Platelet Count: 0.142
4. Relative Bradycardia: 0.118
5. Hepatosplenomegaly: 0.097
6. Widal O-Antigen Titre: 0.084
7. Neutrophil Percentage: 0.071
8. Abdominal Pain: 0.063
9. ESR: 0.048
10. Fever Pattern: 0.026

---

## 10. Non-Functional Requirements

| Requirement | Specification |
|---|---|
| Response time | Diagnosis result within 2 seconds |
| Security | Password hashing (Werkzeug), session tokens, role-based access |
| Auditability | Every action logged to audit_log |
| Data Privacy | No real patient names stored; anonymous case IDs only |
| Offline capability | All computation local; no external API calls |
| Browser support | Chrome, Firefox, Edge (modern versions) |
| Scalability | Prototype only; SQLite sufficient for ≤10,000 records |
| Disclaimer | System output must always show: "This system is a decision support tool. Clinical judgment takes precedence." |

---

## 11. Seed Data Requirements

On first run, the application must:
1. Create all DB tables
2. Seed the 47 knowledge rules from `data/seed_rules.py`
3. Create a default admin user: username=`admin`, password=`Admin@2026` (force change on first login)
4. Load `rf_model.joblib` and `preprocessor.joblib` into memory

The ML model files will be synthetic/demo since real patient data is not available. The training script (`ml/train.py`) must be able to generate a synthetic dataset and train the model when run standalone.

---

## 12. Pages / Routes

| Route | Method | Access | Description |
|---|---|---|---|
| `/` | GET | Any | Redirect to login or dashboard |
| `/login` | GET, POST | Any | Login form |
| `/logout` | GET | Auth | Logout |
| `/dashboard` | GET | Auth | Summary stats, recent diagnoses |
| `/diagnosis/new` | GET, POST | Clinical, Admin | Patient data entry form |
| `/diagnosis/<result_id>` | GET | Auth | Result display |
| `/history` | GET | Auth | List of past diagnoses for this user |
| `/admin` | GET | Admin | Admin panel overview |
| `/admin/rules` | GET | Admin | List all rules |
| `/admin/rules/new` | GET, POST | Admin | Add a new rule |
| `/admin/rules/<rule_id>/edit` | GET, POST | Admin | Edit a rule |
| `/admin/rules/<rule_id>/toggle` | POST | Admin | Activate/deactivate rule |
| `/admin/users` | GET | Admin | List users |
| `/admin/users/new` | GET, POST | Admin | Create user |
| `/admin/retrain` | POST | Admin | Trigger model retraining |
| `/admin/reports` | GET | Admin | Performance stats |

---

## 13. Critical Implementation Notes

1. **The ML model must actually work.** Since real data is not shareable, `ml/train.py` should generate a synthetic dataset of 487 records with realistic typhoid/non-typhoid distributions matching the paper (mean fever duration 8.2d positive vs 4.7d negative, mean WBC 4.1 positive vs 8.7 negative, etc.), train the RF and DT, save both models as joblib.

2. **The preprocessor must be fitted on training data and saved.** When making a prediction, load the pre-fitted preprocessor — do not refit on new patient data.

3. **Rule evaluation is programmatic.** Each rule's `condition_json` field stores a list of conditions like:
   ```json
   [{"field": "fever_duration", "op": ">", "value": 7}, {"field": "leukocyte_count", "op": "<", "value": 4.5}]
   ```
   The inference engine evaluates these against the raw (un-normalized) patient values.

4. **The confidence score display should be capped between 0 and 1.** Display as percentage.

5. **Show a medical disclaimer on every results page.**

6. **The admin "retrain" feature** should accept a CSV upload of new records, append to training data, retrain both models, and replace the joblib files.

7. **The dashboard** should show: total cases today, total positive rate, model accuracy (from last evaluation), a small recent diagnoses table.
