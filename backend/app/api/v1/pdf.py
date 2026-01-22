from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.recommendation import Recommendation
from app.models.patient import PatientEncounter
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.pdf_export import PDFExportService
import tempfile
import os

router = APIRouter()
pdf_service = PDFExportService()

@router.get("/encounter/{encounter_id}/pdf")
async def export_encounter_pdf(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export encounter recommendations as PDF."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        encounter = db.query(PatientEncounter).filter(
            PatientEncounter.id == encounter_id
        ).first()
        
        if not encounter:
            logger.error(f"Encounter {encounter_id} not found")
            raise HTTPException(status_code=404, detail="Encounter not found")
        
        # Get all recommendations for the encounter
        all_recommendations = db.query(Recommendation).filter(
            Recommendation.encounter_id == encounter.id
        ).order_by(Recommendation.id).all()
        
        if not all_recommendations:
            logger.error(f"No recommendations found for encounter {encounter_id}")
            raise HTTPException(status_code=404, detail="No recommendations found for this encounter")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying database: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Build encounter data
    encounter_data = {
        "age_years": encounter.age_years,
        "weight_kg": encounter.weight_kg,
        "sex": encounter.sex,
        "setting": encounter.setting.value.lower() if encounter.setting else None,
        "active_bleeding": encounter.active_bleeding,
        "hemodynamic_instability": encounter.hemodynamic_instability,
        # Add more fields if available
        "created_at": encounter.created_at.isoformat() if encounter.created_at else None
    }
    
    # Build multi-component recommendation dict
    components = []
    for rec in all_recommendations:
        components.append({
            "component": rec.component,
            "action": "recommend",  # Could be enhanced
            "dose_text": rec.dose_text,
            "units": rec.units,
            "volume_ml": rec.volume_ml,
            "expected_increment": rec.expected_increment,
            "recheck_plan": rec.recheck_plan,
            "why": rec.why or [],
            "warnings": rec.warnings or [],
            "references": rec.references or [],
            "rule_ids": rec.rule_ids or [],
        })
    
    recommendation_dict = {
        "components": components,
        "rule_version": all_recommendations[0].rule_version if all_recommendations else "N/A",
        "mtp_protocol": encounter.active_bleeding and len([r for r in all_recommendations if r.component]) >= 2,
        "overall_warnings": []
    }
    
    # Generate PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf_path = pdf_service.generate_recommendation_pdf(
            recommendation_dict,
            encounter_data,
            tmp.name
        )
    
    # Log audit
    from app.models.audit import AuditLog
    audit_log = AuditLog(
        encounter_id=encounter.id,
        recommendation_id=all_recommendations[0].id if all_recommendations else None,
        action="export",
        user_id=current_user.id,
        rule_version=all_recommendations[0].rule_version if all_recommendations else "N/A"
    )
    db.add(audit_log)
    db.commit()
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not created at path: {pdf_path}")
        raise HTTPException(status_code=500, detail="PDF file was not generated")
    
    try:
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"transfusion-recommendation-{encounter_id}.pdf",
            background=None
        )
    except Exception as e:
        logger.error(f"Error returning PDF file: {str(e)}", exc_info=True)
        # Clean up on error
        if os.path.exists(pdf_path):
            try:
                os.unlink(pdf_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to return PDF: {str(e)}")
    # Note: FileResponse will handle file cleanup automatically

@router.get("/{recommendation_id}/pdf")
async def export_recommendation_pdf(
    recommendation_id: int,
    language: str = "en",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export recommendation as PDF with language support (en/bn)."""
    # Get all recommendations for this encounter (multi-component)
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Get all recommendations for the encounter
    encounter = recommendation.encounter
    all_recommendations = db.query(Recommendation).filter(
        Recommendation.encounter_id == encounter.id
    ).order_by(Recommendation.id).all()
    
    # Build encounter data
    encounter_data = {
        "age_years": encounter.age_years,
        "weight_kg": encounter.weight_kg,
        "sex": encounter.sex,
        "setting": encounter.setting.value.lower() if encounter.setting else None,
        "active_bleeding": encounter.active_bleeding,
        "hemodynamic_instability": encounter.hemodynamic_instability,
    }
    
    # Build multi-component recommendation dict
    components = []
    for rec in all_recommendations:
        components.append({
            "component": rec.component,
            "action": "recommend",  # Could be enhanced
            "dose_text": rec.dose_text,
            "units": rec.units,
            "volume_ml": rec.volume_ml,
            "expected_increment": rec.expected_increment,
            "recheck_plan": rec.recheck_plan,
            "why": rec.why,
            "warnings": rec.warnings,
            "references": rec.references,
            "rule_ids": rec.rule_ids,
        })
    
    recommendation_dict = {
        "components": components,
        "rule_version": all_recommendations[0].rule_version if all_recommendations else "N/A",
        "mtp_protocol": encounter.active_bleeding and len([r for r in all_recommendations if r.component]) >= 2,
        "overall_warnings": []
    }
    
    # Generate PDF with language support
    lang = "bn" if language.lower() == "bn" else "en"
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf_path = pdf_service.generate_recommendation_pdf(
            recommendation_dict,
            encounter_data,
            tmp.name,
            language=lang
        )
    
    # Log audit
    from app.models.audit import AuditLog
    audit_log = AuditLog(
        encounter_id=encounter.id,
        recommendation_id=recommendation.id,
        action="export",
        user_id=current_user.id,
        rule_version=recommendation.rule_version
    )
    db.add(audit_log)
    db.commit()
    
    try:
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"transfusion-recommendation-{recommendation_id}.pdf"
        )
    finally:
        # Clean up temp file after response
        if os.path.exists(pdf_path):
            try:
                os.unlink(pdf_path)
            except:
                pass  # Ignore cleanup errors
