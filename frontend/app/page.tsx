'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  Activity, 
  LogOut,
  ArrowRight,
  Droplets,
  Heart,
  Info 
} from 'lucide-react'

export default function Home() {
  const router = useRouter()
  const [userName, setUserName] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token')?.trim()
      if (!token) {
        router.push('/login')
        return
      }

      // Basic user info load
      const storedName = localStorage.getItem('userName')
      setUserName(storedName || 'Clinician')
      
      setLoading(false)
    }
    
    checkAuth()
  }, [router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">Clinomize-CDS</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700 font-medium">
              Dr. {userName}
            </span>
            <button
              onClick={() => {
                localStorage.removeItem('token')
                localStorage.removeItem('userRole')
                localStorage.removeItem('userId')
                localStorage.removeItem('userName')
                localStorage.removeItem('hospitalId')
                router.push('/login')
              }}
              className="p-2 text-gray-500 hover:text-red-600 transition-colors"
              title="Sign Out"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="mb-10 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Select a Module</h2>
          <p className="text-gray-600">Choose a clinical decision support tool to proceed.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* TransfusionIQ Module Card */}
          <Link href="/module/transfusioniq" className="group">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all duration-200 hover:shadow-lg hover:border-blue-500 hover:-translate-y-1 relative overflow-hidden h-full flex flex-col">
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <Droplets className="h-24 w-24 text-blue-600" />
              </div>
              
              <div className="mb-6">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 text-blue-600">
                  <Droplets className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                  TransfusionIQ
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Evidence-based guidance for blood component therapy. Evaluate patients for transfusion requirements based on clinical parameters and lab values.
                </p>
              </div>
              
              <div className="mt-auto flex items-center text-blue-600 font-medium text-sm">
                Launch Module 
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          </Link>

          {/* CardioIQ Module Card */}
          <Link href="/module/cardioiq" className="group">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-all duration-200 hover:shadow-lg hover:border-red-500 hover:-translate-y-1 relative overflow-hidden h-full flex flex-col">
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <Heart className="h-24 w-24 text-red-600" />
              </div>
              
              <div className="mb-6">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4 text-red-600">
                  <Heart className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-red-600 transition-colors">
                  CardioIQ
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Cardiac decision support for acute coronary syndromes. Risk stratification, level of care recommendations, and guideline-aligned management for chest pain and ACS.
                </p>
              </div>
              
              <div className="mt-auto flex items-center text-red-600 font-medium text-sm">
                Launch Module 
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          </Link>
        </div>

        {/* Footer info or disclaimer */}
        <div className="mt-16 pt-8 border-t border-gray-200 flex items-start space-x-3 text-sm text-gray-500 max-w-2xl mx-auto">
          <Info className="h-5 w-5 flex-shrink-0 text-gray-400" />
          <p>
            This platform provides clinical decision support to assist healthcare professionals. 
            All final clinical decisions are the responsibility of the treating physician.
          </p>
        </div>
      </main>
    </div>
  )
}
