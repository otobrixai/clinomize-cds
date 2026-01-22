// frontend/app/hospital-admin/users/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { API_ENDPOINTS } from '@/lib/api-config'
import { 
  Users, 
  UserPlus, 
  UserCheck, 
  UserX, 
  Mail, 
  Key,
  Search,
  Filter,
  Edit,
  Shield,
  Stethoscope,
  Building
} from 'lucide-react'

interface HospitalUser {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
  last_login: string | null
}

export default function HospitalUsersPage() {
  const router = useRouter()
  const [users, setUsers] = useState<HospitalUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Add user form state
  const [showAddForm, setShowAddForm] = useState(false)
  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'doctor'
  })
  const [addingUser, setAddingUser] = useState(false)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setLoading(true)
    setError('')
    
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/login')
        return
      }

      const response = await fetch(API_ENDPOINTS.hospitalAdmin.users, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to load users')
      }

      const data = await response.json()
      setUsers(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load users')
      console.error('Error loading users:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setAddingUser(true)
    setError('')

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/login')
        return
      }

      const response = await fetch(API_ENDPOINTS.hospitalAdmin.users, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newUser),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to add user')
      }

      const addedUser = await response.json()
      setUsers([addedUser, ...users])
      setShowAddForm(false)
      setNewUser({ email: '', password: '', full_name: '', role: 'DOCTOR' })
      
    } catch (err: any) {
      setError(err.message || 'Failed to add user')
    } finally {
      setAddingUser(false)
    }
  }

  const handleToggleUserStatus = async (userId: number, isActive: boolean) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return

      const endpoint = isActive 
        ? `${API_ENDPOINTS.hospitalAdmin.users}/${userId}/deactivate`
        : `${API_ENDPOINTS.hospitalAdmin.users}/${userId}/activate`
      
      console.log('Toggle user status:', { userId, isActive, endpoint })
      
      const response = await fetch(endpoint, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      console.log('Response status:', response.status)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Error response:', errorText)
        throw new Error('Failed to update user status: ' + errorText)
      }

      const result = await response.json()
      console.log('Success:', result)

      // Update local state
      setUsers(users.map(user => 
        user.id === userId ? { ...user, is_active: !isActive } : user
      ))

    } catch (err: any) {
      console.error('Toggle error:', err)
      setError(err.message || 'Failed to update user status')
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'HOSPITAL_ADMIN':
        return <Shield className="w-4 h-4 text-purple-600" />
      case 'DOCTOR':
        return <Stethoscope className="w-4 h-4 text-blue-600" />
      default:
        return <Users className="w-4 h-4 text-gray-600" />
    }
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'HOSPITAL_ADMIN':
        return 'bg-purple-100 text-purple-800'
      case 'DOCTOR':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading users...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600 mt-1">
            Manage doctors and staff in your hospital
          </p>
        </div>
        
        <button
          onClick={() => setShowAddForm(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          <UserPlus className="w-4 h-4" />
          Add New User
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Add User Form */}
      {showAddForm && (
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Add New User</h2>
          
          <form onSubmit={handleAddUser} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Mail className="inline w-4 h-4 mr-2" />
                  Email Address *
                </label>
                <input
                  type="email"
                  required
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="doctor@hospital.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Key className="inline w-4 h-4 mr-2" />
                  Password *
                </label>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={newUser.password}
                  onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="At least 6 characters"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  value={newUser.full_name}
                  onChange={(e) => setNewUser({...newUser, full_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="John Smith"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Role *
                </label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="doctor">Doctor</option>
                  <option value="hospital_admin">Hospital Admin</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={() => {
                  setShowAddForm(false)
                  setNewUser({ email: '', password: '', full_name: '', role: 'DOCTOR' })
                }}
                className="px-4 py-2 text-gray-700 hover:text-gray-900"
                disabled={addingUser}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={addingUser}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {addingUser ? 'Adding...' : 'Add User'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Users List */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Users className="w-5 h-5 text-gray-500" />
              <h2 className="font-semibold text-gray-900">
                Hospital Users ({users.length})
              </h2>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search users..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
              <button className="p-2 border border-gray-300 rounded-md hover:bg-gray-50">
                <Filter className="w-4 h-4 text-gray-600" />
              </button>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left py-3 px-6 text-sm font-medium text-gray-700">User</th>
                <th className="text-left py-3 px-6 text-sm font-medium text-gray-700">Role</th>
                <th className="text-left py-3 px-6 text-sm font-medium text-gray-700">Status</th>
                <th className="text-left py-3 px-6 text-sm font-medium text-gray-700">Last Login</th>
                <th className="text-left py-3 px-6 text-sm font-medium text-gray-700">Actions</th> {/* COMBINED */}
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-gray-500">
                    <Users className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>No users found</p>
                    <p className="text-sm mt-1">Add your first user to get started</p>
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="font-semibold text-blue-600">
                            {user.full_name.charAt(0)}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div>
                            <p className="font-medium text-gray-900">{user.full_name}</p>
                            <p className="text-sm text-gray-500">{user.email}</p>
                          </div>
                          {/* Add "You" badge for current user */}
                          {user.id === parseInt(localStorage.getItem('userId') || '0') && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                              You
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    
                    {/* Keep the role column */}
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-2">
                        {getRoleIcon(user.role)}
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRoleBadgeColor(user.role)}`}>
                          {user.role.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </div>
                    </td>

                    {/* Status column */}
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-2">
                        <div className={`h-2 w-2 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className={user.is_active ? 'text-green-700' : 'text-red-700'}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </td>

                    {/* Last Login column */}
                    <td className="py-4 px-6">
                      <div className="text-sm text-gray-600">
                        {user.last_login 
                          ? new Date(user.last_login).toLocaleString('en-BD', {
                              day: 'numeric',
                              month: 'short',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                              hour12: true,
                              timeZone: 'Asia/Dhaka'
                            })
                          : 'Never'
                        }
                      </div>
                    </td>

                    {/* Actions column */}
                    <td className="py-4 px-6">
                      {user.id !== parseInt(localStorage.getItem('userId') || '0') && (
                        <button
                          onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                          className={`px-3 py-1 rounded-md text-sm font-medium ${
                            user.is_active
                              ? 'bg-red-100 text-red-700 hover:bg-red-200'
                              : 'bg-green-100 text-green-700 hover:bg-green-200'
                          }`}
                        >
                          {user.is_active ? (
                            <>
                              <UserX className="inline w-3 h-3 mr-1" />
                              Deactivate
                            </>
                          ) : (
                            <>
                              <UserCheck className="inline w-3 h-3 mr-1" />
                              Activate
                            </>
                          )}
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <Building className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-medium text-blue-900">User Management Guidelines</h3>
            <ul className="text-blue-800 text-sm mt-2 space-y-1">
              <li>• Hospital admins can add and manage users within their hospital</li>
              <li>• Doctors can use the system to get transfusion recommendations</li>
              <li>• Deactivated users cannot log in but their data is preserved</li>
              <li>• Each user's activity is logged for audit purposes</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}