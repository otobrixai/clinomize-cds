from typing import Dict, Any, List, Optional
from app.rules.loader import load_rules, get_latest_rules_version
from app.models.patient import PatientEncounter

class RulesEngine:
    """
    Deterministic rules engine for transfusion recommendations.
    This is the authoritative source - AI never overrides this.
    """
    
    def __init__(self, version: Optional[str] = None):
        if version is None:
            version = get_latest_rules_version()
        self.version = version
        self.rules_data = load_rules(version)
        self.rules = self.rules_data["rules"]
        # Sort by priority (higher first)
        self.rules.sort(key=lambda r: r["priority"], reverse=True)
    
    def evaluate(self, encounter_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate patient encounter against rules and return ALL matching recommendations.
        
        This allows for multi-component transfusion plans (e.g., RBC + FFP + Platelets).
        
        Args:
            encounter_data: Dictionary with patient encounter data
        
        Returns:
            List of recommendation dictionaries (one per component/match)
        """
        # Convert encounter to dict if it's a model instance
        if hasattr(encounter_data, "__dict__"):
            encounter_dict = self._encounter_to_dict(encounter_data)
        else:
            encounter_dict = encounter_data
        
        # Collect all matching rules
        matching_rules = []
        
        # Evaluate ALL rules in priority order
        for rule in self.rules:
            if self._rule_matches(rule, encounter_dict):
                # Check for conflicts with already-matched rules
                conflict_resolved = self._resolve_conflict(rule, matching_rules, encounter_dict)
                if conflict_resolved is not None:
                    if conflict_resolved == "override_existing":
                        # Remove the overridden rule(s)
                        rule_group = rule.get("exclusive_group")
                        rule_component = rule.get("component")
                        
                        # Remove rules in same exclusive_group
                        if rule_group:
                            matching_rules = [r for r in matching_rules if r.get("exclusive_group") != rule_group]
                        
                        # Remove same-component rules - only one recommendation per component
                        if rule_component:
                            matching_rules = [r for r in matching_rules 
                                            if r.get("component") != rule_component]
                        
                        matching_rules.append(rule)
                    elif conflict_resolved == "add_rule":
                        matching_rules.append(rule)
                    # If conflict_resolved == "skip", do nothing (rule is overridden)
        
        # Build recommendations for each matching rule
        recommendations = []
        for rule in matching_rules:
            # Check if this is a negative/contraindication rule
            action = rule.get("action", "recommend")
            if action == "contraindicate":
                rec = self._build_contraindication(rule, encounter_dict)
            else:
                rec = self._build_recommendation(rule, encounter_dict)
            recommendations.append(rec)
        
        # If no matches, return default negative recommendation
        if not recommendations:
            return [self._build_no_transfusion_recommendation()]
        
        return recommendations
    
    def _encounter_to_dict(self, encounter: PatientEncounter) -> Dict[str, Any]:
        """Convert PatientEncounter model to dictionary."""
        history_flags = encounter.history_flags or {}
        
        return {
            "age_years": encounter.age_years,
            "age_months": encounter.age_months,
            "sex": encounter.sex,
            "weight_kg": encounter.weight_kg,
            "setting": encounter.setting.value if encounter.setting else None,
            "active_bleeding": encounter.active_bleeding,
            "hemodynamic_instability": encounter.hemodynamic_instability or False,
            "hb_gdl": encounter.hb_gdl,
            "platelets_x109l": encounter.platelets_x109l,
            "inr": encounter.inr,
            "aptt_sec": encounter.aptt_sec,
            "fibrinogen_mgdl": encounter.fibrinogen_mgdl,
            "history_flags": history_flags,
            "procedure_risk": encounter.procedure_risk,
            "procedure_timing_hours": encounter.procedure_timing_hours,
            "component_availability": encounter.component_availability or {},
            "rbc_bag_size_ml": encounter.rbc_bag_size_ml,
            "leukoreduction_available": encounter.leukoreduction_available,
        }
    
    def _rule_matches(self, rule: Dict[str, Any], encounter: Dict[str, Any]) -> bool:
        """Check if rule conditions match encounter data."""
        conditions = rule.get("conditions", {})
        
        # Age check
        if "age_min_years" in conditions:
            if encounter.get("age_years", 0) < conditions["age_min_years"]:
                return False
        if "age_max_years" in conditions:
            if encounter.get("age_years", 0) > conditions["age_max_years"]:
                return False
        
        # Setting check
        if "setting" in conditions:
            encounter_setting = encounter.get("setting", "").lower()
            condition_settings = [s.lower() for s in conditions["setting"]]
            if encounter_setting not in condition_settings:
                return False
        
        # Active bleeding check
        if "active_bleeding" in conditions:
            if encounter.get("active_bleeding") != conditions["active_bleeding"]:
                return False
        
        # Hemodynamic instability check
        if "hemodynamic_instability" in conditions:
            if encounter.get("hemodynamic_instability") != conditions["hemodynamic_instability"]:
                return False
        
        # Hb check
        hb = encounter.get("hb_gdl")
        if hb is not None:
            if "hb_min" in conditions and hb < conditions["hb_min"]:
                return False
            if "hb_max" in conditions and hb > conditions["hb_max"]:
                return False
        
        # Platelets check
        platelets = encounter.get("platelets_x109l")
        if platelets is not None:
            if "platelets_min" in conditions and platelets < conditions["platelets_min"]:
                return False
            if "platelets_max" in conditions and platelets > conditions["platelets_max"]:
                return False
        
        # INR check
        inr = encounter.get("inr")
        if inr is not None:
            if "inr_min" in conditions and inr < conditions["inr_min"]:
                return False
            if "inr_max" in conditions and inr > conditions["inr_max"]:
                return False
        
        # Fibrinogen check
        fibrinogen = encounter.get("fibrinogen_mgdl")
        if fibrinogen is not None:
            if "fibrinogen_min" in conditions and fibrinogen < conditions["fibrinogen_min"]:
                return False
            if "fibrinogen_max" in conditions and fibrinogen > conditions["fibrinogen_max"]:
                return False
        
        # History flags check
        if "history_flags" in conditions:
            encounter_flags = encounter.get("history_flags", {})
            for flag, value in conditions["history_flags"].items():
                if value is not None:
                    if encounter_flags.get(flag) != value:
                        return False
        
        # Procedure risk check
        if "procedure_risk" in conditions:
            procedure_risk = encounter.get("procedure_risk")
            if procedure_risk not in conditions["procedure_risk"]:
                return False
        
        # Procedure timing check
        if "procedure_timing_hours" in conditions:
            timing = encounter.get("procedure_timing_hours")
            if timing is None or timing > conditions["procedure_timing_hours"]:
                return False
        
        return True
    
    def _resolve_conflict(self, rule: Dict[str, Any], matched_rules: List[Dict[str, Any]], encounter: Dict[str, Any]) -> Optional[str]:
        """
        Resolve conflicts between a new rule and already-matched rules.
        
        Returns:
            - "add_rule": Add this rule (no conflict)
            - "override_existing": Add this rule and remove conflicting ones
            - "skip": Don't add this rule (it's overridden)
            - None: Unresolvable conflict (should raise error)
        """
        rule_group = rule.get("exclusive_group")
        rule_component = rule.get("component")
        rule_priority = rule.get("priority", 0)
        
        # Find potential conflicts:
        # 1. Same exclusive_group (always conflicting)
        # 2. Same component (should only have one recommendation per component unless explicitly different)
        # 3. Same component + this rule has override_conditions (check if it should override)
        conflicting_rules = []
        
        if rule_group:
            # Check for rules in the same exclusive group
            conflicting_rules.extend([r for r in matched_rules if r.get("exclusive_group") == rule_group])
        
        # Check for same-component conflicts (same component should only have one recommendation)
        if rule_component:
            same_component_rules = [r for r in matched_rules 
                                   if r.get("component") == rule_component 
                                   and r.get("id") not in [cr.get("id") for cr in conflicting_rules]]
            
            # Always treat same-component rules as conflicts - only one recommendation per component
            if same_component_rules:
                conflicting_rules.extend(same_component_rules)
        
        if not conflicting_rules:
            # No conflict
            return "add_rule"
        
        # Check override conditions
        override_conditions = rule.get("override_conditions", {})
        override_rule_ids = override_conditions.get("override_rule_ids", [])
        
        # Check if this rule can override the conflicting ones
        can_override = False
        for conflicting_rule in conflicting_rules:
            if conflicting_rule["id"] in override_rule_ids:
                # Check if override "when" conditions are met
                when_conditions = override_conditions.get("when", {})
                if self._check_override_conditions(when_conditions, encounter):
                    can_override = True
                    break
        
        if can_override:
            return "override_existing"
        
        # Check if any conflicting rule can override this one
        for conflicting_rule in conflicting_rules:
            conf_override = conflicting_rule.get("override_conditions", {})
            conf_override_ids = conf_override.get("override_rule_ids", [])
            if rule["id"] in conf_override_ids:
                conf_when = conf_override.get("when", {})
                if self._check_override_conditions(conf_when, encounter):
                    return "skip"  # This rule is overridden
        
        # If this rule has override_conditions but conflicting rule doesn't, 
        # and they're same component, this rule should take precedence
        # This handles cases like PLT-BLEEDING-OVERRIDE vs PLT-002
        if rule.get("override_conditions") and rule_component:
            conflicting_same_component = [r for r in conflicting_rules 
                                         if r.get("component") == rule_component 
                                         and not r.get("override_conditions")
                                         and r.get("id") not in override_rule_ids]
            if conflicting_same_component:
                # Check if override "when" conditions are met
                when_conditions = override_conditions.get("when", {})
                if when_conditions and self._check_override_conditions(when_conditions, encounter):
                    # This rule has override logic and conflicting ones don't - prefer this one
                    return "override_existing"
                elif not when_conditions:
                    # No "when" conditions means always override
                    return "override_existing"
        
        # Compare priorities as fallback
        rule_priority = rule.get("priority", 0)
        max_conflict_priority = max(r.get("priority", 0) for r in conflicting_rules)
        
        if rule_priority > max_conflict_priority:
            return "override_existing"
        elif rule_priority < max_conflict_priority:
            return "skip"
        else:
            # Same priority and no override - this is an unresolvable conflict
            # Log warning but allow both (this shouldn't happen with proper rule design)
            import logging
            logging.warning(
                f"Unresolvable conflict: rule {rule['id']} conflicts with "
                f"{[r['id'] for r in conflicting_rules]} - both have same priority and no override"
            )
            return "skip"  # Default to skipping the new rule to be conservative
    
    def _check_override_conditions(self, when_conditions: Dict[str, Any], encounter: Dict[str, Any]) -> bool:
        """Check if override 'when' conditions are met."""
        if not when_conditions:
            return True  # No conditions means always override
        
        for key, value in when_conditions.items():
            if key not in encounter:
                return False
            if encounter[key] != value:
                return False
        return True
    
    def _build_recommendation(self, rule: Dict[str, Any], encounter: Dict[str, Any]) -> Dict[str, Any]:
        """Build recommendation structure from matched rule."""
        from app.utils.dosing import calculate_dose
        
        output = rule["output"]
        component = rule["component"]
        
        # Calculate dose using dosing utilities
        dose_result = calculate_dose(
            component=component,
            weight_kg=encounter["weight_kg"],
            age_years=encounter.get("age_years"),
            rbc_bag_size_ml=encounter.get("rbc_bag_size_ml", 350),
            encounter_data=encounter
        )
        
        # Adjust dose_text for pediatric patients
        age_years = encounter.get("age_years")
        weight_kg = encounter.get("weight_kg")
        is_pediatric = age_years is not None and age_years < 18
        
        dose_text = output["dose_text"]
        if is_pediatric and component == "RBC":
            # Pediatric RBC: show mL/kg dosing
            volume_ml = dose_result.get("volume_ml", 0)
            dose_text = f"10-15 mL/kg ({volume_ml:.0f} mL for {weight_kg} kg patient)"
        elif is_pediatric and component == "Platelet":
            # Pediatric Platelet: show mL/kg dosing
            volume_ml = dose_result.get("volume_ml", 0)
            dose_text = f"10-15 mL/kg platelets ({volume_ml:.0f} mL for {weight_kg} kg patient)"
        elif is_pediatric and component == "FFP":
            # FFP is already mL/kg, but ensure it shows pediatric context
            volume_ml = dose_result.get("volume_ml", 0)
            if "mL/kg" not in dose_text:
                dose_text = f"10-15 mL/kg FFP ({volume_ml:.0f} mL for {weight_kg} kg patient)"
        
        # Adjust expected_increment for pediatric RBC
        expected_increment = output["expected_increment"]
        if is_pediatric and component == "RBC" and "±0.5" in expected_increment:
            expected_increment = "+2-3 g/dL Hb (with uncertainty: ±1 g/dL)"
        
        return {
            "component": component if component != "None" else None,
            "action": rule.get("action", "recommend"),
            "dose_text": dose_text,
            "units": dose_result.get("units"),
            "volume_ml": dose_result.get("volume_ml"),
            "expected_increment": expected_increment,
            "recheck_plan": output["recheck_plan"],
            "why": output["why"],
            "warnings": output["warnings"],
            "references": output["references"],
            "rule_ids": [rule["id"]],
            "rule_version": self.version
        }
    
    def _build_contraindication(self, rule: Dict[str, Any], encounter: Dict[str, Any]) -> Dict[str, Any]:
        """Build contraindication structure for negative rules."""
        output = rule["output"]
        component = rule.get("component", "blood products")
        
        return {
            "component": None,
            "action": "contraindicate",
            "dose_text": f"DO NOT transfuse {component}",
            "units": None,
            "volume_ml": None,
            "expected_increment": "N/A",
            "recheck_plan": output.get("recheck_plan", "Continue monitoring. Reassess if clinical status changes."),
            "why": output.get("why", ["Contraindicated based on clinical guidelines"]),
            "warnings": output.get("warnings", []),
            "references": output.get("references", []),
            "rule_ids": [rule["id"]],
            "rule_version": self.version
        }
    
    def _build_no_transfusion_recommendation(self) -> Dict[str, Any]:
        """Build default 'no transfusion' recommendation."""
        return {
            "component": None,
            "action": "recommend",
            "dose_text": "No transfusion recommended",
            "units": None,
            "volume_ml": None,
            "expected_increment": "N/A",
            "recheck_plan": "Continue monitoring. Reassess if clinical status changes.",
            "why": [
                "No transfusion criteria met",
                "Conservative approach preferred when safe"
            ],
            "warnings": [
                "Reassess if bleeding occurs or parameters worsen",
                "Confirm with clinical judgment"
            ],
            "references": [
                "AABB Guidelines 2023",
                "DGHS Transfusion Policy 2024"
            ],
            "rule_ids": ["NONE-DEFAULT"],
            "rule_version": self.version
        }
