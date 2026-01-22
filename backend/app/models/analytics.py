"""Analytics models for blood transfusion cost tracking and ROI calculations"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class BloodProductCost(Base):
    """Hospital-specific blood product pricing"""
    __tablename__ = "blood_product_cost"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    component_type = Column(String(50), nullable=False)  # RBC, FFP, Platelets, Cryo
    unit_cost_bdt = Column(Float, nullable=False)  # Cost per unit in BDT
    units_per_bag = Column(Integer, nullable=False, default=1)  # Units per bag/container
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    hospital = relationship("Hospital", back_populates="blood_product_costs")
    
    def __repr__(self):
        return f"<BloodProductCost {self.component_type}: {self.unit_cost_bdt} BDT>"


class AnalyticsMonthlySummary(Base):
    """Pre-aggregated monthly analytics for performance"""
    __tablename__ = "analytics_monthly_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    summary_date = Column(Date, nullable=False)  # First day of the month
    
    # Counters
    total_encounters = Column(Integer, nullable=False, default=0)
    total_recommendations = Column(Integer, nullable=False, default=0)
    guideline_compliant = Column(Integer, nullable=False, default=0)
    total_overrides = Column(Integer, nullable=False, default=0)
    
    # Component-specific tracking
    rbc_recommended = Column(Integer, nullable=False, default=0)
    rbc_actual = Column(Integer, nullable=False, default=0)
    platelets_recommended = Column(Integer, nullable=False, default=0)
    platelets_actual = Column(Integer, nullable=False, default=0)
    ffp_recommended = Column(Integer, nullable=False, default=0)
    ffp_actual = Column(Integer, nullable=False, default=0)
    cryo_recommended = Column(Integer, nullable=False, default=0)
    cryo_actual = Column(Integer, nullable=False, default=0)
    
    # Financial metrics
    estimated_savings_bdt = Column(Float, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    hospital = relationship("Hospital", back_populates="analytics_summaries")
    
    def __repr__(self):
        return f"<AnalyticsMonthlySummary {self.summary_date}: {self.estimated_savings_bdt} BDT saved>"
    
    @property
    def compliance_rate(self) -> float:
        """Calculate guideline compliance rate"""
        if self.total_recommendations == 0:
            return 0.0
        return (self.guideline_compliant / self.total_recommendations) * 100
    
    @property
    def override_rate(self) -> float:
        """Calculate override rate"""
        if self.total_recommendations == 0:
            return 0.0
        return (self.total_overrides / self.total_recommendations) * 100
