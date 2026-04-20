from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, SystemUser
from config import Config
from pathlib import Path

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return SystemUser.query.get(user_id)
    
    from routes import register_blueprints
    register_blueprints(app)
    
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
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)