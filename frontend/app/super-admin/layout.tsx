// frontend/app/super-admin/layout.tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  Shield, 
  Building, 
  Users, 
  Settings, 
  LogOut,
  BarChart3,
  Home
} from 'lucide-react'

export default function SuperAdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token')
      const role = localStorage.getItem('userRole')
      
      if (!token) {
        router.push('/login')
        return false
      }
      
      if (role !== 'super_admin') {
        alert('Super admin access required')
        router.push('/')
        return false
      }
      
      return true
    }

    if (checkAuth()) {
      setIsLoading(false)
    }
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Verifying super admin access...</p>
        </div>
      </div>
    )
  }

  const navItems = [
    { icon: Home, label: 'Overview', href: '/super-admin/dashboard' },
    { icon: Building, label: 'Hospitals', href: '/super-admin/hospitals' },
    { icon: BarChart3, label: 'Analytics', href: '/super-admin/analytics' },
    { icon: Settings, label: 'Settings', href: '/super-admin/settings' },
  ]

  const userName = localStorage.getItem('userName') || 'Super Admin'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-600 rounded-lg">
                  <Shield className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="font-bold text-xl">Super Admin Dashboard</h1>
                  <p className="text-sm text-gray-500">System Administration</p>
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
              </div>
              
              <button
                onClick={() => {
                  localStorage.clear()
                  router.push('/login')
                }}
                className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
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
          <p>TransfusionIQ Super Admin • Version 1.0 • {new Date().getFullYear()}</p>
        </div>
      </footer>
    </div>
  )
}