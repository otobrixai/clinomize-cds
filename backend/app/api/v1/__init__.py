# backend/app/api/v1/__init__.py
from fastapi import APIRouter

router = APIRouter()

# Import and include routers one by one to avoid circular imports

# Clinical endpoints
from app.api.v1 import recommendations
router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])

from app.api.v1 import rules
router.include_router(rules.router, prefix="/rules", tags=["rules"])

from app.api.v1 import cardioiq
router.include_router(cardioiq.router, prefix="/cardioiq", tags=["cardioiq"])

from app.api.v1 import auth
router.include_router(auth.router, prefix="/auth", tags=["auth"])

from app.api.v1 import analytics
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Audit and PDF
from app.api.v1 import audit
router.include_router(audit.router, prefix="/audit", tags=["audit"])

from app.api.v1 import cors_test
router.include_router(cors_test.router, tags=["test"])

from app.api.v1 import pdf
router.include_router(pdf.router, prefix="/pdf", tags=["pdf"])

# Admin endpoints (including AI)
from app.api.v1.admin import router as admin_router
router.include_router(admin_router, prefix="/admin", tags=["admin"])  # AI features

from app.api.v1.admin_config import thresholds as admin_thresholds
router.include_router(admin_thresholds.router, prefix="/admin/thresholds", tags=["admin-thresholds"])

from app.api.v1 import hospital_admin
router.include_router(hospital_admin.router, prefix="/hospital-admin", tags=["hospital-admin"])

# Super Admin endpoints
try:
    from app.api.v1 import super_admin
    router.include_router(super_admin.router, prefix="/super-admin", tags=["super-admin"])
except ImportError:
    print("Warning: super_admin module not found. Super admin endpoints will not be available.")