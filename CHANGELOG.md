# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Integrated African Typhoid Fever Dataset (17,000 samples) for ML training
- Hybrid diagnosis engine with adaptive thresholds for gray-zone cases
- Full evaluation pipeline with precision/recall metrics

### Changed
- Adjusted Expert System thresholds (HIGH: 0.85, LOW: 0.10) for better recall
- Updated ML training to use real clinical data from HuggingFace

## [1.0.0] - 2024-04-22

### Added
- User authentication and role-based access control
- Hybrid diagnosis engine combining:
  - Rule-based expert system (47 clinical rules)
  - Random Forest machine learning classifier
  - Decision Tree classifier
- Admin panel for:
  - User management
  - Knowledge rule CRUD
  - Diagnosis reports
  - ML model retraining
- Diagnosis history with reasoning trace
- Audit logging

### Fixed
- Database initialization on first startup
- Session management with CSRF protection

## [0.1.0] - 2024-01-15

### Added
- Initial prototype
- Basic Flask structure
- Simplified inference engine