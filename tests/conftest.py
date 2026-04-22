"""
Configuration for pytest.
"""

import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def db(app):
    """Create database for testing."""
    from models import db as _db
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()