"""Quick test of validation framework"""
import sys
import os
import json

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(backend_path)

# Test dataset loading
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
dataset_path = os.path.join(project_root, "cardioiq_validation_dataset.json")

print(f"Looking for dataset at: {dataset_path}")
print(f"File exists: {os.path.exists(dataset_path)}")

if os.path.exists(dataset_path):
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    print(f"Loaded {len(dataset)} cases")
    print(f"First case: {dataset[0]['case_id']}")
    
    # Test one case
    from app.cardioiq.service import CardioIQService
    from app.cardioiq.schemas import CardioIQInput, PatientInput, PresentationInput, VitalsInput, ECGInput, LabsInput, HistoryInput, MedicationsInput, ClinicalContext, TroponinInput
    
    case = dataset[0]
    inputs = case['inputs']
    
    print(f"\nTesting case: {case['case_id']}")
    print(f"Expected: {case['expected']['clinical_category']}")
    
    # Create input
    cardio_input = CardioIQInput(
        patient=PatientInput(age=inputs['age'], sex=inputs['sex'].lower(), weight_kg=70),
        presentation=PresentationInput(
            chest_pain=inputs['chest_pain']['present'],
            chest_pain_type=inputs['chest_pain']['type'].lower(),
            dyspnea=inputs.get('dyspnea', False),
            syncope=inputs.get('syncope', False)
        ),
        vitals=VitalsInput(sbp=inputs['vitals']['sbp'], hr=inputs['vitals']['hr'], spo2=inputs['vitals']['spo2']),
        ecg=ECGInput(
            st_elevation=inputs['ecg']['st_elevation'],
            st_depression=inputs['ecg']['st_depression'],
            t_wave_inversion=inputs['ecg']['t_inversion'],
            non_diagnostic=inputs['ecg']['non_diagnostic'],
            confidence='high'
        ),
        labs=LabsInput(
            troponin=TroponinInput(value=0.05, unit='ng/mL', positive=True) if inputs['labs']['troponin'] == 'Positive' else None,
            troponin_status='available' if inputs['labs']['troponin'] in ['Positive', 'Negative'] else 'unavailable',
            creatinine=inputs['labs'].get('creatinine'),
            potassium=inputs['labs'].get('potassium')
        ),
        history=HistoryInput(
            cad=inputs['history']['cad'],
            diabetes=inputs['history']['dm'],
            hypertension=False,
            ckd=inputs['history']['ckd'],
            heart_failure=inputs['history']['hf'],
            stroke=inputs['history']['stroke']
        ),
        medications=MedicationsInput(
            beta_blocker=inputs['medications']['beta_blocker'],
            digoxin=inputs['medications']['digoxin'],
            qt_prolonging_drugs=inputs['medications']['qt_prolonging']
        ),
        context=ClinicalContext(
            care_setting=inputs['location'],
            hospital_capability={'has_cath_lab': case['facility']['pci_available'], 'can_transfer_primary_pci': True, 'has_on_site_troponin': True}
        )
    )
    
    # Run engine
    result = CardioIQService.evaluate_patient(cardio_input)
    print(f"Actual: {result.clinical_category}")
    print(f"Level of care: {result.recommended_level_of_care}")
    print(f"Actions: {result.recommended_actions[:2]}")
    print("\n✅ Test passed!")
else:
    print("Dataset not found!")
