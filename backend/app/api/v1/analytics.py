"""Analytics API endpoints for hospital ROI and blood utilization tracking"""

from typing import List, Optional
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.hospital import Hospital
from app.models.analytics import BloodProductCost, AnalyticsMonthlySummary
from app.models.recommendation import Recommendation
from app.models.audit import AuditLog
from app.models.patient import PatientEncounter
from app.schemas.analytics import (
    BloodProductCostCreate,
    BloodProductCostUpdate,
    BloodProductCostResponse,
    AnalyticsSummaryResponse,
    HospitalROIResponse,
    ComponentUsageResponse,
    MonthlyTrendResponse,
)

router = APIRouter()


@router.get("/blood-product-costs", response_model=List[BloodProductCostResponse])
def get_blood_product_costs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: Optional[int] = None
):
    """
    Get blood product costs for a hospital.
    Only hospital admins and super admins can access.
    """
    # Check permissions
    if current_user.role not in ["super_admin", "hospital_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Determine which hospital to query
    query_hospital_id = hospital_id or current_user.hospital_id
    
    if not query_hospital_id:
        raise HTTPException(status_code=400, detail="Hospital ID required")
    
    # Verify hospital access
    if current_user.role == "hospital_admin" and current_user.hospital_id != query_hospital_id:
        raise HTTPException(status_code=403, detail="Cannot access other hospital data")
    
    # Query costs
    costs = db.query(BloodProductCost).filter(
        BloodProductCost.hospital_id == query_hospital_id,
        BloodProductCost.is_active == True
    ).order_by(BloodProductCost.component_type).all()
    
    return costs


@router.post("/blood-product-costs", response_model=BloodProductCostResponse)
def create_blood_product_cost(
    cost_data: BloodProductCostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update blood product cost for a hospital.
    Only hospital admins and super admins can access.
    """
    if current_user.role not in ["super_admin", "hospital_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Determine hospital
    hospital_id = cost_data.hospital_id or current_user.hospital_id
    
    if not hospital_id:
        raise HTTPException(status_code=400, detail="Hospital ID required")
    
    # Verify hospital access
    if current_user.role == "hospital_admin" and current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Cannot modify other hospital data")
    
    # Check if cost already exists for this component
    existing = db.query(BloodProductCost).filter(
        BloodProductCost.hospital_id == hospital_id,
        BloodProductCost.component_type == cost_data.component_type
    ).first()
    
    if existing:
        # Update existing
        existing.unit_cost_bdt = cost_data.unit_cost_bdt
        existing.units_per_bag = cost_data.units_per_bag
        existing.is_active = cost_data.is_active
    else:
        # Create new
        existing = BloodProductCost(
            hospital_id=hospital_id,
            component_type=cost_data.component_type,
            unit_cost_bdt=cost_data.unit_cost_bdt,
            units_per_bag=cost_data.units_per_bag,
            is_active=cost_data.is_active
        )
        db.add(existing)
    
    db.commit()
    db.refresh(existing)
    return existing


@router.get("/roi-summary", response_model=HospitalROIResponse)
def get_hospital_roi_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: Optional[int] = None,
    months: int = Query(6, ge=1, le=12, description="Number of months to analyze")
):
    """
    Get ROI summary for a hospital (estimated savings, compliance, etc.)
    Only hospital admins and super admins can access.
    """
    if current_user.role not in ["super_admin", "hospital_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Determine hospital
    query_hospital_id = hospital_id or current_user.hospital_id
    
    if not query_hospital_id:
        raise HTTPException(status_code=400, detail="Hospital ID required")
    
    # Verify hospital access
    if current_user.role == "hospital_admin" and current_user.hospital_id != query_hospital_id:
        raise HTTPException(status_code=403, detail="Cannot access other hospital data")
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - relativedelta(months=months)
    
    # Get monthly summaries from database
    summaries = db.query(AnalyticsMonthlySummary).filter(
        AnalyticsMonthlySummary.hospital_id == query_hospital_id,
        AnalyticsMonthlySummary.summary_date >= start_date,
        AnalyticsMonthlySummary.summary_date <= end_date
    ).order_by(AnalyticsMonthlySummary.summary_date).all()
    
    # If no summaries exist in database, calculate for current month
    if not summaries:
        # Import analytics service
        from app.api.v1.analytics_aggregator import calculate_monthly_analytics
        
        # Calculate for current month
        current_month_result = calculate_monthly_analytics(db, query_hospital_id)
        
        # Get the newly created/updated summary
        new_summary = db.query(AnalyticsMonthlySummary).filter(
            AnalyticsMonthlySummary.hospital_id == query_hospital_id,
            AnalyticsMonthlySummary.summary_date == current_month_result["summary_date"]
        ).first()
        
        if new_summary:
            summaries = [new_summary]
    
    # Calculate totals
    total_encounters = sum(s.total_encounters for s in summaries)
    total_recommendations = sum(s.total_recommendations for s in summaries)
    total_savings = sum(s.estimated_savings_bdt for s in summaries)
    total_compliant = sum(s.guideline_compliant for s in summaries)
    
    # Calculate rates
    compliance_rate = (total_compliant / total_recommendations * 100) if total_recommendations > 0 else 0
    
    # Get component usage
    component_usage = {
        "RBC": {
            "recommended": sum(s.rbc_recommended for s in summaries),
            "actual": sum(s.rbc_actual for s in summaries)
        },
        "Platelets": {
            "recommended": sum(s.platelets_recommended for s in summaries),
            "actual": sum(s.platelets_actual for s in summaries)
        },
        "FFP": {
            "recommended": sum(s.ffp_recommended for s in summaries),
            "actual": sum(s.ffp_actual for s in summaries)
        },
        "Cryo": {
            "recommended": sum(s.cryo_recommended for s in summaries),
            "actual": sum(s.cryo_actual for s in summaries)
        }
    }
    
    # Calculate estimated monthly savings
    monthly_savings = total_savings / len(summaries) if summaries else 0
    
    # Generate monthly trends
    monthly_trends = []
    for s in summaries:
        monthly_compliance_rate = (s.guideline_compliant / s.total_recommendations * 100) if s.total_recommendations > 0 else 0
        monthly_trends.append(
            MonthlyTrendResponse(
                month=s.summary_date.strftime("%Y-%m"),
                encounters=s.total_encounters,
                recommendations=s.total_recommendations,
                compliance_rate=round(monthly_compliance_rate, 1),
                savings_bdt=round(s.estimated_savings_bdt, 2)
            )
        )
    
    return HospitalROIResponse(
        hospital_id=query_hospital_id,
        period_months=months,
        total_encounters=total_encounters,
        total_recommendations=total_recommendations,
        compliance_rate=round(compliance_rate, 1),
        estimated_total_savings_bdt=round(total_savings, 2),
        estimated_monthly_savings_bdt=round(monthly_savings, 2),
        component_usage=component_usage,
        monthly_trends=monthly_trends
    )


@router.get("/component-usage", response_model=ComponentUsageResponse)
def get_component_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: Optional[int] = None,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get detailed component usage statistics.
    Only hospital admins and super admins can access.
    """
    if current_user.role not in ["super_admin", "hospital_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Determine hospital
    query_hospital_id = hospital_id or current_user.hospital_id
    
    if not query_hospital_id:
        raise HTTPException(status_code=400, detail="Hospital ID required")
    
    # Verify hospital access
    if current_user.role == "hospital_admin" and current_user.hospital_id != query_hospital_id:
        raise HTTPException(status_code=403, detail="Cannot access other hospital data")
    
    # Set default date range (last 30 days)
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - relativedelta(days=30)
    
    # Query recommendations in date range
    recommendations = db.query(Recommendation).join(PatientEncounter).filter(
        PatientEncounter.hospital_id == query_hospital_id,
        Recommendation.created_at >= start_date,
        Recommendation.created_at <= end_date
    ).all()
    
    # Query audit logs for overrides
    overrides = db.query(AuditLog).join(PatientEncounter).filter(
        PatientEncounter.hospital_id == query_hospital_id,
        AuditLog.created_at >= start_date,
        AuditLog.created_at <= end_date,
        AuditLog.action == "override"
    ).all()
    
    # Calculate component usage
    component_stats = {}
    for component in ["RBC", "FFP", "Platelets", "Cryoprecipitate"]:
        comp_recommendations = [r for r in recommendations if r.component == component]
        comp_overrides = [o for o in overrides if o.override_component == component]
        
        recommended_units = sum(r.units or 0 for r in comp_recommendations)
        actual_units = recommended_units  # Default to recommended (will need actual data from outcomes)
        
        component_stats[component] = {
            "recommendations_count": len(comp_recommendations),
            "recommended_units": recommended_units,
            "actual_units": actual_units,
            "overrides_count": len(comp_overrides),
            "common_override_reasons": list(set([o.override_reason for o in comp_overrides if o.override_reason]))
        }
    
    return ComponentUsageResponse(
        hospital_id=query_hospital_id,
        period_start=start_date,
        period_end=end_date,
        component_stats=component_stats,
        total_recommendations=len(recommendations),
        total_overrides=len(overrides),
        override_rate=(len(overrides) / len(recommendations) * 100) if recommendations else 0
    )

@router.post("/calculate/{hospital_id}/{year_month}")
def calculate_analytics_for_month(
    hospital_id: int,
    year_month: str,  # Format: YYYY-MM
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate analytics for a specific hospital and month.
    Only hospital admins and super admins can trigger.
    """
    if current_user.role not in ["super_admin", "hospital_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify hospital access
    if current_user.role == "hospital_admin" and current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="Cannot calculate analytics for other hospital")
    
    try:
        # Parse date
        target_date = datetime.strptime(year_month, "%Y-%m").date()
        
        # Import and run analytics service
        from app.api.v1.analytics_aggregator import calculate_monthly_analytics
        
        result = calculate_monthly_analytics(db, hospital_id, target_date)
        
        return {
            "message": f"Analytics calculated for {year_month}",
            "result": result
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating analytics: {str(e)}")


@router.post("/recalculate-monthly/{year_month}")
def recalculate_monthly_analytics(
    year_month: str,  # Format: YYYY-MM
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculate monthly analytics for a specific month.
    This should be called automatically via cron job, but available for manual trigger.
    Only super admins can access.
    """
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admins can trigger recalculation")
    
    # TODO: Implement monthly aggregation logic
    # This would:
    # 1. Query all recommendations/audit logs for the month
    # 2. Calculate savings based on blood product costs
    # 3. Update AnalyticsMonthlySummary table
    
    return {"message": f"Monthly analytics recalculation triggered for {year_month}", "status": "queued"}