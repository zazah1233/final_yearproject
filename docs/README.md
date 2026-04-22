# ZAZAH Medical Diagnostic System

ZAZAH is a Flask-based clinical decision support system for typhoid diagnosis.
It combines:

- A rule-based expert system (knowledge rules)
- A machine learning classifier (Random Forest primary, Decision Tree secondary)
- A web UI with authentication, diagnosis workflow, history, and admin tools

---

## What this setup guide covers

This README includes end-to-end setup for:

1. Python environment and dependencies
2. Environment variables and database bootstrap
3. Running the full web application
4. Training/retraining ML models (automatic + manual)
5. Testing and common troubleshooting

---

## Prerequisites

- Python 3.10+
- `pip`
- Linux/macOS shell (commands below use `bash`/`zsh`)

---

## 1) Clone and enter project

```bash
git clone <your-repo-url>
cd zazah
```

---

## 2) Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Check interpreter location (optional but useful):

```bash
which python
which pip
```

---

## 3) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4) Configure environment variables

Create `.env` from template:

```bash
cp .env.example .env
```

Load variables into your current shell session:

```bash
set -a
source .env
set +a
```

Important variables:

- `SECRET_KEY`: Flask secret
- `DATABASE_URL`: SQLAlchemy connection string (default is local SQLite)
- `ADMIN_USERNAME` and `ADMIN_PASSWORD`: optional bootstrap admin account
- `THRESHOLD_HIGH`, `THRESHOLD_LOW`, `RF_THRESHOLD`: diagnosis thresholds

If you do not load `.env`, defaults from `config.py` are used.

---

## 5) Run the application

```bash
python app.py
```

App URLs:

- `http://127.0.0.1:5000`
- `http://0.0.0.0:5000`

---

## First startup behavior (automatic bootstrap)

When `python app.py` starts for the first time, the app automatically:

1. Creates database tables
2. Seeds default knowledge rules (if rules table is empty)
3. Creates bootstrap admin (only if `ADMIN_USERNAME` and `ADMIN_PASSWORD` are set)
4. Trains ML models if `data/rf_model.joblib` is missing

So a fresh checkout can become fully runnable with a single app start.

---

## Model training and retraining

### Option A: Automatic training (on app startup)

Automatic training runs only when model files are missing.

Trigger it by removing model artifacts, then restart app:

```bash
rm -f data/rf_model.joblib data/dt_model.joblib data/preprocessor.joblib data/feature_columns.joblib data/metrics.json
python app.py
```

### Option B: Manual training (recommended for explicit control)

```bash
python ml/train.py
```

The trainer uses data in this order:

1. Existing CSV files found in `data/`
2. Hugging Face dataset (`electricsheepafrica/african-typhoid-dataset`) if available
3. Clinically informed fallback synthetic generation if no dataset is available

Output artifacts written to `data/`:

- `rf_model.joblib`
- `dt_model.joblib`
- `preprocessor.joblib`
- `feature_columns.joblib`
- `metrics.json`

### CSV dataset compatibility notes

If you provide your own CSV for training, the mapper expects fields matching the trainer mapping (for example: `age`, `sex`, `days_illness`, `headache`, `abdominal_pain`, `splenomegaly`, `wbc_k_ul`, `platelets_k_ul`, `widal_positive`, `diarrhea`, `rose_spots`, `typhoid_status`).

---

## Admin panel capabilities

After logging in as administrator, you can:

- Manage users
- Create/edit/toggle knowledge rules
- View reports (including metrics from `data/metrics.json`)

Note: `/admin/retrain` currently supports CSV upload plumbing/UI, but full in-app retraining flow is not yet implemented in `routes/admin.py`. Use `python ml/train.py` for actual retraining.

---

## Run tests

```bash
pytest tests/
```

---

## Project layout

- `app.py` — Flask entrypoint and startup bootstrap
- `config.py` — configuration defaults and env overrides
- `ml/train.py` — model training pipeline
- `engine/` — hybrid inference logic
- `models/` — SQLAlchemy data models
- `routes/` — auth, diagnosis, history, admin routes
- `templates/`, `static/` — frontend UI assets
- `data/` — model artifacts, metrics, seed data

---

## Troubleshooting

- **Environment variables not applied**: reload `.env` in the same shell before running app.
- **Admin not created**: ensure `ADMIN_USERNAME` and `ADMIN_PASSWORD` are both set before app startup.
- **Port 5000 busy**: stop the conflicting process or change port in `app.py`.
- **Model files missing/corrupt**: rerun `python ml/train.py`.
- **Dependency errors**: confirm active virtual environment and reinstall with `pip install -r requirements.txt`.

---

## License

MIT — see `LICENSE`.
