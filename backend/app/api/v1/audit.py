from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.models.audit import AuditLog
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter()

class OverrideRequest(BaseModel):
    recommendation_id: int
    override_reason: str
    override_component: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    encounter_id: Optional[int]
    recommendation_id: Optional[int]
    action: str
    override_reason: Optional[str]
    override_component: Optional[str]
    rule_version: Optional[str]
    created_at: str

@router.post("/override")
async def log_override(
    override_request: OverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log an override action when clinician deviates from recommendation.
    Requires reason for audit trail.
    """
    # Verify recommendation exists
    from app.models.recommendation import Recommendation
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == override_request.recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Create audit log
    audit_log = AuditLog(
        encounter_id=recommendation.encounter_id,
        recommendation_id=override_request.recommendation_id,
        action="override",
        user_id=current_user.id,
        override_reason=override_request.override_reason,
        override_component=override_request.override_component,
        rule_version=recommendation.rule_version
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return {"message": "Override logged successfully", "audit_log_id": audit_log.id}

@router.get("/logs/{encounter_id}", response_model=List[AuditLogResponse])
async def get_audit_logs(
    encounter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs for a specific encounter."""
    logs = db.query(AuditLog).filter(
        AuditLog.encounter_id == encounter_id
    ).order_by(AuditLog.created_at.desc()).all()
    
    return [
        AuditLogResponse(
            id=log.id,
            encounter_id=log.encounter_id,
            recommendation_id=log.recommendation_id,
            action=log.action,
            override_reason=log.override_reason,
            override_component=log.override_component,
            rule_version=log.rule_version,
            created_at=log.created_at.isoformat()
        )
        for log in logs
    ]
