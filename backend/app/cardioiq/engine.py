import json
import os
from typing import List, Dict, Any, Optional
from app.cardioiq.schemas import (
    CardioIQInput, CardioIQOutput, RiskScore, RecommendationAction,
    CardioIQInput, PresentationInput, VitalsInput, LabsInput, ECGInput, HistoryInput
)

class CardioIQEngine:
    def __init__(self, rules_path: str = None, version: str = "1.1.0"):
        if rules_path is None:
            # Default to latest rules version
            current_dir = os.path.dirname(os.path.abspath(__file__))
            rules_path = os.path.join(current_dir, f"rules_v{version}.json")
        
        with open(rules_path, "r") as f:
            self.rules_data = json.load(f)
            self.rules = self.rules_data["rules"]
            # Sort rules by priority (highest first)
            self.rules.sort(key=lambda r: r["priority"], reverse=True)

    def evaluate(self, input_data: CardioIQInput) -> CardioIQOutput:
        # 1. Compute Derived Variables (Scores etc.)
        derived = self._compute_derived_variables(input_data)
        
        # 2. Evaluate Rules
        rule_hits = []
        actions_collected = []
        clinical_category = "Undetermined"
        rec_level_of_care = "Ward" # Default
        safety_warnings = []
        cost_flags = []
        rationale_collected = []
        guideline_links = []
        
        # We need a flattened context for rule evaluation
        eval_context = {
            "patient": input_data.patient.model_dump(),
            "presentation": input_data.presentation.model_dump(),
            "vitals": input_data.vitals.model_dump(),
            "ecg": input_data.ecg.model_dump(),
            "labs": input_data.labs.model_dump(),
            "history": input_data.history.model_dump(),
            "medications": input_data.medications.model_dump(),
            "context": input_data.context.model_dump(),
            "derived": derived
        }

        matched_rules = []
        
        for rule in self.rules:
            if self._evaluate_conditions(rule["conditions"], eval_context):
                matched_rules.append(rule)
                rule_hits.append(rule["rule_id"])
                
                # Apply Actions
                for action in rule["actions"]:
                    if action["type"] == "set_diagnosis":
                        # High priority rules override lower ones for diagnosis
                        if clinical_category == "Undetermined" or rule["priority"] > 50:
                             clinical_category = action["value"]
                    elif action["type"] == "recommend_level_of_care":
                        # Take the HIGHEST level of care (most severe)
                        level_severity = {"ER": 1, "Ward": 2, "CCU": 3, "ICU": 4}
                        current_severity = level_severity.get(rec_level_of_care, 0)
                        new_severity = level_severity.get(action["value"], 0)
                        if new_severity > current_severity:
                            rec_level_of_care = action["value"]
                    elif action["type"] == "recommend_action":
                        actions_collected.append(action["value"])
                    elif action["type"] == "safety_warning":
                        safety_warnings.append(action["value"])
                    elif action["type"] == "cost_impact":
                        cost_flags.append(action["value"])
                    elif action["type"] == "flag_transfer":
                        # Evaluate specific condition for transfer
                        if self._evaluate_single_condition({"condition": action["condition"]}, eval_context):
                             actions_collected.append(f"TRANSFER FLAG: {action['value']}")

                # Collect Rationale & Guidelines
                if rule.get("rationale"):
                    rationale_collected.append(rule["rationale"])
                if rule.get("guideline_reference"):
                    guideline_links.extend(rule["guideline_reference"])

        # Deduplicate
        actions_collected = list(set(actions_collected))
        safety_warnings = list(set(safety_warnings))
        cost_flags = list(set(cost_flags))
        guideline_links = list(set(guideline_links))
        
        # Scores to return
        risk_scores = []
        if "heart_score" in derived:
             risk_scores.append(RiskScore(
                 score_name="HEART Score",
                 value=float(derived["heart_score"]["total"]),
                 risk_category=self._get_heart_risk_category(derived["heart_score"]["total"]),
                 details=derived["heart_score"]["components"]
             ))

        return CardioIQOutput(
            clinical_category=clinical_category,
            risk_scores=risk_scores,
            recommended_level_of_care=rec_level_of_care,
            recommended_actions=actions_collected,
            safety_warnings=safety_warnings,
            cost_flags=cost_flags,
            rationale_summary=rationale_collected,
            guideline_links=guideline_links,
            rule_hits=rule_hits
        )

    def _compute_derived_variables(self, data: CardioIQInput) -> Dict[str, Any]:
        derived = {}
        
        # QT Risk
        potassium = data.labs.potassium if data.labs.potassium is not None else 4.0
        derived["qt_risk"] = (
            potassium < 3.5 or 
            data.medications.qt_prolonging_drugs
        )
        
        # HEART Score
        # H - History (highly suspicious / moderately / slightly) -> We only have binary fields now.
        # This is a simplification for v1 input. 
        # Let's map: Typical CP + Risk Factors -> Highly Suspicious?
        # For now, simplistic approximation based on input fields:
        
        h_score = 0
        if data.presentation.chest_pain_type == "typical":
            h_score = 2
        elif data.presentation.chest_pain_type == "atypical":
            h_score = 1
            
        e_score = 0
        if data.ecg.st_depression: e_score = 2 
        elif data.ecg.non_diagnostic: e_score = 1 # ? 
        elif data.ecg.t_wave_inversion: e_score = 1 # Simplication
        
        a_score = 0
        if data.patient.age >= 65: a_score = 2
        elif data.patient.age >= 45: a_score = 1
        
        r_score = 0
        risk_count = sum([
            data.history.cad, data.history.diabetes, data.history.hypertension, 
            data.history.ckd, data.history.heart_failure, data.history.stroke
        ]) # + Obesity/Smoking/Lipids if we had them
        
        if risk_count >= 3: r_score = 2
        elif risk_count >= 1: r_score = 1
        
        t_score = 0
        if data.labs.troponin is not None and data.labs.troponin.positive: 
             t_score = 2
        # If we had value limits we'd usage them.
        
        heart_total = h_score + e_score + a_score + r_score + t_score
        
        derived["heart_score"] = {
            "total": heart_total,
            "components": {"H": h_score, "E": e_score, "A": a_score, "R": r_score, "T": t_score}
        }

        return derived

    def _get_heart_risk_category(self, score: int) -> str:
        if score <= 3: return "low"
        if score <= 6: return "intermediate"
        return "high"

    def _evaluate_conditions(self, conditions: List[Dict], context: Dict) -> bool:
        for condition in conditions:
            if not self._evaluate_single_condition(condition, context):
                return False
        return True

    def _evaluate_single_condition(self, condition: Dict, context: Dict) -> bool:
        # Check if it is a python-expression based condition string from "flag_transfer" action
        # The schema in JSON for `flag_transfer` has `condition` as a string expression like "context.hospital_capability.has_cath_lab == false"
        # But normal rule conditions are structured {field, operator, value}
        
        if "condition" in condition and isinstance(condition["condition"], str):
             # Simple eval for expression strings. 
             # WARNING: eval is dangerous. In production, use a safe expression parser. 
             # For this controlled environment with internal rules, we will use a limited scope eval or helper.
             # Implementing a very basic path lookup parser for safety.
             expr = condition["condition"]
             # Support "==" only for now in string expressions for simplicity of parsing
             if "==" in expr:
                 lhs, rhs = expr.split("==")
                 lhs_val = self._get_value_from_path(lhs.strip(), context)
                 # Handle boolean text "false"/"true"
                 rhs = rhs.strip().lower()
                 if rhs == "false": rhs_val = False
                 elif rhs == "true": rhs_val = True
                 else: rhs_val = rhs # String/Number
                 
                 return lhs_val == rhs_val
             return False

        field_path = condition.get("field")
        operator = condition.get("operator")
        target_value = condition.get("value")
        
        actual_value = self._get_value_from_path(field_path, context)
        
        if operator == "==":
            return actual_value == target_value
        elif operator == "!=":
            return actual_value != target_value
        elif operator == "<":
            return actual_value is not None and actual_value < target_value
        elif operator == "<=":
            return actual_value is not None and actual_value <= target_value
        elif operator == ">":
            return actual_value is not None and actual_value > target_value
        elif operator == ">=":
            return actual_value is not None and actual_value >= target_value
            
        return False

    def _get_value_from_path(self, path: str, context: Dict) -> Any:
        # e.g. "patient.age" -> context["patient"]["age"]
        keys = path.split(".")
        val = context
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return None
        return val
