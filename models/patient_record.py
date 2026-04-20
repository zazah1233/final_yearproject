from datetime import datetime
from . import db

class PatientRecord(db.Model):
    __tablename__ = 'patient_records'
    
    case_id = db.Column(db.String(50), primary_key=True)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(20))
    fever_duration = db.Column(db.Float)
    fever_pattern = db.Column(db.String(30))
    headache_severity = db.Column(db.Integer)
    abdominal_pain = db.Column(db.Integer)
    relative_bradycardia = db.Column(db.Integer)
    hepatosplenomegaly = db.Column(db.Integer)
    leukocyte_count = db.Column(db.Float)
    platelet_count = db.Column(db.Float)
    neutrophil_pct = db.Column(db.Float)
    widal_titre = db.Column(db.String(20))
    esr = db.Column(db.Float)
    haemoglobin = db.Column(db.Float)
    lymphocyte_pct = db.Column(db.Float)
    monocyte_pct = db.Column(db.Float)
    temperature = db.Column(db.Float)
    diarrhoea = db.Column(db.Integer)
    vomiting = db.Column(db.Integer)
    rose_spots = db.Column(db.Integer)
    nausea = db.Column(db.Integer)
    constipation = db.Column(db.Integer)
    record_date = db.Column(db.Date, default=datetime.utcnow)
    created_by = db.Column(db.String(50), db.ForeignKey('system_users.user_id'))
    
    results = db.relationship('DiagnosticResult', backref='patient', lazy='dynamic')
    
    def to_dict(self):
        return {
            'case_id': self.case_id,
            'age': self.age,
            'sex': self.sex,
            'fever_duration': self.fever_duration,
            'fever_pattern': self.fever_pattern,
            'headache_severity': self.headache_severity,
            'abdominal_pain': self.abdominal_pain,
            'relative_bradycardia': self.relative_bradycardia,
            'hepatosplenomegaly': self.hepatosplenomegaly,
            'leukocyte_count': self.leukocyte_count,
            'platelet_count': self.platelet_count,
            'neutrophil_pct': self.neutrophil_pct,
            'widal_titre': self.widal_titre,
            'esr': self.esr,
            'haemoglobin': self.haemoglobin,
            'lymphocyte_pct': self.lymphocyte_pct,
            'monocyte_pct': self.monocyte_pct,
            'temperature': self.temperature,
            'diarrhoea': self.diarrhoea,
            'vomiting': self.vomiting,
            'rose_spots': self.rose_spots,
            'nausea': self.nausea,
            'constipation': self.constipation,
        }
