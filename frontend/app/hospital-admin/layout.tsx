// frontend/app/hospital-admin/layout.tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  Building, 
  BarChart3, 
  LogOut,
  Home,
  DollarSign,
  Activity,
  Users
} from 'lucide-react'

export default function HospitalAdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [userName, setUserName] = useState('')

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token')
      const role = localStorage.getItem('userRole')
      
      if (!token) {
        router.push('/login')
        return false
      }
      
      // Allow hospital_admin and super_admin
      if (!['hospital_admin', 'super_admin'].includes(role || '')) {
        alert('Hospital admin access required')
        router.push('/')
        return false
      }
      
      return true
    }

    if (checkAuth()) {
      setIsLoading(false)
      setUserName(localStorage.getItem('userName') || 'Hospital Admin')
    }
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading hospital dashboard...</p>
        </div>
      </div>
    )
  }

  const navItems = [
    { icon: Home, label: 'Overview', href: '/hospital-admin' },
    { icon: BarChart3, label: 'Analytics', href: '/hospital-admin/analytics' },
    { icon: DollarSign, label: 'Costs', href: '/hospital-admin/costs' },
    { icon: Users, label: 'Users', href: '/hospital-admin/users' },
    { icon: Activity, label: 'Reports', href: '/hospital-admin/reports' },
  ]

  const userRole = localStorage.getItem('userRole') || 'hospital_admin'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-600 rounded-lg">
                  <Building className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="font-bold text-xl">Hospital Analytics</h1>
                  <p className="text-sm text-gray-500">
                    {userRole === 'super_admin' ? 'Super Admin View' : 'Blood Utilization Dashboard'}
                  </p>
                </div>
              </div>
              
              {/* Navigation */}
              <nav className="hidden md:flex items-center space-x-1">
                {navItems.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
                    >
                      <Icon className="h-5 w-5" />
                      <span>{item.label}</span>
                    </Link>
                  )
                })}
              </nav>
            </div>

            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-gray-100 rounded-lg">
                <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-700">{userName}</span>
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                  {userRole.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              
              <button
                onClick={() => {
                  localStorage.clear()
                  router.push('/login')
                }}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <LogOut className="h-5 w-5" />
                <span className="hidden md:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Navigation */}
      <div className="md:hidden bg-white border-b">
        <div className="px-4 py-2 flex overflow-x-auto space-x-4">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex flex-col items-center px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 min-w-[80px]"
              >
                <Icon className="h-5 w-5 mb-1" />
                <span className="text-xs">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t bg-white py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-600">
          <p>TransfusionIQ Hospital Analytics • Version 1.0 • {new Date().getFullYear()}</p>
        </div>
      </footer>
    </div>
  )
}