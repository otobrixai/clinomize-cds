# TransfusionIQ API Endpoints

**Total Endpoints:** 35

## Uncategorized

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root |
| `GET` | `/health` | Health |

## admin

| Method | Path | Description |
|--------|------|-------------|
| `DELETE` | `/api/v1/admin/thresholds/thresholds/{config_id}` | Delete Threshold |
| `GET` | `/api/v1/admin/admin/ai/evidence-summary` | Get Ai Evidence Summary |
| `GET` | `/api/v1/admin/admin/ai/evidence-summary` | Get Ai Evidence Summary |
| `GET` | `/api/v1/admin/admin/ai/status` | Get Ai Status |
| `GET` | `/api/v1/admin/admin/ai/status` | Get Ai Status |
| `GET` | `/api/v1/admin/thresholds/thresholds` | Get Thresholds |
| `POST` | `/api/v1/admin/thresholds/thresholds` | Create Threshold |

## admin-thresholds

| Method | Path | Description |
|--------|------|-------------|
| `DELETE` | `/api/v1/admin/thresholds/thresholds/{config_id}` | Delete Threshold |
| `GET` | `/api/v1/admin/thresholds/thresholds` | Get Thresholds |
| `POST` | `/api/v1/admin/thresholds/thresholds` | Create Threshold |

## analytics

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/analytics/blood-product-costs` | Get Blood Product Costs |
| `GET` | `/api/v1/analytics/component-usage` | Get Component Usage |
| `GET` | `/api/v1/analytics/roi-summary` | Get Hospital Roi Summary |
| `POST` | `/api/v1/analytics/blood-product-costs` | Create Blood Product Cost |
| `POST` | `/api/v1/analytics/calculate/{hospital_id}/{year_month}` | Calculate Analytics For Month |
| `POST` | `/api/v1/analytics/recalculate-monthly/{year_month}` | Recalculate Monthly Analytics |

## audit

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/audit/logs/{encounter_id}` | Get Audit Logs |
| `POST` | `/api/v1/audit/override` | Log Override |

## auth

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/auth/me` | Get Current User Info |
| `POST` | `/api/v1/auth/register` | Register |
| `POST` | `/api/v1/auth/token` | Login |

## hospital-admin

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/hospital-admin/users` | Get Hospital Users |
| `POST` | `/api/v1/hospital-admin/users` | Create Hospital User |
| `PUT` | `/api/v1/hospital-admin/users/{user_id}/activate` | Activate User |
| `PUT` | `/api/v1/hospital-admin/users/{user_id}/deactivate` | Deactivate User |

## pdf

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/pdf/encounter/{encounter_id}/pdf` | Export Encounter Pdf |
| `GET` | `/api/v1/pdf/{recommendation_id}/pdf` | Export Recommendation Pdf |

## recommendations

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/recommendations/encounter/{encounter_id}` | Get Recommendations For Encounter |
| `GET` | `/api/v1/recommendations/{recommendation_id}` | Get Recommendation |
| `POST` | `/api/v1/recommendations/evaluate` | Evaluate Patient |
| `POST` | `/api/v1/recommendations/{recommendation_id}/outcome` | Record Outcome |

## rules

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/rules` | Get Rules |
| `GET` | `/api/v1/rules/versions` | List Rule Versions |

## super-admin

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/super-admin/all-users` | Get All Users |
| `GET` | `/api/v1/super-admin/all-users` | Get All Users |
| `GET` | `/api/v1/super-admin/hospitals` | Get Hospitals |
| `GET` | `/api/v1/super-admin/hospitals` | Get Hospitals |
| `GET` | `/api/v1/super-admin/hospitals/{hospital_id}` | Get Hospital |
| `GET` | `/api/v1/super-admin/hospitals/{hospital_id}` | Get Hospital |
| `GET` | `/api/v1/super-admin/hospitals/{hospital_id}/users` | Get Hospital Users |
| `GET` | `/api/v1/super-admin/hospitals/{hospital_id}/users` | Get Hospital Users |
| `GET` | `/api/v1/super-admin/system-stats` | Get System Stats |
| `GET` | `/api/v1/super-admin/system-stats` | Get System Stats |
| `POST` | `/api/v1/super-admin/hospitals` | Create Hospital |
| `POST` | `/api/v1/super-admin/hospitals` | Create Hospital |
| `POST` | `/api/v1/super-admin/users` | Create User |
| `POST` | `/api/v1/super-admin/users` | Create User |

## test

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/cors-test` | Cors Test |
| `GET` | `/api/v1/test-roi-summary` | Test Roi Summary |

