"""
data/seed_rules.py
------------------
Seeds the 47 expert system rules into the database.
Called automatically on app first run if the knowledge_rules table is empty.

Each rule's condition_json is a list of condition dicts:
  {"field": <feature_name>, "op": <">" | "<" | ">=" | "<=" | "==" | "!=">, "value": <value>}

Fields must match the raw (un-normalized) patient record fields:
  fever_duration, leukocyte_count, platelet_count, neutrophil_pct, esr,
  haemoglobin, lymphocyte_pct, temperature, widal_titre_enc (0-6),
  headache_severity (1-5), abdominal_pain (0/1), relative_bradycardia (0/1),
  hepatosplenomegaly (0/1), diarrhoea (0/1), vomiting (0/1),
  rose_spots (0/1), nausea (0/1), constipation (0/1),
  fever_pattern (string), sex (string)
"""

import json
from datetime import date

SEED_RULES = [
    # ─── TYPHOID POSITIVE RULES (18) ───────────────────────────────────
    {
        "rule_id": "R-001",
        "condition_text": "Fever Duration > 7 days AND Leukocyte Count < 4.5 ×10⁹/L",
        "condition_json": json.dumps([
            {"field": "fever_duration", "op": ">", "value": 7},
            {"field": "leukocyte_count", "op": "<", "value": 4.5}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.82,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-002",
        "condition_text": "Relative Bradycardia = Present AND Hepatosplenomegaly = Present",
        "condition_json": json.dumps([
            {"field": "relative_bradycardia", "op": "==", "value": 1},
            {"field": "hepatosplenomegaly", "op": "==", "value": 1}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.78,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-003",
        "condition_text": "Fever Duration > 7 days AND Fever Pattern = Step-ladder",
        "condition_json": json.dumps([
            {"field": "fever_duration", "op": ">", "value": 7},
            {"field": "fever_pattern", "op": "==", "value": "Step-ladder"}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.76,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-004",
        "condition_text": "Leukocyte Count < 4.0 ×10⁹/L AND Neutrophil % < 40%",
        "condition_json": json.dumps([
            {"field": "leukocyte_count", "op": "<", "value": 4.0},
            {"field": "neutrophil_pct", "op": "<", "value": 40}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.75,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-005",
        "condition_text": "Platelet Count < 100 ×10⁹/L AND Leukocyte Count < 5.0 ×10⁹/L",
        "condition_json": json.dumps([
            {"field": "platelet_count", "op": "<", "value": 100},
            {"field": "leukocyte_count", "op": "<", "value": 5.0}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.74,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-006",
        "condition_text": "Widal O-titre ≥ 1:160 AND Fever Duration > 5 days",
        "condition_json": json.dumps([
            {"field": "widal_titre_enc", "op": ">=", "value": 4},
            {"field": "fever_duration", "op": ">", "value": 5}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.71,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-007",
        "condition_text": "Hepatosplenomegaly = Present AND Fever Duration > 7 days",
        "condition_json": json.dumps([
            {"field": "hepatosplenomegaly", "op": "==", "value": 1},
            {"field": "fever_duration", "op": ">", "value": 7}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.70,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-008",
        "condition_text": "Rose Spots = Present AND Fever Duration > 5 days",
        "condition_json": json.dumps([
            {"field": "rose_spots", "op": "==", "value": 1},
            {"field": "fever_duration", "op": ">", "value": 5}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.85,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-009",
        "condition_text": "Relative Bradycardia = Present AND Fever Duration > 7 days",
        "condition_json": json.dumps([
            {"field": "relative_bradycardia", "op": "==", "value": 1},
            {"field": "fever_duration", "op": ">", "value": 7}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.79,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-010",
        "condition_text": "Leukocyte Count < 3.5 ×10⁹/L AND Platelet Count < 120 ×10⁹/L",
        "condition_json": json.dumps([
            {"field": "leukocyte_count", "op": "<", "value": 3.5},
            {"field": "platelet_count", "op": "<", "value": 120}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.80,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-011",
        "condition_text": "Temperature > 39.5°C AND Fever Duration > 7 days AND Leukocyte Count < 5.0",
        "condition_json": json.dumps([
            {"field": "temperature", "op": ">", "value": 39.5},
            {"field": "fever_duration", "op": ">", "value": 7},
            {"field": "leukocyte_count", "op": "<", "value": 5.0}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.77,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-012",
        "condition_text": "Hepatosplenomegaly = Present AND Abdominal Pain = Present AND Fever Duration > 5 days",
        "condition_json": json.dumps([
            {"field": "hepatosplenomegaly", "op": "==", "value": 1},
            {"field": "abdominal_pain", "op": "==", "value": 1},
            {"field": "fever_duration", "op": ">", "value": 5}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.73,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-013",
        "condition_text": "Neutrophil % < 35% AND Lymphocyte % > 40%",
        "condition_json": json.dumps([
            {"field": "neutrophil_pct", "op": "<", "value": 35},
            {"field": "lymphocyte_pct", "op": ">", "value": 40}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.69,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-014",
        "condition_text": "Widal O-titre ≥ 1:320 AND Fever Duration > 3 days",
        "condition_json": json.dumps([
            {"field": "widal_titre_enc", "op": ">=", "value": 5},
            {"field": "fever_duration", "op": ">", "value": 3}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.74,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-015",
        "condition_text": "Fever Pattern = Step-ladder AND Relative Bradycardia = Present",
        "condition_json": json.dumps([
            {"field": "fever_pattern", "op": "==", "value": "Step-ladder"},
            {"field": "relative_bradycardia", "op": "==", "value": 1}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.76,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-016",
        "condition_text": "Platelet Count < 80 ×10⁹/L AND Haemoglobin < 11 g/dL",
        "condition_json": json.dumps([
            {"field": "platelet_count", "op": "<", "value": 80},
            {"field": "haemoglobin", "op": "<", "value": 11}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.72,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-017",
        "condition_text": "Abdominal Pain = Present AND Constipation = Present AND Fever Duration > 5 days",
        "condition_json": json.dumps([
            {"field": "abdominal_pain", "op": "==", "value": 1},
            {"field": "constipation", "op": "==", "value": 1},
            {"field": "fever_duration", "op": ">", "value": 5}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.68,
        "category": "positive",
        "is_active": True,
    },
    {
        "rule_id": "R-018",
        "condition_text": "ESR > 50 mm/hr AND Leukocyte Count < 5.0 ×10⁹/L AND Fever Duration > 7 days",
        "condition_json": json.dumps([
            {"field": "esr", "op": ">", "value": 50},
            {"field": "leukocyte_count", "op": "<", "value": 5.0},
            {"field": "fever_duration", "op": ">", "value": 7}
        ]),
        "outcome": "POSITIVE",
        "confidence_wt": 0.71,
        "category": "positive",
        "is_active": True,
    },

    # ─── TYPHOID NEGATIVE RULES (15) ────────────────────────────────────
    {
        "rule_id": "R-019",
        "condition_text": "Fever Duration < 4 days AND Leukocyte Count > 11 ×10⁹/L",
        "condition_json": json.dumps([
            {"field": "fever_duration", "op": "<", "value": 4},
            {"field": "leukocyte_count", "op": ">", "value": 11}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.80,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-020",
        "condition_text": "Leukocyte Count > 12 ×10⁹/L AND Neutrophil % > 75%",
        "condition_json": json.dumps([
            {"field": "leukocyte_count", "op": ">", "value": 12},
            {"field": "neutrophil_pct", "op": ">", "value": 75}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.82,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-021",
        "condition_text": "Fever Duration < 3 days AND Temperature < 38.5°C",
        "condition_json": json.dumps([
            {"field": "fever_duration", "op": "<", "value": 3},
            {"field": "temperature", "op": "<", "value": 38.5}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.78,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-022",
        "condition_text": "Widal O-titre = Negative AND Leukocyte Count > 10 ×10⁹/L",
        "condition_json": json.dumps([
            {"field": "widal_titre_enc", "op": "==", "value": 0},
            {"field": "leukocyte_count", "op": ">", "value": 10}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.75,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-023",
        "condition_text": "Platelet Count > 300 ×10⁹/L AND Leukocyte Count > 10 ×10⁹/L",
        "condition_json": json.dumps([
            {"field": "platelet_count", "op": ">", "value": 300},
            {"field": "leukocyte_count", "op": ">", "value": 10}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.76,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-024",
        "condition_text": "Fever Duration < 4 days AND Hepatosplenomegaly = Absent AND Relative Bradycardia = Absent",
        "condition_json": json.dumps([
            {"field": "fever_duration", "op": "<", "value": 4},
            {"field": "hepatosplenomegaly", "op": "==", "value": 0},
            {"field": "relative_bradycardia", "op": "==", "value": 0}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.72,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-025",
        "condition_text": "Neutrophil % > 80% AND Fever Duration < 5 days",
        "condition_json": json.dumps([
            {"field": "neutrophil_pct", "op": ">", "value": 80},
            {"field": "fever_duration", "op": "<", "value": 5}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.77,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-026",
        "condition_text": "Leukocyte Count > 15 ×10⁹/L",
        "condition_json": json.dumps([
            {"field": "leukocyte_count", "op": ">", "value": 15}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.83,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-027",
        "condition_text": "Rose Spots = Absent AND Relative Bradycardia = Absent AND Widal O-titre = Negative",
        "condition_json": json.dumps([
            {"field": "rose_spots", "op": "==", "value": 0},
            {"field": "relative_bradycardia", "op": "==", "value": 0},
            {"field": "widal_titre_enc", "op": "==", "value": 0}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.65,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-028",
        "condition_text": "Fever Duration < 2 days AND Vomiting = Present AND Diarrhoea = Present",
        "condition_json": json.dumps([
            {"field": "fever_duration", "op": "<", "value": 2},
            {"field": "vomiting", "op": "==", "value": 1},
            {"field": "diarrhoea", "op": "==", "value": 1}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.70,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-029",
        "condition_text": "Temperature < 37.5°C AND Fever Duration < 3 days",
        "condition_json": json.dumps([
            {"field": "temperature", "op": "<", "value": 37.5},
            {"field": "fever_duration", "op": "<", "value": 3}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.79,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-030",
        "condition_text": "Leukocyte Count > 11 ×10⁹/L AND Platelet Count > 250 ×10⁹/L AND Neutrophil % > 70%",
        "condition_json": json.dumps([
            {"field": "leukocyte_count", "op": ">", "value": 11},
            {"field": "platelet_count", "op": ">", "value": 250},
            {"field": "neutrophil_pct", "op": ">", "value": 70}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.81,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-031",
        "condition_text": "Headache Severity < 2 AND Fever Duration < 3 days AND Leukocyte Count > 9 ×10⁹/L",
        "condition_json": json.dumps([
            {"field": "headache_severity", "op": "<", "value": 2},
            {"field": "fever_duration", "op": "<", "value": 3},
            {"field": "leukocyte_count", "op": ">", "value": 9}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.68,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-032",
        "condition_text": "Widal O-titre ≤ 1:40 AND Leukocyte Count > 9 ×10⁹/L AND Fever Duration < 5 days",
        "condition_json": json.dumps([
            {"field": "widal_titre_enc", "op": "<=", "value": 2},
            {"field": "leukocyte_count", "op": ">", "value": 9},
            {"field": "fever_duration", "op": "<", "value": 5}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.69,
        "category": "negative",
        "is_active": True,
    },
    {
        "rule_id": "R-033",
        "condition_text": "Diarrhoea = Present AND Vomiting = Present AND Fever Duration < 3 days AND Leukocyte Count > 10",
        "condition_json": json.dumps([
            {"field": "diarrhoea", "op": "==", "value": 1},
            {"field": "vomiting", "op": "==", "value": 1},
            {"field": "fever_duration", "op": "<", "value": 3},
            {"field": "leukocyte_count", "op": ">", "value": 10}
        ]),
        "outcome": "NEGATIVE",
        "confidence_wt": 0.71,
        "category": "negative",
        "is_active": True,
    },

    # ─── INTERMEDIATE STATE RULES (14) ──────────────────────────────────
    {
        "rule_id": "R-034",
        "condition_text": "Platelet Count < 100 ×10⁹/L AND Neutrophil % < 40%",
        "condition_json": json.dumps([
            {"field": "platelet_count", "op": "<", "value": 100},
            {"field": "neutrophil_pct", "op": "<", "value": 40}
        ]),
        "outcome": "Haematological Suppression",
        "confidence_wt": 0.74,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-035",
        "condition_text": "Abdominal Pain = Present AND Hepatosplenomegaly = Present",
        "condition_json": json.dumps([
            {"field": "abdominal_pain", "op": "==", "value": 1},
            {"field": "hepatosplenomegaly", "op": "==", "value": 1}
        ]),
        "outcome": "Enteric Fever Syndrome",
        "confidence_wt": 0.71,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-036",
        "condition_text": "Leukocyte Count < 4.5 ×10⁹/L AND ESR > 40 mm/hr",
        "condition_json": json.dumps([
            {"field": "leukocyte_count", "op": "<", "value": 4.5},
            {"field": "esr", "op": ">", "value": 40}
        ]),
        "outcome": "Haematological Suppression",
        "confidence_wt": 0.72,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-037",
        "condition_text": "Fever Duration > 5 days AND Abdominal Pain = Present AND Nausea = Present",
        "condition_json": json.dumps([
            {"field": "fever_duration", "op": ">", "value": 5},
            {"field": "abdominal_pain", "op": "==", "value": 1},
            {"field": "nausea", "op": "==", "value": 1}
        ]),
        "outcome": "Enteric Fever Syndrome",
        "confidence_wt": 0.69,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-038",
        "condition_text": "Temperature > 39°C AND Relative Bradycardia = Present (Faget's Sign)",
        "condition_json": json.dumps([
            {"field": "temperature", "op": ">", "value": 39},
            {"field": "relative_bradycardia", "op": "==", "value": 1}
        ]),
        "outcome": "Faget Sign Present",
        "confidence_wt": 0.80,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-039",
        "condition_text": "Haemoglobin < 10 g/dL AND Platelet Count < 120 ×10⁹/L",
        "condition_json": json.dumps([
            {"field": "haemoglobin", "op": "<", "value": 10},
            {"field": "platelet_count", "op": "<", "value": 120}
        ]),
        "outcome": "Haematological Suppression",
        "confidence_wt": 0.73,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-040",
        "condition_text": "Fever Pattern = Step-ladder AND Temperature > 38.5°C",
        "condition_json": json.dumps([
            {"field": "fever_pattern", "op": "==", "value": "Step-ladder"},
            {"field": "temperature", "op": ">", "value": 38.5}
        ]),
        "outcome": "Enteric Fever Syndrome",
        "confidence_wt": 0.70,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-041",
        "condition_text": "Hepatosplenomegaly = Present AND ESR > 50 mm/hr",
        "condition_json": json.dumps([
            {"field": "hepatosplenomegaly", "op": "==", "value": 1},
            {"field": "esr", "op": ">", "value": 50}
        ]),
        "outcome": "Systemic Inflammatory Response",
        "confidence_wt": 0.68,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-042",
        "condition_text": "Neutrophil % < 40% AND Lymphocyte % > 45%",
        "condition_json": json.dumps([
            {"field": "neutrophil_pct", "op": "<", "value": 40},
            {"field": "lymphocyte_pct", "op": ">", "value": 45}
        ]),
        "outcome": "Atypical Differential",
        "confidence_wt": 0.71,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-043",
        "condition_text": "Widal O-titre ≥ 1:160 (Seropositive, suspicious for typhoid)",
        "condition_json": json.dumps([
            {"field": "widal_titre_enc", "op": ">=", "value": 4}
        ]),
        "outcome": "Seropositive Suspicious",
        "confidence_wt": 0.67,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-044",
        "condition_text": "Rose Spots = Present",
        "condition_json": json.dumps([
            {"field": "rose_spots", "op": "==", "value": 1}
        ]),
        "outcome": "Rose Spot Present",
        "confidence_wt": 0.88,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-045",
        "condition_text": "Constipation = Present AND Fever Duration > 5 days",
        "condition_json": json.dumps([
            {"field": "constipation", "op": "==", "value": 1},
            {"field": "fever_duration", "op": ">", "value": 5}
        ]),
        "outcome": "Enteric Fever Syndrome",
        "confidence_wt": 0.66,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-046",
        "condition_text": "Relative Bradycardia = Present (Faget's Sign)",
        "condition_json": json.dumps([
            {"field": "relative_bradycardia", "op": "==", "value": 1}
        ]),
        "outcome": "Faget Sign Present",
        "confidence_wt": 0.75,
        "category": "intermediate",
        "is_active": True,
    },
    {
        "rule_id": "R-047",
        "condition_text": "Leukocyte Count < 4.5 AND Platelet Count < 150 AND Haemoglobin < 12 g/dL",
        "condition_json": json.dumps([
            {"field": "leukocyte_count", "op": "<", "value": 4.5},
            {"field": "platelet_count", "op": "<", "value": 150},
            {"field": "haemoglobin", "op": "<", "value": 12}
        ]),
        "outcome": "Haematological Suppression",
        "confidence_wt": 0.76,
        "category": "intermediate",
        "is_active": True,
    },
]

# Intermediate outcome additive weights (added to positive confidence when fired)
INTERMEDIATE_ADDITIVE_WEIGHTS = {
    "Haematological Suppression": 0.12,
    "Enteric Fever Syndrome": 0.10,
    "Faget Sign Present": 0.15,
    "Rose Spot Present": 0.20,
    "Atypical Differential": 0.08,
    "Seropositive Suspicious": 0.06,
    "Systemic Inflammatory Response": 0.07,
}


def seed_rules(db_session, KnowledgeRule):
    """
    Seeds rules into DB if table is empty.
    Call from app.py after db.create_all()
    """
    from datetime import date as _date
    if db_session.query(KnowledgeRule).count() > 0:
        return  # Already seeded

    for rule_data in SEED_RULES:
        rule = KnowledgeRule(
            rule_id=rule_data['rule_id'],
            condition_text=rule_data['condition_text'],
            condition_json=rule_data['condition_json'],
            outcome=rule_data['outcome'],
            confidence_wt=rule_data['confidence_wt'],
            category=rule_data['category'],
            is_active=rule_data['is_active'],
            last_updated=_date.today(),
            updated_by='system'
        )
        db_session.add(rule)

    db_session.commit()
    print(f"[SEED] Seeded {len(SEED_RULES)} knowledge rules.")
