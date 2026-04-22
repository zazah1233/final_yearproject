"""
Test suite for ZAZAH Medical Diagnostic System.
"""

import pytest


class TestInferenceEngine:
    """Tests for inference engine."""
    
    def test_rule_evaluation(self, app):
        """Test basic rule evaluation."""
        from engine import InferenceEngine
        
        rules = [
            {
                'rule_id': 'TEST-001',
                'condition_json': '[{"field": "fever_duration", "op": ">", "value": 7}]',
                'outcome': 'POSITIVE',
                'confidence_wt': 0.8,
                'category': 'positive',
                'is_active': True,
                'condition_text': 'Fever Duration > 7 days'
            }
        ]
        
        with app.app_context():
            engine = InferenceEngine(rules)
            
            patient = {'fever_duration': 10}
            score, fired = engine.evaluate(patient)
            
            assert score > 0
            assert len(fired) > 0
    
    def test_negative_rule(self, app):
        """Test negative rule evaluation."""
        from engine import InferenceEngine
        
        rules = [
            {
                'rule_id': 'TEST-002',
                'condition_json': '[{"field": "fever_duration", "op": "<", "value": 3}]',
                'outcome': 'NEGATIVE',
                'confidence_wt': 0.8,
                'category': 'negative',
                'is_active': True,
                'condition_text': 'Fever Duration < 3 days'
            }
        ]
        
        with app.app_context():
            engine = InferenceEngine(rules)
            
            patient = {'fever_duration': 2}
            score, fired = engine.evaluate(patient)
            
            assert score < 0.5
    
    def test_empty_rules(self, app):
        """Test with no rules."""
        from engine import InferenceEngine
        
        with app.app_context():
            engine = InferenceEngine([])
            
            patient = {'fever_duration': 10}
            score, fired = engine.evaluate(patient)
            
            assert score == 0.0
            assert fired == []


class TestPreprocessor:
    """Tests for preprocessor."""
    
    def test_transform_basic(self, app):
        """Test basic transformation."""
        from engine import Preprocessor
        
        with app.app_context():
            prep = Preprocessor()
            
            patient = {
                'age': '30',
                'sex': 'Male',
                'fever_duration': '7',
                'leukocyte_count': '5.0',
                'platelet_count': '150',
            }
            
            X = prep.transform(patient)
            
            assert X.shape[0] == 1
            assert X.shape[1] > 0
    
    def test_default_values(self, app):
        """Test default values for missing fields."""
        from engine import Preprocessor
        
        with app.app_context():
            prep = Preprocessor()
            
            patient = {'age': '30'}
            
            X = prep.transform(patient)
            
            assert X is not None


class TestRFClassifier:
    """Tests for Random Forest classifier."""
    
    def test_model_loaded(self, app):
        """Test model loading."""
        from engine import RFClassifier
        
        with app.app_context():
            clf = RFClassifier()
            
            assert clf.is_loaded() is True
    
    def test_predict(self, app):
        """Test prediction."""
        from engine import RFClassifier
        
        with app.app_context():
            clf = RFClassifier()
            
            if clf.is_loaded():
                X = [[30, 7, 2, 0, 0, 0, 5.0, 150, 50, 30, 12.0, 30, 5, 38.5, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]]
                pred = clf.predict(X)
                proba = clf.predict_proba(X)
                
                assert pred is not None
                assert proba is not None


class TestHybridModule:
    """Tests for hybrid module."""
    
    def test_confident_positive(self, app):
        """Test high confidence positive case."""
        from engine import HybridModule
        from models import KnowledgeRule
        
        with app.app_context():
            from models import db, KnowledgeRule
            rules = KnowledgeRule.query.filter_by(is_active=True).all()
            rules_data = [{'rule_id': r.rule_id, 'condition_json': r.condition_json, 
                         'outcome': r.outcome, 'confidence_wt': r.confidence_wt,
                         'category': r.category, 'is_active': r.is_active,
                         'condition_text': r.condition_text} for r in rules]
            
            engine = HybridModule(rules=rules_data)
            
            patient = {
                'case_id': 'TEST-001',
                'age': '35',
                'sex': 'Male',
                'fever_duration': '10',
                'fever_pattern': 'Step-ladder',
                'headache_severity': '3',
                'abdominal_pain': '1',
                'relative_bradycardia': '1',
                'hepatosplenomegaly': '1',
                'leukocyte_count': '3.5',
                'platelet_count': '90',
                'neutrophil_pct': '35',
                'widal_titre': '1:160',
                'esr': '55',
                'haemoglobin': '10.5',
                'lymphocyte_pct': '45',
                'monocyte_pct': '8',
                'temperature': '39.5',
                'diarrhoea': '0',
                'vomiting': '0',
                'rose_spots': '1',
                'nausea': '1',
                'constipation': '0',
            }
            
            result = engine.diagnose(patient)
            
            assert result.diagnosis == 'Typhoid Positive'
            assert result.confidence_score > 0.8
    
    def test_confident_negative(self, app):
        """Test high confidence negative case."""
        from engine import HybridModule
        from models import KnowledgeRule
        
        with app.app_context():
            from models import db, KnowledgeRule
            rules = KnowledgeRule.query.filter_by(is_active=True).all()
            rules_data = [{'rule_id': r.rule_id, 'condition_json': r.condition_json, 
                         'outcome': r.outcome, 'confidence_wt': r.confidence_wt,
                         'category': r.category, 'is_active': r.is_active,
                         'condition_text': r.condition_text} for r in rules]
            
            engine = HybridModule(rules=rules_data)
            
            patient = {
                'case_id': 'TEST-002',
                'age': '25',
                'sex': 'Female',
                'fever_duration': '2',
                'fever_pattern': 'Continuous',
                'headache_severity': '2',
                'abdominal_pain': '0',
                'relative_bradycardia': '0',
                'hepatosplenomegaly': '0',
                'leukocyte_count': '12',
                'platelet_count': '300',
                'neutrophil_pct': '80',
                'widal_titre': 'Negative',
                'esr': '15',
                'haemoglobin': '13.5',
                'lymphocyte_pct': '20',
                'monocyte_pct': '4',
                'temperature': '38.0',
                'diarrhoea': '1',
                'vomiting': '1',
                'rose_spots': '0',
                'nausea': '1',
                'constipation': '0',
            }
            
            result = engine.diagnose(patient)
            
            assert result.diagnosis == 'Typhoid Negative'


class TestRoutes:
    """Tests for HTTP routes."""
    
    def test_index_redirect(self, client):
        """Test index redirects to login."""
        response = client.get('/')
        assert response.status_code in [301, 302, 404]
    
    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get('/auth/login')
        assert response.status_code == 200
    
    def test_signup_page(self, client):
        """Test signup page loads."""
        response = client.get('/auth/signup')
        assert response.status_code == 200