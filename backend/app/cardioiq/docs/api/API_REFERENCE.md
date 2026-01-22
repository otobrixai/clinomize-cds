# CardioIQ API Reference

## Base URL

```
http://localhost:8000/api/v1/cardioiq
```

---

## Authentication

All endpoints require JWT authentication.

```http
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### 1. Evaluate Patient

**POST** `/evaluate`

Evaluates a patient and returns cardiac recommendations.

#### Request Body

```json
{
  "patient": {
    "age": 55,
    "sex": "male",
    "weight_kg": 70
  },
  "presentation": {
    "chest_pain": true,
    "chest_pain_type": "typical",
    "dyspnea": false,
    "syncope": false
  },
  "vitals": {
    "sbp": 120,
    "hr": 80,
    "spo2": 98
  },
  "ecg": {
    "st_elevation": false,
    "st_depression": false,
    "t_wave_inversion": false,
    "non_diagnostic": false,
    "confidence": "high"
  },
  "labs": {
    "troponin_status": "available",
    "troponin": {
      "positive": false,
      "value": 0.01,
      "unit": "ng/mL"
    },
    "creatinine": 1.0,
    "potassium": 4.0
  },
  "history": {
    "cad": false,
    "diabetes": false,
    "hypertension": false,
    "ckd": false,
    "heart_failure": false,
    "stroke": false
  },
  "medications": {
    "beta_blocker": false,
    "digoxin": false,
    "qt_prolonging_drugs": false
  },
  "context": {
    "care_setting": "ER",
    "hospital_capability": {
      "has_cath_lab": false,
      "can_transfer_primary_pci": false,
      "has_on_site_troponin": true
    }
  }
}
```

#### Response

```json
{
  "clinical_category": "Low Risk Chest Pain",
  "recommended_level_of_care": "ER",
  "risk_scores": [
    {
      "score_name": "HEART Score",
      "value": 3,
      "risk_category": "Low",
      "details": {
        "history": 0,
        "ecg": 0,
        "age": 1,
        "risk_factors": 1,
        "troponin": 0
      }
    }
  ],
  "recommended_actions": ["Consider safe discharge with follow-up"],
  "safety_warnings": [],
  "cost_flags": ["Potentially avoidable admission"],
  "rationale_summary": [
    "Low HEART score (<=3) with negative troponin and non-ischemic ECG indicates low short-term risk of MACE."
  ],
  "guideline_links": ["ACC Chest Pain Guideline 2021"],
  "rule_hits": ["CP_RULEOUT_001"]
}
```

#### Status Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing or invalid token
- `500 Internal Server Error` - Server error

---

### 2. Get Encounter

**GET** `/encounter/{encounter_id}`

Retrieves a specific CardioIQ encounter and its recommendation.

#### Parameters

- `encounter_id` (path, required) - The encounter ID

#### Response

```json
{
  "encounter": {
    "id": 1,
    "patient_id": "CARDIO_1_1",
    "age": 55,
    "sex": "male",
    "chest_pain": true,
    "sbp": 120,
    "created_at": "2026-01-21T01:00:00Z"
  },
  "recommendation": {
    "id": 1,
    "encounter_id": 1,
    "clinical_category": "Low Risk Chest Pain",
    "recommended_level_of_care": "ER",
    "recommended_actions": ["..."],
    "created_at": "2026-01-21T01:00:00Z"
  }
}
```

---

### 3. Record Outcome

**POST** `/{recommendation_id}/outcome`

Records the actual outcome for QA purposes.

#### Parameters

- `recommendation_id` (path, required) - The recommendation ID

#### Request Body

```json
{
  "actual_level_of_care": "Ward",
  "recommendation_followed": true,
  "outcome_notes": "Patient admitted for observation per protocol"
}
```

#### Response

```json
{
  "status": "outcome recorded",
  "recommendation_id": 1
}
```

---

## Data Models

### CardioIQInput

Complete patient data for evaluation.

| Field        | Type         | Required | Description           |
| ------------ | ------------ | -------- | --------------------- |
| patient      | Patient      | Yes      | Demographics          |
| presentation | Presentation | Yes      | Clinical presentation |
| vitals       | Vitals       | Yes      | Vital signs           |
| ecg          | ECG          | Yes      | ECG findings          |
| labs         | Labs         | Yes      | Laboratory results    |
| history      | History      | Yes      | Medical history       |
| medications  | Medications  | Yes      | Current medications   |
| context      | Context      | Yes      | Clinical context      |

### CardioIQOutput

Recommendation from the CDS engine.

| Field                     | Type        | Description                  |
| ------------------------- | ----------- | ---------------------------- |
| clinical_category         | string      | Clinical diagnosis category  |
| recommended_level_of_care | string      | ER, Ward, CCU, or ICU        |
| risk_scores               | RiskScore[] | Calculated risk scores       |
| recommended_actions       | string[]    | Recommended clinical actions |
| safety_warnings           | string[]    | Safety alerts                |
| cost_flags                | string[]    | Cost-related flags           |
| rationale_summary         | string[]    | Clinical rationale           |
| guideline_links           | string[]    | Guideline references         |
| rule_hits                 | string[]    | Rules that fired             |

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid input: age must be between 0 and 120"
}
```

### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found

```json
{
  "detail": "Encounter not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Error evaluating patient: <error message>"
}
```

---

## Examples

### Example 1: STEMI Case

```bash
curl -X POST http://localhost:8000/api/v1/cardioiq/evaluate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "patient": {"age": 58, "sex": "male", "weight_kg": 80},
    "presentation": {"chest_pain": true, "chest_pain_type": "typical", "dyspnea": false, "syncope": false},
    "vitals": {"sbp": 110, "hr": 90, "spo2": 96},
    "ecg": {"st_elevation": true, "st_depression": false, "t_wave_inversion": false, "non_diagnostic": false, "confidence": "high"},
    "labs": {"troponin_status": "available", "troponin": {"positive": true, "value": 2.5, "unit": "ng/mL"}},
    "history": {"cad": false, "diabetes": true, "hypertension": true, "ckd": false, "heart_failure": false, "stroke": false},
    "medications": {"beta_blocker": false, "digoxin": false, "qt_prolonging_drugs": false},
    "context": {"care_setting": "ER", "hospital_capability": {"has_cath_lab": true, "can_transfer_primary_pci": false, "has_on_site_troponin": true}}
  }'
```

**Expected Response**: STEMI with CCU recommendation

---

### Example 2: Low Risk Chest Pain

```bash
curl -X POST http://localhost:8000/api/v1/cardioiq/evaluate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "patient": {"age": 45, "sex": "female", "weight_kg": 65},
    "presentation": {"chest_pain": true, "chest_pain_type": "atypical", "dyspnea": false, "syncope": false},
    "vitals": {"sbp": 125, "hr": 75, "spo2": 99},
    "ecg": {"st_elevation": false, "st_depression": false, "t_wave_inversion": false, "non_diagnostic": false, "confidence": "high"},
    "labs": {"troponin_status": "available", "troponin": {"positive": false, "value": 0.005, "unit": "ng/mL"}},
    "history": {"cad": false, "diabetes": false, "hypertension": false, "ckd": false, "heart_failure": false, "stroke": false},
    "medications": {"beta_blocker": false, "digoxin": false, "qt_prolonging_drugs": false},
    "context": {"care_setting": "ER", "hospital_capability": {"has_cath_lab": false, "can_transfer_primary_pci": false, "has_on_site_troponin": true}}
  }'
```

**Expected Response**: Low Risk Chest Pain with ER/discharge recommendation

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider:

- 100 requests per minute per user
- 1000 requests per hour per hospital

---

## Versioning

API Version: `v1`

Breaking changes will result in a new API version (v2, v3, etc.)

---

## Changelog

### v1.0.0 (2026-01-21)

- Initial API release
- `/evaluate` endpoint
- `/encounter/{id}` endpoint
- `/{id}/outcome` endpoint
- Database integration
- Audit logging
