from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("patient_encounters.id"), nullable=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True)
    
    action = Column(String, nullable=False)  # create, override, view, export
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Override details
    override_reason = Column(Text, nullable=True)
    override_component = Column(String, nullable=True)
    
    # Metadata
    rule_version = Column(String, nullable=True)
    additional_metadata = Column(JSON, nullable=True)  # Additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    encounter = relationship("PatientEncounter", back_populates="audit_logs")
    recommendation = relationship("Recommendation", back_populates="audit_logs")
