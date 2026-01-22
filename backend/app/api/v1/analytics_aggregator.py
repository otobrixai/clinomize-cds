# backend/app/services/analytics_service.py
"""Analytics data aggregation functions"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from app.models.recommendation import Recommendation
from app.models.patient import PatientEncounter
from app.models.audit import AuditLog
from app.models.analytics import BloodProductCost, AnalyticsMonthlySummary


def calculate_monthly_analytics(
    db: Session,
    hospital_id: int,
    target_month: Optional[date] = None
) -> Dict:
    """
    Calculate monthly analytics for a hospital.
    If target_month is None, calculates for current month.
    """
    if target_month is None:
        target_month = date.today().replace(day=1)
    
    # Date range for the month
    start_date = target_month
    end_date = (target_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
    # Get encounters for this hospital in date range
    encounters = db.query(PatientEncounter).filter(
        PatientEncounter.hospital_id == hospital_id,
        PatientEncounter.created_at >= start_date,
        PatientEncounter.created_at <= end_date
    ).all()
    
    # Get recommendations for these encounters
    encounter_ids = [e.id for e in encounters]
    recommendations = []
    
    if encounter_ids:
        recommendations = db.query(Recommendation).filter(
            Recommendation.encounter_id.in_(encounter_ids)
        ).all()
    
    # Get overrides from audit logs
    overrides = []
    if encounter_ids:
        overrides = db.query(AuditLog).filter(
            AuditLog.encounter_id.in_(encounter_ids),
            AuditLog.action == "override"
        ).all()
    
    # Get blood product costs for ROI calculation
    blood_costs = db.query(BloodProductCost).filter(
        BloodProductCost.hospital_id == hospital_id,
        BloodProductCost.is_active == True
    ).all()
    
    cost_dict = {cost.component_type: cost.unit_cost_bdt for cost in blood_costs}
    
    # Calculate component usage
    component_stats = {
        "RBC": {"recommended": 0, "actual": 0, "overrides": 0},
        "FFP": {"recommended": 0, "actual": 0, "overrides": 0},
        "Platelets": {"recommended": 0, "actual": 0, "overrides": 0},
        "Cryoprecipitate": {"recommended": 0, "actual": 0, "overrides": 0}
    }
    
    # Process recommendations
    for rec in recommendations:
        component = rec.component
        if component in component_stats:
            recommended_units = rec.units or 0
            component_stats[component]["recommended"] += recommended_units
            
            # For now, assume actual = recommended (need outcome data)
            component_stats[component]["actual"] += recommended_units
    
    # Process overrides
    for override in overrides:
        component = override.override_component
        if component in component_stats:
            component_stats[component]["overrides"] += 1
    
    # Calculate guideline compliance
    total_recommendations = len(recommendations)
    guideline_compliant = total_recommendations - len(overrides)
    compliance_rate = (guideline_compliant / total_recommendations * 100) if total_recommendations > 0 else 0
    
    # Calculate estimated savings
    estimated_savings = 0
    for component, stats in component_stats.items():
        if component in cost_dict:
            # Savings = (Recommended - Actual) × Cost per unit
            savings = (stats["recommended"] - stats["actual"]) * cost_dict[component]
            estimated_savings += max(savings, 0)  # Only positive savings
    
    # Prepare result
    result = {
        "hospital_id": hospital_id,
        "summary_date": target_month,
        "total_encounters": len(encounters),
        "total_recommendations": total_recommendations,
        "guideline_compliant": guideline_compliant,
        "total_overrides": len(overrides),
        "compliance_rate": round(compliance_rate, 1),
        "component_stats": component_stats,
        "estimated_savings_bdt": round(estimated_savings, 2),
        "has_cost_data": len(cost_dict) > 0,
        "has_recommendations": total_recommendations > 0
    }
    
    # Update or create analytics summary
    existing_summary = db.query(AnalyticsMonthlySummary).filter(
        AnalyticsMonthlySummary.hospital_id == hospital_id,
        AnalyticsMonthlySummary.summary_date == target_month
    ).first()
    
    if existing_summary:
        # Update existing
        existing_summary.total_encounters = result["total_encounters"]
        existing_summary.total_recommendations = result["total_recommendations"]
        existing_summary.guideline_compliant = result["guideline_compliant"]
        existing_summary.total_overrides = result["total_overrides"]
        existing_summary.estimated_savings_bdt = result["estimated_savings_bdt"]
        
        # Update component stats
        existing_summary.rbc_recommended = component_stats["RBC"]["recommended"]
        existing_summary.rbc_actual = component_stats["RBC"]["actual"]
        existing_summary.ffp_recommended = component_stats["FFP"]["recommended"]
        existing_summary.ffp_actual = component_stats["FFP"]["actual"]
        existing_summary.platelets_recommended = component_stats["Platelets"]["recommended"]
        existing_summary.platelets_actual = component_stats["Platelets"]["actual"]
        existing_summary.cryo_recommended = component_stats["Cryoprecipitate"]["recommended"]
        existing_summary.cryo_actual = component_stats["Cryoprecipitate"]["actual"]
    else:
        # Create new
        summary = AnalyticsMonthlySummary(
            hospital_id=hospital_id,
            summary_date=target_month,
            total_encounters=result["total_encounters"],
            total_recommendations=result["total_recommendations"],
            guideline_compliant=result["guideline_compliant"],
            total_overrides=result["total_overrides"],
            rbc_recommended=component_stats["RBC"]["recommended"],
            rbc_actual=component_stats["RBC"]["actual"],
            ffp_recommended=component_stats["FFP"]["recommended"],
            ffp_actual=component_stats["FFP"]["actual"],
            platelets_recommended=component_stats["Platelets"]["recommended"],
            platelets_actual=component_stats["Platelets"]["actual"],
            cryo_recommended=component_stats["Cryoprecipitate"]["recommended"],
            cryo_actual=component_stats["Cryoprecipitate"]["actual"],
            estimated_savings_bdt=result["estimated_savings_bdt"]
        )
        db.add(summary)
    
    db.commit()
    
    return result