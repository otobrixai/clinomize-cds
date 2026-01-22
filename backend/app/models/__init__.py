# Import order matters to avoid circular dependencies
from app.core.database import Base

# Core models first
from app.models.user import User
from app.models.hospital import Hospital
from app.models.patient import PatientEncounter
from app.models.recommendation import Recommendation
from app.models.audit import AuditLog
from app.models.user import User
from app.models.hospital_config import HospitalConfig

# Analytics models (depends on Hospital)
from app.models.analytics import BloodProductCost, AnalyticsMonthlySummary

# Optional: Create a list of all models for easy access
__all__ = [
    "Base",
    "User",
    "Hospital", 
    "PatientEncounter",
    "Recommendation",
    "AuditLog",
    "HospitalConfig",
    "BloodProductCost",
    "AnalyticsMonthlySummary",
]
