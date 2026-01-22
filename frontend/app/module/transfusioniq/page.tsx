// frontend/app/module/transfusioniq/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import MultiStepForm from '@/components/MultiStepForm'
import RecommendationCard from '@/components/RecommendationCard'
import { RecommendationResponse, PatientInput } from '@/types/api'
import { API_ENDPOINTS } from '@/lib/api-config'
import { 
  Activity, 
  LogOut,
  User,
  Shield,
  CheckCircle,
  AlertTriangle,
  Trash2,
  Heart,
  Droplets,
  Pill,
  Stethoscope,
  ClipboardCheck,
  BookOpen,
  FileText,
  ArrowLeft
} from 'lucide-react'
import { FadeIn, SlideUp } from '@/components/Animations'

export default function ClinicianDashboard() {
  const router = useRouter()
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null)
  const [patientData, setPatientData] = useState<PatientInput | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isAdmin, setIsAdmin] = useState(false)
  const [userName, setUserName] = useState<string>('')
  const [recentEvaluations, setRecentEvaluations] = useState<Array<{
    id: number;
    patient: string;
    time: string;
    recommendation: string;
  }>>([])
  const [formKey, setFormKey] = useState(Date.now())

  // Check auth
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token')?.trim()
      if (!token) {
        router.push('/login')
        return
      }

      const userRole = localStorage.getItem('userRole') || 'doctor'
      setIsAdmin(userRole === 'admin')
      
      // Initialize userName from localStorage immediately
      const storedName = localStorage.getItem('userName')
      if (storedName) {
        setUserName(storedName)
      }
      
      // Load recent evaluations
      loadRecentEvaluations()

      // Fetch user info in background (don't await)
      fetchUserInfo(token)
    }
    
    checkAuth()
  }, [router])

  // fetch user info
  const fetchUserInfo = async (token: string) => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.me, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      })
      
      if (response.ok) {
        const userData = await response.json()
        // Use full_name if available, otherwise fall back to email or "Clinician"
        setUserName(userData.full_name || userData.email?.split('@')[0] || 'Clinician')
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
      setUserName('Clinician') // Default fallback
    }
  }  

  const loadRecentEvaluations = () => {
    // Load from localStorage or API
    const stored = localStorage.getItem('recentEvaluations')
    if (stored) {
      setRecentEvaluations(JSON.parse(stored))
    }
  }

  const handleSubmit = async (data: any) => {
    setLoading(true)
    setError(null)
    
    try {
      // Clean data for submission
      const cleanedData: any = {
        age_years: parseFloat(data.age_years),
        weight_kg: parseFloat(data.weight_kg),
        sex: data.sex,
        setting: data.setting,
        active_bleeding: Boolean(data.active_bleeding),
        hemodynamic_instability: Boolean(data.hemodynamic_instability ?? false),
      }
      
      // Add lab values if provided
      if (data.hb_gdl) cleanedData.hb_gdl = parseFloat(data.hb_gdl)
      if (data.platelets_x109l) cleanedData.platelets_x109l = parseFloat(data.platelets_x109l)
      if (data.inr) cleanedData.inr = parseFloat(data.inr)
      if (data.fibrinogen_mgdl) cleanedData.fibrinogen_mgdl = parseFloat(data.fibrinogen_mgdl)
      
      // Add history flags
      cleanedData.history_flags = data.history_flags || {}
      
      const token = localStorage.getItem('token')?.trim()
      if (!token) {
        throw new Error('Please login first')
      }
      
      // Save patient data for display
      setPatientData(cleanedData)
      
      // API call
      const response = await fetch(API_ENDPOINTS.recommendations.evaluate, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(cleanedData),
      })

      if (!response.ok) {
        throw new Error('Failed to get recommendation')
      }

      const result = await response.json()
      setRecommendation(result)
      
      // Save to recent evaluations
      const newEvaluation = {
        id: Date.now(),
        patient: `Patient (${data.age_years}${data.sex === 'M' ? 'M' : 'F'})`,
        time: 'Just now',
        recommendation: result.components[0]?.dose_text || 'No transfusion'
      }
      
      const updatedEvaluations = [newEvaluation, ...recentEvaluations.slice(0, 4)]
      setRecentEvaluations(updatedEvaluations)
      localStorage.setItem('recentEvaluations', JSON.stringify(updatedEvaluations))
      
    } catch (err: any) {
      console.error('Error in handleSubmit:', err)
      setError(err.message || 'Failed to get recommendation')
    } finally {
      setLoading(false)
    }
  }

  const handleClearForm = () => {
    if (window.confirm('Clear all form data and start over?')) {
      setFormKey(Date.now())
      setError(null)
      setPatientData(null) // Also clear patient data
    }
  }

  // Helper function to get active history flags
  const getActiveHistoryFlags = () => {
    if (!patientData?.history_flags) return []
    return Object.entries(patientData.history_flags)
      .filter(([_, value]) => value)
      .map(([key]) => key)
  }

  // Helper to format setting display
  const formatSetting = (setting: string) => {
    const settingsMap: Record<string, string> = {
      'ward': 'Ward',
      'icu': 'ICU',
      'or': 'Operating Room',
      'er': 'Emergency Room'
    }
    return settingsMap[setting] || setting
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              href="/"
              className="p-2 hover:bg-gray-100 rounded-md transition-colors"
              title="Back to Module Selection"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600" />
            </Link>
            <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">TransfusionIQ</h1>
              <p className="text-sm text-gray-600">Clinical Decision Support System</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">            
            {isAdmin && (
              <Link
                href="/admin/dashboard"
                className="hidden md:flex items-center px-4 py-2 bg-purple-50 text-purple-700 rounded-md hover:bg-purple-100 transition-colors text-sm"
              >
                <Shield className="h-4 w-4 mr-2" />
                Admin Dashboard
              </Link>
            )}
            
            <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-gray-50 rounded-md">
              <User className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-700">
                {userName ? `Dr. ${userName}` : 'Loading...'}
              </span>
            </div>
            
            <button
              onClick={() => {
                localStorage.removeItem('token')
                localStorage.removeItem('userRole')
                router.push('/login')
              }}
              className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            >
              <LogOut className="h-4 w-4 mr-2" />
              <span className="hidden md:inline">Sign Out</span>
            </button>
            
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {loading ? (
          <FadeIn>
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
            </div>
          </FadeIn>  
        ) : recommendation !== null ? (
          <SlideUp>
            <div className="space-y-6">
              {/* Page Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-semibold text-gray-800">Transfusion Recommendation</h2>
                  <p className="text-sm text-gray-600 mt-2">
                    Evidence-based guidance for patient management
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>

              {/* Patient Details Card - NEW */}
              {patientData && (
                <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-blue-50 rounded-lg">
                        <User className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">Patient Details</h3>
                        <p className="text-sm text-gray-500">
                          Submitted by {userName.startsWith('Dr. ') ? userName : `Dr. ${userName}`} • {new Date().toLocaleString('en-US', { 
                            month: 'short', 
                            day: 'numeric', 
                            year: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit',
                            hour12: true
                          })}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    {/* Demographics Section */}
                    <div className="border-b pb-6">
                      <h4 className="font-medium text-gray-800 mb-4 flex items-center">
                        <User className="h-4 w-4 mr-2 text-gray-500" />
                        Demographics
                      </h4>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 md:gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Age</p>
                          <p className="font-medium text-gray-900">{patientData.age_years} years</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Weight</p>
                          <p className="font-medium text-gray-900">{patientData.weight_kg} kg</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Sex</p>
                          <p className="font-medium text-gray-900">
                            {patientData.sex === 'M' ? 'Male' : 'Female'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Setting</p>
                          <p className="font-medium text-gray-900">{formatSetting(patientData.setting)}</p>
                        </div>
                      </div>
                    </div>

                    {/* Laboratory Values Section */}
                    <div className="border-b pb-6">
                      <h4 className="font-medium text-gray-800 mb-4 flex items-center">
                        <Droplets className="h-4 w-4 mr-2 text-gray-500" />
                        Laboratory Values
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Hemoglobin</p>
                          <p className="font-medium text-gray-900">
                            {patientData.hb_gdl ? `${patientData.hb_gdl} g/dL` : 'Not provided'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Platelets</p>
                          <p className="font-medium text-gray-900">
                            {patientData.platelets_x109l ? `${patientData.platelets_x109l} ×10⁹/L` : 'Not provided'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">INR</p>
                          <p className="font-medium text-gray-900">
                            {patientData.inr ? patientData.inr : 'Not provided'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Fibrinogen</p>
                          <p className="font-medium text-gray-900">
                            {patientData.fibrinogen_mgdl ? `${patientData.fibrinogen_mgdl} mg/dL` : 'Not provided'}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Clinical Context Section */}
                    <div>
                      <h4 className="font-medium text-gray-800 mb-4 flex items-center">
                        <Stethoscope className="h-4 w-4 mr-2 text-gray-500" />
                        Clinical Context
                      </h4>
                      <div className="space-y-4">
                        {/* Active Conditions */}
                        <div>
                          <p className="text-sm text-gray-500 mb-2">Active Conditions</p>
                          <div className="flex flex-wrap gap-2">
                            {patientData.active_bleeding && (
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                <AlertTriangle className="h-3 w-3 mr-1" />
                                Active Bleeding
                              </span>
                            )}
                            {patientData.hemodynamic_instability && (
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                                <Heart className="h-3 w-3 mr-1" /> {/* Heart for hemodynamic issues */}
                                Hemodynamic Instability
                              </span>
                            )}
                            {!patientData.active_bleeding && !patientData.hemodynamic_instability && (
                              <span className="text-sm text-gray-500">No active conditions</span>
                            )}
                          </div>
                        </div>

                        {/* Medical History */}
                        <div>
                          <p className="text-sm text-gray-500 mb-2">Medical History</p>
                          <div className="flex flex-wrap gap-2">
                            {getActiveHistoryFlags().length > 0 ? (
                              getActiveHistoryFlags().map((flag) => (
                                <span key={flag} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  <Pill className="h-3 w-3 mr-1" /> {/* Pill for medical history */}
                                  {flag.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                                </span>
                              ))
                            ) : (
                              <span className="text-sm text-gray-500">No significant history flags</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Recommendation Card */}
              <div className="bg-white shadow-lg rounded-lg p-8">
                <div className="mb-6">
                  {recommendation.mtp_protocol && (
                    <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-md">
                      <h3 className="text-sm font-semibold text-red-800 mb-2">MASSIVE TRANSFUSION PROTOCOL</h3>
                      <p className="text-sm text-red-700">
                        Multiple components required. Activate blood bank MTP protocol. Follow institutional guidelines.
                      </p>
                    </div>
                  )}

                  <div className="mb-6 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-md">
                    <p className="text-sm text-yellow-800 font-medium">
                      Clinical decision support only. Confirm with local hospital policy and clinical judgment.
                    </p>
                  </div>

                  <RecommendationCard 
                    recommendation={recommendation}
                  />
                </div>

                {/* Add this New Evaluation button at bottom */}
                <div className="border-t pt-6 mt-6">
                  <div className="flex justify-between items-center">
                    <div className="text-sm text-gray-600">
                      Evaluation completed • {new Date().toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                    <button
                      onClick={() => {
                        setRecommendation(null)
                        setPatientData(null)
                      }}
                      className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
                    >
                      Start New Evaluation
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </SlideUp>  
        ) : (
          <FadeIn>
            <div className="space-y-8">
              {/* Main Content Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Right Column - Form */}
                <div className="lg:col-span-2">
                  <div className="bg-white shadow-lg rounded-lg p-8">
                    <div className="mb-8">
                      <h2 className="text-2xl font-semibold text-gray-800 mb-2">Patient Evaluation</h2>
                      <p className="text-sm text-gray-600">
                        Complete all relevant patient information for evidence-based recommendations
                      </p>
                    </div>

                    <button
                      onClick={handleClearForm}
                      className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-xs sm:text-sm mb-6"
                      type="button"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Clear Form
                    </button>                  
                    
                    <MultiStepForm key={formKey} onSubmit={handleSubmit} loading={loading} />
                    
                    {error && (
                      <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-sm text-red-800">{error}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Left Column - Recent Evaluations and Quick Reference */}
                <div className="lg:col-span-1 space-y-6">
                  {/* Recent Evaluations Card - IMPROVED */}
                  <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        <div className="p-2 bg-blue-50 rounded-lg">
                          <ClipboardCheck className="h-4 w-4 text-blue-600" />
                        </div>
                        <h3 className="font-semibold text-gray-800">Recent Evaluations</h3>
                      </div>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                        {recentEvaluations.length}
                      </span>
                    </div>
                    
                    {recentEvaluations.length > 0 ? (
                      <div className="space-y-3">
                        {recentEvaluations.map((evaluation) => (
                          <div 
                            key={evaluation.id} 
                            className="group flex items-center justify-between p-3 hover:bg-blue-50 rounded-lg transition-colors duration-200 border border-transparent hover:border-blue-100"
                          >
                            <div className="flex items-center space-x-3">
                              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">{evaluation.patient}</p>
                                <p className="text-xs text-gray-500">{evaluation.time}</p>
                              </div>
                            </div>
                            <div className="flex items-center">
                              <span className="text-xs font-medium bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                {evaluation.recommendation}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="py-8 text-center">
                        <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-3">
                          <FileText className="h-6 w-6 text-gray-400" />
                        </div>
                        <p className="text-sm text-gray-500 mb-1">No evaluations yet</p>
                        <p className="text-xs text-gray-400">Complete your first assessment</p>
                      </div>
                    )}
                  </div>

                  {/* Quick Reference - IMPROVED */}
                  <div className="bg-gradient-to-br from-blue-50 to-gray-50 rounded-xl border border-blue-100 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center space-x-2">
                        <div className="p-2 bg-white rounded-lg shadow-sm border border-blue-200">
                          <BookOpen className="h-4 w-4 text-blue-600" />
                        </div>
                        <h3 className="font-semibold text-gray-800">Quick Reference</h3>
                      </div>
                      <span className="text-xs font-medium text-blue-700 bg-blue-100 px-2 py-1 rounded-full">
                        Guidelines
                      </span>
                    </div>
                    
                    <div className="space-y-5">
                      {/* Hemoglobin Section */}
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <div className="flex items-center mb-3">
                          <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                          <h4 className="text-sm font-semibold text-gray-800">Hemoglobin</h4>
                        </div>
                        <div className="space-y-2.5">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">Stable ward:</span>
                            <span className="text-sm font-semibold text-red-600">&lt;7 g/dL</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">ICU/cardiac:</span>
                            <span className="text-sm font-semibold text-red-600">&lt;8 g/dL</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">Active bleeding:</span>
                            <span className="text-sm font-semibold text-red-600">&lt;8-9 g/dL</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Platelets Section */}
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <div className="flex items-center mb-3">
                          <div className="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
                          <h4 className="text-sm font-semibold text-gray-800">Platelets</h4>
                        </div>
                        <div className="space-y-2.5">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">Dengue bleeding:</span>
                            <span className="text-sm font-semibold text-orange-600">&lt;10 ×10⁹/L</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">High-risk procedure:</span>
                            <span className="text-sm font-semibold text-orange-600">&gt;50 ×10⁹/L</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">Active bleeding:</span>
                            <span className="text-sm font-semibold text-orange-600">&gt;50 ×10⁹/L</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Special Considerations */}
                      <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-4 border border-red-100">
                        <div className="flex items-center mb-3">
                          <div className="w-3 h-3 bg-red-600 rounded-full mr-2"></div>
                          <h4 className="text-sm font-semibold text-gray-800">Special Considerations</h4>
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 flex-shrink-0"></div>
                            <p className="text-xs text-gray-700">Active bleeding + instability = MTP</p>
                          </div>
                          <div className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 flex-shrink-0"></div>
                            <p className="text-xs text-gray-700">Cardiac: Maintain Hb &gt;8 g/dL</p>
                          </div>
                          <div className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 flex-shrink-0"></div>
                            <p className="text-xs text-gray-700">Post-op: Check coagulation factors</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </FadeIn>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-600">
          <p className="font-medium mb-2">
            Clinical decision support only. Not a substitute for clinical judgment.
          </p>
          <p>
            TransfusionIQ Clinical Decision Support System • Version 1.0
          </p>
        </div>
      </footer>
    </div>
  )
}
