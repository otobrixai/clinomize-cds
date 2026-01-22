// frontend/components/CardioIQForm.tsx

'use client'

import { useState } from 'react'
import { CardioIQInput } from '@/types/cardioiq'
import { Heart, Activity, Zap, Droplets, Pill, Stethoscope } from 'lucide-react'

interface CardioIQFormProps {
  onSubmit: (data: CardioIQInput) => void
  loading: boolean
  disabled?: boolean
}

export default function CardioIQForm({ onSubmit, loading, disabled = false }: CardioIQFormProps) {
  const [formData, setFormData] = useState<CardioIQInput>({
    patient: {
      age: 0,
      sex: 'male',
      weight_kg: 0
    },
    presentation: {
      chest_pain: false,
      chest_pain_type: 'unknown',
      dyspnea: false,
      syncope: false
    },
    vitals: {
      sbp: 0,
      hr: 0,
      spo2: 0
    },
    ecg: {
      st_elevation: false,
      st_depression: false,
      t_wave_inversion: false,
      non_diagnostic: false,
      confidence: 'high'
    },
    labs: {
      troponin: null,
      troponin_status: 'available',
      creatinine: null,
      potassium: null
    },
    history: {
      cad: false,
      diabetes: false,
      hypertension: false,
      ckd: false,
      heart_failure: false,
      stroke: false
    },
    medications: {
      beta_blocker: false,
      digoxin: false,
      qt_prolonging_drugs: false
    },
    context: {
      care_setting: 'ER',
      hospital_capability: {
        has_cath_lab: false,
        can_transfer_primary_pci: false,
        has_on_site_troponin: true
      }
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Patient Demographics */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="p-2 bg-red-50 rounded-lg">
            <Heart className="h-4 w-4 text-red-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800">Patient Demographics</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Age (years)</label>
            <input
              type="number"
              value={formData.patient.age}
              onChange={(e) => setFormData({...formData, patient: {...formData.patient, age: parseInt(e.target.value)}})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sex</label>
            <select
              value={formData.patient.sex}
              onChange={(e) => setFormData({...formData, patient: {...formData.patient, sex: e.target.value as 'male' | 'female'}})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Weight (kg)</label>
            <input
              type="number"
              value={formData.patient.weight_kg}
              onChange={(e) => setFormData({...formData, patient: {...formData.patient, weight_kg: parseFloat(e.target.value)}})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            />
          </div>
        </div>
      </div>

      {/* Presentation */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="p-2 bg-orange-50 rounded-lg">
            <Stethoscope className="h-4 w-4 text-orange-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800">Presentation</h3>
        </div>
        
        <div className="space-y-3">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.presentation.chest_pain}
              onChange={(e) => setFormData({...formData, presentation: {...formData.presentation, chest_pain: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">Chest Pain</span>
          </label>
          
          {formData.presentation.chest_pain && (
            <div className="ml-7">
              <label className="block text-sm font-medium text-gray-700 mb-2">Chest Pain Type</label>
              <select
                value={formData.presentation.chest_pain_type}
                onChange={(e) => setFormData({...formData, presentation: {...formData.presentation, chest_pain_type: e.target.value as any}})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500"
              >
                <option value="typical">Typical</option>
                <option value="atypical">Atypical</option>
                <option value="non_cardiac">Non-Cardiac</option>
                <option value="unknown">Unknown</option>
              </select>
            </div>
          )}
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.presentation.dyspnea}
              onChange={(e) => setFormData({...formData, presentation: {...formData.presentation, dyspnea: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">Dyspnea</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.presentation.syncope}
              onChange={(e) => setFormData({...formData, presentation: {...formData.presentation, syncope: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">Syncope</span>
          </label>
        </div>
      </div>

      {/* Vitals */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="p-2 bg-blue-50 rounded-lg">
            <Activity className="h-4 w-4 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800">Vitals</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Systolic BP (mmHg)</label>
            <input
              type="number"
              value={formData.vitals.sbp}
              onChange={(e) => setFormData({...formData, vitals: {...formData.vitals, sbp: parseInt(e.target.value)}})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Heart Rate (bpm)</label>
            <input
              type="number"
              value={formData.vitals.hr}
              onChange={(e) => setFormData({...formData, vitals: {...formData.vitals, hr: parseInt(e.target.value)}})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">SpO₂ (%)</label>
            <input
              type="number"
              value={formData.vitals.spo2}
              onChange={(e) => setFormData({...formData, vitals: {...formData.vitals, spo2: parseInt(e.target.value)}})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500"
              required
            />
          </div>
        </div>
      </div>

      {/* ECG */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="p-2 bg-purple-50 rounded-lg">
            <Zap className="h-4 w-4 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800">ECG Findings</h3>
        </div>
        
        <div className="space-y-3">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.ecg.st_elevation}
              onChange={(e) => setFormData({...formData, ecg: {...formData.ecg, st_elevation: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">ST Elevation</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.ecg.st_depression}
              onChange={(e) => setFormData({...formData, ecg: {...formData.ecg, st_depression: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">ST Depression</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.ecg.t_wave_inversion}
              onChange={(e) => setFormData({...formData, ecg: {...formData.ecg, t_wave_inversion: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">T-Wave Inversion</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.ecg.non_diagnostic}
              onChange={(e) => setFormData({...formData, ecg: {...formData.ecg, non_diagnostic: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">Non-Diagnostic</span>
          </label>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">ECG Interpretation Confidence</label>
            <select
              value={formData.ecg.confidence}
              onChange={(e) => setFormData({...formData, ecg: {...formData.ecg, confidence: e.target.value as any}})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500"
            >
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Labs */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="p-2 bg-green-50 rounded-lg">
            <Droplets className="h-4 w-4 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800">Laboratory</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Troponin Status</label>
            <select
              value={formData.labs.troponin_status}
              onChange={(e) => setFormData({...formData, labs: {...formData.labs, troponin_status: e.target.value as any}})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500"
            >
              <option value="available">Available</option>
              <option value="pending">Pending</option>
              <option value="unavailable">Unavailable</option>
            </select>
          </div>
          
          {formData.labs.troponin_status === 'available' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 ml-4">
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={formData.labs.troponin?.positive || false}
                  onChange={(e) => setFormData({...formData, labs: {...formData.labs, troponin: {value: 0.01, unit: 'ng/mL', positive: e.target.checked}}})}
                  className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                />
                <span className="text-sm font-medium text-gray-700">Troponin Positive</span>
              </label>
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Creatinine (mg/dL)</label>
              <input
                type="number"
                step="0.1"
                value={formData.labs.creatinine || ''}
                onChange={(e) => setFormData({...formData, labs: {...formData.labs, creatinine: e.target.value ? parseFloat(e.target.value) : null}})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500"
                placeholder="Optional"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Potassium (mmol/L)</label>
              <input
                type="number"
                step="0.1"
                value={formData.labs.potassium || ''}
                onChange={(e) => setFormData({...formData, labs: {...formData.labs, potassium: e.target.value ? parseFloat(e.target.value) : null}})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500"
                placeholder="Optional"
              />
            </div>
          </div>
        </div>
      </div>

      {/* History */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="p-2 bg-yellow-50 rounded-lg">
            <Pill className="h-4 w-4 text-yellow-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800">Medical History</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.history.cad}
              onChange={(e) => setFormData({...formData, history: {...formData.history, cad: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">CAD</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.history.diabetes}
              onChange={(e) => setFormData({...formData, history: {...formData.history, diabetes: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">Diabetes</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.history.hypertension}
              onChange={(e) => setFormData({...formData, history: {...formData.history, hypertension: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">Hypertension</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.history.ckd}
              onChange={(e) => setFormData({...formData, history: {...formData.history, ckd: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">CKD</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.history.heart_failure}
              onChange={(e) => setFormData({...formData, history: {...formData.history, heart_failure: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">Heart Failure</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={formData.history.stroke}
              onChange={(e) => setFormData({...formData, history: {...formData.history, stroke: e.target.checked}})}
              className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            <span className="text-sm font-medium text-gray-700">Stroke</span>
          </label>
        </div>
      </div>

      {/* Context */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-800">Clinical Context</h3>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Care Setting</label>
          <select
            value={formData.context.care_setting}
            onChange={(e) => setFormData({...formData, context: {...formData.context, care_setting: e.target.value as any}})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500"
          >
            <option value="ER">Emergency Room</option>
            <option value="WARD">Ward</option>
            <option value="CCU">CCU</option>
            <option value="ICU">ICU</option>
          </select>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading || disabled}
        className="w-full py-3 px-6 bg-gradient-to-r from-red-600 to-red-700 text-white font-semibold rounded-md hover:from-red-700 hover:to-red-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Evaluating...' : disabled ? 'Acknowledge disclaimer to continue' : 'Get Recommendation'}
      </button>
    </form>
  )
}
