from datetime import datetime
from . import db

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    
    log_id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('diagnostic_results.result_id'))
    user_id = db.Column(db.String(50), db.ForeignKey('system_users.user_id'))
    action_type = db.Column(db.String(30))
    ip_address = db.Column(db.String(50))
    session_id = db.Column(db.String(100))
    log_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('SystemUser', backref='audit_logs')
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'result_id': self.result_id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'ip_address': self.ip_address,
            'session_id': self.session_id,
            'log_timestamp': self.log_timestamp,
        }