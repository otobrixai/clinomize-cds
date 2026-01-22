"""
CardioIQ Database Models
Stores cardiac evaluation encounters and recommendations
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class CardioIQEncounter(Base):
    """Stores patient encounters for CardioIQ evaluations"""
    __tablename__ = "cardioiq_encounters"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    patient_id = Column(String, index=True)  # Pseudonymized ID
    
    # Demographics
    age = Column(Integer, nullable=False)
    sex = Column(String(10), nullable=False)
    weight_kg = Column(Float, nullable=False)
    
    # Presentation
    chest_pain = Column(Boolean, nullable=False)
    chest_pain_type = Column(String(20), nullable=True)  # typical, atypical, non_cardiac
    dyspnea = Column(Boolean, default=False)
    syncope = Column(Boolean, default=False)
    
    # Vitals
    sbp = Column(Integer, nullable=False)
    hr = Column(Integer, nullable=False)
    spo2 = Column(Integer, nullable=False)
    
    # ECG
    st_elevation = Column(Boolean, default=False)
    st_depression = Column(Boolean, default=False)
    t_wave_inversion = Column(Boolean, default=False)
    non_diagnostic_ecg = Column(Boolean, default=False)
    ecg_confidence = Column(String(10), default='high')  # high, medium, low
    
    # Labs
    troponin_status = Column(String(20), nullable=False)  # available, pending, unavailable
    troponin_positive = Column(Boolean, nullable=True)
    troponin_value = Column(Float, nullable=True)
    creatinine = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    
    # History
    history_cad = Column(Boolean, default=False)
    history_diabetes = Column(Boolean, default=False)
    history_hypertension = Column(Boolean, default=False)
    history_ckd = Column(Boolean, default=False)
    history_heart_failure = Column(Boolean, default=False)
    history_stroke = Column(Boolean, default=False)
    
    # Medications
    on_beta_blocker = Column(Boolean, default=False)
    on_digoxin = Column(Boolean, default=False)
    on_qt_prolonging_drugs = Column(Boolean, default=False)
    
    # Context
    care_setting = Column(String(10), nullable=False)  # ER, WARD, CCU, ICU
    has_cath_lab = Column(Boolean, default=False)
    can_transfer_pci = Column(Boolean, default=False)
    has_troponin = Column(Boolean, default=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    hospital = relationship("Hospital", back_populates="cardioiq_encounters")
    creator = relationship("User", foreign_keys=[created_by])
    recommendation = relationship("CardioIQRecommendation", back_populates="encounter", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("CardioIQAuditLog", back_populates="encounter", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CardioIQEncounter {self.id} ({self.age}{self.sex})>"


class CardioIQRecommendation(Base):
    """Stores CardioIQ CDS recommendations"""
    __tablename__ = "cardioiq_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("cardioiq_encounters.id"), nullable=False, unique=True)
    
    # Recommendation output
    clinical_category = Column(String(100), nullable=False)
    recommended_level_of_care = Column(String(20), nullable=False)  # ER, Ward, CCU, ICU
    
    # Risk scores (stored as JSON)
    risk_scores = Column(JSON, nullable=True)  # [{score_name, value, risk_category, details}]
    
    # Actions and warnings
    recommended_actions = Column(JSON, nullable=False)  # List of strings
    safety_warnings = Column(JSON, nullable=True)  # List of strings
    cost_flags = Column(JSON, nullable=True)  # List of strings
    
    # Rationale
    rationale_summary = Column(JSON, nullable=True)  # List of strings
    guideline_links = Column(JSON, nullable=True)  # List of strings
    rule_hits = Column(JSON, nullable=False)  # List of rule IDs that fired
    
    # Engine metadata
    rule_version = Column(String(20), nullable=False)
    engine_version = Column(String(20), nullable=False)
    
    # Outcome tracking (for QA)
    actual_level_of_care = Column(String(20), nullable=True)
    recommendation_followed = Column(Boolean, nullable=True)
    outcome_notes = Column(Text, nullable=True)
    outcome_recorded_at = Column(DateTime(timezone=True), nullable=True)
    outcome_recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    encounter = relationship("CardioIQEncounter", back_populates="recommendation")
    outcome_recorder = relationship("User", foreign_keys=[outcome_recorded_by])
    
    def __repr__(self):
        return f"<CardioIQRecommendation {self.id} - {self.clinical_category}>"


class CardioIQAuditLog(Base):
    """Audit trail for CardioIQ actions"""
    __tablename__ = "cardioiq_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("cardioiq_encounters.id"), nullable=False)
    recommendation_id = Column(Integer, ForeignKey("cardioiq_recommendations.id"), nullable=True)
    
    # Action details
    action = Column(String(50), nullable=False)  # create, view, override, outcome_recorded
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Context
    rule_version = Column(String(20), nullable=True)
    action_metadata = Column(JSON, nullable=True)  # Additional context (renamed from 'metadata' to avoid SQLAlchemy conflict)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    encounter = relationship("CardioIQEncounter", back_populates="audit_logs")
    user = relationship("User")
    
    def __repr__(self):
        return f"<CardioIQAuditLog {self.id} - {self.action}>"
