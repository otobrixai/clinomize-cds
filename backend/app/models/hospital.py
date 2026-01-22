from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.patient import PatientEncounter


class Hospital(Base):
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    address = Column(String)
    city = Column(String)
    country = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships - ADD THIS ENCOUNTERS RELATIONSHIP
    encounters = relationship("PatientEncounter", back_populates="hospital", foreign_keys="PatientEncounter.hospital_id")
    
    # Existing relationships
    users = relationship("User", back_populates="hospital", foreign_keys="User.hospital_id")
    configs = relationship("HospitalConfig", back_populates="hospital", foreign_keys="HospitalConfig.hospital_id")
    blood_product_costs = relationship("BloodProductCost", back_populates="hospital", cascade="all, delete-orphan", foreign_keys="BloodProductCost.hospital_id")
    analytics_summaries = relationship("AnalyticsMonthlySummary", back_populates="hospital", cascade="all, delete-orphan", foreign_keys="AnalyticsMonthlySummary.hospital_id")
    cardioiq_encounters = relationship("CardioIQEncounter", back_populates="hospital", foreign_keys="CardioIQEncounter.hospital_id")
    
    def __repr__(self):
        return f"<Hospital {self.name}>"