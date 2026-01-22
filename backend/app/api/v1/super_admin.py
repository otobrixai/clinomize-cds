# backend/app/api/v1/super_admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.core.auth import require_super_admin
from app.models.user import User, UserRole
from app.models.hospital import Hospital
from app.models.hospital_config import HospitalConfig
from app.models.patient import PatientEncounter
from app.models.recommendation import Recommendation
from app.models.recommendation import Recommendation
from app.models.analytics import AnalyticsMonthlySummary
from app.schemas.hospital_config import ConfigCreate, ConfigResponse
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta

router = APIRouter(tags=["super-admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models for request/response
class HospitalCreate(BaseModel):
    name: str
    address: str = None
    city: str = None
    country: str = "Bangladesh"
    # Optional initial admin creation
    admin_email: EmailStr = None
    admin_password: str = None
    admin_name: str = None

class HospitalUpdate(BaseModel):
    name: str = None
    address: str = None
    city: str = None
    country: str = None
    is_active: bool = None

class HospitalResponse(BaseModel):
    id: int
    name: str
    address: str = None
    city: str = None
    country: str
    is_active: bool
    users_count: int = 0
    created_at: datetime = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    hospital_id: int = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    hospital_id: int = None
    is_active: bool
    created_at: datetime = None

    class Config:
        from_attributes = True

# ========== HOSPITAL ENDPOINTS ==========

@router.get("/hospitals", response_model=List[HospitalResponse])
async def get_hospitals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get all hospitals (super admin only)
    """
    try:
        hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
        
        result = []
        for hospital in hospitals:
            # Count users in this hospital
            user_count = db.query(User).filter(
                User.hospital_id == hospital.id,
                User.is_active == True
            ).count()
            
            hospital_dict = {
                "id": hospital.id,
                "name": hospital.name,
                "address": hospital.address,
                "city": hospital.city,
                "country": hospital.country,
                "is_active": hospital.is_active,
                "users_count": user_count,
                "created_at": hospital.created_at
            }
            result.append(hospital_dict)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching hospitals: {str(e)}"
        )

@router.post("/hospitals", response_model=HospitalResponse)
async def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Create a new hospital (super admin only)
    """
    try:
        # Check if hospital name already exists
        existing = db.query(Hospital).filter(Hospital.name == hospital_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital with this name already exists"
            )
        
        hospital = Hospital(
            name=hospital_data.name,
            address=hospital_data.address,
            city=hospital_data.city,
            country=hospital_data.country,
            created_by=current_user.id
        )
        
        db.add(hospital)
        db.commit()
        db.refresh(hospital)
        
        # Create Initial Admin if provided
        if hospital_data.admin_email and hospital_data.admin_password:
            # Check if email exists
            existing_user = db.query(User).filter(User.email == hospital_data.admin_email).first()
            if existing_user:
                # We won't rollback hospital creation, but we can't create the user
                # Alternatively, we could rollback. Let's rollback for better UX.
                db.delete(hospital)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hospital Admin email already registered. Hospital creation rolled back."
                )
            
            hashed_pw = pwd_context.hash(hospital_data.admin_password)
            admin_user = User(
                email=hospital_data.admin_email,
                hashed_password=hashed_pw,
                full_name=hospital_data.admin_name or "Hospital Admin",
                role=UserRole.HOSPITAL_ADMIN,
                hospital_id=hospital.id,
                is_active=True,
                created_by=current_user.id
            )
            db.add(admin_user)
            db.commit()
        
        return HospitalResponse(
            id=hospital.id,
            name=hospital.name,
            address=hospital.address,
            city=hospital.city,
            country=hospital.country,
            is_active=hospital.is_active,
            users_count=1 if (hospital_data.admin_email and hospital_data.admin_password) else 0,
            created_at=hospital.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating hospital: {str(e)}"
        )

@router.get("/hospitals/{hospital_id}/users", response_model=List[UserResponse])
async def get_hospital_users(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get all users in a hospital (super admin only)
    """
    try:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        users = db.query(User).filter(
            User.hospital_id == hospital_id,
            User.is_active == True
        ).all()
        
        return users
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching hospital users: {str(e)}"
        )


# Add this endpoint in super_admin.py after the get_hospitals endpoint

@router.get("/hospitals/{hospital_id}", response_model=HospitalResponse)
async def get_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get a specific hospital (super admin only)
    """
    try:
        hospital = db.query(Hospital).filter(
            Hospital.id == hospital_id,
            Hospital.is_active == True
        ).first()
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        # Count users in this hospital
        user_count = db.query(User).filter(
            User.hospital_id == hospital.id,
            User.is_active == True
        ).count()
        
        return HospitalResponse(
            id=hospital.id,
            name=hospital.name,
            address=hospital.address,
            city=hospital.city,
            country=hospital.country,
            is_active=hospital.is_active,
            users_count=user_count,
            created_at=hospital.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching hospital: {str(e)}"
        )

@router.put("/hospitals/{hospital_id}", response_model=HospitalResponse)
async def update_hospital(
    hospital_id: int,
    hospital_data: HospitalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Update hospital details
    """
    try:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        # Check name uniqueness if changed
        if hospital_data.name and hospital_data.name != hospital.name:
            existing = db.query(Hospital).filter(Hospital.name == hospital_data.name).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hospital with this name already exists"
                )
        
        # Update fields
        if hospital_data.name:
            hospital.name = hospital_data.name
        if hospital_data.address:
            hospital.address = hospital_data.address
        if hospital_data.city:
            hospital.city = hospital_data.city
        if hospital_data.country:
            hospital.country = hospital_data.country
        if hospital_data.is_active is not None:
            hospital.is_active = hospital_data.is_active
            
        db.commit()
        db.refresh(hospital)
        
        # Get user count
        user_count = db.query(User).filter(
            User.hospital_id == hospital.id,
            User.is_active == True
        ).count()
        
        return HospitalResponse(
            id=hospital.id,
            name=hospital.name,
            address=hospital.address,
            city=hospital.city,
            country=hospital.country,
            is_active=hospital.is_active,
            users_count=user_count,
            created_at=hospital.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating hospital: {str(e)}"
        )

@router.put("/hospitals/{hospital_id}/deactivate")
async def deactivate_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Deactivate (soft delete) a hospital
    """
    try:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
            
        hospital.is_active = False
        db.commit()
        
        return {"message": f"Hospital {hospital.name} deactivated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deactivating hospital: {str(e)}")

@router.put("/hospitals/{hospital_id}/activate")
async def activate_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Activate a hospital
    """
    try:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
            
        hospital.is_active = True
        db.commit()
        
        return {"message": f"Hospital {hospital.name} activated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error activating hospital: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error activating hospital: {str(e)}")

# ========== HOSPITAL CONFIGURATION ENDPOINTS ==========

@router.get("/hospitals/{hospital_id}/configs", response_model=List[ConfigResponse])
async def get_hospital_configs(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get configurations for a specific hospital
    """
    try:
        configs = db.query(HospitalConfig).filter(
            HospitalConfig.hospital_id == hospital_id,
            HospitalConfig.is_active == True
        ).all()
        return configs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching hospital configs: {str(e)}"
        )

@router.post("/hospitals/{hospital_id}/configs", response_model=ConfigResponse)
async def create_hospital_config(
    hospital_id: int,
    config_data: ConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Create or update configuration for a specific hospital
    """
    try:
        # Check if hospital exists
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")

        # Check for existing config
        existing_config = db.query(HospitalConfig).filter(
            HospitalConfig.hospital_id == hospital_id,
            HospitalConfig.config_key == config_data.config_key
        ).first()
        
        if existing_config:
            existing_config.config_value = config_data.config_value
            existing_config.config_type = config_data.config_type
            existing_config.updated_by = current_user.id
            db.commit()
            db.refresh(existing_config)
            return existing_config
        else:
            new_config = HospitalConfig(
                hospital_id=hospital_id,
                config_type=config_data.config_type,
                config_key=config_data.config_key,
                config_value=config_data.config_value,
                is_active=True,
                created_by=current_user.id
            )
            db.add(new_config)
            db.commit()
            db.refresh(new_config)
            return new_config
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating hospital config: {str(e)}"
        )

# ========== USER MANAGEMENT ENDPOINTS ==========

@router.get("/all-users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get all users in the system (super admin only)
    """
    try:
        users = db.query(User).filter(User.is_active == True).all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Create a new user (super admin only)
    """
    try:
        # Validate hospital if specified
        # Validate hospital if specified or required
        # HOSPITAL_ADMIN and DOCTOR roles MUST belong to a hospital
        if user_data.role in [UserRole.HOSPITAL_ADMIN, UserRole.DOCTOR, UserRole.ADMIN]:
            if not user_data.hospital_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Hospital ID is required for role {user_data.role}"
                )
        
        if user_data.hospital_id:
            hospital = db.query(Hospital).filter(Hospital.id == user_data.hospital_id).first()
            if not hospital:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hospital not found"
                )
        
        # Check if email already exists
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
        
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)
        
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            hospital_id=user_data.hospital_id,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            hospital_id=user.hospital_id,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

# ========== SYSTEM STATS ENDPOINT ==========

class SystemStats(BaseModel):
    total_hospitals: int
    total_users: int
    total_patient_encounters: int
    total_recommendations: int
    active_hospitals: int

@router.get("/system-stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get system statistics (super admin only)
    """
    try:
        # Optimizing counts - for very large tables, estimate or cache
        total_hospitals = db.query(Hospital).filter(Hospital.is_active == True).count()
        active_hospitals = db.query(Hospital).filter(Hospital.is_active == True).count()
        total_users = db.query(User).filter(User.is_active == True).count()
        total_patient_encounters = db.query(PatientEncounter).count()
        total_recommendations = db.query(Recommendation).count()
        
        return SystemStats(
            total_hospitals=total_hospitals,
            total_users=total_users,
            total_patient_encounters=total_patient_encounters,
            total_recommendations=total_recommendations,
            active_hospitals=active_hospitals
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching system stats: {str(e)}"
        )


# ========== ANALYTICS ENDPOINTS ==========

class GlobalAnalyticsResponse(BaseModel):
    total_savings_bdt: float
    avg_compliance_rate: float
    total_patient_encounters: int
    total_recommendations: int
    
    # Trends (last 6 months)
    monthly_trends: List[dict]  # {month: "2023-01", savings: 1000, compliance: 85.5}
    
    # Component Mix
    component_distribution: List[dict] # {name: "RBC", value: 500}

class HospitalLeaderboardItem(BaseModel):
    id: int
    name: str
    total_encounters: int
    total_savings: float
    compliance_rate: float

@router.get("/analytics/global", response_model=GlobalAnalyticsResponse)
async def get_global_analytics(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get aggregated analytics across all hospitals
    """
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30 * months)
        
        # 1. Global KPIs
        # We'll sum up data from AnalyticsMonthlySummary for historical accuracy + performance
        summaries = db.query(AnalyticsMonthlySummary).filter(
            AnalyticsMonthlySummary.summary_date >= start_date
        ).all()
        
        total_savings = sum(s.estimated_savings_bdt for s in summaries)
        total_recs = sum(s.total_recommendations for s in summaries)
        total_compliant = sum(s.guideline_compliant for s in summaries)
        total_encounters = sum(s.total_encounters for s in summaries)
        
        avg_compliance = (total_compliant / total_recs * 100) if total_recs > 0 else 0
        
        # 2. Monthly Trends
        trends_map = {}
        for s in summaries:
            m_key = s.summary_date.strftime("%Y-%m")
            if m_key not in trends_map:
                trends_map[m_key] = {"savings": 0, "compliant": 0, "total": 0, "encounters": 0}
            
            trends_map[m_key]["savings"] += s.estimated_savings_bdt
            trends_map[m_key]["compliant"] += s.guideline_compliant
            trends_map[m_key]["total"] += s.total_recommendations
            trends_map[m_key]["encounters"] += s.total_encounters
            
        monthly_trends = []
        # Ensure we have entries for all months
        for i in range(months):
            d = start_date + timedelta(days=30 * i)
            m_key = d.strftime("%Y-%m")
            if m_key in trends_map:
                data = trends_map[m_key]
                comp_rate = (data["compliant"] / data["total"] * 100) if data["total"] > 0 else 0
                monthly_trends.append({
                    "month": m_key,
                    "savings": round(data["savings"], 2),
                    "compliance": round(comp_rate, 1),
                    "encounters": data["encounters"]
                })
            else:
                monthly_trends.append({
                    "month": m_key,
                    "savings": 0,
                    "compliance": 0,
                    "encounters": 0
                })
        
        # Sort by month
        monthly_trends.sort(key=lambda x: x["month"])
        
        # 3. Component Distribution
        # Aggregating from summaries
        rbc_total = sum(s.rbc_actual for s in summaries)
        ffp_total = sum(s.ffp_actual for s in summaries)
        plt_total = sum(s.platelets_actual for s in summaries)
        cryo_total = sum(s.cryo_actual for s in summaries)
        
        component_distribution = [
            {"name": "RBC", "value": rbc_total},
            {"name": "FFP", "value": ffp_total},
            {"name": "Platelets", "value": plt_total},
            {"name": "Cryo", "value": cryo_total},
        ]
        
        return GlobalAnalyticsResponse(
            total_savings_bdt=round(total_savings, 2),
            avg_compliance_rate=round(avg_compliance, 1),
            total_patient_encounters=total_encounters,
            total_recommendations=total_recs,
            monthly_trends=monthly_trends,
            component_distribution=component_distribution
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generation global analytics: {str(e)}"
        )

@router.get("/analytics/leaderboard", response_model=List[HospitalLeaderboardItem])
async def get_hospital_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get hospitals ranked by performance (savings/compliance)
    """
    try:
        # Get all hospitals
        hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
        
        leaderboard = []
        
        for h in hospitals:
            # Simple aggregation from summaries
            summaries = db.query(AnalyticsMonthlySummary).filter(
                AnalyticsMonthlySummary.hospital_id == h.id
            ).all()
            
            savings = sum(s.estimated_savings_bdt for s in summaries)
            compliant = sum(s.guideline_compliant for s in summaries)
            total = sum(s.total_recommendations for s in summaries)
            encounters = sum(s.total_encounters for s in summaries)
            
            comp_rate = (compliant / total * 100) if total > 0 else 0
            
            leaderboard.append(
                HospitalLeaderboardItem(
                    id=h.id,
                    name=h.name,
                    total_encounters=encounters,
                    total_savings=round(savings, 2),
                    compliance_rate=round(comp_rate, 1)
                )
            )
            
        # Sort by savings descending
        leaderboard.sort(key=lambda x: x.total_savings, reverse=True)
        
        return leaderboard
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating leaderboard: {str(e)}"
        )


# ========== PROFILE & SETTINGS ==========

class ProfileUpdate(BaseModel):
    full_name: str
    email: EmailStr

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    profile: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Update current user profile"""
    try:
        # Check email uniqueness if changed
        if profile.email != current_user.email:
            existing = db.query(User).filter(User.email == profile.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already in use")
        
        current_user.full_name = profile.full_name
        current_user.email = profile.email
        
        db.commit()
        db.refresh(current_user)
        return current_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

@router.post("/change-password")
async def change_password(
    pwd_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Change current user password"""
    if not pwd_context.verify(pwd_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    if len(pwd_data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
        
    current_user.hashed_password = pwd_context.hash(pwd_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}