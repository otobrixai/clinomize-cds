// frontend/app/super-admin/hospitals/[id]/users/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { 
  Users, 
  Plus, 
  Edit, 
  Trash2, 
  ArrowLeft,
  Building,
  Mail,
  Shield,
  User,
  Check,
  X,
  Eye
} from 'lucide-react'
import { API_ENDPOINTS } from '@/lib/api-config'

interface Hospital {
  id: number
  name: string
  city?: string
  country: string
}

interface HospitalUser {
  id: number
  email: string
  full_name: string
  role: 'doctor' | 'admin' | 'hospital_admin' | 'super_admin'
  is_active: boolean
  created_at: string
}

export default function HospitalUsersPage() {
  const router = useRouter()
  const params = useParams()
  const hospitalId = params.id as string
  
  const [hospital, setHospital] = useState<Hospital | null>(null)
  const [users, setUsers] = useState<HospitalUser[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'doctor' as 'doctor' | 'hospital_admin',
    hospital_id: parseInt(hospitalId)
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
      loadHospital()
      loadHospitalUsers()
    }
  }, [router, hospitalId])

  const loadHospital = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_ENDPOINTS.superAdmin.hospitals}/${hospitalId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setHospital(data)
      }
    } catch (error) {
      console.error('Error loading hospital:', error)
    }
  }

  const loadHospitalUsers = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(API_ENDPOINTS.superAdmin.hospitalUsers(parseInt(hospitalId)), {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setUsers(data)
      } else {
        setError('Failed to load users')
      }
    } catch (error) {
      console.error('Error loading users:', error)
      setError('Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  const handleAddUser = async () => {
    // Validate
    if (!newUser.email.trim() || !newUser.password.trim() || !newUser.full_name.trim()) {
      setError('All fields are required')
      return
    }

    if (newUser.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(API_ENDPOINTS.superAdmin.addUser, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newUser)
      })
      
      if (response.ok) {
        setSuccess('User added successfully!')
        setNewUser({
          email: '',
          password: '',
          full_name: '',
          role: 'doctor',
          hospital_id: parseInt(hospitalId)
        })
        setShowAddForm(false)
        loadHospitalUsers()
        
        setTimeout(() => setSuccess(''), 3000)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to add user')
      }
    } catch (error) {
      console.error('Error adding user:', error)
      setError('Failed to add user')
    }
  }

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      // Note: We need to create a DELETE endpoint for users
      // For now, we'll just show a message
      setError('Delete functionality will be implemented in the backend')
      // TODO: Implement actual delete when backend endpoint is ready
    } catch (error) {
      console.error('Error deleting user:', error)
      setError('Failed to delete user')
    }
  }

  const getRoleBadge = (role: string) => {
    const roles = {
      'doctor': { color: 'bg-blue-100 text-blue-800', label: 'Doctor' },
      'hospital_admin': { color: 'bg-purple-100 text-purple-800', label: 'Hospital Admin' },
      'admin': { color: 'bg-green-100 text-green-800', label: 'Admin' },
      'super_admin': { color: 'bg-red-100 text-red-800', label: 'Super Admin' }
    }
    
    const roleConfig = roles[role as keyof typeof roles] || { color: 'bg-gray-100 text-gray-800', label: role }
    
    return (
      <span className={`px-2 py-1 text-xs rounded-full ${roleConfig.color}`}>
        {roleConfig.label}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading users...</p>
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
            href="/super-admin/hospitals"
            className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-2"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Hospitals
          </Link>
          <div className="flex items-center mb-2">
            <Building className="h-5 w-5 text-gray-400 mr-2" />
            <h1 className="text-2xl font-bold text-gray-900">
              {hospital?.name || 'Hospital'} Users
            </h1>
          </div>
          <p className="text-gray-600">
            Manage users for {hospital?.name || 'this hospital'}
            {hospital?.city && ` • ${hospital.city}, ${hospital.country}`}
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="h-5 w-5 mr-2" />
          Add User
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

      {/* Add User Form */}
      {showAddForm && (
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Add New User</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  value={newUser.full_name}
                  onChange={(e) => setNewUser({...newUser, full_name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Dr. John Doe"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="doctor@hospital.com"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password *
                </label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Minimum 6 characters"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">User will use this to login</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role *
                </label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({...newUser, role: e.target.value as 'doctor' | 'hospital_admin'})}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="doctor">Doctor</option>
                  <option value="hospital_admin">Hospital Admin</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  {newUser.role === 'doctor' 
                    ? 'Can access clinical features' 
                    : 'Can manage hospital users and settings'}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleAddUser}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Add User
              </button>
              <button
                onClick={() => {
                  setShowAddForm(false)
                  setNewUser({
                    email: '',
                    password: '',
                    full_name: '',
                    role: 'doctor',
                    hospital_id: parseInt(hospitalId)
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

      {/* Users List */}
      <div className="bg-white border rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">Hospital Users ({users.length})</h2>
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-sm">
                <div className="h-2 w-2 bg-green-500 rounded-full mr-2"></div>
                <span className="text-gray-600">{users.filter(u => u.is_active).length} active</span>
              </div>
              <div className="text-sm text-gray-500">
                {users.filter(u => u.role === 'doctor').length} doctors
              </div>
            </div>
          </div>
        </div>

        {users.length === 0 ? (
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No users yet</h3>
            <p className="text-gray-600 mb-6">Add the first user to this hospital</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Add First User
            </button>
          </div>
        ) : (
          <div className="divide-y">
            {users.map((user) => (
              <div key={user.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <div className="flex items-center">
                        {user.role === 'doctor' ? (
                          <User className="h-5 w-5 text-blue-500 mr-2" />
                        ) : user.role === 'hospital_admin' ? (
                          <Shield className="h-5 w-5 text-purple-500 mr-2" />
                        ) : (
                          <Users className="h-5 w-5 text-gray-500 mr-2" />
                        )}
                        <h3 className="text-lg font-medium text-gray-900">{user.full_name}</h3>
                      </div>
                      <div className="ml-3">
                        {getRoleBadge(user.role)}
                      </div>
                      <div className={`ml-3 px-2 py-1 text-xs rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </div>
                    </div>
                    <div className="flex items-center text-sm text-gray-600 mb-3">
                      <Mail className="h-4 w-4 mr-1" />
                      {user.email}
                    </div>
                    <div className="text-sm text-gray-500">
                      Added {new Date(user.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {/* View user details */}}
                      className="p-2 text-gray-500 hover:text-gray-700"
                      title="View Details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => {/* Edit user */}}
                      className="p-2 text-blue-500 hover:text-blue-700"
                      title="Edit"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      className="p-2 text-red-500 hover:text-red-700"
                      title="Delete"
                      disabled={user.role === 'super_admin'}
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Role Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <User className="h-5 w-5 text-blue-600 mr-2" />
            <h3 className="font-medium text-blue-900">Doctor Role</h3>
          </div>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Access to clinical decision support</li>
            <li>• Can evaluate patients and get recommendations</li>
            <li>• Can view patient history (within their hospital)</li>
            <li>• Cannot manage users or system settings</li>
          </ul>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <Shield className="h-5 w-5 text-purple-600 mr-2" />
            <h3 className="font-medium text-purple-900">Hospital Admin Role</h3>
          </div>
          <ul className="text-sm text-purple-800 space-y-1">
            <li>• All doctor privileges</li>
            <li>• Can add/edit doctors in their hospital</li>
            <li>• Can configure hospital-specific thresholds</li>
            <li>• Can view hospital analytics and reports</li>
            <li>• Cannot access super admin features</li>
          </ul>
        </div>
      </div>
    </div>
  )
}