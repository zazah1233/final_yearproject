import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        f'sqlite:///{BASE_DIR / "zazah.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    THRESHOLD_HIGH = 0.65
    THRESHOLD_LOW = 0.45
    
    MODEL_PATH = BASE_DIR / 'data' / 'rf_model.joblib'
    PREPROCESSOR_PATH = BASE_DIR / 'data' / 'preprocessor.joblib'
    
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
