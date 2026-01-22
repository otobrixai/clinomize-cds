from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.cardioiq.service import CardioIQService
from app.cardioiq.schemas import CardioIQInput, CardioIQOutput
from app.models.cardioiq import CardioIQEncounter, CardioIQRecommendation, CardioIQAuditLog
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/evaluate", response_model=CardioIQOutput)
async def evaluate_patient(
    patient_input: CardioIQInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluate patient data and return cardiac recommendation.
    Rules engine is authoritative - deterministic logic only.
    Saves encounter and recommendation to database with audit trail.
    """
    try:
        # Create encounter record
        encounter = CardioIQEncounter(
            hospital_id=current_user.hospital_id,
            patient_id=f"CARDIO_{current_user.hospital_id}_{db.query(CardioIQEncounter).count() + 1}",  # Pseudonymized
            age=patient_input.patient.age,
            sex=patient_input.patient.sex,
            weight_kg=patient_input.patient.weight_kg,
            chest_pain=patient_input.presentation.chest_pain,
            chest_pain_type=patient_input.presentation.chest_pain_type,
            dyspnea=patient_input.presentation.dyspnea,
            syncope=patient_input.presentation.syncope,
            sbp=patient_input.vitals.sbp,
            hr=patient_input.vitals.hr,
            spo2=patient_input.vitals.spo2,
            st_elevation=patient_input.ecg.st_elevation,
            st_depression=patient_input.ecg.st_depression,
            t_wave_inversion=patient_input.ecg.t_wave_inversion,
            non_diagnostic_ecg=patient_input.ecg.non_diagnostic,
            ecg_confidence=patient_input.ecg.confidence,
            troponin_status=patient_input.labs.troponin_status,
            troponin_positive=patient_input.labs.troponin.positive if patient_input.labs.troponin else None,
            troponin_value=patient_input.labs.troponin.value if patient_input.labs.troponin else None,
            creatinine=patient_input.labs.creatinine,
            potassium=patient_input.labs.potassium,
            history_cad=patient_input.history.cad,
            history_diabetes=patient_input.history.diabetes,
            history_hypertension=patient_input.history.hypertension,
            history_ckd=patient_input.history.ckd,
            history_heart_failure=patient_input.history.heart_failure,
            history_stroke=patient_input.history.stroke,
            on_beta_blocker=patient_input.medications.beta_blocker,
            on_digoxin=patient_input.medications.digoxin,
            on_qt_prolonging_drugs=patient_input.medications.qt_prolonging_drugs,
            care_setting=patient_input.context.care_setting,
            has_cath_lab=patient_input.context.hospital_capability.get('has_cath_lab', False),
            can_transfer_pci=patient_input.context.hospital_capability.get('can_transfer_primary_pci', False),
            has_troponin=patient_input.context.hospital_capability.get('has_on_site_troponin', True),
            created_by=current_user.id
        )
        
        db.add(encounter)
        db.flush()  # Get encounter ID without committing
        
        # Call CardioIQ service
        result = CardioIQService.evaluate_patient(patient_input)
        
        # Save recommendation
        recommendation = CardioIQRecommendation(
            encounter_id=encounter.id,
            clinical_category=result.clinical_category,
            recommended_level_of_care=result.recommended_level_of_care,
            risk_scores=[score.model_dump() for score in result.risk_scores] if result.risk_scores else [],
            recommended_actions=result.recommended_actions,
            safety_warnings=result.safety_warnings,
            cost_flags=result.cost_flags,
            rationale_summary=result.rationale_summary,
            guideline_links=result.guideline_links,
            rule_hits=result.rule_hits,
            rule_version="1.1.0",
            engine_version="1.0.0"
        )
        
        db.add(recommendation)
        db.flush()
        
        # Create audit log
        audit_log = CardioIQAuditLog(
            encounter_id=encounter.id,
            recommendation_id=recommendation.id,
            action="create",
            user_id=current_user.id,
            rule_version="1.1.0",
            action_metadata={
                "clinical_category": result.clinical_category,
                "level_of_care": result.recommended_level_of_care,
                "num_actions": len(result.recommended_actions),
                "num_warnings": len(result.safety_warnings) if result.safety_warnings else 0
            }
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(encounter)
        db.refresh(recommendation)
        
        return result
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error evaluating patient: {str(e)}")


@router.get("/encounter/{encounter_id}")
async def get_encounter(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CardioIQ encounter and recommendation by ID"""
    encounter = db.query(CardioIQEncounter).filter(
        CardioIQEncounter.id == encounter_id
    ).first()
    
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    return {
        "encounter": encounter,
        "recommendation": encounter.recommendation
    }


@router.post("/{recommendation_id}/outcome")
async def record_outcome(
    recommendation_id: int,
    actual_level_of_care: str,
    recommendation_followed: bool,
    outcome_notes: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record actual outcome for QA purposes"""
    recommendation = db.query(CardioIQRecommendation).filter(
        CardioIQRecommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.actual_level_of_care = actual_level_of_care
    recommendation.recommendation_followed = recommendation_followed
    recommendation.outcome_notes = outcome_notes
    recommendation.outcome_recorded_by = current_user.id
    from sqlalchemy.sql import func
    recommendation.outcome_recorded_at = func.now()
    
    # Create audit log
    audit_log = CardioIQAuditLog(
        encounter_id=recommendation.encounter_id,
        recommendation_id=recommendation.id,
        action="outcome_recorded",
        user_id=current_user.id,
        action_metadata={
            "actual_level_of_care": actual_level_of_care,
            "recommendation_followed": recommendation_followed
        }
    )
    
    db.add(audit_log)
    db.commit()
    
    return {"status": "outcome recorded", "recommendation_id": recommendation_id}
