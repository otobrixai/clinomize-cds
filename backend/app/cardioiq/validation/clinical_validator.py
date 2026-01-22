"""
CardioIQ Clinical Validation Framework
Production-grade testing for pilot readiness using full 72-case dataset

Tests:
1. Clinical Safety (no unsafe discharge)
2. Guideline Alignment (ESC/ACC adapted to BD)
3. Cost Control (avoid unnecessary CCU)
4. Engine Determinism (same input → same output)
"""

import sys
import os
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(backend_path)

from app.cardioiq.schemas import CardioIQInput, PatientInput, PresentationInput, VitalsInput, ECGInput, LabsInput, HistoryInput, MedicationsInput, ClinicalContext, TroponinInput
from app.cardioiq.service import CardioIQService

@dataclass
class ValidationResult:
    case_id: str
    passed: bool
    failures: List[str]
    warnings: List[str]
    actual_output: Dict[str, Any]
    expected_output: Dict[str, Any]

class ClinicalValidator:
    def __init__(self, dataset_path: str):
        with open(dataset_path, 'r') as f:
            self.dataset = json.load(f)
        self.results: List[ValidationResult] = []
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation tests"""
        print("\n" + "="*80)
        print("CardioIQ Clinical Validation Framework - Full 72-Case Dataset")
        print("="*80)
        
        total_cases = len(self.dataset)
        print(f"\nTotal cases to validate: {total_cases}")
        
        # Category counts
        categories = {}
        for case in self.dataset:
            # Infer category from expected clinical_category
            cat = case['expected']['clinical_category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nCase Distribution:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")
        
        print("\n" + "-"*80)
        print("Running Validation Tests...")
        print("-"*80 + "\n")
        
        for case in self.dataset:
            result = self._validate_case(case)
            self.results.append(result)
            
            # Print result
            status = "[PASS]" if result.passed else "[FAIL]"
            print(f"{status} | {result.case_id} | {case['expected']['clinical_category']}")
            
            if not result.passed:
                for failure in result.failures:
                    print(f"      X {failure}")
            
            if result.warnings:
                for warning in result.warnings:
                    print(f"      ! {warning}")
        
        # Summary
        return self._generate_summary()
    
    def _validate_case(self, case: Dict) -> ValidationResult:
        """Validate a single case"""
        case_id = case['case_id']
        failures = []
        warnings = []
        
        try:
            # Convert case to CardioIQInput
            cardio_input = self._case_to_input(case)
            
            # Run engine (test determinism by running 3 times)
            outputs = []
            for _ in range(3):
                output = CardioIQService.evaluate_patient(cardio_input)
                outputs.append(output.model_dump())
            
            # Check determinism
            if not all(o == outputs[0] for o in outputs):
                failures.append("Non-deterministic output detected")
            
            actual = outputs[0]
            expected = case['expected']
            
            # Safety-critical checks - STEMI/NSTEMI should NEVER allow discharge
            expected_cat = expected.get('clinical_category', '').upper()
            if 'STEMI' in expected_cat or 'NSTEMI' in expected_cat:
                # These are safety-critical
                if expected.get('discharge_allowed') == False:
                    # Check if discharge is mentioned in actions
                    actions_text = ' '.join(actual.get('recommended_actions', [])).lower()
                    if 'discharge' in actions_text and 'do not discharge' not in actions_text:
                        failures.append("CRITICAL: Discharge action for ACS case")
            
            # Level of care check
            expected_loc = expected.get('level_of_care', '').upper()
            actual_loc = actual.get('recommended_level_of_care', '').upper()
            
            if expected_loc and actual_loc:
                # Map levels to severity
                level_severity = {'ER': 1, 'MONITORED WARD': 2, 'WARD': 2, 'CCU': 3, 'ICU': 4}
                expected_severity = level_severity.get(expected_loc, 0)
                actual_severity = level_severity.get(actual_loc, 0)
                
                # For safety-critical cases, actual should be >= expected
                if 'STEMI' in expected_cat or 'NSTEMI' in expected_cat:
                    if actual_severity < expected_severity:
                        failures.append(f"CRITICAL: Level of care too low: {actual_loc} < {expected_loc}")
                else:
                    # For non-critical, allow some flexibility
                    if actual_severity < expected_severity - 1:
                        warnings.append(f"Level of care lower than expected: {actual_loc} vs {expected_loc}")
            
            # Required actions check (fuzzy match)
            if 'actions' in expected and expected['actions']:
                actions_text = ' '.join(actual.get('recommended_actions', [])).lower()
                for required in expected['actions']:
                    # Check if any keyword from required action is present
                    keywords = required.lower().split()
                    if not any(keyword in actions_text for keyword in keywords if len(keyword) > 3):
                        warnings.append(f"Expected action not found: {required}")
            
            # Discharge allowed check
            if expected.get('discharge_allowed') == True:
                # Low-risk cases should allow discharge
                if 'discharge' not in ' '.join(actual.get('recommended_actions', [])).lower():
                    warnings.append("Cost optimization: discharge should be mentioned for low-risk case")
            
            # Clinical category check (fuzzy match)
            actual_cat = actual.get('clinical_category', '').upper()
            
            # Flexible matching
            category_match = False
            if expected_cat in actual_cat:
                category_match = True
            elif 'STEMI' in expected_cat and 'STEMI' in actual_cat:
                category_match = True
            elif 'NSTEMI' in expected_cat and 'NSTEMI' in actual_cat:
                category_match = True
            elif 'LOW RISK' in expected_cat and 'LOW RISK' in actual_cat:
                category_match = True
            elif 'UNSTABLE ANGINA' in expected_cat and ('UNSTABLE' in actual_cat or 'ANGINA' in actual_cat):
                category_match = True
            
            if not category_match:
                warnings.append(f"Category mismatch: expected '{expected_cat}', got '{actual_cat}'")
            
            passed = len(failures) == 0
            
            return ValidationResult(
                case_id=case_id,
                passed=passed,
                failures=failures,
                warnings=warnings,
                actual_output=actual,
                expected_output=expected
            )
            
        except Exception as e:
            import traceback
            return ValidationResult(
                case_id=case_id,
                passed=False,
                failures=[f"Exception: {str(e)}", f"Traceback: {traceback.format_exc()[:200]}"],
                warnings=[],
                actual_output={},
                expected_output=case.get('expected', {})
            )
    
    def _case_to_input(self, case: Dict) -> CardioIQInput:
        """Convert validation case to CardioIQInput"""
        inputs = case['inputs']
        facility = case['facility']
        
        # Parse chest pain
        chest_pain_present = inputs.get('chest_pain', {}).get('present', False)
        chest_pain_type = inputs.get('chest_pain', {}).get('type', 'unknown').lower()
        
        # Parse troponin
        troponin = None
        troponin_status = 'available'
        troponin_val = inputs['labs'].get('troponin', 'Negative')
        
        if troponin_val == 'Positive':
            troponin = TroponinInput(value=0.05, unit='ng/mL', positive=True)
            troponin_status = 'available'
        elif troponin_val == 'Negative':
            troponin = TroponinInput(value=0.001, unit='ng/mL', positive=False)
            troponin_status = 'available'
        elif troponin_val == 'Pending':
            troponin = None
            troponin_status = 'pending'
        elif troponin_val == 'Unavailable':
            troponin = None
            troponin_status = 'unavailable'
        
        # Parse ECG
        ecg = inputs['ecg']
        
        return CardioIQInput(
            patient=PatientInput(
                age=inputs['age'],
                sex=inputs['sex'].lower(),
                weight_kg=70  # Default
            ),
            presentation=PresentationInput(
                chest_pain=chest_pain_present,
                chest_pain_type=chest_pain_type,
                dyspnea=inputs.get('dyspnea', False),
                syncope=inputs.get('syncope', False)
            ),
            vitals=VitalsInput(
                sbp=inputs['vitals']['sbp'],
                hr=inputs['vitals']['hr'],
                spo2=inputs['vitals']['spo2']
            ),
            ecg=ECGInput(
                st_elevation=ecg.get('st_elevation', False),
                st_depression=ecg.get('st_depression', False),
                t_wave_inversion=ecg.get('t_inversion', False),
                non_diagnostic=ecg.get('non_diagnostic', False),
                confidence='high'  # Default
            ),
            labs=LabsInput(
                troponin=troponin,
                troponin_status=troponin_status,
                creatinine=inputs['labs'].get('creatinine'),
                potassium=inputs['labs'].get('potassium')
            ),
            history=HistoryInput(
                cad=inputs['history'].get('cad', False),
                diabetes=inputs['history'].get('dm', False),
                hypertension=False,  # Not in dataset
                ckd=inputs['history'].get('ckd', False),
                heart_failure=inputs['history'].get('hf', False),
                stroke=inputs['history'].get('stroke', False)
            ),
            medications=MedicationsInput(
                beta_blocker=inputs['medications'].get('beta_blocker', False),
                digoxin=inputs['medications'].get('digoxin', False),
                qt_prolonging_drugs=inputs['medications'].get('qt_prolonging', False)
            ),
            context=ClinicalContext(
                care_setting=inputs['location'],
                hospital_capability={
                    'has_cath_lab': facility.get('pci_available', False),
                    'can_transfer_primary_pci': not facility.get('pci_available', False),
                    'has_on_site_troponin': True
                }
            )
        )
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        # Category breakdown
        category_results = {}
        for result in self.results:
            # Find category from dataset
            case = next(c for c in self.dataset if c['case_id'] == result.case_id)
            cat = case['expected']['clinical_category']
            
            if cat not in category_results:
                category_results[cat] = {'total': 0, 'passed': 0, 'failed': 0}
            
            category_results[cat]['total'] += 1
            if result.passed:
                category_results[cat]['passed'] += 1
            else:
                category_results[cat]['failed'] += 1
        
        # Safety-critical failures
        safety_failures = []
        for result in self.results:
            if not result.passed:
                case = next(c for c in self.dataset if c['case_id'] == result.case_id)
                cat = case['expected']['clinical_category'].upper()
                if 'STEMI' in cat or 'NSTEMI' in cat:
                    safety_failures.append(result.case_id)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_cases': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': f"{(passed/total*100):.1f}%",
            'category_breakdown': category_results,
            'safety_critical_failures': safety_failures,
            'pilot_ready': failed == 0 and len(safety_failures) == 0
        }
        
        # Print summary
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        print(f"\nTotal Cases: {total}")
        print(f"Passed: {passed} ({summary['pass_rate']})")
        print(f"Failed: {failed}")
        
        print("\nCategory Breakdown:")
        for cat, stats in sorted(category_results.items()):
            status = "[OK]" if stats['failed'] == 0 else "[!!]"
            print(f"  {status} {cat}: {stats['passed']}/{stats['total']} passed")
        
        if safety_failures:
            print(f"\n[CRITICAL] {len(safety_failures)} safety-critical failures (STEMI/NSTEMI)")
            for case_id in safety_failures[:10]:  # Show first 10
                print(f"   - {case_id}")
            if len(safety_failures) > 10:
                print(f"   ... and {len(safety_failures) - 10} more")
        
        print("\n" + "="*80)
        if summary['pilot_ready']:
            print("[PILOT READY] All validation tests passed")
        else:
            print("[NOT PILOT READY] Fix failures before deployment")
        print("="*80 + "\n")
        
        return summary

if __name__ == "__main__":
    # Run validation - dataset is in project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    dataset_path = os.path.join(project_root, "cardioiq_validation_dataset.json")
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        sys.exit(1)
    
    validator = ClinicalValidator(dataset_path)
    summary = validator.validate_all()
    
    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "validation_results.json")
    with open(output_path, 'w') as f:
        json.dump({
            'summary': summary,
            'detailed_results': [
                {
                    'case_id': r.case_id,
                    'passed': r.passed,
                    'failures': r.failures,
                    'warnings': r.warnings
                }
                for r in validator.results
            ]
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_path}")
    
    # Exit code
    sys.exit(0 if summary['pilot_ready'] else 1)
