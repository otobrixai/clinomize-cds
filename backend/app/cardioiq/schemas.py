from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field, conint, confloat

# =============================================================================
# INPUT SCHEMAS
# =============================================================================

class PatientInput(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    sex: Literal["male", "female"]
    weight_kg: float = Field(..., gt=0, description="Patient weight in kg")

class PresentationInput(BaseModel):
    chest_pain: bool
    chest_pain_type: Literal["typical", "atypical", "non_cardiac", "unknown"]
    dyspnea: bool
    syncope: bool

class VitalsInput(BaseModel):
    sbp: int = Field(..., description="Systolic Blood Pressure (mmHg)")
    hr: int = Field(..., description="Heart Rate (bpm)")
    spo2: int = Field(..., description="Oxygen Saturation (%)")

class ECGInput(BaseModel):
    st_elevation: bool = False
    st_depression: bool = False
    t_wave_inversion: bool = False
    non_diagnostic: bool = False
    confidence: Literal["high", "medium", "low"] = Field("high", description="Clinician confidence in interpretation")

class TroponinInput(BaseModel):
    value: float
    unit: Literal["ng/L", "ng/mL"]
    positive: bool

class LabsInput(BaseModel):
    troponin: Optional[TroponinInput] = None
    troponin_status: Literal["available", "pending", "unavailable"] = "available"
    creatinine: Optional[float] = Field(None, description="Serum Creatinine (mg/dL)")
    potassium: Optional[float] = Field(None, description="Serum Potassium (mmol/L or mEq/L)")

class HistoryInput(BaseModel):
    cad: bool = False
    diabetes: bool = False
    hypertension: bool = False
    ckd: bool = False
    heart_failure: bool = False
    stroke: bool = False

class MedicationsInput(BaseModel):
    beta_blocker: bool = False
    digoxin: bool = False
    qt_prolonging_drugs: bool = False

class ClinicalContext(BaseModel):
    care_setting: Literal["ER", "WARD", "CCU", "ICU"]
    hospital_capability: Dict[str, bool] = Field(
        default_factory=lambda: {
            "has_cath_lab": False,
            "can_transfer_primary_pci": False,
            "has_on_site_troponin": True
        }
    )

class CardioIQInput(BaseModel):
    patient: PatientInput
    presentation: PresentationInput
    vitals: VitalsInput
    ecg: ECGInput
    labs: LabsInput
    history: HistoryInput
    medications: MedicationsInput
    context: ClinicalContext = Field(default_factory=lambda: ClinicalContext(care_setting="ER"))


# =============================================================================
# OUTPUT SCHEMAS
# =============================================================================

class RecommendationAction(BaseModel):
    type: str  # e.g., "set_diagnosis", "recommend_level_of_care", "recommend_action"
    value: str
    rationale: Optional[str] = None

class RiskScore(BaseModel):
    score_name: str
    value: float
    risk_category: Literal["low", "intermediate", "high"]
    details: Dict[str, float] = {}

class CardioIQOutput(BaseModel):
    clinical_category: str = Field(..., description="Guideline-aligned clinical category (e.g., STEMI)")
    risk_scores: List[RiskScore] = []
    recommended_level_of_care: str
    recommended_actions: List[str] = []
    safety_warnings: List[str] = []
    cost_flags: List[str] = []
    rationale_summary: List[str] = []
    guideline_links: List[str] = []
    rule_hits: List[str] = Field(..., description="IDs of rules that triggered")
