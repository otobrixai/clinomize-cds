from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.patient import PatientEncounter, Setting
from app.models.recommendation import Recommendation
from app.models.audit import AuditLog
from app.rules.engine import RulesEngine
from app.utils.safety import generate_safety_warnings, check_component_availability
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter()

class PatientInput(BaseModel):
    # Demographics
    age_years: float = Field(..., description="Patient age in years")
    age_months: float = Field(None, description="Patient age in months (for pediatrics)")
    sex: str = Field(..., description="Patient sex (M, F, Other)")
    weight_kg: float = Field(..., description="Patient weight in kg")
    
    # Context
    setting: str = Field(..., description="Setting: icu, or, er, ward")
    active_bleeding: bool = Field(False, description="Active bleeding present")
    hemodynamic_instability: bool = Field(False, description="Hemodynamic instability present")
    
    # Labs
    hb_gdl: float = Field(None, description="Hemoglobin in g/dL")
    platelets_x109l: float = Field(None, description="Platelets in ×10⁹/L")
    inr: float = Field(None, description="INR")
    aptt_sec: float = Field(None, description="aPTT in seconds")
    fibrinogen_mgdl: float = Field(None, description="Fibrinogen in mg/dL")
    
    # History flags
    history_flags: Dict[str, bool] = Field(default_factory=dict, description="History flags")
    
    # Procedure context
    procedure_risk: str = Field(None, description="Procedure risk: low, medium, high")
    procedure_timing_hours: float = Field(None, description="Procedure timing in hours")
    
    # Local constraints
    component_availability: Dict[str, bool] = Field(default_factory=dict)
    rbc_bag_size_ml: int = Field(350, description="RBC bag size: 350 or 450 mL")
    leukoreduction_available: bool = Field(True, description="Leukoreduction available")

class ComponentRecommendation(BaseModel):
    """Single component recommendation"""
    component: str | None
    action: str = "recommend"  # "recommend" or "contraindicate"
    dose_text: str
    units: float | None
    volume_ml: float | None
    expected_increment: str
    recheck_plan: str
    why: list[str]
    warnings: list[str]
    references: list[str]
    rule_ids: list[str]

class RecommendationResponse(BaseModel):
    """Multi-component recommendation plan"""
    components: list[ComponentRecommendation]
    rule_version: str
    overall_warnings: list[str] = []  # System-level warnings
    mtp_protocol: bool = False  # Indicates if this is MTP context
    encounter_id: int | None = None  # ID of the patient encounter
    recommendation_ids: list[int] = []  # IDs of saved recommendations

@router.post("/evaluate", response_model=RecommendationResponse)
async def evaluate_patient(
    patient_input: PatientInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluate patient data and return transfusion recommendation.
    Rules engine is authoritative - AI never overrides.
    """
    try:
        # Validate setting - convert to uppercase for enum
        setting_upper = patient_input.setting.upper()
        try:
            setting_enum = Setting(setting_upper)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid setting: {patient_input.setting}")
        
        # Create encounter record
        encounter = PatientEncounter(
            age_years=patient_input.age_years,
            age_months=patient_input.age_months,
            sex=patient_input.sex,
            weight_kg=patient_input.weight_kg,
            setting=setting_enum,
            active_bleeding=patient_input.active_bleeding,
            hemodynamic_instability=patient_input.hemodynamic_instability or False,
            hb_gdl=patient_input.hb_gdl,
            platelets_x109l=patient_input.platelets_x109l,
            inr=patient_input.inr,
            aptt_sec=patient_input.aptt_sec,
            fibrinogen_mgdl=patient_input.fibrinogen_mgdl,
            history_flags=patient_input.history_flags,
            procedure_risk=patient_input.procedure_risk,
            procedure_timing_hours=patient_input.procedure_timing_hours,
            component_availability=patient_input.component_availability,
            rbc_bag_size_ml=patient_input.rbc_bag_size_ml,
            leukoreduction_available=patient_input.leukoreduction_available,
            created_by=current_user.id
        )
        
        db.add(encounter)
        db.commit()
        db.refresh(encounter)
        
        # Pseudonymize by default (PHI protection)
        from app.services.pseudonymization import pseudonymize_encounter
        encounter = pseudonymize_encounter(encounter, db)
        db.refresh(encounter)
        
        # Evaluate using rules engine - returns list of recommendations
        rules_engine = RulesEngine()
        encounter_dict = {
            "age_years": encounter.age_years,
            "age_months": encounter.age_months,
            "sex": encounter.sex,
            "weight_kg": encounter.weight_kg,
            "setting": encounter.setting.value.lower(),  # Convert to lowercase for rules matching
            "active_bleeding": encounter.active_bleeding,
            "hemodynamic_instability": encounter.hemodynamic_instability or False,
            "hb_gdl": encounter.hb_gdl,
            "platelets_x109l": encounter.platelets_x109l,
            "inr": encounter.inr,
            "aptt_sec": encounter.aptt_sec,
            "fibrinogen_mgdl": encounter.fibrinogen_mgdl,
            "history_flags": encounter.history_flags or {},
            "procedure_risk": encounter.procedure_risk,
            "procedure_timing_hours": encounter.procedure_timing_hours,
            "component_availability": encounter.component_availability or {},
            "rbc_bag_size_ml": encounter.rbc_bag_size_ml,
            "leukoreduction_available": encounter.leukoreduction_available,
        }
        
        # Get ALL matching recommendations (list)
        recommendation_candidates = rules_engine.evaluate(encounter_dict)
        
        # Process each recommendation candidate
        saved_recommendations = []
        overall_warnings = []
        component_recommendations = []
        
        for rec_data in recommendation_candidates:
            # Add safety warnings per component
            component = rec_data.get("component")
            safety_warnings = generate_safety_warnings(encounter_dict)
            rec_data["warnings"].extend(safety_warnings)
            
            # Check component availability (only for positive recommendations)
            if component and rec_data.get("action") == "recommend":
                available = check_component_availability(
                    component,
                    encounter_dict.get("component_availability", {})
                )
                if not available:
                    warning_msg = f"{component} not available - check local inventory"
                    rec_data["warnings"].append(warning_msg)
                    overall_warnings.append(warning_msg)
            
            # Save each component recommendation separately to database
            recommendation = Recommendation(
                encounter_id=encounter.id,
                component=component,
                dose_text=rec_data["dose_text"],
                units=rec_data.get("units"),
                volume_ml=rec_data.get("volume_ml"),
                expected_increment=rec_data["expected_increment"],
                recheck_plan=rec_data["recheck_plan"],
                why=rec_data["why"],
                warnings=rec_data["warnings"],
                references=rec_data["references"],
                rule_ids=rec_data["rule_ids"],
                rule_version=rec_data["rule_version"]
            )
            db.add(recommendation)
            saved_recommendations.append(recommendation)
            
            # Build component recommendation for response
            component_recommendations.append(
                ComponentRecommendation(
                    component=component,
                    action=rec_data.get("action", "recommend"),
                    dose_text=rec_data["dose_text"],
                    units=rec_data.get("units"),
                    volume_ml=rec_data.get("volume_ml"),
                    expected_increment=rec_data["expected_increment"],
                    recheck_plan=rec_data["recheck_plan"],
                    why=rec_data["why"],
                    warnings=rec_data["warnings"],
                    references=rec_data["references"],
                    rule_ids=rec_data["rule_ids"]
                )
            )
        
        db.commit()
        
        # Refresh to get IDs
        for rec in saved_recommendations:
            db.refresh(rec)
        
        # Check if this is MTP context (multiple components + active bleeding)
        positive_components = [r for r in saved_recommendations if r.component and r.component != "None"]
        is_mtp = (
            encounter.active_bleeding and 
            len(positive_components) >= 2
        )
        
        if is_mtp:
            overall_warnings.insert(0, "Massive Transfusion Protocol (MTP) context: Multiple components recommended")
        
        # Log audit for encounter (one log entry for the entire evaluation)
        from app.models.audit import AuditLog
        audit_log = AuditLog(
            encounter_id=encounter.id,
            recommendation_id=saved_recommendations[0].id if saved_recommendations else None,
            action="create",
            user_id=current_user.id,
            rule_version=recommendation_candidates[0]["rule_version"] if recommendation_candidates else rules_engine.version,
            metadata={
                "component_count": len(positive_components),
                "is_mtp": is_mtp,
                "component_types": [r.component for r in positive_components] if positive_components else []
            }
        )
        db.add(audit_log)
        db.commit()
        
        return RecommendationResponse(
            components=component_recommendations,
            rule_version=recommendation_candidates[0]["rule_version"] if recommendation_candidates else rules_engine.version,
            overall_warnings=overall_warnings,
            mtp_protocol=is_mtp,
            encounter_id=encounter.id,
            recommendation_ids=[r.id for r in saved_recommendations]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating patient: {str(e)}")

@router.get("/encounter/{encounter_id}", response_model=RecommendationResponse)
async def get_recommendations_for_encounter(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all recommendations for a specific encounter."""
    recommendations = db.query(Recommendation).filter(
        Recommendation.encounter_id == encounter_id
    ).order_by(Recommendation.id).all()
    
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found for this encounter")
    
    # Check if MTP context
    encounter = db.query(PatientEncounter).filter(PatientEncounter.id == encounter_id).first()
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    positive_components = [r for r in recommendations if r.component and r.component != "None"]
    is_mtp = encounter.active_bleeding and len(positive_components) >= 2
    
    overall_warnings = []
    if is_mtp:
        overall_warnings.append("Massive Transfusion Protocol (MTP) context: Multiple components recommended")
    
    component_recommendations = [
        ComponentRecommendation(
            component=r.component,
            action="recommend",  # Default, could be enhanced later
            dose_text=r.dose_text,
            units=r.units,
            volume_ml=r.volume_ml,
            expected_increment=r.expected_increment,
            recheck_plan=r.recheck_plan,
            why=r.why,
            warnings=r.warnings,
            references=r.references,
            rule_ids=r.rule_ids
        )
        for r in recommendations
    ]
    
    return RecommendationResponse(
        components=component_recommendations,
        rule_version=recommendations[0].rule_version,
        overall_warnings=overall_warnings,
        mtp_protocol=is_mtp,
        encounter_id=encounter_id,
        recommendation_ids=[r.id for r in recommendations]
    )

@router.get("/{recommendation_id}")
async def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific recommendation by ID (for backward compatibility)."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Return single component recommendation (for backward compatibility)
    return ComponentRecommendation(
        component=recommendation.component,
        action="recommend",
        dose_text=recommendation.dose_text,
        units=recommendation.units,
        volume_ml=recommendation.volume_ml,
        expected_increment=recommendation.expected_increment,
        recheck_plan=recommendation.recheck_plan,
        why=recommendation.why,
        warnings=recommendation.warnings,
        references=recommendation.references,
        rule_ids=recommendation.rule_ids
    )

class OutcomeUpdate(BaseModel):
    """Model for recording actual transfusion outcome"""
    actual_transfusion_given: bool
    components_given: Dict[str, bool] = Field(default_factory=dict)
    post_transfusion_hb: Optional[float] = None
    post_transfusion_platelets: Optional[float] = None

@router.post("/{recommendation_id}/outcome")
async def record_outcome(
    recommendation_id: int,
    outcome: OutcomeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record actual transfusion outcome (optional, for QA purposes).
    
    This allows tracking whether recommendations were followed and
    what the actual outcomes were, which is valuable for quality
    improvement and regulatory compliance.
    """
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Update outcome fields
    recommendation.actual_transfusion_given = outcome.actual_transfusion_given
    recommendation.components_given = outcome.components_given
    recommendation.post_transfusion_hb = outcome.post_transfusion_hb
    recommendation.post_transfusion_platelets = outcome.post_transfusion_platelets
    recommendation.outcome_recorded_at = func.now()
    recommendation.outcome_recorded_by = current_user.id
    
    db.commit()
    db.refresh(recommendation)
    
    # Log audit
    audit_log = AuditLog(
        recommendation_id=recommendation.id,
        encounter_id=recommendation.encounter_id,
        action="outcome_recorded",
        user_id=current_user.id,
        metadata={
            "outcome": outcome.dict(),
            "recommendation_component": recommendation.component
        }
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "status": "outcome recorded",
        "recommendation_id": recommendation.id,
        "recorded_at": recommendation.outcome_recorded_at.isoformat() if recommendation.outcome_recorded_at else None
    }