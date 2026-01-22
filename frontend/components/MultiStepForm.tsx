// frontend/components/MultiStepForm.tsx
'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { PatientInput } from '@/types/api'
import { 
  ChevronRight, 
  ChevronLeft,
  User,
  Stethoscope,
  ClipboardCheck,
  AlertTriangle,
  FileText
} from 'lucide-react'

interface MultiStepFormProps {
  onSubmit: (_data: PatientInput) => void
  loading: boolean
}

export default function MultiStepForm({ onSubmit, loading }: MultiStepFormProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const { register, handleSubmit, formState: { errors }, trigger, watch } = useForm<PatientInput>({
    defaultValues: {
      active_bleeding: false,
      hemodynamic_instability: false,
      history_flags: {},
    },
    mode: 'onChange'
  })

  const activeBleeding = watch('active_bleeding')
  const steps = [
    { id: 1, title: 'Patient & Labs', icon: User },
    { id: 2, title: 'Clinical Context', icon: Stethoscope },
    { id: 3, title: 'Review', icon: ClipboardCheck },
  ]

  const handleNext = async () => {
    let fieldsToValidate: (keyof PatientInput)[] = []
    
    if (currentStep === 1) {
      fieldsToValidate = ['age_years', 'weight_kg', 'sex', 'setting']
    }
    
    const isValid = await trigger(fieldsToValidate)
    if (isValid) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    setCurrentStep(currentStep - 1)
  }

  const onSubmitForm = (data: PatientInput) => {
    onSubmit(data)
  }

  return (
    <div className="space-y-8">
      {/* Simple Card with Progress */}
      <div className="mb-8 bg-gradient-to-r from-blue-50 to-gray-50 rounded-xl p-6 border border-blue-100">
        
        <div className="flex justify-between items-center">
          {steps.map((step, index) => {
            const isCompleted = currentStep > step.id
            const isActive = currentStep === step.id
            const isLast = index === steps.length - 1
            
            return (
              <div key={step.id} className="flex items-center">
                {/* Step indicator */}
                <div className="flex flex-col items-center">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center mb-2
                    transition-all duration-300
                    ${isCompleted 
                      ? 'bg-green-500 text-white' 
                      : isActive 
                      ? 'bg-blue-600 text-white ring-4 ring-blue-200' 
                      : 'bg-white border border-gray-300 text-gray-400'
                    }
                  `}>
                    {isCompleted ? (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <step.icon className="w-4 h-4" />
                    )}
                  </div>
                  
                  <span className={`
                    text-xs font-medium
                    ${isCompleted ? 'text-green-700' : 
                      isActive ? 'text-blue-700 font-semibold' : 
                      'text-gray-500'}
                  `}>
                    {step.title}
                  </span>
                </div>
                
                {/* Line connector */}
                {!isLast && (
                  <div className={`
                    w-12 md:w-20 h-0.5 mx-1 md:mx-2
                    ${currentStep > step.id ? 'bg-green-300' : 'bg-gray-200'}
                  `} />
                )}
              </div>
            )
          })}
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmitForm)}>
      {/* Step 1: Patient & Labs */}
      {currentStep === 1 && (
        <div className="space-y-6">          
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Patient Demographics</h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Age (years) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('age_years', { required: true, min: 0 })}
                  className="w-full px-4 py-3 md:py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 45"
                />
                {errors.age_years && (
                  <p className="mt-1 text-sm text-red-600">Required</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Weight (kg) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('weight_kg', { required: true, min: 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 70"
                />
                {errors.weight_kg && (
                  <p className="mt-1 text-sm text-red-600">Required</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sex *
                </label>
                <select
                  {...register('sex', { required: true })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select...</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
                {errors.sex && (
                  <p className="mt-1 text-sm text-red-600">Required</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Setting *
                </label>
                <select
                  {...register('setting', { required: true })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select...</option>
                  <option value="ward">Ward</option>
                  <option value="icu">ICU</option>
                  <option value="or">OR</option>
                  <option value="er">ER</option>
                </select>
                {errors.setting && (
                  <p className="mt-1 text-sm text-red-600">Required</p>
                )}
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Laboratory Values</h3>
            <p className="text-sm text-gray-500 mb-6">Optional - Enter available values</p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hemoglobin (g/dL)
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('hb_gdl', { min: 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 8.5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Platelets (×10⁹/L)
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('platelets_x109l', { min: 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 150"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  INR
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('inr', { min: 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 1.2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fibrinogen (mg/dL)
                </label>
                <input
                  type="number"
                  step="0.1"
                  {...register('fibrinogen_mgdl', { min: 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 250"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="button"
              onClick={handleNext}
              className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <span>Next: Clinical Context</span>
              <ChevronRight className="h-5 w-5 ml-2" />
            </button>
          </div>
        </div>
      )}

        {/* Step 2: Clinical Context */}
        {currentStep === 2 && (
          <div className="space-y-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Clinical Context</h3>
              
              {/* Quick Toggles - ALTERNATIVE DRAMATIC DESIGN */}
              <div className="mb-8">
                <div className="text-center mb-4">
                  <h4 className="text-lg font-semibold text-gray-800">CRITICAL SCENARIOS</h4>
                  <p className="text-sm text-gray-600">Check if present - tFhese significantly change recommendations</p>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
                  {/* Active Bleeding - Card Style */}
                  <div className={`rounded-xl border-2 p-5 cursor-pointer transition-all duration-300 ${
                    activeBleeding 
                      ? 'border-red-500 bg-gradient-to-br from-red-50 to-red-100 shadow-lg' 
                      : 'border-gray-200 hover:border-red-300 hover:shadow-md'
                  }`}>
                    <label className="flex items-start cursor-pointer">
                      <div className="mr-4">
                        <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                          activeBleeding ? 'bg-red-600' : 'bg-gray-200'
                        }`}>
                          {activeBleeding ? (
                            <span className="text-white text-lg font-bold">✓</span>
                          ) : null}
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className={`text-xl font-bold ${
                            activeBleeding ? 'text-red-800' : 'text-gray-800'
                          }`}>
                            ACTIVE BLEEDING
                          </h4>
                          <span className={`text-sm font-medium px-3 py-1 rounded-full ${
                            activeBleeding 
                              ? 'bg-red-200 text-red-800' 
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {activeBleeding ? 'CRITICAL' : 'Optional'}
                          </span>
                        </div>
                        
                        <p className={`mt-2 ${
                          activeBleeding ? 'text-red-700' : 'text-gray-600'
                        }`}>
                          Patient has active, ongoing bleeding requiring intervention
                        </p>
                        
                        {activeBleeding && (
                          <div className="mt-4 p-3 bg-white/80 rounded-lg border border-red-200">
                            <p className="text-sm font-medium text-red-800 mb-2">⚠️ Immediate Actions Required:</p>
                            <ul className="text-sm text-red-700 space-y-1">
                              <li>• Activate massive transfusion protocol if severe</li>
                              <li>• Lower hemoglobin thresholds apply (Hb &lt;8-9 g/dL)</li>
                              <li>• Consider multiple component transfusion</li>
                            </ul>
                          </div>
                        )}
                        
                        <input
                          type="checkbox"
                          {...register('active_bleeding')}
                          className="sr-only"
                        />
                      </div>
                    </label>
                  </div>

                  {/* Hemodynamic Instability - Card Style */}
                  <div className={`rounded-xl border-2 p-5 cursor-pointer transition-all duration-300 ${
                    watch('hemodynamic_instability')
                      ? 'border-orange-500 bg-gradient-to-br from-orange-50 to-orange-100 shadow-lg' 
                      : 'border-gray-200 hover:border-orange-300 hover:shadow-md'
                  }`}>
                    <label className="flex items-start cursor-pointer">
                      <div className="mr-4">
                        <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                          watch('hemodynamic_instability') ? 'bg-orange-600' : 'bg-gray-200'
                        }`}>
                          {watch('hemodynamic_instability') ? (
                            <span className="text-white text-lg font-bold">✓</span>
                          ) : null}
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className={`text-xl font-bold ${
                            watch('hemodynamic_instability') ? 'text-orange-800' : 'text-gray-800'
                          }`}>
                            HEMODYNAMIC INSTABILITY
                          </h4>
                          <span className={`text-sm font-medium px-3 py-1 rounded-full ${
                            watch('hemodynamic_instability') 
                              ? 'bg-orange-200 text-orange-800' 
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {watch('hemodynamic_instability') ? 'CRITICAL' : 'Optional'}
                          </span>
                        </div>
                        
                        <p className={`mt-2 ${
                          watch('hemodynamic_instability') ? 'text-orange-700' : 'text-gray-600'
                        }`}>
                          Unstable BP, tachycardia, signs of shock, or requiring vasopressors
                        </p>
                        
                        {watch('hemodynamic_instability') && (
                          <div className="mt-4 p-3 bg-white/80 rounded-lg border border-orange-200">
                            <p className="text-sm font-medium text-orange-800 mb-2">⚠️ Clinical Implications:</p>
                            <ul className="text-sm text-orange-700 space-y-1">
                              <li>• Higher acuity setting (ICU) recommended</li>
                              <li>• More aggressive resuscitation may be needed</li>
                              <li>• Cardiac/respiratory monitoring required</li>
                            </ul>
                          </div>
                        )}
                        
                        <input
                          type="checkbox"
                          {...register('hemodynamic_instability')}
                          className="sr-only"
                        />
                      </div>
                    </label>
                  </div>
                </div>
                
                {/* Combined Warning */}
                {(watch('active_bleeding') && watch('hemodynamic_instability')) && (
                  <div className="mt-6 p-4 bg-gradient-to-r from-red-500 to-orange-500 rounded-xl text-white">
                    <div className="flex items-center">
                      <AlertTriangle className="h-8 w-8 mr-3" />
                      <div>
                        <h4 className="font-bold text-lg">🚨 MASSIVE TRANSFUSION PROTOCOL (MTP) SCENARIO</h4>
                        <p className="text-sm opacity-90 mt-1">
                          Active bleeding + hemodynamic instability = High likelihood of MTP activation.
                          Prepare for multi-component transfusion and notify blood bank immediately.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* History Flags */}
              <div>
                <h4 className="font-medium text-gray-800 mb-4">Medical History</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {[
                    { key: 'cad', label: 'CAD' },
                    { key: 'cardiac_disease', label: 'Cardiac Disease' },
                    { key: 'liver_disease', label: 'Liver Disease' },
                    { key: 'renal_failure', label: 'Renal Failure' },
                    { key: 'dengue', label: 'Dengue' },
                    { key: 'pregnancy', label: 'Pregnancy' },
                  ].map((flag) => (
                    <label key={flag.key} className="flex items-center space-x-3 cursor-pointer">
                      <input
                        type="checkbox"
                        {...register(`history_flags.${flag.key}`)}
                        className="h-5 w-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 border-gray-300"
                      />
                      <span className="text-sm text-gray-700">{flag.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <button
                type="button"
                onClick={handlePrevious}
                className="flex items-center px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
              >
                <ChevronLeft className="h-5 w-5 mr-2" />
                <span>Previous</span>
              </button>
              <button
                type="button"
                onClick={handleNext}
                className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <span>Next: Review</span>
                <ChevronRight className="h-5 w-5 ml-2" />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Review - UPDATED with proper review data */}
        {currentStep === 3 && (
          <div className="space-y-8">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Review & Submit</h3>
            
            {/* Review Summary */}
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="mb-6">
                <div className="flex items-start space-x-3 mb-4">
                  <AlertTriangle className="h-6 w-6 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm text-gray-700 mb-2">
                      Review the entered information before generating recommendations.
                    </p>
                    <div className="space-y-2">
                      <p className="text-sm">
                        <span className="font-medium">Recommendations will include:</span>
                      </p>
                      <ul className="text-sm text-gray-600 space-y-1 ml-4 list-disc">
                        <li>Component-specific transfusion guidance</li>
                        <li>Evidence-based rationale</li>
                        <li>Dosing calculations</li>
                        <li>Follow-up plan</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Review Sections */}
              <div className="space-y-6">
                {/* Demographics Review */}
                <div className="border-b pb-4">
                  <h4 className="font-medium text-gray-800 mb-3 flex items-center">
                    <User className="h-4 w-4 mr-2 text-gray-500" />
                    Demographics
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Age</p>
                      <p className="font-medium text-gray-900">{watch('age_years') || '—'} years</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Weight</p>
                      <p className="font-medium text-gray-900">{watch('weight_kg') || '—'} kg</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Sex</p>
                      <p className="font-medium text-gray-900">
                        {watch('sex') === 'M' ? 'Male' : watch('sex') === 'F' ? 'Female' : '—'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Setting</p>
                      <p className="font-medium text-gray-900">
                        {watch('setting') === 'ward' ? 'Ward' :
                         watch('setting') === 'icu' ? 'ICU' :
                         watch('setting') === 'or' ? 'OR' :
                         watch('setting') === 'er' ? 'ER' : '—'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Labs Review */}
                <div className="border-b pb-4">
                  <h4 className="font-medium text-gray-800 mb-3 flex items-center">
                    <FileText className="h-4 w-4 mr-2 text-gray-500" />
                    Laboratory Values
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Hemoglobin</p>
                      <p className="font-medium text-gray-900">
                        {watch('hb_gdl') ? `${watch('hb_gdl')} g/dL` : 'Not provided'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Platelets</p>
                      <p className="font-medium text-gray-900">
                        {watch('platelets_x109l') ? `${watch('platelets_x109l')} ×10⁹/L` : 'Not provided'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">INR</p>
                      <p className="font-medium text-gray-900">
                        {watch('inr') ? watch('inr') : 'Not provided'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Fibrinogen</p>
                      <p className="font-medium text-gray-900">
                        {watch('fibrinogen_mgdl') ? `${watch('fibrinogen_mgdl')} mg/dL` : 'Not provided'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Clinical Context Review */}
                <div>
                  <h4 className="font-medium text-gray-800 mb-3 flex items-center">
                    <Stethoscope className="h-4 w-4 mr-2 text-gray-500" />
                    Clinical Context
                  </h4>
                  <div className="space-y-3">
                    {/* Active Conditions */}
                    <div className="flex flex-wrap gap-2">
                      {watch('active_bleeding') && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Active Bleeding
                        </span>
                      )}
                      {watch('hemodynamic_instability') && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                          Hemodynamic Instability
                        </span>
                      )}
                    </div>

                    {/* History Flags */}
                    <div>
                      <p className="text-sm text-gray-500 mb-2">Medical History</p>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(watch('history_flags') || {}).map(([key, value]) => 
                          value ? (
                            <span key={key} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                            </span>
                          ) : null
                        )}
                        {Object.values(watch('history_flags') || {}).filter(Boolean).length === 0 && (
                          <span className="text-sm text-gray-500">No significant history flags</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <button
                type="button"
                onClick={handlePrevious}
                className="flex items-center px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
              >
                <ChevronLeft className="h-5 w-5 mr-2" />
                <span>Previous</span>
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? (
                  <div className="flex items-center">
                    <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Processing...
                  </div>
                ) : (
                  'Get Recommendation'
                )}
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  )
}