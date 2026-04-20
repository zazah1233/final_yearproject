from datetime import datetime
import json
from . import db

class DiagnosticResult(db.Model):
    __tablename__ = 'diagnostic_results'
    
    result_id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(50), db.ForeignKey('patient_records.case_id'))
    diagnosis = db.Column(db.String(30))
    confidence_score = db.Column(db.Float)
    es_score = db.Column(db.Float)
    rf_probability = db.Column(db.Float)
    route_used = db.Column(db.String(20))
    reasoning_trace = db.Column(db.Text)
    result_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_reasoning_trace(self, fired_rules):
        self.reasoning_trace = json.dumps(fired_rules)
    
    def get_reasoning_trace(self):
        if self.reasoning_trace:
            return json.loads(self.reasoning_trace)
        return []
    
    def to_dict(self):
        return {
            'result_id': self.result_id,
            'case_id': self.case_id,
            'diagnosis': self.diagnosis,
            'confidence_score': self.confidence_score,
            'es_score': self.es_score,
            'rf_probability': self.rf_probability,
            'route_used': self.route_used,
            'reasoning_trace': self.get_reasoning_trace(),
            'result_timestamp': self.result_timestamp,
        }