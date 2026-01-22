# TransfusionIQ - Complete API Documentation

## SYSTEM OVERVIEW
Blood Transfusion Clinical Decision Support System with Hospital Analytics

### Core Purpose
1. **Clinical Tool**: Help doctors decide when to transfuse blood components
2. **Hospital Analytics**: Show ROI and blood utilization to hospital administrators
3. **Compliance Tracking**: Monitor guideline adherence

### Technology Stack
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Auth**: JWT tokens with role-based access

---

## AUTHENTICATION SYSTEM

### JWT Token Flow
1. POST `/api/v1/auth/token` - Login (returns JWT)
2. Include `Authorization: Bearer <token>` in all requests
3. Token contains: `{"sub": "user_id", "exp": expiry}`

### User Roles
```python
UserRole = {
    "doctor": "Can use CDS tool only",
    "hospital_admin": "Can manage hospital users + view analytics",
    "super_admin": "Full system access",
    "admin": "Legacy admin role"
}

---

## API ENDPOINTS

### AUTHENTICATION
```
POST   /api/v1/auth/token          - Login (JWT)
POST   /api/v1/auth/register       - Register new user
GET    /api/v1/auth/me             - Get current user
```

### RECOMMENDATIONS (CDS Engine)
```
POST   /api/v1/recommendations/evaluate          - Evaluate patient, get recommendation
GET    /api/v1/recommendations/{id}              - Get single recommendation
GET    /api/v1/recommendations/encounter/{id}    - Get all recs for encounter
POST   /api/v1/recommendations/{id}/outcome      - Record transfusion outcome
```

### ANALYTICS (Hospital Admin)
```
GET    /api/v1/analytics/roi-summary            - ROI data (savings, compliance)
GET    /api/v1/analytics/component-usage        - Blood component usage stats
GET    /api/v1/analytics/blood-product-costs    - Get blood product prices
POST   /api/v1/analytics/blood-product-costs    - Set blood product prices
```

### HOSPITAL ADMIN
```
GET    /api/v1/hospital-admin/users             - List hospital users
POST   /api/v1/hospital-admin/users             - Add new user
PUT    /api/v1/hospital-admin/users/{id}/activate    - Activate user
PUT    /api/v1/hospital-admin/users/{id}/deactivate  - Deactivate user
```

### AUDIT
```
POST   /api/v1/audit/override                   - Log override action
GET    /api/v1/audit/logs/{encounter_id}        - Get audit logs
```

### PDF EXPORT
```
GET    /api/v1/pdf/encounter/{id}/pdf?language=en|bn  - Export encounter as PDF
GET    /api/v1/pdf/{recommendation_id}/pdf?language=en|bn - Export single rec as PDF
```

### ADMIN (Super Admin)
```
GET    /api/v1/admin/thresholds                 - Get configurable thresholds
POST   /api/v1/admin/thresholds                 - Update thresholds
GET    /api/v1/admin/ai/evidence-summary        - AI guideline summary (admin only)
```

### SUPER ADMIN
```
GET    /api/v1/super-admin/hospitals            - List all hospitals
GET    /api/v1/super-admin/hospitals/{id}/users - Get hospital users
POST   /api/v1/super-admin/users                - Add user (any hospital)
GET    /api/v1/super-admin/all-users            - Get all users
```

---

## BUSINESS LOGIC & RULES

### 1. Recommendation Engine
- Rules stored in `app/rules/` as JSON files
- Deterministic - AI never overrides
- Multi-component support (RBC + FFP + Platelets simultaneously)
- Conflict resolution: priority > exclusive groups > override conditions

### 2. ROI Calculation
```
Savings = (Recommended_units - Actual_units) × Unit_cost
Compliance_rate = (Guideline_compliant / Total_recommendations) × 100
```

### 3. User Permissions
- **Doctors**: Only CDS tool + own patient encounters
- **Hospital Admins**: CDS + analytics + user management (own hospital only)
- **Super Admins**: Everything + cross-hospital access

### 4. Data Flow
```
Patient Input → Rules Engine → Recommendations → 
└─ Doctor accepts/overrides → Audit log → 
   └─ Monthly aggregation → Analytics dashboard
```

---

## FRONTEND STRUCTURE

### App Router (Next.js 14)
```
app/
├── layout.tsx                    # Root layout
├── page.tsx                      # Home (redirects based on role)
├── login/page.tsx                # Login page
│
├── clinician/                    # Doctor interface
│   └── page.tsx                  # CDS tool (3-step form)
│
├── hospital-admin/               # Hospital admin interface
│   ├── layout.tsx                # Admin layout (header + logout)
│   ├── page.tsx                  # Analytics dashboard
│   └── users/
│       └── page.tsx              # User management
│
└── super-admin/                  # Super admin interface
    ├── layout.tsx                # Super admin layout
    ├── dashboard/page.tsx        # Super admin dashboard
    └── hospitals/page.tsx        # Hospital management
```

### Key Components
- `MultiStepForm.tsx` - 3-step patient input form
- `RecommendationCard.tsx` - Display transfusion recommendations
- `ContextBadges.tsx` - Visual patient context indicators

---

## ENVIRONMENT CONFIGURATION

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=jwt-secret-key
CORS_ORIGINS=["http://localhost:3000"]
OPENAI_API_KEY=optional
AI_ENABLED=False
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## DEPLOYMENT ARCHITECTURE

### Development
- PostgreSQL: Local installation
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`

### Production (Recommended)
- Database: **Supabase** (PostgreSQL)
- Backend: **Vercel** (FastAPI)
- Frontend: **Vercel** (Next.js)

---

## ADDING NEW FEATURES - TEMPLATE

### 1. New API Endpoint
```python
# 1. Create model in app/models/
# 2. Create schema in app/schemas/
# 3. Create router in app/api/v1/
# 4. Add to __init__.py
# 5. Create migration: alembic revision -m "add_feature"
```

### 2. New Frontend Page
```typescript
// 1. Create app/feature-name/page.tsx
// 2. Add to API config in lib/api-config.ts
// 3. Add navigation link in layout if needed
// 4. Update role permissions if required
```

### 3. New Database Table
```sql
-- 1. Create model with SQLAlchemy
-- 2. Create migration
-- 3. Add relationships to existing models
-- 4. Update API documentation
```

---

## COMMON PATTERNS

### 1. Role-based Access Control
```python
if current_user.role not in ["hospital_admin", "super_admin"]:
    raise HTTPException(403, "Not authorized")
```

### 2. Hospital Scoping
```python
# Hospital admins only see their hospital's data
query = query.filter(User.hospital_id == current_user.hospital_id)
```

### 3. Response Format
```python
{
    "success": true,
    "data": {...},
    "message": "Optional message"
}
```

### 4. Error Handling
- 400: Bad Request (validation errors)
- 401: Unauthorized (no/invalid token)
- 403: Forbidden (no permission)
- 404: Not Found
- 500: Internal Server Error

---

## TESTING DATA

### Sample Hospital Admin
```sql
email: admin@testhospital.com
password: password123
role: hospital_admin
hospital_id: 1
```

### Sample Doctor
```sql
email: doctor@hospital.com  
password: password123
role: doctor
hospital_id: 1
```

---

## IMPORTANT NOTES

1. **PHI Protection**: Patient data pseudonymized by default
2. **AI Safety**: AI features admin-only, never in clinical UI
3. **Audit Trail**: All actions logged for compliance
4. **Multi-language**: PDF export supports English & Bangla
5. **Blood Safety**: Rules based on established transfusion guidelines

---

## SUPPORT & MAINTENANCE

### Common Issues
1. CORS errors: Check `CORS_ORIGINS` in backend .env
2. Database errors: Run `alembic upgrade head`
3. Authentication: Clear localStorage tokens
4. Missing data: Check user hospital_id assignments

### Monitoring
- Backend logs: Uvicorn output
- Frontend logs: Browser console
- Database: `psql -U postgres -d transfusion_cds`

---

## VERSION HISTORY
- v1.0.0: Initial release with CDS + Analytics
- Current: Hospital admin user management added
```

