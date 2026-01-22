"""Hospital admin API endpoints for user management"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.hospital_config import HospitalConfig
from app.schemas.user import UserCreate, UserResponse
from app.schemas.hospital_config import ConfigCreate, ConfigResponse
from app.api.v1.auth import get_password_hash

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
def get_hospital_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all users in the hospital (hospital admin only).
    """
    # Check if user is hospital admin or super admin
    if current_user.role not in [UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get ALL users in the same hospital (not just active)
    # If super admin, allow viewing users if hospital_id is provided in context or if they are just checking via this endpoint
    # Ideally super admin uses super_admin endpoints, but for robustness:
    hospital_id = current_user.hospital_id
    
    # Note: Super Admin user usually has hospital_id=None, so this endpoint 
    # as currently designed only works for a logged-in Hospital Admin.
    # To strictly support "Hospital Admin Flow" as requested, this is sufficient.
    # The Super Admin has their own endpoints.
    
    if not hospital_id and current_user.role == UserRole.SUPER_ADMIN:
         # Fallback or empty if super admin tries to access this 'my-hospital' endpoint without context
         return []

    users = db.query(User).filter(
        User.hospital_id == hospital_id
    ).order_by(
        User.is_active.desc(),  # Show active users first
        User.created_at.desc()
    ).all()
    
    return users


@router.post("/users", response_model=UserResponse)
def create_hospital_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user in the hospital (hospital admin only).
    """
    # DEBUG: Log incoming data
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating user with data: {user_data.dict()}")

    # DEBUG: Log current user info
    logger.info(f"Current user: {current_user.email}, role: {current_user.role}")

    # Check if user is hospital admin or super admin
    if current_user.role not in [UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate role (hospital admin can only create doctors and hospital_admins)
    if current_user.role == UserRole.HOSPITAL_ADMIN:
        # Convert string role to UserRole enum for comparison
        try:
            user_role_enum = UserRole(user_data.role)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {user_data.role}")
        
        if user_role_enum not in [UserRole.DOCTOR, UserRole.HOSPITAL_ADMIN]:
            raise HTTPException(status_code=403, detail="Cannot create users with this role")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=UserRole(user_data.role),
        hospital_id=current_user.hospital_id,
        is_active=True,
        created_by=current_user.id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate a user in the hospital (hospital admin only).
    """
    # Check if user is hospital admin or super admin
    if current_user.role not in [UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get the user to deactivate
    user = db.query(User).filter(
        User.id == user_id,
        User.hospital_id == current_user.hospital_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Cannot deactivate yourself
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    # Deactivate the user
    user.is_active = False
    user.updated_by = current_user.id
    db.commit()
    
    return {"message": f"User {user.email} deactivated successfully"}


@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Activate a user in the hospital (hospital admin only).
    """
    # Check if user is hospital admin or super admin
    if current_user.role not in [UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get the user to activate
    user = db.query(User).filter(
        User.id == user_id,
        User.hospital_id == current_user.hospital_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Activate the user
    user.is_active = True
    user.updated_by = current_user.id
    db.commit()
    
    return {"message": f"User {user.email} activated successfully"}


# ========== CONFIGURATION ENDPOINTS ==========

@router.get("/configs", response_model=List[ConfigResponse])
def get_hospital_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get configurations for the current hospital (hospital admin only).
    """
    if current_user.role not in [UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    configs = db.query(HospitalConfig).filter(
        HospitalConfig.hospital_id == current_user.hospital_id,
        HospitalConfig.is_active == True
    ).all()
    
    return configs

@router.post("/configs", response_model=ConfigResponse)
def create_or_update_config(
    config_data: ConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update a configuration setting (hospital admin only).
    """
    if current_user.role not in [UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Check if config exists for this key
    existing_config = db.query(HospitalConfig).filter(
        HospitalConfig.hospital_id == current_user.hospital_id,
        HospitalConfig.config_key == config_data.config_key
    ).first()
    
    if existing_config:
        # Update existing
        existing_config.config_value = config_data.config_value
        existing_config.config_type = config_data.config_type # allow type update too
        existing_config.updated_by = current_user.id
        db.commit()
        db.refresh(existing_config)
        return existing_config
    else:
        # Create new
        new_config = HospitalConfig(
            hospital_id=current_user.hospital_id,
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