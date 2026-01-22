import sys
import os

# Ensure backend path is in pythonpath
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up 4 levels to get to 'transfusion-cds/backend' -> we want 'backend' to be the root for 'app' imports?
# Actually simpler: add 'backend' folder to sys.path
backend_path = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(backend_path)

from app.cardioiq.schemas import (
    CardioIQInput, PatientInput, PresentationInput, VitalsInput, 
    ECGInput, LabsInput, HistoryInput, MedicationsInput, 
    TroponinInput, ClinicalContext
)
from app.cardioiq.service import CardioIQService

# from rich import print as rprint
rprint = print

def create_mock_input(
    chest_pain=True, st_elevation=False, troponin_pos=False, 
    potassium=4.0, age=55, **kwargs
):
    return CardioIQInput(
        patient=PatientInput(age=age, sex=kwargs.get("sex", "male"), weight_kg=70),
        presentation=PresentationInput(
            chest_pain=chest_pain, 
            chest_pain_type=kwargs.get("chest_pain_type", "typical" if chest_pain else "non_cardiac"),
            dyspnea=kwargs.get("dyspnea", False), 
            syncope=False
        ),
        vitals=VitalsInput(sbp=120, hr=80, spo2=98),
        ecg=ECGInput(
            st_elevation=st_elevation,
            st_depression=kwargs.get("st_depression", False),
            confidence=kwargs.get("ecg_confidence", "high")
        ),
        labs=LabsInput(
            troponin=TroponinInput(value=0.01, unit="ng/mL", positive=troponin_pos) if kwargs.get("troponin_status", "available") == "available" else None,
            troponin_status=kwargs.get("troponin_status", "available"),
            creatinine=kwargs.get("creatinine", 0.9),
            potassium=potassium
        ),
        history=HistoryInput(cad=kwargs.get("cad", False)),
        medications=MedicationsInput(),
        context=ClinicalContext(care_setting="ER")
    )

def test_stemi_scenario():
    rprint("\n[TEST 1: STEMI]")
    data = create_mock_input(chest_pain=True, st_elevation=True)
    result = CardioIQService.evaluate_patient(data)
    
    rprint(f"  Category: {result.clinical_category}")
    rprint(f"  Level: {result.recommended_level_of_care}")
    
    assert "STEMI" in result.clinical_category
    assert "CCU" == result.recommended_level_of_care
    rprint("  ✅ PASS\n")

def test_nstemi_equivocal():
    rprint("\n[TEST 2: NSTEMI Equivocal - ST Depression + Pending Troponin]")
    data = create_mock_input(
        chest_pain=True, 
        st_depression=True, 
        troponin_status="pending"
    )
    result = CardioIQService.evaluate_patient(data)
    
    rprint(f"  Category: {result.clinical_category}")
    rprint(f"  Level: {result.recommended_level_of_care}")
    rprint(f"  Warnings: {result.safety_warnings}")
    
    assert "Pending" in result.clinical_category or "Possible ACS" in result.clinical_category
    assert "CCU" == result.recommended_level_of_care
    rprint("  ✅ PASS\n")

def test_elderly_atypical():
    rprint("\n[TEST 3: Elderly Atypical Presentation]")
    data = create_mock_input(
        chest_pain=True,
        chest_pain_type="atypical",
        dyspnea=True,
        age=75
    )
    result = CardioIQService.evaluate_patient(data)
    
    rprint(f"  Category: {result.clinical_category}")
    rprint(f"  Warnings: {result.safety_warnings}")
    
    assert any("Elderly" in w or "atypical" in w.lower() for w in result.safety_warnings + [result.clinical_category])
    rprint("  ✅ PASS\n")

def test_renal_troponin():
    rprint("\n[TEST 4: Renal Failure + Positive Troponin]")
    data = create_mock_input(
        troponin_pos=True,
        creatinine=3.5
    )
    result = CardioIQService.evaluate_patient(data)
    
    rprint(f"  Category: {result.clinical_category}")
    rprint(f"  Warnings: {result.safety_warnings}")
    
    assert any("Renal" in w or "kidney" in w.lower() for w in result.safety_warnings + [result.clinical_category])
    rprint("  ✅ PASS\n")

def test_prior_mi():
    rprint("\n[TEST 5: Prior CAD + Chest Pain + Negative Troponin]")
    data = create_mock_input(
        chest_pain=True,
        troponin_pos=False,
        cad=True
    )
    result = CardioIQService.evaluate_patient(data)
    
    rprint(f"  Category: {result.clinical_category}")
    rprint(f"  Warnings: {result.safety_warnings}")
    
    assert any("CAD" in w or "serial" in w.lower() for w in result.safety_warnings + result.recommended_actions)
    rprint("  ✅ PASS\n")

def test_female_atypical():
    rprint("\n[TEST 6: Female Atypical Presentation]")
    data = create_mock_input(
        chest_pain=True,
        chest_pain_type="atypical",
        age=60,
        sex="female"
    )
    result = CardioIQService.evaluate_patient(data)
    
    rprint(f"  Warnings: {result.safety_warnings}")
    
    assert any("Female" in w or "Women" in w for w in result.safety_warnings + result.recommended_actions)
    rprint("  ✅ PASS\n")

def test_troponin_unavailable():
    rprint("\n[TEST 7: Troponin Unavailable (Bangladesh Reality)]")
    data = create_mock_input(
        chest_pain=True,
        troponin_status="unavailable"
    )
    result = CardioIQService.evaluate_patient(data)
    
    rprint(f"  Category: {result.clinical_category}")
    rprint(f"  Warnings: {result.safety_warnings}")
    
    assert any("unavailable" in w.lower() or "judgment" in w.lower() for w in result.safety_warnings + [result.clinical_category])
    rprint("  ✅ PASS\n")

def test_low_ecg_confidence():
    rprint("\n[TEST 8: Low ECG Confidence]")
    data = create_mock_input(
        chest_pain=True,
        ecg_confidence="low"
    )
    result = CardioIQService.evaluate_patient(data)
    
    rprint(f"  Warnings: {result.safety_warnings}")
    
    assert any("ECG" in w and ("uncertain" in w.lower() or "confidence" in w.lower()) for w in result.safety_warnings + result.recommended_actions)
    rprint("  ✅ PASS\n")

def test_low_risk():
    rprint("\n[TEST 9: Low Risk Chest Pain (Cost Saver)]")
    data = create_mock_input(chest_pain=True, st_elevation=False, troponin_pos=False, age=30)
    data.history.cad = False 
    
    result = CardioIQService.evaluate_patient(data)
    
    rprint(f"  Category: {result.clinical_category}")
    rprint(f"  Cost Flags: {result.cost_flags}")
    
    assert "Low Risk" in result.clinical_category
    rprint("  ✅ PASS\n")

if __name__ == "__main__":
    try:
        test_stemi_scenario()
        test_nstemi_equivocal()
        test_elderly_atypical()
        test_renal_troponin()
        test_prior_mi()
        test_female_atypical()
        test_troponin_unavailable()
        test_low_ecg_confidence()
        test_low_risk()
        
        rprint("\n" + "="*60)
        rprint("✅ ALL EDGE CASE TESTS PASSED")
        rprint("="*60)
    except Exception as e:
        rprint(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
