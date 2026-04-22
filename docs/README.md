# ZAZAH Medical Diagnostic System

A Flask-based clinical decision support system for typhoid fever diagnosis, combining rule-based expert system reasoning with machine learning.

## Features

- **Hybrid Diagnosis Engine**: Combines clinical rules with Random Forest ML
- **Expert System**: 47 evidence-based knowledge rules for typhoid diagnosis
- **ML Classification**: Random Forest and Decision Tree models trained on clinical data
- **Admin Panel**: User management, rule editing, reports, model retraining
- **Audit Logging**: Complete diagnosis history with reasoning traces

## Technology Stack

- Flask 2.3.x
- SQLAlchemy 2.0.x
- scikit-learn 1.3.x
- SQLite (default, easily swappable)

## Quick Start

```bash
# Clone and setup
git clone https://github.com/your-repo/zazah.git
cd zazah

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run the application
python app.py
```

Open http://127.0.0.1:5000 to access the application.

## Architecture

### Hybrid Diagnosis Flow

```
Patient Data → Expert System → [High/Low Confidence] → Direct Result
                     ↓ Gray Zone
              Random Forest → Probability → Final Diagnosis
```

### File Structure

```
zazah/
├── app.py              # Flask entrypoint
├── config.py           # Configuration
├── engine/            # Diagnosis engine
│   ├── inference_engine.py
│   ├── hybrid_module.py
│   ├── preprocessor.py
│   └── rf_classifier.py
├── models/            # Database models
├── routes/            # API routes
├── ml/               # ML training
├── data/             # Trained models, rules
├── templates/        # Jinja2 templates
└── static/          # CSS, JS assets
```

## Configuration

See `.env.example` for available environment variables:

- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string
- `ADMIN_USERNAME`/`ADMIN_PASSWORD`: Bootstrap admin credentials
- `ML_MODEL_RETRAIN_TOKEN`: Token for retraining API

## Development

### Running Tests

```bash
pytest tests/
```

### Retraining Models

```bash
python ml/train.py
```

Or via admin panel at `/admin/retrain` (requires authentication).

## License

MIT License - see LICENSE file for details.

## Citation

If you use this system in research, please cite:

```
ZAZAH Medical Diagnostic System, 2024.
https://github.com/your-repo/zazah
```