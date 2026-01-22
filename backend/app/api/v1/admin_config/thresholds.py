"""
Admin API for hospital-configurable thresholds.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.core.auth import require_admin
from app.models.user import User
from app.models.hospital_config import HospitalConfig

router = APIRouter(prefix="/thresholds", tags=["admin"])

class ThresholdConfig(BaseModel):
    config_key: str = Field(..., description="Configuration key (e.g., 'rbc_threshold_ward')")
    config_value: Any = Field(..., description="Configuration value")
    config_type: str = Field(default="threshold", description="Type of config")
    is_active: bool = Field(default=True)

class ThresholdConfigResponse(BaseModel):
    id: int
    config_key: str
    config_value: Any
    config_type: str
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None

@router.get("", response_model=List[ThresholdConfigResponse])
async def get_thresholds(
    config_type: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Get all hospital threshold configurations."""
    query = db.query(HospitalConfig).filter(HospitalConfig.is_active == True)
    
    if config_type:
        query = query.filter(HospitalConfig.config_type == config_type)
    
    configs = query.order_by(HospitalConfig.config_key).all()
    
    return [
        ThresholdConfigResponse(
            id=c.id,
            config_key=c.config_key,
            config_value=c.config_value,
            config_type=c.config_type,
            is_active=c.is_active,
            created_at=c.created_at.isoformat() if c.created_at else "",
            updated_at=c.updated_at.isoformat() if c.updated_at else None
        )
        for c in configs
    ]

@router.post("", response_model=ThresholdConfigResponse)
async def create_threshold(
    config: ThresholdConfig,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Create or update a threshold configuration."""
    # Check if exists
    existing = db.query(HospitalConfig).filter(
        HospitalConfig.config_key == config.config_key,
        HospitalConfig.config_type == config.config_type,
        HospitalConfig.is_active == True
    ).first()
    
    if existing:
        # Update existing
        existing.config_value = config.config_value
        existing.is_active = config.is_active
        existing.updated_at = func.now()
        existing.created_by = admin_user.id
    else:
        # Create new
        existing = HospitalConfig(
            config_key=config.config_key,
            config_value=config.config_value,
            config_type=config.config_type,
            is_active=config.is_active,
            created_by=admin_user.id
        )
        db.add(existing)
    
    db.commit()
    db.refresh(existing)
    
    return ThresholdConfigResponse(
        id=existing.id,
        config_key=existing.config_key,
        config_value=existing.config_value,
        config_type=existing.config_type,
        is_active=existing.is_active,
        created_at=existing.created_at.isoformat() if existing.created_at else "",
        updated_at=existing.updated_at.isoformat() if existing.updated_at else None
    )

@router.delete("/{config_id}")
async def delete_threshold(
    config_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Deactivate a threshold configuration."""
    config = db.query(HospitalConfig).filter(HospitalConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    config.is_active = False
    config.updated_at = func.now()
    db.commit()
    
    return {"status": "deactivated", "config_id": config_id}
