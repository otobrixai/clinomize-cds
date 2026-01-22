// frontend/app/super-admin/hospitals/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  Building, 
  Plus, 
  Edit, 
  Trash2, 
  Users,
  ArrowLeft,
  Check,
  X
} from 'lucide-react'
import { API_ENDPOINTS } from '@/lib/api-config'

interface Hospital {
  id: number
  name: string
  address?: string
  city?: string
  country: string
  is_active: boolean
  users_count: number
  created_at: string
}

export default function HospitalsPage() {
  const router = useRouter()
  const [hospitals, setHospitals] = useState<Hospital[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newHospital, setNewHospital] = useState({
    name: '',
    address: '',
    city: '',
    country: 'Bangladesh',
    admin_name: '',
    admin_email: '',
    admin_password: ''
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

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
      } else {
        setError('Failed to load hospitals')
      }
    } catch (error) {
      console.error('Error loading hospitals:', error)
      setError('Failed to load hospitals')
    } finally {
      setLoading(false)
    }
  }

  const handleAddHospital = async () => {
    if (!newHospital.name.trim()) {
      setError('Hospital name is required')
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(API_ENDPOINTS.superAdmin.hospitals, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newHospital)
      })
      
      if (response.ok) {
        setSuccess('Hospital added successfully!')
        setNewHospital({ 
          name: '', 
          address: '', 
          city: '', 
          country: 'Bangladesh',
          admin_name: '',
          admin_email: '',
          admin_password: ''
        })
        setShowAddForm(false)
        loadHospitals()
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to add hospital')
      }
    } catch (error) {
      console.error('Error adding hospital:', error)
      setError('Failed to add hospital')
    }
  }

  const handleDeleteHospital = async (hospitalId: number) => {
    if (!confirm('Are you sure you want to delete this hospital? This action cannot be undone.')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_ENDPOINTS.superAdmin.hospitals}/${hospitalId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      })
      
      if (response.ok) {
        setSuccess('Hospital deleted successfully!')
        loadHospitals()
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to delete hospital')
      }
    } catch (error) {
      console.error('Error deleting hospital:', error)
      setError('Failed to delete hospital')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading hospitals...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link
            href="/super-admin/dashboard"
            className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-2"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Hospital Management</h1>
          <p className="text-gray-600">Add and manage hospitals in the system</p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="h-5 w-5 mr-2" />
          Add Hospital
        </button>
      </div>

      {/* Messages */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <X className="h-5 w-5 text-red-600 mr-2" />
            <p className="text-red-800">{error}</p>
          </div>
          <button
            onClick={() => setError('')}
            className="mt-2 text-sm text-red-600 hover:text-red-800"
          >
            Dismiss
          </button>
        </div>
      )}

      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <Check className="h-5 w-5 text-green-600 mr-2" />
            <p className="text-green-800">{success}</p>
          </div>
        </div>
      )}

      {/* Add Hospital Form */}
      {showAddForm && (
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Add New Hospital</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hospital Name *
                </label>
                <input
                  type="text"
                  value={newHospital.name}
                  onChange={(e) => setNewHospital({...newHospital, name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter hospital name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  City
                </label>
                <input
                  type="text"
                  value={newHospital.city}
                  onChange={(e) => setNewHospital({...newHospital, city: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter city"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address
                </label>
                <input
                  type="text"
                  value={newHospital.address}
                  onChange={(e) => setNewHospital({...newHospital, address: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter full address"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Country
                </label>
                <select
                  value={newHospital.country}
                  onChange={(e) => setNewHospital({...newHospital, country: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="Bangladesh">Bangladesh</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            {/* Admin Section */}
            <div className="border-t pt-4 mt-4">
              <h3 className="text-md font-medium text-gray-900 mb-3">Initial Hospital Admin (Optional)</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">
                    Admin Full Name
                  </label>
                  <input
                    type="text"
                    value={newHospital.admin_name}
                    onChange={(e) => setNewHospital({...newHospital, admin_name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g. Dr. Admin"
                  />
                </div>
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">
                    Admin Email
                  </label>
                  <input
                    type="email"
                    value={newHospital.admin_email}
                    onChange={(e) => setNewHospital({...newHospital, admin_email: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="admin@hospital.com"
                  />
                </div>
                 <div className="md:col-span-2">
                   <label className="block text-sm font-medium text-gray-700 mb-1">
                    Admin Password
                  </label>
                  <input
                    type="password"
                    value={newHospital.admin_password}
                    onChange={(e) => setNewHospital({...newHospital, admin_password: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Secure password"
                  />
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleAddHospital}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Save Hospital
              </button>
              <button
                onClick={() => {
                  setShowAddForm(false)
                  setNewHospital({ 
                    name: '', 
                    address: '', 
                    city: '', 
                    country: 'Bangladesh',
                    admin_name: '',
                    admin_email: '',
                    admin_password: ''
                  })
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Hospitals List */}
      <div className="bg-white border rounded-lg overflow-hidden">
        {hospitals.length === 0 ? (
          <div className="text-center py-12">
            <Building className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hospitals yet</h3>
            <p className="text-gray-600 mb-6">Get started by adding your first hospital</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Add First Hospital
            </button>
          </div>
        ) : (
          <>
            <div className="px-6 py-4 border-b">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">All Hospitals ({hospitals.length})</h2>
                <span className="text-sm text-gray-500">Sorted by latest</span>
              </div>
            </div>
            <div className="divide-y">
              {hospitals.map((hospital) => (
                <div key={hospital.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <Building className="h-5 w-5 text-gray-400 mr-2" />
                        <h3 className="text-lg font-medium text-gray-900">{hospital.name}</h3>
                        <span className={`ml-3 px-2 py-1 text-xs rounded-full ${hospital.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                          {hospital.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mb-3">
                        {hospital.city && <span>{hospital.city}, </span>}
                        {hospital.country}
                        {hospital.address && (
                          <>
                            <br />
                            <span className="text-gray-500">{hospital.address}</span>
                          </>
                        )}
                      </div>
                      <div className="flex items-center space-x-4 text-sm">
                        <div className="flex items-center text-gray-600">
                          <Users className="h-4 w-4 mr-1" />
                          {hospital.users_count} users
                        </div>
                        <div className="text-gray-500">
                          Added {new Date(hospital.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Link
                        href={`/super-admin/hospitals/${hospital.id}/users`}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200"
                      >
                        Manage Users
                      </Link>
                      <button
                        onClick={() => {/* Edit functionality */}}
                        className="p-2 text-gray-500 hover:text-gray-700"
                        title="Edit"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteHospital(hospital.id)}
                        className="p-2 text-red-500 hover:text-red-700"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Help Text */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">About Hospital Management</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Each hospital gets its own isolated environment</li>
          <li>• Hospital admins can only manage users in their own hospital</li>
          <li>• Doctors are assigned to specific hospitals</li>
          <li>• Clinical data is separated by hospital</li>
        </ul>
      </div>
    </div>
  )
}