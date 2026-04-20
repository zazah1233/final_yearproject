"""
ml/train.py
-----------
Generates a synthetic dataset matching the paper's statistics,
trains both Decision Tree and Random Forest classifiers,
and saves all artefacts to data/ directory.

Run this ONCE before starting the Flask app:
    python ml/train.py

Paper stats to match:
  - n=487 total (241 positive, 246 negative)
  - Fever duration: positive mean=8.2d (SD 3.1), negative mean=4.7d (SD 2.6)
  - WBC: positive mean=4.1 (SD 1.8), negative mean=8.7 (SD 3.2)
  - Platelet: positive mean=142 (SD 67), negative mean=224 (SD 89)
  - Hepatosplenomegaly: positive 58.1%, negative 12.2%
  - Relative bradycardia: positive 43.6%, negative 8.9%
  - RF performance target: ~91.8% accuracy, AUC ~0.963
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, confusion_matrix,
                              classification_report)

# Ensure we can import from parent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(DATA_DIR, exist_ok=True)


# ──────────────────────────────────────────────
# 1. SYNTHETIC DATA GENERATION
# ──────────────────────────────────────────────

def generate_synthetic_dataset(n_positive=241, n_negative=246):
    """
    Generate a synthetic dataset matching the published paper statistics.
    Each feature is sampled from distributions calibrated to the paper.
    """
    rng = np.random.RandomState(RANDOM_STATE)

    def make_group(n, label):
        is_pos = (label == 1)

        data = {}
        data['label'] = [label] * n

        # Demographics
        data['age'] = rng.normal(24.7 if is_pos else 26.1,
                                  14.3 if is_pos else 15.8, n).clip(1, 90).astype(int)
        data['sex'] = rng.choice(['Male', 'Female'], n, p=[0.476, 0.524])

        # Fever duration
        data['fever_duration'] = rng.normal(8.2 if is_pos else 4.7,
                                             3.1 if is_pos else 2.6, n).clip(1, 30)

        # Fever pattern
        if is_pos:
            data['fever_pattern'] = rng.choice(
                ['Step-ladder', 'Continuous', 'Remittent', 'Intermittent'],
                n, p=[0.45, 0.30, 0.15, 0.10])
        else:
            data['fever_pattern'] = rng.choice(
                ['Step-ladder', 'Continuous', 'Remittent', 'Intermittent'],
                n, p=[0.10, 0.40, 0.30, 0.20])

        # Headache severity (1-5)
        data['headache_severity'] = rng.choice([1,2,3,4,5], n,
            p=[0.05, 0.15, 0.30, 0.35, 0.15] if is_pos else
               [0.20, 0.30, 0.25, 0.20, 0.05])

        # Binary symptoms
        data['abdominal_pain'] = rng.binomial(1, 0.72 if is_pos else 0.28, n)
        data['relative_bradycardia'] = rng.binomial(1, 0.436 if is_pos else 0.089, n)
        data['hepatosplenomegaly'] = rng.binomial(1, 0.581 if is_pos else 0.122, n)
        data['diarrhoea'] = rng.binomial(1, 0.25 if is_pos else 0.35, n)
        data['vomiting'] = rng.binomial(1, 0.35 if is_pos else 0.45, n)
        data['rose_spots'] = rng.binomial(1, 0.15 if is_pos else 0.01, n)
        data['nausea'] = rng.binomial(1, 0.55 if is_pos else 0.50, n)
        data['constipation'] = rng.binomial(1, 0.40 if is_pos else 0.20, n)

        # Laboratory values
        data['leukocyte_count'] = rng.normal(4.1 if is_pos else 8.7,
                                              1.8 if is_pos else 3.2, n).clip(0.5, 25)
        data['platelet_count'] = rng.normal(142 if is_pos else 224,
                                             67 if is_pos else 89, n).clip(20, 600)
        data['neutrophil_pct'] = rng.normal(40 if is_pos else 72,
                                             12 if is_pos else 10, n).clip(5, 95)
        data['esr'] = rng.normal(45 if is_pos else 28,
                                  20 if is_pos else 15, n).clip(1, 120)
        data['haemoglobin'] = rng.normal(11.3 if is_pos else 12.4,
                                          2.1 if is_pos else 1.8, n).clip(5, 18)
        data['lymphocyte_pct'] = rng.normal(45 if is_pos else 22,
                                             10 if is_pos else 8, n).clip(5, 80)
        data['monocyte_pct'] = rng.normal(8 if is_pos else 7,
                                           3 if is_pos else 3, n).clip(0, 20)
        data['temperature'] = rng.normal(38.9 if is_pos else 38.3,
                                          0.8 if is_pos else 0.9, n).clip(36.5, 41.5)

        # Widal titre
        if is_pos:
            data['widal_titre'] = rng.choice(
                ['Negative', '1:20', '1:40', '1:80', '1:160', '1:320', '>=1:640'],
                n, p=[0.05, 0.05, 0.10, 0.19, 0.30, 0.20, 0.11])
        else:
            data['widal_titre'] = rng.choice(
                ['Negative', '1:20', '1:40', '1:80', '1:160', '1:320', '>=1:640'],
                n, p=[0.35, 0.20, 0.17, 0.15, 0.08, 0.04, 0.01])

        return pd.DataFrame(data)

    pos_df = make_group(n_positive, 1)
    neg_df = make_group(n_negative, 0)
    df = pd.concat([pos_df, neg_df], ignore_index=True)
    df = df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    return df


# ──────────────────────────────────────────────
# 2. PREPROCESSING
# ──────────────────────────────────────────────

WIDAL_ORDER = ['Negative', '1:20', '1:40', '1:80', '1:160', '1:320', '>=1:640']
FEVER_PATTERN_CATS = ['Step-ladder', 'Continuous', 'Remittent', 'Intermittent']
SEX_CATS = ['Male', 'Female', 'Other']

CONTINUOUS_COLS = ['age', 'fever_duration', 'leukocyte_count', 'platelet_count',
                   'neutrophil_pct', 'esr', 'haemoglobin', 'lymphocyte_pct',
                   'monocyte_pct', 'temperature']

BINARY_COLS = ['abdominal_pain', 'relative_bradycardia', 'hepatosplenomegaly',
               'diarrhoea', 'vomiting', 'rose_spots', 'nausea', 'constipation']


def preprocess(df, scaler=None, fit=False):
    """
    Transforms raw DataFrame into a numeric feature matrix.
    Returns (X_array, fitted_scaler, feature_names)
    """
    df = df.copy()

    # Label encode Widal titre (ordinal)
    df['widal_titre_enc'] = df['widal_titre'].map(
        {v: i for i, v in enumerate(WIDAL_ORDER)}).fillna(0).astype(int)

    # Headache severity already numeric 1-5; shift to 0-4
    df['headache_severity_enc'] = df['headache_severity'] - 1

    # One-hot encode sex
    for cat in SEX_CATS:
        df[f'sex_{cat}'] = (df['sex'] == cat).astype(int)

    # One-hot encode fever pattern
    for cat in FEVER_PATTERN_CATS:
        df[f'fever_pattern_{cat.replace("-","_")}'] = (df['fever_pattern'] == cat).astype(int)

    # Build feature columns list
    feature_cols = (
        CONTINUOUS_COLS +
        BINARY_COLS +
        ['widal_titre_enc', 'headache_severity_enc'] +
        [f'sex_{c}' for c in SEX_CATS] +
        [f'fever_pattern_{c.replace("-","_")}' for c in FEVER_PATTERN_CATS]
    )

    X = df[feature_cols].values.astype(float)

    if fit:
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)
    else:
        X = scaler.transform(X)

    return X, scaler, feature_cols


# ──────────────────────────────────────────────
# 3. TRAINING
# ──────────────────────────────────────────────

def train():
    print("=" * 60)
    print("ZAZAH — ML Training Script")
    print("=" * 60)

    # Generate data
    print("\n[1/5] Generating synthetic dataset...")
    df = generate_synthetic_dataset()
    print(f"      Dataset: {len(df)} records ({df['label'].sum()} positive, "
          f"{(df['label']==0).sum()} negative)")

    # Split
    print("\n[2/5] Splitting 70/30 stratified...")
    X_raw_train, X_raw_test, y_train, y_test = train_test_split(
        df.drop('label', axis=1), df['label'],
        test_size=0.30, stratify=df['label'], random_state=RANDOM_STATE
    )
    print(f"      Train: {len(X_raw_train)}, Test: {len(X_raw_test)}")

    # Preprocess
    print("\n[3/5] Preprocessing...")
    X_train, fitted_scaler, feature_names = preprocess(X_raw_train, fit=True)
    X_test, _, _ = preprocess(X_raw_test, scaler=fitted_scaler, fit=False)

    # Save preprocessor artefact
    preprocessor_artefact = {
        'scaler': fitted_scaler,
        'feature_names': feature_names,
        'widal_order': WIDAL_ORDER,
        'fever_pattern_cats': FEVER_PATTERN_CATS,
        'sex_cats': SEX_CATS,
        'continuous_cols': CONTINUOUS_COLS,
        'binary_cols': BINARY_COLS,
    }
    joblib.dump(preprocessor_artefact, os.path.join(DATA_DIR, 'preprocessor.joblib'))
    print(f"      Preprocessor saved → data/preprocessor.joblib")
    print(f"      Feature count: {len(feature_names)}")

    # Train models
    print("\n[4/5] Training models...")

    # Decision Tree
    dt = DecisionTreeClassifier(
        max_depth=7, min_samples_split=5, min_samples_leaf=2,
        criterion='gini', random_state=RANDOM_STATE
    )
    dt.fit(X_train, y_train)
    joblib.dump(dt, os.path.join(DATA_DIR, 'dt_model.joblib'))

    # Random Forest
    rf = RandomForestClassifier(
        n_estimators=200, max_depth=10, max_features='sqrt',
        min_samples_split=2, bootstrap=True,
        criterion='gini', random_state=RANDOM_STATE, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    joblib.dump(rf, os.path.join(DATA_DIR, 'rf_model.joblib'))
    print("      Models saved → data/rf_model.joblib, data/dt_model.joblib")

    # Feature importance
    importances = dict(zip(feature_names, rf.feature_importances_))
    sorted_importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
    joblib.dump(sorted_importances, os.path.join(DATA_DIR, 'feature_importances.joblib'))

    # Evaluate
    print("\n[5/5] Evaluation on test set (n={})...".format(len(X_test)))
    for name, model in [('Decision Tree', dt), ('Random Forest', rf)]:
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        print(f"\n  {name}:")
        print(f"    Accuracy:  {acc:.3f}")
        print(f"    Precision: {prec:.3f}")
        print(f"    Recall:    {rec:.3f}")
        print(f"    F1-Score:  {f1:.3f}")
        print(f"    ROC-AUC:   {auc:.3f}")
        cm = confusion_matrix(y_test, y_pred)
        print(f"    Confusion Matrix:\n{cm}")

    # Save evaluation metrics for the admin dashboard
    eval_metrics = {
        'rf': {
            'accuracy': float(accuracy_score(y_test, rf.predict(X_test))),
            'precision': float(precision_score(y_test, rf.predict(X_test))),
            'recall': float(recall_score(y_test, rf.predict(X_test))),
            'f1': float(f1_score(y_test, rf.predict(X_test))),
            'auc': float(roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1])),
        },
        'dt': {
            'accuracy': float(accuracy_score(y_test, dt.predict(X_test))),
            'f1': float(f1_score(y_test, dt.predict(X_test))),
            'auc': float(roc_auc_score(y_test, dt.predict_proba(X_test)[:, 1])),
        },
        'n_train': len(X_train),
        'n_test': len(X_test),
        'feature_names': feature_names,
    }
    joblib.dump(eval_metrics, os.path.join(DATA_DIR, 'eval_metrics.joblib'))

    print("\n" + "=" * 60)
    print("Training complete. All artefacts saved to data/")
    print("=" * 60)


if __name__ == '__main__':
    train()
