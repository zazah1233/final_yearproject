# ZAZAH

Flask-based diagnostic support web app with:
- User authentication and role-based access
- Hybrid diagnosis engine (rules + ML)
- Admin panel for users, rules, reports, and retraining upload

## Requirements

- Python 3.10+ (recommended)
- `pip`
- Linux/macOS shell (commands below use bash/zsh)

## 1) Clone and enter project

```bash
git clone <your-repo-url>
cd zazah
```

## 2) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4) Configure environment variables

Create your local env file from the template:

```bash
cp .env.example .env
```

Then load it into your current shell session (required when running `python app.py`):

```bash
set -a
source .env
set +a
```

You can edit `.env` values as needed. If you skip this step, app defaults from `config.py` are used.

## 5) Run the app

```bash
python app.py
```

App starts on:
- `http://127.0.0.1:5000`
- `http://0.0.0.0:5000`

## First startup behavior

On startup, the app will:
- Create database tables automatically
- Seed default knowledge rules if none exist
- Create bootstrap admin only if `ADMIN_USERNAME` and `ADMIN_PASSWORD` are set
- Train ML models automatically if model files are missing in `data/`

## Login

- Open `http://127.0.0.1:5000`
- Use your bootstrap admin credentials if you set them
- Or create a normal user account from the signup page

## Project structure (high level)

- `app.py` — Flask entrypoint and app factory
- `config.py` — app configuration and environment-based settings
- `routes/` — auth, diagnosis, history, and admin routes
- `engine/` — inference and hybrid diagnostic logic
- `ml/` — model training script
- `models/` — SQLAlchemy models
- `templates/`, `static/` — frontend templates and assets
- `data/` — trained models, metrics, and seed rules

## Troubleshooting

- If dependency install fails, verify active venv and rerun:
  ```bash
  which python
  which pip
  ```
- If env variables are not being picked up, re-run:
  ```bash
  set -a
  source .env
  set +a
  ```
- If port `5000` is in use, stop the conflicting process or run with a different port in `app.py`.
- If admin user is not created, ensure both `ADMIN_USERNAME` and `ADMIN_PASSWORD` are exported in the same shell session before starting the app.
