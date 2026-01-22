# CardioIQ Validation Testing Guide

## Quick Start

Run the comprehensive clinical validation:

```bash
cd backend
python app/cardioiq/validation/clinical_validator.py
```

This will:

1. Load all 72 validation cases
2. Test each case against the CardioIQ engine
3. Check for safety violations
4. Verify determinism (same input → same output)
5. Generate a pass/fail report

## What Gets Tested

### 1. Clinical Safety (CRITICAL)

- ✅ No unsafe discharge recommendations
- ✅ STEMI always escalated to CCU
- ✅ Missing data fails conservatively
- ✅ ECG ischemia overrides risk scores

### 2. Guideline Alignment

- ✅ ESC ACS 2023 compliance
- ✅ ACC/AHA Chest Pain 2021 compliance
- ✅ Bangladesh adaptations present

### 3. Cost Control

- ✅ Low-risk chest pain → discharge allowed
- ✅ Cost flags set appropriately
- ✅ Unnecessary CCU admissions avoided

### 4. Engine Determinism

- ✅ Same input produces same output (3 runs)
- ✅ No random ordering
- ✅ Stable category assignment

## Test Categories

| Category             | Cases  | Purpose                  |
| -------------------- | ------ | ------------------------ |
| STEMI                | 12     | Core safety - never miss |
| NSTEMI               | 10     | Troponin logic           |
| Low-Risk Chest Pain  | 12     | Cost control             |
| ECG Ambiguous        | 8      | Bangladesh reality       |
| Troponin Unavailable | 6      | Resource constraints     |
| AHF Overlap          | 6      | Mixed presentations      |
| Medication Safety    | 6      | Non-ACS alerts           |
| **TOTAL**            | **72** | **Complete coverage**    |

## Pass/Fail Criteria

### PASS Requirements

- ✅ All 72 cases pass validation
- ✅ Zero safety-critical failures
- ✅ Deterministic outputs (100% match)
- ✅ Required actions present
- ✅ Required warnings present

### FAIL Triggers

- ❌ Any STEMI recommended for discharge
- ❌ Missing data → reassurance given
- ❌ ECG ischemia overridden by low score
- ❌ Non-deterministic output
- ❌ Level of care too low for severity

## Expected Output

```
================================================================================
CardioIQ Clinical Validation Framework
================================================================================

Total cases to validate: 72

Case Distribution:
  STEMI: 12
  NSTEMI: 10
  Low Risk: 12
  ECG Ambiguous: 8
  Troponin Unavailable: 6
  AHF Overlap: 6
  Medication Safety: 6

--------------------------------------------------------------------------------
Running Validation Tests...
--------------------------------------------------------------------------------

✅ PASS | BD_ACS_001 | STEMI
✅ PASS | BD_ACS_002 | STEMI
✅ PASS | BD_ACS_003 | STEMI
...

================================================================================
VALIDATION SUMMARY
================================================================================

Total Cases: 72
Passed: 72 (100.0%)
Failed: 0

Category Breakdown:
  STEMI: 12/12 passed
  NSTEMI: 10/10 passed
  Low Risk: 12/12 passed
  ECG Ambiguous: 8/8 passed
  Troponin Unavailable: 6/6 passed
  AHF Overlap: 6/6 passed
  Medication Safety: 6/6 passed

================================================================================
✅ PILOT READY - All validation tests passed
================================================================================
```

## Next Steps After Validation

1. **If ALL PASS**:
   - ✅ Proceed to doctor review (use `DOCTOR_REVIEW_FORM.md`)
   - ✅ Complete `PILOT_READINESS_CHECKLIST.md`
   - ✅ Schedule pilot deployment

2. **If ANY FAIL**:
   - ❌ Review `validation_results.json` for details
   - ❌ Fix failing rules in `rules_v1.1.0.json`
   - ❌ Re-run validation
   - ❌ Do NOT proceed to pilot

## Troubleshooting

### Common Issues

**Issue**: "Non-deterministic output detected"

- **Cause**: Engine has randomness or time-dependent logic
- **Fix**: Review engine.py for any random/time-based code

**Issue**: "Level of care too low"

- **Cause**: Rule priority incorrect
- **Fix**: Increase priority of safety-critical rules

**Issue**: "Missing required action"

- **Cause**: Rule actions incomplete
- **Fix**: Add missing actions to rule JSON

## Files Generated

- `validation_results.json` - Detailed pass/fail for each case
- Console output - Summary report

## Manual Testing (Optional)

After automated validation, manually test edge cases:

1. Try to make the system recommend discharge for STEMI
2. Test with all missing data
3. Test with conflicting inputs
4. Verify latency < 30 seconds

## Doctor Review Process

1. Run automated validation (must pass 100%)
2. Select 10-15 cases for doctor review
3. Use `DOCTOR_REVIEW_FORM.md`
4. Address any doctor concerns
5. Re-validate
6. Get sign-off

## Pilot Deployment Checklist

Before going live:

- [ ] Automated validation: 100% pass
- [ ] Doctor review: Approved
- [ ] Latency test: < 30 seconds
- [ ] Legal disclaimers: Present
- [ ] Audit logging: Working
- [ ] Pilot hospital: Identified
- [ ] Champion physician: Committed

---

**Remember**: Code passing tests ≠ clinically safe.  
This validation framework bridges that gap.
