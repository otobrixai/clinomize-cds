# CardioIQ Clinical Review Form

# For Doctor Sign-Off

**Hospital**: ****\_\_\_****  
**Date**: ****\_\_\_****  
**Reviewer Name**: ****\_\_\_****  
**Specialty**: [ ] Cardiology [ ] Emergency Medicine [ ] Internal Medicine  
**Years of Experience**: ****\_\_\_****

---

## Instructions

Please review the following 10 representative cases from CardioIQ.  
For each case, answer the single most important question:

> **"Would this recommendation ever cause harm or delay?"**

If you hesitate → the rule needs revision.

---

## Case Review

### Case 1: STEMI - Typical Presentation

**Input**:

- Age 55M, typical chest pain
- ST elevation present
- Positive troponin
- No cath lab available

**CardioIQ Output**:

- Category: STEMI
- Level of Care: CCU
- Action: "Assess for immediate reperfusion (Primary PCI vs Thrombolysis). Transfer to PCI-capable center if transport < 120min"

**Your Assessment**:

- [ ] ✅ Safe - Would follow this recommendation
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe - Would cause harm/delay

**Comments**: ****\_\_\_****

---

### Case 2: NSTEMI - Equivocal

**Input**:

- Age 58M, typical chest pain
- ST depression present
- Troponin pending (not yet available)

**CardioIQ Output**:

- Category: Possible ACS - Troponin Pending
- Level of Care: CCU
- Action: "Admit for serial troponin monitoring. Repeat in 3-6 hours."
- Warning: "ST depression present - do not discharge until troponin results available"

**Your Assessment**:

- [ ] ✅ Safe
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe

**Comments**: ****\_\_\_****

---

### Case 3: Low-Risk Chest Pain (Cost Control)

**Input**:

- Age 32M, atypical chest pain
- Normal ECG
- Negative troponin
- No risk factors

**CardioIQ Output**:

- Category: Low Risk Chest Pain
- Level of Care: ER
- Action: "Consider safe discharge with follow-up"
- Cost Flag: "Potentially avoidable admission"

**Your Assessment**:

- [ ] ✅ Safe
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe

**Comments**: ****\_\_\_****

---

### Case 4: Troponin Unavailable (Bangladesh Reality)

**Input**:

- Age 55M, typical chest pain
- ST depression present
- **Troponin unavailable** (facility constraint)

**CardioIQ Output**:

- Category: Chest Pain - Troponin Unavailable (Clinical Judgment Required)
- Level of Care: Ward
- Action: "Base decision on ECG, clinical presentation, and risk factors. Consider transfer if high suspicion."
- Warning: "No troponin available - rely on clinical judgment and ECG findings"

**Your Assessment**:

- [ ] ✅ Safe
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe

**Comments**: ****\_\_\_****

---

### Case 5: Elderly Atypical Presentation

**Input**:

- Age 75F, atypical chest pain (epigastric)
- Dyspnea present
- Normal ECG
- Negative troponin

**CardioIQ Output**:

- Category: Atypical ACS Presentation (Elderly)
- Level of Care: Ward
- Action: "Rule out ACS with troponin and ECG. Consider atypical presentations in elderly."
- Warning: "Elderly patients may present atypically - maintain high index of suspicion"

**Your Assessment**:

- [ ] ✅ Safe
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe

**Comments**: ****\_\_\_****

---

### Case 6: Renal Failure + Positive Troponin

**Input**:

- Age 65M, chest pain
- Creatinine 3.5 (CKD)
- Positive troponin
- No ST elevation

**CardioIQ Output**:

- Category: Elevated Troponin with Renal Dysfunction
- Level of Care: CCU
- Action: "Correlate with clinical presentation and ECG. Consider serial troponins and cardiology consult."
- Warning: "Chronic kidney disease can cause baseline troponin elevation - assess trend and clinical context"

**Your Assessment**:

- [ ] ✅ Safe
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe

**Comments**: ****\_\_\_****

---

### Case 7: Female Atypical Presentation

**Input**:

- Age 60F, atypical chest pain
- Fatigue, nausea
- Normal ECG
- Negative troponin

**CardioIQ Output**:

- Action: "Consider ACS despite atypical presentation. Women often present differently."
- Warning: "Female patients may have atypical ACS presentations - maintain clinical vigilance"

**Your Assessment**:

- [ ] ✅ Safe
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe

**Comments**: ****\_\_\_****

---

### Case 8: Low ECG Confidence

**Input**:

- Age 60M, typical chest pain
- ECG interpretation confidence: LOW
- Negative troponin

**CardioIQ Output**:

- Action: "Repeat ECG or obtain expert interpretation. Do not rely solely on uncertain ECG."
- Warning: "ECG interpretation uncertain - consider cardiology consult or repeat ECG"

**Your Assessment**:

- [ ] ✅ Safe
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe

**Comments**: ****\_\_\_****

---

### Case 9: Prior MI + Chest Pain

**Input**:

- Age 62M, known CAD, prior MI
- Chest pain
- Negative troponin (initial)

**CardioIQ Output**:

- Category: Chest Pain with CAD History - Troponin Negative
- Level of Care: Ward
- Action: "Observe and repeat troponin. Consider stress testing if low risk."
- Warning: "Prior CAD increases risk - do not discharge without serial troponins"

**Your Assessment**:

- [ ] ✅ Safe
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe

**Comments**: ****\_\_\_****

---

### Case 10: Medication Safety (QT Risk)

**Input**:

- Age 48F, no chest pain
- Potassium 2.8 (hypokalemia)

**CardioIQ Output**:

- Warning: "Increased risk of QT prolongation"
- Action: "Review QT-prolonging medications and electrolytes"

**Your Assessment**:

- [ ] ✅ Safe
- [ ] ⚠️ Acceptable with modifications: ****\_\_\_****
- [ ] ❌ Unsafe

**Comments**: ****\_\_\_****

---

## Overall Assessment

### 1. Clinical Safety

Would you trust this system in your ER?

- [ ] Yes, without reservation
- [ ] Yes, with minor modifications
- [ ] No, needs major revision

**Explanation**: ****\_\_\_****

### 2. Bangladesh Applicability

Does this account for local constraints (troponin availability, ECG quality, cath lab access)?

- [ ] Yes, well adapted
- [ ] Partially - needs improvement
- [ ] No, not realistic

**Explanation**: ****\_\_\_****

### 3. Guideline Alignment

Are recommendations consistent with ESC/ACC guidelines adapted for Bangladesh?

- [ ] Yes
- [ ] Mostly
- [ ] No

**Explanation**: ****\_\_\_****

### 4. Medico-Legal Protection

Are disclaimers and decision support language adequate?

- [ ] Yes, legally defensible
- [ ] Needs strengthening
- [ ] Insufficient

**Explanation**: ****\_\_\_****

### 5. Workflow Integration

Could this be used in a busy ER without disrupting workflow?

- [ ] Yes, < 2 minutes per patient
- [ ] Maybe, depends on training
- [ ] No, too slow/complex

**Explanation**: ****\_\_\_****

---

## Final Recommendation

- [ ] ✅ **APPROVE** for pilot testing
- [ ] ⚠️ **CONDITIONAL APPROVAL** - address issues below
- [ ] ❌ **DO NOT PILOT** - major safety concerns

**Critical Issues to Address** (if not approved):

1. ***
2. ***
3. ***

**Suggested Improvements**:

1. ***
2. ***
3. ***

---

**Reviewer Signature**: ****\_\_\_****  
**Date**: ****\_\_\_****  
**Contact**: ****\_\_\_****

---

## For CardioIQ Team Use Only

**Review Received**: ****\_\_\_****  
**Issues Addressed**: ****\_\_\_****  
**Follow-up Required**: [ ] Yes [ ] No  
**Next Steps**: ****\_\_\_****
