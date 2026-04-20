from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .system_user import SystemUser
from .patient_record import PatientRecord
from .diagnostic_result import DiagnosticResult
from .knowledge_rule import KnowledgeRule
from .audit_log import AuditLog

__all__ = ['db', 'SystemUser', 'PatientRecord', 'DiagnosticResult', 'KnowledgeRule', 'AuditLog']