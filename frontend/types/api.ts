export interface PatientInput {
  age_years: number
  age_months?: number
  sex: string
  weight_kg: number
  setting: string
  active_bleeding: boolean
  hemodynamic_instability?: boolean
  hb_gdl?: number
  platelets_x109l?: number
  inr?: number
  aptt_sec?: number
  fibrinogen_mgdl?: number
  history_flags?: Record<string, boolean>
  procedure_risk?: string
  procedure_timing_hours?: number
  component_availability?: Record<string, boolean>
  rbc_bag_size_ml?: number
  leukoreduction_available?: boolean
}

export interface ComponentRecommendation {
  component: string | null
  action: string  // "recommend" or "contraindicate"
  dose_text: string
  units: number | null
  volume_ml: number | null
  expected_increment: string
  recheck_plan: string
  why: string[]
  warnings: string[]
  references: string[]
  rule_ids: string[]
}

export interface RecommendationResponse {
  components: ComponentRecommendation[]
  rule_version: string
  overall_warnings: string[]
  mtp_protocol: boolean
  encounter_id?: number | null
  recommendation_ids?: number[]
}

export interface User {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
}
