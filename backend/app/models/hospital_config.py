# backend/app/models/hospital_config.py
"""
Hospital configuration model for configurable thresholds.
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class HospitalConfig(Base):
    """Hospital-specific configuration overrides."""
    __tablename__ = "hospital_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)  # FIXED: Added ForeignKey
    config_type = Column(String(50), nullable=False)  # 'threshold', 'unit_size', 'rule_override'
    config_key = Column(String(100), nullable=False)  # e.g., 'rbc_threshold_ward', 'rbc_bag_size'
    config_value = Column(JSON, nullable=False)  # Configuration value (can be any JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    hospital = relationship("Hospital", back_populates="configs")  # ADDED: Relationship
    
    # Example configs:
    # {"type": "threshold", "key": "rbc_threshold_ward", "value": 7.0}
    # {"type": "threshold", "key": "rbc_threshold_icu", "value": 8.5}
    # {"type": "unit_size", "key": "rbc_bag_size_ml", "value": 450}