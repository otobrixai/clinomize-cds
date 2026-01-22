# CardioIQ Getting Started Guide

## Quick Start (5 Minutes)

### 1. Prerequisites

- Python 3.9+
- PostgreSQL database
- Virtual environment activated

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Set Up Database

```bash
# Run migrations
alembic upgrade head

# Verify CardioIQ tables exist
alembic current  # Should show: cardioiq_001 (head)
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload
```

**Expected output**:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 5. Test the API

```bash
curl http://localhost:8000/api/v1/cardioiq/evaluate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d @test_case.json
```

---

## Directory Structure

```
backend/app/cardioiq/
├── docs/                          # Documentation
│   ├── README.md                 # Main docs index
│   ├── GETTING_STARTED.md        # This file
│   ├── api/
│   │   ├── API_REFERENCE.md      # API documentation
│   │   └── INTEGRATION_GUIDE.md  # Frontend integration
│   ├── validation/
│   │   ├── VALIDATION_GUIDE.md
│   │   ├── DOCTOR_REVIEW_FORM.md
│   │   └── PILOT_READINESS_CHECKLIST.md
│   └── deployment/
│       ├── DATABASE_MIGRATION.md
│       ├── DEPLOYMENT_GUIDE.md
│       └── TROUBLESHOOTING.md
├── engine.py                      # Rules engine
├── schemas.py                     # Data models
├── service.py                     # Business logic
├── rules_v1.1.0.json             # Clinical rules
├── tests/                         # Unit tests
└── validation/                    # Validation framework
    ├── clinical_validator.py
    ├── cardioiq_validation_dataset.json
    └── validation_results.json
```

---

## Core Concepts

### 1. Rules Engine

The CardioIQ engine is **deterministic** - same input always produces same output.

**Key file**: `engine.py`

```python
from app.cardioiq.service import CardioIQService
from app.cardioiq.schemas import CardioIQInput

# Evaluate patient
result = CardioIQService.evaluate_patient(patient_input)
```

### 2. Clinical Rules

Rules are defined in JSON with priority-based resolution.

**Key file**: `rules_v1.1.0.json`

```json
{
  "rule_id": "ACS_STEMI_001",
  "priority": 100,
  "conditions": [...],
  "actions": [...],
  "rationale": "...",
  "guideline": "ESC ACS 2023"
}
```

### 3. Database Models

Three main tables store CardioIQ data:

- `cardioiq_encounters` - Patient evaluations
- `cardioiq_recommendations` - CDS recommendations
- `cardioiq_audit_logs` - Audit trail

**Key file**: `backend/app/models/cardioiq.py`

### 4. API Endpoints

RESTful API for frontend integration.

**Key file**: `backend/app/api/v1/cardioiq.py`

- `POST /api/v1/cardioiq/evaluate` - Evaluate patient
- `GET /api/v1/cardioiq/encounter/{id}` - Get encounter
- `POST /api/v1/cardioiq/{id}/outcome` - Record outcome

---

## Development Workflow

### 1. Make Changes to Rules

Edit `rules_v1.1.0.json`:

```json
{
  "rule_id": "MY_NEW_RULE",
  "priority": 90,
  "conditions": [{ "field": "vitals.sbp", "operator": "<", "value": 90 }],
  "actions": [{ "type": "recommend_level_of_care", "value": "ICU" }]
}
```

### 2. Test Changes

```bash
# Run validation
python app/cardioiq/validation/clinical_validator.py

# Check results
cat app/cardioiq/validation/validation_results.json
```

### 3. Update Version

Update version in:

- `rules_v1.1.0.json` → `rules_v1.2.0.json`
- `engine.py` - Update version constant
- `API_REFERENCE.md` - Document changes

### 4. Deploy

See [DEPLOYMENT_GUIDE.md](./deployment/DEPLOYMENT_GUIDE.md)

---

## Running Tests

### Unit Tests

```bash
pytest app/cardioiq/tests/
```

### Validation Tests

```bash
python app/cardioiq/validation/clinical_validator.py
```

**Expected output**:

```
Total Cases: 72
Passed: 72 (100.0%)
Failed: 0

[PILOT READY] All validation tests passed
```

---

## Common Tasks

### Add a New Rule

1. Edit `rules_v1.1.0.json`
2. Add rule with appropriate priority
3. Run validation: `python app/cardioiq/validation/clinical_validator.py`
4. Update tests if needed

### Update Database Schema

1. Create migration: `alembic revision -m "description"`
2. Edit migration file in `alembic/versions/`
3. Run migration: `alembic upgrade head`
4. Verify: `alembic current`

### Debug a Failing Case

1. Check `validation/validation_results.json`
2. Find the failing case
3. Review rule hits and conditions
4. Adjust rules or test expectations

---

## Environment Variables

Create `.env` file in `backend/`:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

---

## Troubleshooting

### Backend won't start

```bash
# Check database connection
psql -U your_user -d your_database -c "SELECT 1;"

# Check migrations
alembic current

# Check Python version
python --version  # Should be 3.9+
```

### Validation fails

```bash
# Check dataset exists
ls cardioiq_validation_dataset.json

# Run with verbose output
python app/cardioiq/validation/clinical_validator.py --verbose
```

### API returns 500 error

```bash
# Check backend logs
# Look for stack traces in console

# Check database
psql -U your_user -d your_database -c "\dt cardioiq*"
```

See [TROUBLESHOOTING.md](./deployment/TROUBLESHOOTING.md) for more help.

---

## Next Steps

- **For Development**: Read [API_REFERENCE.md](./api/API_REFERENCE.md)
- **For Validation**: Read [VALIDATION_GUIDE.md](./validation/VALIDATION_GUIDE.md)
- **For Deployment**: Read [DEPLOYMENT_GUIDE.md](./deployment/DEPLOYMENT_GUIDE.md)

---

## Support

- **Technical Issues**: Check logs and [TROUBLESHOOTING.md](./deployment/TROUBLESHOOTING.md)
- **Clinical Questions**: Review rules in `rules_v1.1.0.json`
- **Deployment Help**: See [DEPLOYMENT_GUIDE.md](./deployment/DEPLOYMENT_GUIDE.md)
