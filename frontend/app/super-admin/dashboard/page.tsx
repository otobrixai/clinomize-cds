// frontend/app/super-admin/dashboard/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  Building, 
  Users, 
  Activity,
  TrendingUp,
  Plus,
  ArrowRight
} from 'lucide-react'
import { API_ENDPOINTS } from '@/lib/api-config'

interface Hospital {
  id: number
  name: string
  city?: string
  country: string
  users_count: number
  is_active: boolean
}

export default function SuperAdminDashboard() {
  const router = useRouter()
  const [hospitals, setHospitals] = useState<Hospital[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalHospitals: 0,
    totalUsers: 0,
    activeHospitals: 0,
  })

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token')
      const role = localStorage.getItem('userRole')
      
      if (!token || role !== 'super_admin') {
        router.push('/login')
        return false
      }
      return true
    }

    if (checkAuth()) {
      loadHospitals()
    }
  }, [router])

  const loadHospitals = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(API_ENDPOINTS.superAdmin.hospitals, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setHospitals(data)
        
        // Calculate stats
        const totalHospitals = data.length
        const activeHospitals = data.filter((h: Hospital) => h.is_active).length
        const totalUsers = data.reduce((sum: number, h: Hospital) => sum + h.users_count, 0)
        
        setStats({
          totalHospitals,
          totalUsers,
          activeHospitals
        })
      }
    } catch (error) {
      console.error('Error loading hospitals:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const recentHospitals = hospitals.slice(0, 3)

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">Welcome, Super Admin!</h1>
            <p className="opacity-90">
              Manage hospitals, users, and system configuration
            </p>
          </div>
          <div className="mt-4 md:mt-0">
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm">System Status: Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Hospitals</p>
              <p className="text-3xl font-bold mt-2">{stats.totalHospitals}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Building className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-green-600">
            <TrendingUp className="h-4 w-4 mr-1" />
            <span>{stats.activeHospitals} active</span>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Users</p>
              <p className="text-3xl font-bold mt-2">{stats.totalUsers}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Users className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4">
            <Link href="/super-admin/users" className="text-sm text-blue-600 hover:text-blue-700">
              View all users →
            </Link>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">System Health</p>
              <p className="text-3xl font-bold mt-2">100%</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-green-600">
            <div className="h-2 w-2 bg-green-500 rounded-full mr-2"></div>
            <span>All systems operational</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              href="/super-admin/hospitals"
              className="flex items-center justify-between p-4 border rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg mr-3">
                  <Building className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium">Manage Hospitals</p>
                  <p className="text-sm text-gray-500">Add or edit hospitals</p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </Link>
            
            <Link
              href="/super-admin/users"
              className="flex items-center justify-between p-4 border rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors"
            >
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg mr-3">
                  <Users className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="font-medium">Manage Users</p>
                  <p className="text-sm text-gray-500">Add or edit users</p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </Link>
          </div>
        </div>

        {/* Recent Hospitals */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Hospitals</h2>
            <Link 
              href="/super-admin/hospitals"
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              View all
            </Link>
          </div>
          
          {recentHospitals.length > 0 ? (
            <div className="space-y-3">
              {recentHospitals.map((hospital) => (
                <div key={hospital.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">{hospital.name}</p>
                    <p className="text-sm text-gray-500">
                      {hospital.city ? `${hospital.city}, ` : ''}{hospital.country}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">{hospital.users_count} users</span>
                    <div className={`h-2 w-2 rounded-full ${hospital.is_active ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Building className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 mb-4">No hospitals yet</p>
              <Link
                href="/super-admin/hospitals"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add First Hospital
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* System Info */}
      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">System Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Database</p>
            <p className="font-medium">PostgreSQL • Connected</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Backend API</p>
            <p className="font-medium">FastAPI • Running</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Frontend</p>
            <p className="font-medium">Next.js • Version 14</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Last Updated</p>
            <p className="font-medium">{new Date().toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  )
}