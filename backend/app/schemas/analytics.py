"""Pydantic schemas for analytics data"""

from datetime import date, datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class BloodProductCostBase(BaseModel):
    component_type: str = Field(..., description="Blood component type (RBC, FFP, Platelets, Cryo)")
    unit_cost_bdt: float = Field(..., description="Cost per unit in BDT", gt=0)
    units_per_bag: int = Field(1, description="Units per bag/container", gt=0)
    is_active: bool = Field(True, description="Whether this pricing is active")


class BloodProductCostCreate(BloodProductCostBase):
    hospital_id: Optional[int] = Field(None, description="Hospital ID (optional, uses current user's hospital)")


class BloodProductCostUpdate(BaseModel):
    unit_cost_bdt: Optional[float] = None
    units_per_bag: Optional[int] = None
    is_active: Optional[bool] = None


class BloodProductCostResponse(BloodProductCostBase):
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MonthlyTrendResponse(BaseModel):
    month: str  # YYYY-MM
    encounters: int
    recommendations: int
    compliance_rate: float
    savings_bdt: float


class ComponentStatsResponse(BaseModel):
    recommendations_count: int
    recommended_units: float
    actual_units: float
    overrides_count: int
    common_override_reasons: List[str]


class ComponentUsageResponse(BaseModel):
    hospital_id: int
    period_start: date
    period_end: date
    component_stats: Dict[str, ComponentStatsResponse]
    total_recommendations: int
    total_overrides: int
    override_rate: float


class HospitalROIResponse(BaseModel):
    hospital_id: int
    period_months: int
    total_encounters: int
    total_recommendations: int
    compliance_rate: float
    estimated_total_savings_bdt: float
    estimated_monthly_savings_bdt: float
    component_usage: Dict[str, Dict[str, int]]
    monthly_trends: List[MonthlyTrendResponse]


class AnalyticsSummaryResponse(BaseModel):
    id: int
    hospital_id: int
    summary_date: date
    total_encounters: int
    total_recommendations: int
    guideline_compliant: int
    total_overrides: int
    rbc_recommended: int
    rbc_actual: int
    platelets_recommended: int
    platelets_actual: int
    ffp_recommended: int
    ffp_actual: int
    cryo_recommended: int
    cryo_actual: int
    estimated_savings_bdt: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True