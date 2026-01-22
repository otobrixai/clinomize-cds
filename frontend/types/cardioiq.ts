// frontend/types/cardioiq.ts

export interface CardioIQInput {
  patient: {
    age: number
    sex: 'male' | 'female'
    weight_kg: number
  }
  presentation: {
    chest_pain: boolean
    chest_pain_type: 'typical' | 'atypical' | 'non_cardiac' | 'unknown'
    dyspnea: boolean
    syncope: boolean
  }
  vitals: {
    sbp: number
    hr: number
    spo2: number
  }
  ecg: {
    st_elevation: boolean
    st_depression: boolean
    t_wave_inversion: boolean
    non_diagnostic: boolean
    confidence: 'high' | 'medium' | 'low'
  }
  labs: {
    troponin: {
      value: number
      unit: 'ng/L' | 'ng/mL'
      positive: boolean
    } | null
    troponin_status: 'available' | 'pending' | 'unavailable'
    creatinine: number | null
    potassium: number | null
  }
  history: {
    cad: boolean
    diabetes: boolean
    hypertension: boolean
    ckd: boolean
    heart_failure: boolean
    stroke: boolean
  }
  medications: {
    beta_blocker: boolean
    digoxin: boolean
    qt_prolonging_drugs: boolean
  }
  context: {
    care_setting: 'ER' | 'WARD' | 'CCU' | 'ICU'
    hospital_capability: {
      has_cath_lab: boolean
      can_transfer_primary_pci: boolean
      has_on_site_troponin: boolean
    }
  }
}

export interface RiskScore {
  score_name: string
  value: number
  risk_category: 'low' | 'intermediate' | 'high'
  details: Record<string, number>
}

export interface CardioIQOutput {
  clinical_category: string
  risk_scores: RiskScore[]
  recommended_level_of_care: string
  recommended_actions: string[]
  safety_warnings: string[]
  cost_flags: string[]
  rationale_summary: string[]
  guideline_links: string[]
  rule_hits: string[]
}
