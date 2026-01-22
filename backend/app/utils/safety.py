"""
Safety guardrails and warnings generator.
"""
from typing import Dict, Any, List

def generate_safety_warnings(encounter_data: Dict[str, Any]) -> List[str]:
    """
    Generate comprehensive safety warnings based on patient factors.
    
    Args:
        encounter_data: Patient encounter data
    
    Returns:
        List of warning strings
    """
    warnings = []
    history_flags = encounter_data.get("history_flags", {})
    age_years = encounter_data.get("age_years", 0)
    hemodynamic_instability = encounter_data.get("hemodynamic_instability", False)
    
    # Always show policy confirmation
    warnings.append("Confirm local hospital policy before proceeding")
    
    # TACO risk (Transfusion-Associated Circulatory Overload)
    taco_risk_factors = []
    taco_risk_count = 0
    
    if age_years > 70:
        taco_risk_factors.append("age >70")
        taco_risk_count += 1
    if history_flags.get("chf"):
        taco_risk_factors.append("CHF")
        taco_risk_count += 1
    if history_flags.get("ckd") or history_flags.get("renal_failure"):
        taco_risk_factors.append("CKD/renal failure")
        taco_risk_count += 1
    if history_flags.get("low_albumin"):
        taco_risk_factors.append("low albumin")
        taco_risk_count += 1
    
    if taco_risk_factors:
        warning = f"⚠️ TACO risk: {', '.join(taco_risk_factors)}"
        if taco_risk_count >= 2:
            warning += " → Consider slow rate + diuretic prophylaxis"
        warnings.append(warning)
    
    # TRALI risk (Transfusion-Related Acute Lung Injury)
    trali_risk_factors = []
    if history_flags.get("prior_transfusion_reaction"):
        trali_risk_factors.append("prior reaction")
    if history_flags.get("multiparous_female"):  # Female with multiple pregnancies
        trali_risk_factors.append("multiparous female")
    
    if trali_risk_factors:
        warnings.append(f"⚠️ TRALI risk: {', '.join(trali_risk_factors)} → Consider premedication or alternative")
    
    # Prior transfusion reaction
    if history_flags.get("prior_transfusion_reaction"):
        warnings.append("Prior transfusion reaction → use premedication (antihistamine + steroid) and monitor closely")
    
    # Iron therapy consideration
    hb = encounter_data.get("hb_gdl")
    if hb is not None and hb < 10.0 and not encounter_data.get("active_bleeding"):
        warnings.append("💡 Consider iron therapy evaluation if chronic anemia (non-bleeding patient)")
    
    # Specialist consult prompts
    consult_needed = []
    if history_flags.get("cardiac_disease") or history_flags.get("cad"):
        consult_needed.append("Cardiology")
    if history_flags.get("liver_disease"):
        consult_needed.append("Hepatology/Gastroenterology")
    if history_flags.get("renal_failure") or history_flags.get("ckd"):
        consult_needed.append("Nephrology")
    if encounter_data.get("active_bleeding") and hemodynamic_instability:
        consult_needed.append("ICU/Critical Care")
    
    if consult_needed:
        warnings.append(f"📋 Consider specialist consult: {', '.join(set(consult_needed))}")
    
    # Dengue-specific warnings
    if history_flags.get("dengue"):
        if not encounter_data.get("active_bleeding"):
            warnings.append("🦟 Dengue: No prophylactic platelet transfusion without bleeding")
        else:
            warnings.append("🦟 Dengue with bleeding: Platelet transfusion may be indicated - monitor closely")
    
    # Hemodynamic instability
    if hemodynamic_instability:
        warnings.append("⚠️ Hemodynamic instability present → Consider ICU monitoring, rapid response team alert")
    
    # Chronic transfusion dependency
    if history_flags.get("chronic_transfusions"):
        warnings.append("🔄 Chronic transfusion dependency → Screen for iron overload, consider iron chelation")
    
    return warnings

def check_component_availability(
    component: str,
    component_availability: Dict[str, bool]
) -> bool:
    """
    Check if component is available.
    
    Args:
        component: Component to check
        component_availability: Dictionary of component availability
    
    Returns:
        True if available, False otherwise
    """
    if not component_availability:
        return True  # Assume available if not specified
    
    component_key = component.lower().replace(" ", "_")
    return component_availability.get(component_key, True)
