# CardioIQ Backend Documentation

## Overview

This directory contains all documentation for the CardioIQ Clinical Decision Support module.

---

## Documentation Structure

```
backend/app/cardioiq/docs/
├── README.md                          # This file
├── GETTING_STARTED.md                 # Quick start guide
├── api/
│   ├── API_REFERENCE.md              # API endpoint documentation
│   └── INTEGRATION_GUIDE.md          # How to integrate with frontend
├── validation/
│   ├── VALIDATION_GUIDE.md           # How to run validation
│   ├── DOCTOR_REVIEW_FORM.md         # Clinical expert review template
│   ├── PILOT_READINESS_CHECKLIST.md  # Go/No-Go checklist
│   └── dataset_v1.0.yaml             # Validation dataset schema
└── ../../../../                      # Project Root
    ├── DATABASE_PRODUCTION_SETUP.md  # Database setup guide
    ├── DEPLOYMENT_READINESS.md       # Production deployment
    └── TROUBLESHOOTING.md            # Common issues and solutions
```

---

## Quick Links

### For Developers

- [Getting Started](./GETTING_STARTED.md) - Set up and run CardioIQ
- [API Reference](./api/API_REFERENCE.md) - API endpoints and usage
- [Integration Guide](./api/INTEGRATION_GUIDE.md) - Frontend integration

### For Clinical Validation

- [Validation Guide](./validation/VALIDATION_GUIDE.md) - Run automated tests
- [Doctor Review Form](./validation/DOCTOR_REVIEW_FORM.md) - Clinical expert review
- [Pilot Readiness Checklist](./validation/PILOT_READINESS_CHECKLIST.md) - Pre-deployment checklist

### For Deployment

- [Database Migration](../../../../DATABASE_PRODUCTION_SETUP.md) - Set up database
- [Deployment Guide](../../../../DEPLOYMENT_READINESS.md) - Deploy to production
- [Troubleshooting](../../../../TROUBLESHOOTING.md) - Fix common issues

---

## Module Structure

```
backend/app/cardioiq/
├── docs/                  # Documentation (you are here)
├── engine.py             # Rules engine implementation
├── schemas.py            # Pydantic data models
├── service.py            # Business logic layer
├── rules_v1.1.0.json    # Clinical decision rules
├── tests/               # Unit tests
└── validation/          # Validation framework
    ├── clinical_validator.py
    ├── dataset_v1.0.yaml
    └── validation_results.json
```

---

## Key Files

### Core Implementation

- **`engine.py`** - CardioIQ rules engine (deterministic logic)
- **`schemas.py`** - Input/output data models
- **`service.py`** - Service layer for API
- **`rules_v1.1.0.json`** - Clinical decision rules (v1.1.0)

### Database

- **`backend/app/models/cardioiq.py`** - Database models
- **`backend/alembic/versions/cardioiq_001_create_tables.py`** - Migration script

### API

- **`backend/app/api/v1/cardioiq.py`** - REST API endpoints

### Validation

- **`validation/clinical_validator.py`** - Automated testing framework
- **`validation/dataset_v1.0.yaml`** - 72-case validation dataset

---

## Current Status

| Component          | Status       | Version      |
| ------------------ | ------------ | ------------ |
| Rules Engine       | ✅ Complete  | v1.1.0       |
| Database Models    | ✅ Complete  | v1.0         |
| API Endpoints      | ✅ Complete  | v1.0         |
| Frontend UI        | ✅ Complete  | v1.0         |
| Validation         | ✅ 100% Pass | 72 cases     |
| Database Migration | ✅ Complete  | cardioiq_001 |
| Doctor Review      | ⏳ Pending   | -            |
| Pilot Deployment   | ⏳ Pending   | -            |

---

## Getting Started

### 1. Run the Backend

```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
uvicorn app.main:app --reload
```

### 2. Test the API

```bash
curl -X POST http://localhost:8000/api/v1/cardioiq/evaluate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d @test_case.json
```

### 3. Run Validation

```bash
cd backend
python app/cardioiq/validation/clinical_validator.py
```

---

## For Clinical Reviewers

If you're a doctor reviewing CardioIQ for clinical safety:

1. Read [DOCTOR_REVIEW_FORM.md](./validation/DOCTOR_REVIEW_FORM.md)
2. Review 10-15 representative cases
3. Answer the single critical question: "Would this cause harm or delay?"
4. Provide feedback and sign off

---

## For Hospital Administrators

If you're evaluating CardioIQ for pilot deployment:

1. Review [PILOT_READINESS_CHECKLIST.md](./validation/PILOT_READINESS_CHECKLIST.md)
2. Verify all technical requirements are met
3. Ensure legal disclaimers are in place
4. Confirm doctor sign-off
5. Make Go/No-Go decision

---

## Support

For technical issues:

- Check [TROUBLESHOOTING.md](./deployment/TROUBLESHOOTING.md)
- Review validation results in `validation/validation_results.json`
- Check backend logs for errors

For clinical questions:

- Review rules in `rules_v1.1.0.json`
- Check guideline references in rule metadata
- Consult with cardiology team

---

## Version History

### v1.1.0 (Current)

- ✅ 13 clinical decision rules
- ✅ Hemodynamic instability detection (ICU escalation)
- ✅ Bangladesh-specific constraints
- ✅ 100% validation pass rate (72 cases)
- ✅ Database integration with audit logging
- ✅ Legal disclaimers on UI

### v1.0.0 (Initial)

- Basic STEMI/NSTEMI detection
- 8 core rules
- Initial validation framework

---

## License & Disclaimer

**IMPORTANT**: This is a Clinical Decision Support system, NOT a diagnostic tool.

- Final clinical decisions rest with the treating physician
- Recommendations must be verified against local protocols
- System outputs are advisory only, not prescriptive
- All recommendations require clinical correlation

---

## Contributing

To contribute to CardioIQ:

1. Follow existing code patterns
2. Add tests for new rules
3. Update validation dataset
4. Document changes in this README
5. Get clinical review for rule changes

---

## Contact

For questions or issues:

- Technical: [Your Dev Team]
- Clinical: [Your Clinical Team]
- Deployment: [Your DevOps Team]
