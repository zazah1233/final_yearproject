from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
diagnosis_bp = Blueprint('diagnosis', __name__)
history_bp = Blueprint('history', __name__)
admin_bp = Blueprint('admin', __name__)

def register_blueprints(app):
    from .auth import auth_bp as auth
    from .diagnosis import diagnosis_bp as diagnosis
    from .history import history_bp as history
    from .admin import admin_bp as admin
    
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(diagnosis, url_prefix='/diagnosis')
    app.register_blueprint(history, url_prefix='/history')
    app.register_blueprint(admin, url_prefix='/admin')