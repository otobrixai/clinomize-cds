# Backend API

FastAPI backend for Blood Transfusion CDS system (TransfusionIQ MVP).

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and update `DATABASE_URL` in `.env`

3. Run migrations:
```bash
alembic upgrade head
```

4. Start server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login (get JWT token)
- `GET /api/v1/auth/me` - Get current user info

### Recommendations
- `POST /api/v1/recommendations/evaluate` - Evaluate patient and get multi-component recommendations
- `GET /api/v1/recommendations/{recommendation_id}` - Get single recommendation by ID
- `GET /api/v1/recommendations/encounter/{encounter_id}` - Get all recommendations for an encounter
- `POST /api/v1/recommendations/{recommendation_id}/outcome` - Record transfusion outcome (QA)

### Rules
- `GET /api/v1/rules` - Get current rules JSON
- `GET /api/v1/rules/versions` - List all rule versions

### PDF Export
- `GET /api/v1/pdf/encounter/{encounter_id}/pdf?language=en|bn` - Export encounter recommendations as PDF
- `GET /api/v1/pdf/{recommendation_id}/pdf?language=en|bn` - Export single recommendation as PDF

### Audit
- `POST /api/v1/audit/override` - Log override action
- `GET /api/v1/audit/logs/{encounter_id}` - Get audit logs for encounter

### Admin (Admin-only)
- `GET /api/v1/admin/thresholds` - List hospital-configurable thresholds
- `POST /api/v1/admin/thresholds` - Create/update threshold
- `GET /api/v1/admin/ai/evidence-summary` - Get AI-generated guideline summary (admin only)

## Features

### Multi-Component Recommendations
The system supports recommending multiple blood components simultaneously (e.g., RBC + FFP + Platelets) based on clinical context.

### Rules Engine
- Rules stored in JSON files in `app/rules/`
- Deterministic and authoritative - AI never overrides it
- Supports rule versioning and conflict resolution
- Negative rules (contraindications) explicitly supported

### Outcome Tracking
Optional fields for tracking actual transfusion outcomes:
- `actual_transfusion_given` (Y/N/Unknown)
- `components_given` (JSON)
- `post_transfusion_hb` (optional)

### PHI Pseudonymization
Patient data can be pseudonymized by default for privacy compliance.

### PDF Export with i18n
PDF generation supports both English and Bangla with proper font rendering.

## Rules Engine

Rules are stored in JSON files in `app/rules/`. The rules engine is deterministic and authoritative - AI never overrides it.

### Key Features:
- **Multi-component aggregation**: Multiple rules can fire simultaneously
- **Conflict resolution**: Based on priority, exclusive groups, and override conditions
- **Negative rules**: Explicit contraindications with explanations
- **Version tracking**: All recommendations include rule version for audit
