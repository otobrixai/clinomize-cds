// frontend/app/module/cardioiq/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { CardioIQInput, CardioIQOutput } from '@/types/cardioiq'
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
  Activity as Pulse,
  Stethoscope,
  ClipboardCheck,
  BookOpen,
  FileText,
  ArrowLeft
} from 'lucide-react'
import { FadeIn, SlideUp } from '@/components/Animations'
import CardioIQForm from '@/components/CardioIQForm'
import CardioIQRecommendationCard from '@/components/CardioIQRecommendationCard'

export default function CardioIQDashboard() {
  const router = useRouter()
  const [recommendation, setRecommendation] = useState<CardioIQOutput | null>(null)
  const [patientData, setPatientData] = useState<CardioIQInput | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isAdmin, setIsAdmin] = useState(false)
  const [userName, setUserName] = useState<string>('')
  const [recentEvaluations, setRecentEvaluations] = useState<Array<{
    id: number;
    patient: string;
    time: string;
    category: string;
  }>>([])
  const [formKey, setFormKey] = useState(Date.now())
  const [disclaimerAcknowledged, setDisclaimerAcknowledged] = useState(false)

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
      
      const storedName = localStorage.getItem('userName')
      if (storedName) {
        setUserName(storedName)
      }
      
      loadRecentEvaluations()
      fetchUserInfo(token)
    }
    
    checkAuth()
  }, [router])

  const fetchUserInfo = async (token: string) => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.me, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUserName(userData.full_name || userData.email?.split('@')[0] || 'Clinician')
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
      setUserName('Clinician')
    }
  }  

  const loadRecentEvaluations = () => {
    const stored = localStorage.getItem('cardioiqRecentEvaluations')
    if (stored) {
      setRecentEvaluations(JSON.parse(stored))
    }
  }

  const handleSubmit = async (data: CardioIQInput) => {
    setLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('token')?.trim()
      if (!token) {
        throw new Error('Please login first')
      }
      
      setPatientData(data)
      
      // API call to evaluate patient data
      const response = await fetch(API_ENDPOINTS.cardioiq.evaluate, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Failed to get recommendation')
      }

      const result = await response.json()
      setRecommendation(result)
      
      // Save to recent evaluations
      const newEvaluation = {
        id: Date.now(),
        patient: `Patient (${data.patient.age}${data.patient.sex === 'male' ? 'M' : 'F'})`,
        time: 'Just now',
        category: result.clinical_category || 'Evaluated'
      }
      
      const updatedEvaluations = [newEvaluation, ...recentEvaluations.slice(0, 4)]
      setRecentEvaluations(updatedEvaluations)
      localStorage.setItem('cardioiqRecentEvaluations', JSON.stringify(updatedEvaluations))
      
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
      setPatientData(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-gray-100">
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
            <div className="p-2 bg-gradient-to-br from-red-500 to-red-600 rounded-lg">
              <Heart className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">CardioIQ</h1>
              <p className="text-sm text-gray-600">Cardiac Decision Support System</p>
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
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-red-600"></div>
            </div>
          </FadeIn>  
        ) : recommendation !== null ? (
          <SlideUp>
            <div className="space-y-6">
              {/* Page Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-semibold text-gray-800">Cardiac Recommendation</h2>
                  <p className="text-sm text-gray-600 mt-2">
                    Evidence-based guidance for acute cardiac care
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>

              {/* Patient Details Card */}
              {patientData && (
                <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-red-50 rounded-lg">
                        <User className="h-5 w-5 text-red-600" />
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
                    {/* Demographics */}
                    <div className="border-b pb-6">
                      <h4 className="font-medium text-gray-800 mb-4 flex items-center">
                        <User className="h-4 w-4 mr-2 text-gray-500" />
                        Demographics
                      </h4>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 md:gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Age</p>
                          <p className="font-medium text-gray-900">{patientData.patient.age} years</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Weight</p>
                          <p className="font-medium text-gray-900">{patientData.patient.weight_kg} kg</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Sex</p>
                          <p className="font-medium text-gray-900">
                            {patientData.patient.sex === 'male' ? 'Male' : 'Female'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Setting</p>
                          <p className="font-medium text-gray-900">{patientData.context.care_setting}</p>
                        </div>
                      </div>
                    </div>

                    {/* Presentation */}
                    <div className="border-b pb-6">
                      <h4 className="font-medium text-gray-800 mb-4 flex items-center">
                        <Stethoscope className="h-4 w-4 mr-2 text-gray-500" />
                        Presentation
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {patientData.presentation.chest_pain && (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            Chest Pain ({patientData.presentation.chest_pain_type})
                          </span>
                        )}
                        {patientData.presentation.dyspnea && (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            <Pulse className="h-3 w-3 mr-1" />
                            Dyspnea
                          </span>
                        )}
                        {patientData.presentation.syncope && (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            Syncope
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Vitals & Labs */}
                    <div>
                      <h4 className="font-medium text-gray-800 mb-4 flex items-center">
                        <Activity className="h-4 w-4 mr-2 text-gray-500" />
                        Vitals & Laboratory
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-gray-500">BP</p>
                          <p className="font-medium text-gray-900">{patientData.vitals.sbp} mmHg</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">HR</p>
                          <p className="font-medium text-gray-900">{patientData.vitals.hr} bpm</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">SpO₂</p>
                          <p className="font-medium text-gray-900">{patientData.vitals.spo2}%</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Troponin</p>
                          <p className="font-medium text-gray-900">
                            {patientData.labs.troponin ? (patientData.labs.troponin.positive ? 'Positive' : 'Negative') : 'N/A'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Recommendation Card */}
              <div className="bg-white shadow-lg rounded-lg p-8">
                <div className="mb-6">
                  <div className="mb-6 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-md">
                    <p className="text-sm text-yellow-800 font-medium">
                      Clinical decision support only. Confirm with local hospital policy and clinical judgment.
                    </p>
                  </div>

                  <CardioIQRecommendationCard recommendation={recommendation} />
                </div>

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
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Form */}
                <div className="lg:col-span-2">
                  <div className="bg-white shadow-lg rounded-lg p-8">
                    <div className="mb-8">
                      <h2 className="text-2xl font-semibold text-gray-800 mb-2">Cardiac Evaluation</h2>
                      <p className="text-sm text-gray-600">
                        Complete patient information for evidence-based cardiac recommendations
                      </p>
                    </div>

                    {/* Legal Disclaimer Banner */}
                    {!disclaimerAcknowledged && (
                      <div className="mb-6 p-6 bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-400 rounded-lg">
                        <div className="flex items-start space-x-3">
                          <AlertTriangle className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-1" />
                          <div className="flex-1">
                            <h3 className="text-lg font-bold text-gray-900 mb-2">
                              ⚖️ Legal Disclaimer - Required Acknowledgment
                            </h3>
                            <div className="space-y-2 text-sm text-gray-800 mb-4">
                              <p className="font-medium">
                                This system provides <strong>DECISION SUPPORT ONLY</strong>. It is NOT a substitute for clinical judgment.
                              </p>
                              <ul className="list-disc list-inside space-y-1 ml-2">
                                <li>Final clinical decisions rest with the treating physician</li>
                                <li>Recommendations must be verified against local hospital protocols</li>
                                <li>System outputs are advisory only and not prescriptive</li>
                                <li>All recommendations require clinical correlation and validation</li>
                              </ul>
                            </div>
                            <label className="flex items-center space-x-3 cursor-pointer">
                              <input
                                type="checkbox"
                                checked={disclaimerAcknowledged}
                                onChange={(e) => setDisclaimerAcknowledged(e.target.checked)}
                                className="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-red-500"
                              />
                              <span className="text-sm font-medium text-gray-900">
                                I understand and acknowledge that this is decision support only
                              </span>
                            </label>
                          </div>
                        </div>
                      </div>
                    )}

                    {disclaimerAcknowledged && (
                      <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm text-green-800">Disclaimer acknowledged</span>
                      </div>
                    )}

                    <button
                      onClick={handleClearForm}
                      className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-xs sm:text-sm mb-6"
                      type="button"
                      disabled={!disclaimerAcknowledged}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Clear Form
                    </button>                  
                    
                    <CardioIQForm 
                      key={formKey} 
                      onSubmit={handleSubmit} 
                      loading={loading}
                      disabled={!disclaimerAcknowledged}
                    />
                    
                    {error && (
                      <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-sm text-red-800">{error}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Sidebar */}
                <div className="lg:col-span-1 space-y-6">
                  {/* Recent Evaluations */}
                  <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        <div className="p-2 bg-red-50 rounded-lg">
                          <ClipboardCheck className="h-4 w-4 text-red-600" />
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
                            className="group flex items-center justify-between p-3 hover:bg-red-50 rounded-lg transition-colors duration-200 border border-transparent hover:border-red-100"
                          >
                            <div className="flex items-center space-x-3">
                              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">{evaluation.patient}</p>
                                <p className="text-xs text-gray-500">{evaluation.time}</p>
                              </div>
                            </div>
                            <div className="flex items-center">
                              <span className="text-xs font-medium bg-red-100 text-red-800 px-2 py-1 rounded">
                                {evaluation.category}
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

                  {/* Quick Reference */}
                  <div className="bg-gradient-to-br from-red-50 to-gray-50 rounded-xl border border-red-100 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center space-x-2">
                        <div className="p-2 bg-white rounded-lg shadow-sm border border-red-200">
                          <BookOpen className="h-4 w-4 text-red-600" />
                        </div>
                        <h3 className="font-semibold text-gray-800">Quick Reference</h3>
                      </div>
                      <span className="text-xs font-medium text-red-700 bg-red-100 px-2 py-1 rounded-full">
                        Guidelines
                      </span>
                    </div>
                    
                    <div className="space-y-5">
                      {/* STEMI */}
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <div className="flex items-center mb-3">
                          <div className="w-3 h-3 bg-red-600 rounded-full mr-2"></div>
                          <h4 className="text-sm font-semibold text-gray-800">STEMI</h4>
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 flex-shrink-0"></div>
                            <p className="text-xs text-gray-700">Primary PCI within 90 min</p>
                          </div>
                          <div className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 flex-shrink-0"></div>
                            <p className="text-xs text-gray-700">Thrombolysis if PCI delayed</p>
                          </div>
                        </div>
                      </div>
                      
                      {/* NSTEMI */}
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <div className="flex items-center mb-3">
                          <div className="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
                          <h4 className="text-sm font-semibold text-gray-800">NSTEMI</h4>
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></div>
                            <p className="text-xs text-gray-700">Risk stratify (GRACE/HEART)</p>
                          </div>
                          <div className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></div>
                            <p className="text-xs text-gray-700">Early invasive if high risk</p>
                          </div>
                        </div>
                      </div>
                      
                      {/* Chest Pain */}
                      <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-4 border border-blue-100">
                        <div className="flex items-center mb-3">
                          <div className="w-3 h-3 bg-green-600 rounded-full mr-2"></div>
                          <h4 className="text-sm font-semibold text-gray-800">Low Risk Chest Pain</h4>
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                            <p className="text-xs text-gray-700">HEART ≤3: Safe discharge</p>
                          </div>
                          <div className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                            <p className="text-xs text-gray-700">Avoid unnecessary admission</p>
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
            CardioIQ Clinical Decision Support System • Version 1.1.0
          </p>
        </div>
      </footer>
    </div>
  )
}
