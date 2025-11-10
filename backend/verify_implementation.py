#!/usr/bin/env python3
"""Verification script for backend implementation."""
import sys
from pathlib import Path

def verify_structure():
    """Verify all required files exist."""
    required_files = [
        "app/main.py",
        "app/core/config.py",
        "app/db/session.py",
        "app/models/__init__.py",
        "app/schemas/__init__.py",
        "app/services/risk_service.py",
        "app/api/risk.py",
        "app/api/locations.py",
        "app/api/hazards.py",
        "app/api/historical.py",
        "tests/conftest.py",
        "tests/unit/test_schemas.py",
        "tests/unit/test_risk_service.py",
        "tests/integration/test_api_endpoints.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "init_db.py",
        "run.py",
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print("❌ Missing files:")
        for f in missing:
            print(f"  - {f}")
        return False
    
    print("✅ All required files present")
    return True

def verify_imports():
    """Verify key modules can be imported."""
    try:
        from app.main import app
        from app.core.config import settings
        from app.models import Location, Hazard, RiskAssessment, HistoricalData
        from app.schemas import LocationCreate, RiskAssessmentRequest
        from app.services import RiskCalculationService
        print("✅ All modules import successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all verifications."""
    print("Backend Implementation Verification\n")
    
    checks = [
        verify_structure(),
        verify_imports(),
    ]
    
    if all(checks):
        print("\n🎉 All verifications passed!")
        return 0
    else:
        print("\n⚠️  Some verifications failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
