import json

class InferenceEngine:
    INTERMEDIATE_WEIGHTS = {
        "Haematological Suppression": 0.12,
        "Enteric Fever Syndrome": 0.10,
        "Faget Sign Present": 0.15,
        "Rose Spot Present": 0.20,
        "Atypical Differential": 0.08,
        "Seropositive Suspicious": 0.06,
        "Systemic Inflammatory Response": 0.07,
    }
    
    def __init__(self, rules=None):
        self.rules = rules or []
    
    def set_rules(self, rules):
        """Set rules from database."""
        self.rules = rules
    
    def evaluate(self, patient_dict):
        """
        Evaluate patient against all rules using forward chaining.
        Returns: (confidence_score, list of fired rules)
        """
        confidence_score = 0.0
        fired_rules = []
        
        patient = self._normalize_patient(patient_dict)
        
        for rule in self.rules:
            if not rule.get('is_active', True):
                continue
            
            try:
                conditions = json.loads(rule['condition_json']) if isinstance(rule['condition_json'], str) else rule['condition_json']
            except (json.JSONDecodeError, TypeError):
                continue
            
            if self._evaluate_conditions(conditions, patient):
                category = rule.get('category', '')
                weight = rule.get('confidence_wt', 0)
                
                if category == 'positive':
                    confidence_score += weight
                elif category == 'negative':
                    confidence_score -= weight
                elif category == 'intermediate':
                    outcome = rule.get('outcome', '')
                    additive = self.INTERMEDIATE_WEIGHTS.get(outcome, 0)
                    confidence_score += additive
                
                fired_rules.append({
                    'rule_id': rule['rule_id'],
                    'outcome': rule.get('outcome', ''),
                    'weight': weight,
                    'condition_text': rule.get('condition_text', '')
                })
        
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        return confidence_score, fired_rules
    
    def _evaluate_conditions(self, conditions, patient):
        """Evaluate all conditions (AND logic)."""
        for cond in conditions:
            field = cond.get('field')
            op = cond.get('op')
            value = cond.get('value')
            
            if field not in patient or patient[field] is None:
                return False
            
            patient_value = patient[field]
            
            if not self._compare(patient_value, op, value):
                return False
        
        return True
    
    def _compare(self, patient_value, operator, threshold):
        """Compare patient value to threshold using operator."""
        try:
            patient_value = float(patient_value)
            threshold = float(threshold)
        except (ValueError, TypeError):
            return str(patient_value) == str(threshold)
        
        if operator == '>':
            return patient_value > threshold
        elif operator == '<':
            return patient_value < threshold
        elif operator == '>=':
            return patient_value >= threshold
        elif operator == '<=':
            return patient_value <= threshold
        elif operator == '==':
            return patient_value == threshold
        elif operator == '!=':
            return patient_value != threshold
        
        return False
    
    def _normalize_patient(self, patient_dict):
        """Normalize patient dict for rule evaluation."""
        normalized = {}
        for key, value in patient_dict.items():
            if value == '' or value is None:
                normalized[key] = None
            elif key in ['abdominal_pain', 'relative_bradycardia', 'hepatosplenomegaly',
                        'diarrhoea', 'vomiting', 'rose_spots', 'nausea', 'constipation']:
                normalized[key] = 1 if value in [True, 1, '1', 'on', 'yes'] else 0
            elif key == 'widal_titre':
                normalized['widal_titre_enc'] = self._encode_widal(value)
            elif key == 'fever_pattern':
                normalized[key] = value
            else:
                try:
                    normalized[key] = float(value)
                except (ValueError, TypeError):
                    normalized[key] = value
        return normalized
    
    def _encode_widal(self, widal_value):
        """Encode Widal titre to numeric."""
        if widal_value is None:
            return 0
        widal_map = {
            'Negative': 0, '1:20': 1, '1:40': 2, '1:80': 3,
            '1:160': 4, '1:320': 5, '>=1:640': 6
        }
        return widal_map.get(str(widal_value), 0)
