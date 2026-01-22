"""
Dosing calculator utilities for blood components.
Implements exact dosing logic as specified.
"""
from typing import Dict, Any, Optional

def calculate_dose(
    component: Optional[str],
    weight_kg: float,
    age_years: Optional[float] = None,
    rbc_bag_size_ml: int = 350,
    encounter_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Optional[float]]:
    """
    Calculate units and volume for blood component.
    
    Args:
        component: Blood component (RBC, Platelet, FFP, Cryo, Whole Blood, or None)
        weight_kg: Patient weight in kg
        age_years: Patient age in years (for pediatric calculations)
        rbc_bag_size_ml: RBC bag size (350 or 450 mL)
        encounter_data: Full encounter data for context
    
    Returns:
        Dictionary with 'units' and 'volume_ml'
    """
    if component is None:
        return {"units": None, "volume_ml": None}
    
    is_pediatric = age_years is not None and age_years < 18
    
    if component == "RBC":
        if is_pediatric:
            # Pediatric: 10-15 mL/kg
            volume_ml = weight_kg * 12.5  # Use midpoint
            # Estimate units (1 unit ≈ 350 mL)
            units = round(volume_ml / rbc_bag_size_ml, 1)
            if units < 0.5:
                units = 0.5  # Minimum half unit
        else:
            # Adult: 1 unit
            units = 1.0
            volume_ml = float(rbc_bag_size_ml)
    
    elif component == "Platelet":
        if is_pediatric:
            # Pediatric: 10-15 mL/kg
            volume_ml = weight_kg * 12.5  # Use midpoint
            # Random pool: ~50-70 mL per unit, apheresis: ~200-300 mL
            # Assume random pool for calculation
            units = round(volume_ml / 60, 1)
            if units < 0.5:
                units = 0.5
        else:
            # Adult: 1 unit random pool
            units = 1.0
            volume_ml = 60.0  # Approximate volume for random pool
    
    elif component == "FFP":
        # 10-15 mL/kg for all ages
        volume_ml = weight_kg * 12.5  # Use midpoint
        # FFP units are typically 200-250 mL each
        units = round(volume_ml / 225, 1)
        if units < 0.5:
            units = 0.5
    
    elif component == "Cryo":
        if is_pediatric:
            # Pediatric: 1-2 units per 10 kg
            units = max(1.0, round((weight_kg / 10) * 1.5, 1))
        else:
            # Adult: 10 units
            units = 10.0
        # Cryo units are typically 15-20 mL each
        volume_ml = units * 17.5  # Use midpoint
    
    elif component == "Whole Blood":
        # Whole blood: typically 450-500 mL per unit
        if is_pediatric:
            volume_ml = weight_kg * 15  # mL/kg for whole blood
            units = round(volume_ml / 475, 1)
            if units < 0.5:
                units = 0.5
        else:
            units = 1.0
            volume_ml = 475.0
    
    else:
        return {"units": None, "volume_ml": None}
    
    return {
        "units": round(units, 1),
        "volume_ml": round(volume_ml, 1)
    }

def calculate_expected_increment(
    component: Optional[str],
    units: Optional[float],
    weight_kg: float,
    age_years: Optional[float] = None,
    rbc_bag_size_ml: int = 350
) -> str:
    """
    Calculate expected increment text (already in rule output, but useful for validation).
    """
    if component is None or units is None:
        return "N/A"
    
    is_pediatric = age_years is not None and age_years < 18
    
    if component == "RBC":
        if is_pediatric:
            # 10-15 mL/kg ≈ +2-3 g/dL
            return "+2-3 g/dL Hb (with uncertainty: ±1 g/dL)"
        else:
            # 1 unit ≈ +1 g/dL
            return "+1 g/dL Hb (with uncertainty: ±0.5 g/dL)"
    
    elif component == "Platelet":
        # Random pool: +20-40 ×10⁹/L, Apheresis: +30-60 ×10⁹/L
        return "+20-40 ×10⁹/L (with uncertainty: ±10 ×10⁹/L)"
    
    elif component == "FFP":
        return "INR reduction by 0.3-0.5 (recheck 30-60 min post-infusion)"
    
    elif component == "Cryo":
        # 10 units → +70-100 mg/dL
        if units >= 10:
            return "+70-100 mg/dL fibrinogen (with uncertainty: ±20 mg/dL)"
        else:
            # Proportional
            increment = (units / 10) * 85  # Midpoint
            return f"+{increment:.0f} mg/dL fibrinogen (with uncertainty: ±{increment*0.2:.0f} mg/dL)"
    
    return "See rule output"
