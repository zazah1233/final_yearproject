import numpy as np
import joblib
from pathlib import Path

class Preprocessor:
    WIDAL_MAP = {
        'Negative': 0, '1:20': 1, '1:40': 2, '1:80': 3,
        '1:160': 4, '1:320': 5, '>=1:640': 6
    }
    
    FEVER_PATTERN_MAP = {
        'Continuous': 0, 'Step-ladder': 1, 'Remittent': 2, 'Intermittent': 3
    }
    
    CONTINUOUS_COLS = ['age', 'fever_duration', 'headache_severity',
                       'leukocyte_count', 'platelet_count', 'neutrophil_pct',
                       'esr', 'haemoglobin', 'lymphocyte_pct', 'monocyte_pct', 'temperature']
    
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = Path(__file__).parent.parent / 'data' / 'preprocessor.joblib'
        
        self.model_path = model_path
        self.preprocessor_data = None
        self.feature_columns = None
        self._load()
    
    def _load(self):
        if self.model_path.exists():
            self.preprocessor_data = joblib.load(self.model_path)
            feat_path = self.model_path.parent / 'feature_columns.joblib'
            if feat_path.exists():
                self.feature_columns = joblib.load(feat_path)
    
    def transform(self, patient_dict):
        """Transform patient dict to ML-ready feature vector."""
        patient = self._normalize_patient(patient_dict)
        
        features = []
        
        features.append(patient.get('age', 0) or 0)
        features.append(patient.get('fever_duration', 0) or 0)
        features.append(patient.get('headache_severity', 0) or 0)
        
        features.append(patient.get('abdominal_pain', 0))
        features.append(patient.get('relative_bradycardia', 0))
        features.append(patient.get('hepatosplenomegaly', 0))
        
        features.append(patient.get('leukocyte_count', 0) or 0)
        features.append(patient.get('platelet_count', 0) or 0)
        features.append(patient.get('neutrophil_pct', 0) or 0)
        features.append(patient.get('esr', 0) or 0)
        features.append(patient.get('haemoglobin', 0) or 0)
        features.append(patient.get('lymphocyte_pct', 0) or 0)
        features.append(patient.get('monocyte_pct', 0) or 0)
        features.append(patient.get('temperature', 0) or 0)
        
        features.append(patient.get('diarrhoea', 0))
        features.append(patient.get('vomiting', 0))
        features.append(patient.get('rose_spots', 0))
        features.append(patient.get('nausea', 0))
        features.append(patient.get('constipation', 0))
        
        widal_val = patient.get('widal_titre', 'Negative')
        features.append(self.WIDAL_MAP.get(widal_val, 0))
        
        fp_val = patient.get('fever_pattern', 'Continuous')
        features.append(self.FEVER_PATTERN_MAP.get(fp_val, 0))
        
        sex = patient.get('sex', 'Male')
        features.append(1 if sex == 'Male' else 0)
        features.append(1 if sex == 'Female' else 0)
        features.append(1 if sex == 'Other' else 0)
        
        if self.preprocessor_data and 'scaler' in self.preprocessor_data:
            scaler = self.preprocessor_data['scaler']
            continuous_vals = np.array(features[:11]).reshape(1, -1)
            scaled = scaler.transform(continuous_vals)
            features[:11] = scaled[0].tolist()
        
        return np.array(features).reshape(1, -1)
    
    def _normalize_patient(self, patient_dict):
        """Normalize patient dict values."""
        normalized = {}
        for key, value in patient_dict.items():
            if value == '' or value is None:
                normalized[key] = None
            elif key in ['abdominal_pain', 'relative_bradycardia', 'hepatosplenomegaly',
                        'diarrhoea', 'vomiting', 'rose_spots', 'nausea', 'constipation']:
                normalized[key] = 1 if value in [True, 1, '1', 'on', 'yes'] else 0
            elif key in ['age', 'fever_duration', 'headache_severity', 'leukocyte_count',
                        'platelet_count', 'neutrophil_pct', 'esr', 'haemoglobin',
                        'lymphocyte_pct', 'monocyte_pct', 'temperature']:
                try:
                    normalized[key] = float(value)
                except (ValueError, TypeError):
                    normalized[key] = None
            else:
                normalized[key] = value
        return normalized
    
    def get_feature_names(self):
        if self.feature_columns:
            return self.feature_columns
        return [
            'age', 'fever_duration', 'headache_severity',
            'abdominal_pain', 'relative_bradycardia', 'hepatosplenomegaly',
            'leukocyte_count', 'platelet_count', 'neutrophil_pct',
            'esr', 'haemoglobin', 'lymphocyte_pct', 'monocyte_pct', 'temperature',
            'diarrhoea', 'vomiting', 'rose_spots', 'nausea', 'constipation',
            'widal_titre_enc', 'fever_pattern_enc',
            'sex_Male', 'sex_Female', 'sex_Other'
        ]
