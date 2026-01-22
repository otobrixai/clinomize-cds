# backend/app/api/v1/admin.py
"""
Admin-only endpoints.
AI features are ONLY accessible to admins - never to clinical users.
This enforces the AI boundary strictly.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.auth import require_admin
from app.models.user import User
from app.models.audit import AuditLog
from app.services.ai_explanation import AIExplanationService
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])

class EvidenceSummaryRequest(BaseModel):
    guideline_id: str
    topic: str = None

@router.get("/ai/evidence-summary")
async def get_ai_evidence_summary(
    guideline_id: str,
    topic: str = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)  # ADMIN ONLY - enforced
):
    """
    AI-generated evidence summary - ADMIN ONLY, never in clinical UI.
    
    This endpoint is strictly admin-only. AI features are never exposed
    to clinical users to maintain trust and regulatory compliance.
    """
    if not settings.AI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI is not enabled. Set AI_ENABLED=True in environment."
        )
    
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured"
        )
    
    try:
        service = AIExplanationService()
        summary = service.generate_evidence_summary(guideline_id, topic)
        
        # Log AI usage for audit trail
        audit_log = AuditLog(
            user_id=admin_user.id,
            action="ai_evidence_summary",
            metadata={
                "guideline_id": guideline_id,
                "topic": topic,
                "ai_enabled": True,
                "ai_model": "openai"  # Could be dynamic
            }
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "summary": summary,
            "disclaimer": "AI-generated content for administrative review only. Not for clinical use.",
            "guideline_id": guideline_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating AI summary: {str(e)}"
        )

@router.get("/ai/status")
async def get_ai_status(
    admin_user: User = Depends(require_admin)
):
    """
    Get AI service status - ADMIN ONLY.
    """
    return {
        "ai_enabled": settings.AI_ENABLED,
        "api_key_configured": bool(settings.OPENAI_API_KEY),
        "clinical_access": False,  # Hard-coded: AI never accessible to clinical users
        "admin_only": True,
        "note": "AI features are strictly admin-only and never exposed to clinical users"
    }
