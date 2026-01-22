'use client'

import { useForm } from 'react-hook-form'
import { PatientInput } from '@/types/api'
import { useState } from 'react'

interface PatientFormProps {
  onSubmit: (_data: PatientInput) => void
  loading: boolean
}

export default function PatientForm({ onSubmit, loading }: PatientFormProps) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<PatientInput>({
      defaultValues: {
      active_bleeding: false,
      hemodynamic_instability: false,
      rbc_bag_size_ml: 350,
      leukoreduction_available: true,
      history_flags: {},
      component_availability: {},
    }
  })

  const [showAdvanced, setShowAdvanced] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [showConstraints, setShowConstraints] = useState(false)

  const activeBleeding = watch('active_bleeding')

  const onSubmitForm = (data: PatientInput) => {
    onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmitForm)} className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold mb-6 text-gray-900">Patient Information</h2>

      {/* Quick Action: Active Bleeding Toggle */}
      <div className="mb-6 p-4 bg-red-50 border-2 border-red-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <label className="text-lg font-semibold text-red-900">Active Bleeding?</label>
            <p className="text-sm text-red-700 mt-1">Quick toggle for bleeding scenarios</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              {...register('active_bleeding')}
              className="sr-only peer"
            />
            <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-red-600"></div>
          </label>
        </div>
        {activeBleeding && (
          <div className="mt-3 p-3 bg-red-100 rounded text-sm text-red-900">
            <strong>⚠️ Bleeding Scenario:</strong> This will trigger bleeding-specific rules and may recommend multiple components (MTP protocol).
          </div>
        )}
      </div>

      {/* Demographics */}
      <div className="space-y-4 mb-6">
        <h3 className="text-lg font-medium text-gray-700">Demographics</h3>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Age (years) *
            </label>
            <input
              type="number"
              step="0.1"
              {...register('age_years', { required: true, min: 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            {errors.age_years && (
              <p className="text-red-500 text-xs mt-1">Required</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Weight (kg) *
            </label>
            <input
              type="number"
              step="0.1"
              {...register('weight_kg', { required: true, min: 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            {errors.weight_kg && (
              <p className="text-red-500 text-xs mt-1">Required</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sex *
          </label>
          <select
            {...register('sex', { required: true })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Select...</option>
            <option value="M">Male</option>
            <option value="F">Female</option>
            <option value="Other">Other</option>
          </select>
          {errors.sex && (
            <p className="text-red-500 text-xs mt-1">Required</p>
          )}
        </div>
      </div>

      {/* Context */}
      <div className="space-y-4 mb-6">
        <h3 className="text-lg font-medium text-gray-700">Clinical Context</h3>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Setting *
          </label>
          <select
            {...register('setting', { required: true })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Select...</option>
            <option value="ward">Ward</option>
            <option value="icu">ICU</option>
            <option value="or">OR</option>
            <option value="er">ER</option>
          </select>
          {errors.setting && (
            <p className="text-red-500 text-xs mt-1">Required</p>
          )}
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            {...register('active_bleeding')}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label className="ml-2 block text-sm text-gray-700">
            Active bleeding present
          </label>
        </div>
      </div>

      {/* Labs */}
      <div className="space-y-4 mb-6">
        <h3 className="text-lg font-medium text-gray-700">Laboratory Values</h3>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hemoglobin (g/dL)
            </label>
            <input
              type="number"
              step="0.1"
              {...register('hb_gdl', { min: 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Platelets (×10⁹/L)
            </label>
            <input
              type="number"
              step="0.1"
              {...register('platelets_x109l', { min: 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              INR
            </label>
            <input
              type="number"
              step="0.1"
              {...register('inr', { min: 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fibrinogen (mg/dL)
            </label>
            <input
              type="number"
              step="0.1"
              {...register('fibrinogen_mgdl', { min: 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Advanced Options */}
      <div className="mb-6">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          {showAdvanced ? '▼' : '▶'} Advanced Options
        </button>

        {showAdvanced && (
          <div className="mt-4 space-y-4 p-4 bg-gray-50 rounded-md">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Procedure Risk
              </label>
              <select
                {...register('procedure_risk')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">None</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Procedure Timing (hours)
              </label>
              <input
                type="number"
                step="0.1"
                {...register('procedure_timing_hours', { min: 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        )}
      </div>

      {/* History Flags */}
      <div className="mb-6">
        <button
          type="button"
          onClick={() => setShowHistory(!showHistory)}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          {showHistory ? '▼' : '▶'} History Flags
        </button>

        {showHistory && (
          <div className="mt-4 space-y-2 p-4 bg-gray-50 rounded-md">
            {[
              { key: 'cad', label: 'CAD / Ischemic heart disease' },
              { key: 'liver_disease', label: 'Liver disease' },
              { key: 'renal_failure', label: 'Renal failure / CKD' },
              { key: 'chemotherapy', label: 'Chemotherapy' },
              { key: 'dengue', label: 'Dengue' },
              { key: 'pregnancy', label: 'Pregnancy' },
              { key: 'chf', label: 'CHF' },
              { key: 'ckd', label: 'CKD' },
              { key: 'low_albumin', label: 'Low albumin' },
              { key: 'prior_transfusion_reaction', label: 'Prior transfusion reaction' },
            ].map((flag) => (
              <div key={flag.key} className="flex items-center">
                <input
                  type="checkbox"
                  {...register(`history_flags.${flag.key}`)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-700">
                  {flag.label}
                </label>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Local Constraints */}
      <div className="mb-6">
        <button
          type="button"
          onClick={() => setShowConstraints(!showConstraints)}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          {showConstraints ? '▼' : '▶'} Local Constraints
        </button>

        {showConstraints && (
          <div className="mt-4 space-y-4 p-4 bg-gray-50 rounded-md">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                RBC Bag Size (mL)
              </label>
              <select
                {...register('rbc_bag_size_ml')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="350">350 mL</option>
                <option value="450">450 mL</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                {...register('leukoreduction_available')}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-700">
                Leukoreduction available
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Evaluating...' : 'Get Recommendation'}
      </button>
    </form>
  )
}
