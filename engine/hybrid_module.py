from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from flask import current_app
from .inference_engine import InferenceEngine
from .rf_classifier import RFClassifier
from .preprocessor import Preprocessor

@dataclass
class DiagnosticResult:
    diagnosis: str
    confidence_score: float
    route: str
    fired_rules: List[Dict[str, Any]]
    rf_probability: Optional[float] = None
    es_score: float = 0.0
    feature_importances: Optional[Dict[str, float]] = None

class HybridModule:
    def __init__(self, rules=None, preprocessor_path=None, rf_model_path=None):
        self.inference_engine = InferenceEngine(rules)
        self.preprocessor = Preprocessor(preprocessor_path)
        self.rf_classifier = RFClassifier(rf_model_path)
        
        self._threshold_high = 0.85
        self._threshold_low = 0.10
        self._rf_threshold = 0.50
        
        try:
            self._threshold_high = current_app.config.get('THRESHOLD_HIGH', 0.85)
            self._threshold_low = current_app.config.get('THRESHOLD_LOW', 0.10)
            self._rf_threshold = current_app.config.get('RF_THRESHOLD', 0.50)
        except RuntimeError:
            pass
    
    @property
    def THRESHOLD_HIGH(self):
        return self._threshold_high
    
    @property
    def THRESHOLD_LOW(self):
        return self._threshold_low
    
    @property
    def RF_THRESHOLD(self):
        return self._rf_threshold
    
    def set_rules(self, rules):
        """Set rules for inference engine."""
        self.inference_engine.set_rules(rules)
    
    def diagnose(self, patient_dict) -> DiagnosticResult:
        """
        Run hybrid diagnosis on patient data.
        """
        es_score, fired_rules = self.inference_engine.evaluate(patient_dict)
        
        if es_score > self.THRESHOLD_HIGH:
            confidence = min(es_score, 1.0)
            return DiagnosticResult(
                diagnosis='Typhoid Positive',
                confidence_score=confidence,
                route='ExpertSystem',
                fired_rules=fired_rules,
                rf_probability=None,
                es_score=es_score
            )
        
        elif es_score < self.THRESHOLD_LOW:
            confidence = 1.0 - max(es_score, 0)
            return DiagnosticResult(
                diagnosis='Typhoid Negative',
                confidence_score=confidence,
                route='ExpertSystem',
                fired_rules=fired_rules,
                rf_probability=None,
                es_score=es_score
            )
        
        else:
            if not self.rf_classifier.is_loaded():
                return DiagnosticResult(
                    diagnosis='Typhoid Negative' if es_score < 0.55 else 'Typhoid Positive',
                    confidence_score=abs(es_score - 0.5) + 0.5,
                    route='ExpertSystem (fallback)',
                    fired_rules=fired_rules,
                    rf_probability=None,
                    es_score=es_score
                )
            
            try:
                X = self.preprocessor.transform(patient_dict)
                rf_proba = self.rf_classifier.predict_proba(X)[0][1]
            except Exception as e:
                rf_proba = 0.5 if es_score >= 0.55 else 0.45
            
            diagnosis = 'Typhoid Positive' if rf_proba >= self.RF_THRESHOLD else 'Typhoid Negative'
            
            feature_importances = self.rf_classifier.get_feature_importances()
            
            return DiagnosticResult(
                diagnosis=diagnosis,
                confidence_score=rf_proba,
                route='RandomForest',
                fired_rules=fired_rules,
                rf_probability=rf_proba,
                es_score=es_score,
                feature_importances=feature_importances
            )
    
    def is_ready(self):
        """Check if engine is ready for diagnosis."""
        return self.rf_classifier.is_loaded()
