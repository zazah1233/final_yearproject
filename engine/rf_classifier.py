import numpy as np
import joblib
from pathlib import Path

class RFClassifier:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = Path(__file__).parent.parent / 'data' / 'rf_model.joblib'
        
        self.model_path = model_path
        self.model = None
        self.feature_importances_ = None
        self._load()
    
    def _load(self):
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importances_ = self.model.feature_importances_
    
    def predict_proba(self, X):
        """Get probability predictions."""
        if self.model is None:
            raise RuntimeError("Random Forest model not loaded")
        return self.model.predict_proba(X)
    
    def predict(self, X):
        """Get class predictions."""
        if self.model is None:
            raise RuntimeError("Random Forest model not loaded")
        return self.model.predict(X)
    
    def get_feature_importances(self):
        """Get feature importances as dict."""
        if self.feature_importances_ is None:
            return {}
        
        feature_names = [
            'age', 'fever_duration', 'headache_severity',
            'abdominal_pain', 'relative_bradycardia', 'hepatosplenomegaly',
            'leukocyte_count', 'platelet_count', 'neutrophil_pct',
            'esr', 'haemoglobin', 'lymphocyte_pct', 'monocyte_pct', 'temperature',
            'diarrhoea', 'vomiting', 'rose_spots', 'nausea', 'constipation',
            'widal_titre_enc', 'fever_pattern_enc',
            'sex_Male', 'sex_Female', 'sex_Other'
        ]
        
        importances = {}
        for i, name in enumerate(feature_names):
            if i < len(self.feature_importances_):
                importances[name] = float(self.feature_importances_[i])
        
        return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
    
    def is_loaded(self):
        return self.model is not None
