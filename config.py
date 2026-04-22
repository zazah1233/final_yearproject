import os
from pathlib import Path
from datetime import timedelta
import logging

BASE_DIR = Path(__file__).parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        f'sqlite:///{BASE_DIR / "zazah.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    THRESHOLD_HIGH = float(os.environ.get('THRESHOLD_HIGH', 0.85))
    THRESHOLD_LOW = float(os.environ.get('THRESHOLD_LOW', 0.10))
    RF_THRESHOLD = float(os.environ.get('RF_THRESHOLD', 0.50))
    
    MODEL_PATH = BASE_DIR / 'data' / 'rf_model.joblib'
    PREPROCESSOR_PATH = BASE_DIR / 'data' / 'preprocessor.joblib'
    
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    REMEMBER_COOKIE_SECURE = os.environ.get('REMEMBER_COOKIE_SECURE', 'false').lower() == 'true'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = os.environ.get('REMEMBER_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    LOG_LEVEL = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
    LOG_FILE = os.environ.get('LOG_FILE', str(BASE_DIR / 'zazah.log'))
