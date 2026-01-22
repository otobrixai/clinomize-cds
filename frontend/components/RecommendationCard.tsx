// frontend/components/RecommendationCard.tsx

'use client'

import { RecommendationResponse } from '@/types/api'
import { useState } from 'react'
import { FadeIn } from './Animations'

interface RecommendationCardProps {
  recommendation: RecommendationResponse
}

export default function RecommendationCard({ recommendation }: RecommendationCardProps) {
  const [showOverride, setShowOverride] = useState(false)
  const [overrideReason, setOverrideReason] = useState('')
  const [copied, setCopied] = useState(false)

  const handleExportPDF = async () => {
    // Call backend PDF endpoint with language parameter using encounter_id
    try {
      const token = localStorage.getItem('token')?.trim()
      if (!token) {
        alert('Please login first to export PDF')
        return
      }
      
      if (!recommendation.encounter_id) {
        alert('Cannot export PDF: encounter ID not available. Please submit the form first.')
        return
      }
      
      const { API_ENDPOINTS } = await import('@/lib/api-config')
      const url = API_ENDPOINTS.pdf.encounter(recommendation.encounter_id)
      console.log('Exporting PDF from:', url)
      console.log('Encounter ID:', recommendation.encounter_id)
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      })
      
      console.log('PDF response status:', response.status)
      
      if (!response.ok) {
        let errorMessage = 'Failed to export PDF'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch {
          const errorText = await response.text()
          errorMessage = `HTTP ${response.status}: ${errorText || response.statusText}`
        }
        console.error('PDF export error:', errorMessage)
        alert(`Failed to export PDF: ${errorMessage}`)
        return
      }
      
      // Check if response is actually a PDF
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/pdf')) {
        console.error('Response is not a PDF:', contentType)
        const text = await response.text()
        alert(`Failed to export PDF: Server returned non-PDF response. ${text.substring(0, 100)}`)
        return
      }
      
      const blob = await response.blob()
      const blobUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = `transfusion-recommendation-${recommendation.encounter_id}-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(blobUrl)
      document.body.removeChild(a)
      
      console.log('PDF exported successfully')
    } catch (error: any) {
      console.error('PDF export error:', error)
      const errorMessage = error.message || 'Network error. Please check console for details.'
      alert(`Failed to export PDF: ${errorMessage}`)
    }
  }

  const handleCopyOrderNote = () => {
    const orderNote = formatOrderNote(recommendation)
    navigator.clipboard.writeText(orderNote)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const formatOrderNote = (rec: RecommendationResponse): string => {
    let note = 'TRANSFUSION ORDER NOTE\n\n'
    if (rec.mtp_protocol) {
      note += '⚠️ MTP PROTOCOL ACTIVE\n\n'
    }
    rec.components.forEach((comp, idx) => {
      if (comp.action === 'contraindicate') {
        note += `❌ ${comp.dose_text}\n`
      } else if (comp.component) {
        note += `✅ ${comp.component}: ${comp.dose_text}\n`
        if (comp.units) {
          note += `   Units: ${comp.units}, Volume: ${comp.volume_ml} mL\n`
        }
      }
      if (idx < rec.components.length - 1) note += '\n'
    })
    return note
  }

  const handleOverride = async () => {
    if (!overrideReason.trim()) {
      alert('Please provide a reason for override')
      return
    }

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        alert('Please login first')
        return
      }

      // Get first recommendation ID (or all if multiple components)
      const firstRecommendationId = recommendation.recommendation_ids?.[0]
      if (!firstRecommendationId) {
        alert('Cannot log override: recommendation ID not available')
        return
      }

      const { API_ENDPOINTS } = await import('@/lib/api-config')
      const response = await fetch(API_ENDPOINTS.audit.override, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          recommendation_id: firstRecommendationId,
          override_reason: overrideReason,
          override_component: null, // Can be enhanced to specify component
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to log override')
      }

      alert('Override logged successfully')
      setShowOverride(false)
      setOverrideReason('')
    } catch (error: any) {
      console.error('Override logging error:', error)
      alert(`Failed to log override: ${error.message || 'Unknown error'}`)
    }
  }

  const positiveComponents = recommendation.components.filter(c => c.component && c.action === 'recommend')
  const contraindications = recommendation.components.filter(c => c.action === 'contraindicate')
  const noTransfusionComponents = recommendation.components.filter(c => !c.component && c.action === 'recommend')


  return (
    <div className="bg-white rounded-lg shadow-md p-4 md:p-6">
      <div className="flex justify-between items-start mb-4">
        <h2 className="text-2xl font-semibold text-gray-900">Recommendation</h2>
        <div className="flex gap-2">
          <button
            onClick={handleCopyOrderNote}
            className="px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-md hover:bg-gray-200"
            title="Copy order note to clipboard"
          >
            {copied ? '✓ Copied to Clipboard' : 'Copy to Clipboard'}
          </button>
          <button
            onClick={handleExportPDF}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
          >
            Export PDF
          </button>
        </div>
      </div>

      {/* MTP Protocol Warning */}
      {recommendation.mtp_protocol && (
        <div className="mb-4 p-4 bg-orange-50 border border-orange-300 rounded-md">
          <h3 className="text-lg font-semibold text-orange-800 mb-2">⚠️ MASSIVE TRANSFUSION PROTOCOL (MTP)</h3>
          <p className="text-orange-700 text-sm">
            Multiple component transfusion plan for active bleeding. Follow MTP protocol.
          </p>
        </div>
      )}

      {/* Overall Warnings */}
      {recommendation.overall_warnings.length > 0 && (
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <h3 className="text-lg font-medium text-yellow-800 mb-2">System Warnings</h3>
          <ul className="list-disc list-inside space-y-1">
            {recommendation.overall_warnings.map((warning, idx) => (
              <li key={idx} className="text-yellow-800 text-sm">⚠ {warning.replace(/[⚠️📋]/g, '').trim()}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Contraindications */}
      {contraindications.length > 0 && (
        <div className="mb-4 p-4 bg-red-50 border border-red-300 rounded-md">
          <h3 className="text-lg font-semibold text-red-800 mb-2">❌ Contraindications</h3>
          {contraindications.map((contra, idx) => (
            <div key={idx} className="mb-3">
              <p className="font-semibold text-red-900">{contra.dose_text}</p>
              <ul className="list-disc list-inside space-y-1 mt-2">
                {contra.why.map((point, i) => (
                  <li key={i} className="text-red-800 text-sm">{point}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      {/* Component Recommendations */}
      {positiveComponents.length > 0 && (
        <div className="mb-4">
          <h3 className="text-lg font-medium text-gray-700 mb-3">Recommended Components</h3>
          {positiveComponents.map((comp, idx) => (
            <FadeIn key={idx} delay={idx * 100}>
              <div className="mb-4 p-4 border border-gray-200 rounded-md">
                {/* Component Header - ALWAYS VISIBLE */}
                <h4 className="text-xl font-semibold text-primary-600 mb-2">{comp.component}</h4>
                
                {/* Component Details - ALWAYS VISIBLE */}
                <div className="mb-2">
                  <span className="text-sm font-medium text-gray-700">Dose: </span>
                  <span className="text-gray-900">{comp.dose_text}</span>
                </div>
                
                {comp.units && (
                  <div className="mb-2 text-sm text-gray-600">
                    Units: {comp.units} | Volume: {comp.volume_ml} mL
                  </div>
                )}

                <div className="mb-2">
                  <span className="text-sm font-medium text-gray-700">Expected Increment: </span>
                  <span className="text-gray-900">{comp.expected_increment}</span>
                </div>

                <div className="mt-3">
                  <span className="text-sm font-medium text-gray-700">Rationale:</span>
                  <ul className="list-disc list-inside space-y-1 mt-1">
                    {comp.why.map((point, i) => (
                      <li key={i} className="text-gray-700 text-sm">{point}</li>
                    ))}
                  </ul>
                </div>

                <div className="mt-3">
                  <span className="text-sm font-medium text-gray-700">Recheck Plan: </span>
                  <span className="text-gray-900 text-sm">{comp.recheck_plan}</span>
                </div>

                {comp.warnings.length > 0 && (
                  <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <span className="text-sm font-medium text-yellow-800">Warnings:</span>
                    <ul className="list-disc list-inside space-y-1 mt-1">
                      {comp.warnings.map((warning, i) => (
                        <li key={i} className="text-yellow-800 text-xs">⚠ {warning.replace(/[⚠️📋]/g, '').trim()}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600">
                  <strong>Rule IDs:</strong> {comp.rule_ids.join(', ')}
                </div>
                

                {/* Required Actions (Visual Indicators) */}
                <div className="mt-3 flex gap-2">
                  {comp.component === 'RBC' && (
                    <>
                      <div className="px-3 py-1.5 bg-gray-50 text-gray-600 rounded-md text-sm flex items-center gap-2">
                        <span>🧪</span>
                        <span>Type & Screen</span>
                      </div>
                      <div className="px-3 py-1.5 bg-gray-50 text-gray-600 rounded-md text-sm flex items-center gap-2">
                        <span>🔬</span>
                        <span>Cross-match</span>
                      </div>
                    </>
                  )}
                  {comp.component === 'Platelets' && (
                    <>
                      <div className="px-3 py-1.5 bg-gray-50 text-gray-600 rounded-md text-sm flex items-center gap-2">
                        <span>📦</span>
                        <span>Check inventory</span>
                      </div>
                      <div className="px-3 py-1.5 bg-gray-50 text-gray-600 rounded-md text-sm flex items-center gap-2">
                        <span>⏰</span>
                        <span>Schedule infusion</span>
                      </div>
                    </>
                  )}
                  {comp.component === 'FFP' && (
                    <div className="px-3 py-1.5 bg-gray-50 text-gray-600 rounded-md text-sm flex items-center gap-2">
                      <span>❄️</span>
                      <span>Thaw required (30-60 min)</span>
                    </div>
                  )}
                  {comp.component === 'Cryoprecipitate' && (
                    <div className="px-3 py-1.5 bg-gray-50 text-gray-600 rounded-md text-sm flex items-center gap-2">
                      <span>❄️</span>
                      <span>Thaw required (20-30 min)</span>
                    </div>
                  )}
                </div>
              </div>
            </FadeIn>
          ))}
        </div>
      )}

      {/* No Transfusion */}
      {noTransfusionComponents.length > 0 && positiveComponents.length === 0 && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">No Transfusion Recommended</h3>
          {noTransfusionComponents.map((comp, idx) => (
            <div key={idx}>
              <p className="text-blue-900 mb-2">{comp.dose_text}</p>
              <div className="mb-2">
                <span className="text-sm font-medium text-blue-800">Why not transfuse?</span>
                <ul className="list-disc list-inside space-y-1 mt-1">
                  {comp.why.map((point, i) => (
                    <li key={i} className="text-blue-800 text-sm">{point}</li>
                  ))}
                </ul>
              </div>
              <div className="mt-2">
                <span className="text-sm font-medium text-blue-800">Plan: </span>
                <span className="text-blue-900 text-sm">{comp.recheck_plan}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* References (from first component) */}
      {recommendation.components.length > 0 && recommendation.components[0].references.length > 0 && (
        <div className="mb-4">
          <h3 className="text-lg font-medium text-gray-700 mb-2">References</h3>
          <ul className="list-disc list-inside space-y-1">
            {recommendation.components[0].references.map((ref, idx) => (
              <li key={idx} className="text-gray-700 text-sm">{ref}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Rule Version */}
      <div className="mb-4 p-3 bg-gray-50 rounded-md">
        <p className="text-xs text-gray-600">
          <strong>Rule Version:</strong> {recommendation.rule_version}
        </p>
      </div>

      {/* Override Button */}
      <div className="border-t pt-4">
        <button
          onClick={() => setShowOverride(!showOverride)}
          className="text-sm text-red-600 hover:text-red-700 font-medium"
        >
          Override Recommendation
        </button>

        {showOverride && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <label className="block text-sm font-medium text-red-800 mb-2">
              Reason for Override (Required for Audit)
            </label>
            <textarea
              value={overrideReason}
              onChange={(e) => setOverrideReason(e.target.value)}
              className="w-full px-3 py-2 border border-red-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              rows={3}
              placeholder="Enter reason for deviating from recommendation..."
            />
            <div className="mt-2 flex gap-2">
              <button
                onClick={handleOverride}
                className="px-4 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700"
              >
                Log Override
              </button>
              <button
                onClick={() => {
                  setShowOverride(false)
                  setOverrideReason('')
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 text-sm rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
