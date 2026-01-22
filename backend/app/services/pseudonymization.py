"""
PHI Pseudonymization Service
Pseudonymizes patient identifiers by default for privacy protection.
"""
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.patient import PatientEncounter

def generate_pseudonymized_id(encounter_id: int, created_at: datetime) -> str:
    """
    Generate a pseudonymized ID for a patient encounter.
    Uses hash of encounter ID + timestamp for consistency.
    """
    # Use a combination that's consistent but not reversible
    salt = "transfusion_cds_salt_2024"  # In production, use env var
    data = f"{encounter_id}_{created_at.isoformat()}_{salt}"
    hash_obj = hashlib.sha256(data.encode())
    # Take first 16 characters for readability
    return f"ENC-{hash_obj.hexdigest()[:16].upper()}"

def pseudonymize_encounter(encounter: PatientEncounter, db: Session) -> PatientEncounter:
    """
    Pseudonymize a patient encounter by default.
    Removes or masks PHI while preserving clinical data.
    """
    if encounter.is_pseudonymized is False:
        # Already not pseudonymized, skip
        return encounter
    
    # Generate pseudonymized ID if not exists
    if not encounter.pseudonymized_id:
        encounter.pseudonymized_id = generate_pseudonymized_id(
            encounter.id,
            encounter.created_at or datetime.utcnow()
        )
    
    encounter.is_pseudonymized = True
    db.commit()
    return encounter

def get_pseudonymized_response(encounter: PatientEncounter, include_phi: bool = False) -> Dict[str, Any]:
    """
    Return encounter data with PHI removed/masked if pseudonymized.
    
    Args:
        encounter: PatientEncounter model
        include_phi: If True and user is authorized, include full data
    
    Returns:
        Dictionary with encounter data (pseudonymized by default)
    """
    if include_phi and not encounter.is_pseudonymized:
        # Authorized user requesting full data
        return {
            "id": encounter.id,
            "age_years": encounter.age_years,
            "age_months": encounter.age_months,
            "sex": encounter.sex,
            "weight_kg": encounter.weight_kg,
            "setting": encounter.setting.value if encounter.setting else None,
            "active_bleeding": encounter.active_bleeding,
            "hemodynamic_instability": encounter.hemodynamic_instability,
            # ... all fields
        }
    else:
        # Pseudonymized response (default)
        return {
            "pseudonymized_id": encounter.pseudonymized_id or f"ENC-{encounter.id:06d}",
            "age_years": encounter.age_years,  # Age is generally okay
            "age_months": encounter.age_months,
            # Sex might be masked depending on privacy policy
            "sex": "X" if encounter.is_pseudonymized else encounter.sex,
            "weight_kg": encounter.weight_kg,  # Clinical data preserved
            "setting": encounter.setting.value if encounter.setting else None,
            "active_bleeding": encounter.active_bleeding,
            "hemodynamic_instability": encounter.hemodynamic_instability,
            "hb_gdl": encounter.hb_gdl,
            "platelets_x109l": encounter.platelets_x109l,
            "inr": encounter.inr,
            "aptt_sec": encounter.aptt_sec,
            "fibrinogen_mgdl": encounter.fibrinogen_mgdl,
            "history_flags": encounter.history_flags,
            "procedure_risk": encounter.procedure_risk,
            "procedure_timing_hours": encounter.procedure_timing_hours,
            "component_availability": encounter.component_availability,
            "rbc_bag_size_ml": encounter.rbc_bag_size_ml,
            "leukoreduction_available": encounter.leukoreduction_available,
            "created_at": encounter.created_at.isoformat() if encounter.created_at else None,
            "is_pseudonymized": True,
            # Exclude: specific identifiers, created_by user info, etc.
        }
