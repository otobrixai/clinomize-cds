# CardioIQ Pilot Readiness Checklist

# Use this LITERALLY before hospital deployment

## Clinical Validation ✓

- [ ] **50+ synthetic cases validated**
  - Current: 72 cases in `dataset_v1.0.yaml`
  - Status: ****\_\_\_****
- [ ] **10+ cases reviewed by local doctors**
  - Cardiologist sign-off: ****\_\_\_****
  - ER Physician sign-off: ****\_\_\_****
  - Date: ****\_\_\_****

- [ ] **Edge cases explicitly handled**
  - NSTEMI equivocal: ✓
  - Elderly atypical: ✓
  - Renal troponin: ✓
  - Prior MI: ✓
  - Female risk: ✓
  - Troponin unavailable: ✓
  - Low ECG confidence: ✓
  - Status: ****\_\_\_****

- [ ] **Missing data fails safely**
  - No discharge when data insufficient: ****\_\_\_****
  - Conservative escalation verified: ****\_\_\_****
  - Status: ****\_\_\_****

## Engine Verification ✓

- [ ] **Deterministic outputs confirmed**
  - Same input → same output (100 runs): ****\_\_\_****
  - No random ordering: ****\_\_\_****
  - Status: ****\_\_\_****

- [ ] **Facility capability logic tested**
  - PCI available vs unavailable: ****\_\_\_****
  - Transfer recommendations correct: ****\_\_\_****
  - Status: ****\_\_\_****

## Legal & Compliance ✓

- [ ] **Legal disclaimer embedded**
  - "Decision Support Only" visible: ****\_\_\_****
  - Location: ****\_\_\_****
  - Status: ****\_\_\_****

- [ ] **Rule citation present**
  - Guideline references shown: ****\_\_\_****
  - Version number displayed: ****\_\_\_****
  - Status: ****\_\_\_****

- [ ] **Decision audit log generated**
  - Timestamp recorded: ****\_\_\_****
  - User ID captured: ****\_\_\_****
  - Rule version logged: ****\_\_\_****
  - Status: ****\_\_\_****

- [ ] **No autonomous decision language**
  - All text reviewed: ****\_\_\_****
  - "Recommend" vs "Order" verified: ****\_\_\_****
  - Status: ****\_\_\_****

## Safety Testing ✓

- [ ] **STEMI never discharged**
  - All 12 STEMI cases escalated: ****\_\_\_****
  - Status: ****\_\_\_****

- [ ] **ECG ischemia overrides scores**
  - Precedence verified: ****\_\_\_****
  - Status: ****\_\_\_****

- [ ] **Red-team test passed**
  - Doctor attempted to break system: ****\_\_\_****
  - Doctor name: ****\_\_\_****
  - Result: ****\_\_\_****
  - Status: ****\_\_\_****

## Performance ✓

- [ ] **Latency acceptable**
  - Rapid Mode < 30 seconds: ****\_\_\_****
  - Full Mode < 2 minutes: ****\_\_\_****
  - Status: ****\_\_\_****

## Bangladesh-Specific ✓

- [ ] **Troponin unavailable handled**
  - Conservative recommendations: ****\_\_\_****
  - Clinical judgment notes: ****\_\_\_****
  - Status: ****\_\_\_****

- [ ] **ECG confidence levels work**
  - Low confidence → expert review: ****\_\_\_****
  - Status: ****\_\_\_****

- [ ] **Facility capability branching**
  - Cath lab logic verified: ****\_\_\_****
  - Transfer logic verified: ****\_\_\_****
  - Status: ****\_\_\_****

---

## FINAL GO / NO-GO DECISION

**Date**: ****\_\_\_****

**Reviewers**:

- Clinical Lead: ****\_\_\_****
- Technical Lead: ****\_\_\_****
- Hospital Admin: ****\_\_\_****

**Decision**:

- [ ] ✅ GO - Pilot Approved
- [ ] ❌ NO-GO - Address issues below

**Issues to Address** (if NO-GO):

1. ***
2. ***
3. ***

**Pilot Plan** (if GO):

- Hospital: ****\_\_\_****
- Department: ER Chest Pain Triage Only
- Duration: ****\_\_\_**** (recommended: 2-4 weeks)
- Champion Physician: ****\_\_\_****
- Success Criteria: ****\_\_\_****

---

## Post-Pilot Review Checklist

- [ ] No adverse events
- [ ] Doctor adoption rate > 50%
- [ ] Average evaluation time < 2 min
- [ ] Cost savings documented
- [ ] Feedback collected
- [ ] Refinements identified

**Signature**: ****\_\_\_****  
**Date**: ****\_\_\_****
