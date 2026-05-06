from flask import Flask, redirect, url_for, session, request, flash
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, SystemUser
from config import Config
from pathlib import Path
import sys
import uuid

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

if sys.version_info < (3, 10) or sys.version_info >= (3, 14):
    print(f"[ERROR] Python 3.10-3.13 required. Found {sys.version}.")
    print("Activate the project venv: source .venv/bin/activate")
    sys.exit(1)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    limiter.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @app.before_request
    def ensure_csrf_token():
        if 'csrf_token' not in session:
            session['csrf_token'] = uuid.uuid4().hex
    
    @login_manager.user_loader
    def load_user(user_id):
        return SystemUser.query.get(user_id)
    
    from routes import register_blueprints
    register_blueprints(app)
    
    # Apply rate limiting to login POST requests
    limiter.limit("5 per minute")(app.view_functions['auth.login'])
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    with app.app_context():
        db.create_all()
        
        from models.knowledge_rule import KnowledgeRule
        if KnowledgeRule.query.count() == 0:
            from data.seed_rules import seed_rules
            seed_rules(db.session, KnowledgeRule)
        
        from routes.auth import create_default_admin
        create_default_admin()
        
        data_dir = Path(__file__).parent / 'data'
        rf_model = data_dir / 'rf_model.joblib'
        if not rf_model.exists():
            print("[APP] ML models not found. Running training...")
            from ml.train import main as train_main
            try:
                train_main()
            except Exception as e:
                print(f"[APP] Training failed: {e}")
    
    return app

if __name__ == '__main__':
    import os
    app = create_app()
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000)