from datetime import datetime
from . import db

class KnowledgeRule(db.Model):
    __tablename__ = 'knowledge_rules'
    
    rule_id = db.Column(db.String(20), primary_key=True)
    condition_text = db.Column(db.Text)
    condition_json = db.Column(db.Text)
    outcome = db.Column(db.String(30))
    confidence_wt = db.Column(db.Float)
    category = db.Column(db.String(20))
    last_updated = db.Column(db.Date, default=datetime.utcnow)
    updated_by = db.Column(db.String(50), db.ForeignKey('system_users.user_id'))
    is_active = db.Column(db.Boolean, default=True)
    
    def get_conditions(self):
        import json
        return json.loads(self.condition_json)
    
    def to_dict(self):
        return {
            'rule_id': self.rule_id,
            'condition_text': self.condition_text,
            'condition_json': self.condition_json,
            'outcome': self.outcome,
            'confidence_wt': self.confidence_wt,
            'category': self.category,
            'is_active': self.is_active,
        }