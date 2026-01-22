from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("patient_encounters.id"), nullable=False)
    
    # Structured output
    component = Column(String, nullable=True)  # RBC, Platelet, FFP, Cryo, Whole Blood, or null for "No transfusion"
    dose_text = Column(Text, nullable=False)
    units = Column(Float, nullable=True)
    volume_ml = Column(Float, nullable=True)
    expected_increment = Column(Text, nullable=False)
    recheck_plan = Column(Text, nullable=False)
    why = Column(JSON, nullable=False)  # Array of strings
    warnings = Column(JSON, nullable=False)  # Array of strings
    references = Column(JSON, nullable=False)  # Array of strings
    rule_ids = Column(JSON, nullable=False)  # Array of strings
    
    # Metadata
    rule_version = Column(String, nullable=False)  # e.g., "1.2.0"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Outcome tracking (optional, for QA purposes)
    actual_transfusion_given = Column(Boolean, nullable=True)
    components_given = Column(JSON, nullable=True)  # {"rbc": true, "platelets": false, ...}
    post_transfusion_hb = Column(Float, nullable=True)
    post_transfusion_platelets = Column(Float, nullable=True)
    outcome_recorded_at = Column(DateTime(timezone=True), nullable=True)
    outcome_recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    encounter = relationship("PatientEncounter", back_populates="recommendations")
    audit_logs = relationship("AuditLog", back_populates="recommendation")
    outcome_recorder = relationship("User", foreign_keys=[outcome_recorded_by])

    # Cost tracking
    estimated_cost_bdt = Column(Float, nullable=True)  # Estimated cost based on recommendation
    actual_cost_bdt = Column(Float, nullable=True)     # Actual cost based on components
