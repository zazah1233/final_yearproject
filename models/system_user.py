from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class SystemUser(db.Model):
    __tablename__ = 'system_users'
    
    user_id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    facility_id = db.Column(db.String(50))
    created_date = db.Column(db.Date, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_administrator(self):
        return self.role == 'administrator'
    
    def is_clinical_user(self):
        return self.role in ('clinical_user', 'administrator')
    
    def get_id(self):
        return self.user_id
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
