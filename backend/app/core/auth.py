# backend/app/core/auth.py - Complete file
from functools import wraps
from fastapi import HTTPException, Depends, status
from app.api.v1.auth import get_current_user
from app.models.user import User, UserRole

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin role.
    Used to enforce AI boundary - AI features are admin-only.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. AI features are not available to clinical users."
        )
    return current_user

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require super admin role.
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user

def require_hospital_admin_or_super(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require hospital admin or super admin role.
    """
    if current_user.role not in [UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital admin or super admin access required"
        )
    return current_user

def require_doctor_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require doctor or admin role.
    Clinical endpoints require at least doctor role.
    """
    allowed_roles = [UserRole.DOCTOR, UserRole.ADMIN, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor or admin access required"
        )
    return current_user