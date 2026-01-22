from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class Setting(str, enum.Enum):
    ICU = "ICU"
    OR = "OR"
    ER = "ER"
    WARD = "WARD"

class PatientEncounter(Base):
    __tablename__ = "patient_encounters"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    patient_id = Column(String, index=True)  # Pseudonymized ID
    
    # NEW FIELD: Department for analytics
    department = Column(String(50), default='General Ward')  # ICU, Ward, Surgery, ER, Clinic    
    
    # Demographics
    age_years = Column(Float, nullable=False)
    age_months = Column(Float, nullable=True)  # For pediatrics
    sex = Column(String(10), nullable=False)  # M, F, Other
    weight_kg = Column(Float, nullable=False)

    # Clinical context
    active_bleeding = Column(Boolean, nullable=False, default=False)
    hemodynamic_instability = Column(Boolean, nullable=True, default=False)
    planned_procedure = Column(String(100), nullable=True)

    # Context
    setting = Column(Enum(Setting), nullable=False)
    
    # Labs
    hb_gdl = Column(Float, nullable=True)
    platelets_x109l = Column(Float, nullable=True)
    inr = Column(Float, nullable=True)
    aptt_sec = Column(Float, nullable=True)
    fibrinogen_mgdl = Column(Float, nullable=True)

    # History flags
    history_flags = Column(JSON, nullable=True)  # {cad: bool, liver_disease: bool, etc.}
    
    # Procedure context
    procedure_risk = Column(String, nullable=True)  # low, medium, high
    procedure_timing_hours = Column(Float, nullable=True)
    
    # Local constraints
    component_availability = Column(JSON, nullable=True)  # {rbc: bool, platelets: bool, etc.}
    rbc_bag_size_ml = Column(Integer, default=350)  # 350 or 450
    leukoreduction_available = Column(Boolean, default=True)
    
    # Pseudonymization (PHI protection)
    pseudonymized_id = Column(String, nullable=True, index=True)
    is_pseudonymized = Column(Boolean, nullable=True, default=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships - ADD AUDIT_LOGS HERE
    hospital = relationship("Hospital", back_populates="encounters")
    creator = relationship("User", foreign_keys=[created_by])
    recommendations = relationship("Recommendation", back_populates="encounter", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="encounter", cascade="all, delete-orphan")  # ADD THIS LINE
    
    def __repr__(self):
        return f"<PatientEncounter {self.id} ({self.age_years}{self.sex})>"