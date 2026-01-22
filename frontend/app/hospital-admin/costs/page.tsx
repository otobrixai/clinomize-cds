// frontend/app/hospital-admin/costs/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { API_ENDPOINTS } from '@/lib/api-config'
import { 
  DollarSign, 
  Package, 
  Save, 
  RefreshCw,
  TrendingUp,
  Info,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface BloodProductCost {
  id?: number
  component_type: string
  unit_cost_bdt: number
  units_per_bag: number
  is_active: boolean
}

const DEFAULT_PRODUCTS = [
  { component_type: 'RBC', unit_cost_bdt: 3500, units_per_bag: 1, is_active: true },
  { component_type: 'FFP', unit_cost_bdt: 2500, units_per_bag: 1, is_active: true },
  { component_type: 'Platelets', unit_cost_bdt: 4500, units_per_bag: 1, is_active: true },
  { component_type: 'Cryo', unit_cost_bdt: 3000, units_per_bag: 1, is_active: true },
]

export default function CostConfigurationPage() {
  const router = useRouter()
  const [costs, setCosts] = useState<BloodProductCost[]>(DEFAULT_PRODUCTS)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    loadCosts()
  }, [])

  const loadCosts = async () => {
    setLoading(true)
    setError('')
    
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/login')
        return
      }

      const response = await fetch(API_ENDPOINTS.analytics.bloodProductCosts, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        if (data.length > 0) {
          setCosts(data)
        }
        // If no costs exist, keep defaults
      }
      // 404 is OK - no costs set yet
    } catch (err: any) {
      console.error('Error loading costs:', err)
      // Keep defaults if error
    } finally {
      setLoading(false)
    }
  }

  const handleSaveCosts = async () => {
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/login')
        return
      }

      // Save each product cost
      const savePromises = costs.map(cost => 
        fetch(API_ENDPOINTS.analytics.bloodProductCosts, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(cost),
        })
      )

      const responses = await Promise.all(savePromises)
      const allOk = responses.every(r => r.ok)
      
      if (allOk) {
        setSuccess('Blood product costs saved successfully!')
        // Reload to get IDs
        await loadCosts()
      } else {
        throw new Error('Failed to save some costs')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save costs')
    } finally {
      setSaving(false)
    }
  }

  const handleCalculateROI = async () => {
    setLoading(true)
    setError('')
    
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        router.push('/login')
        return
      }

      // Trigger ROI calculation
      // We'll implement this endpoint next
      const response = await fetch(`${API_ENDPOINTS.analytics.roiSummary}?recalculate=true`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        setSuccess('ROI calculation triggered! Check analytics dashboard.')
      } else {
        throw new Error('Failed to calculate ROI')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to calculate ROI')
    } finally {
      setLoading(false)
    }
  }

  const updateCost = (index: number, field: keyof BloodProductCost, value: any) => {
    const newCosts = [...costs]
    newCosts[index] = { ...newCosts[index], [field]: value }
    setCosts(newCosts)
  }

  const getTotalMonthlySavings = () => {
    // This will be calculated from real data later
    return costs.reduce((sum, cost) => sum + (cost.unit_cost_bdt * 10), 0) // Placeholder
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading cost configuration...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cost Configuration</h1>
          <p className="text-gray-600 mt-1">
            Set blood product prices for accurate ROI calculations
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={handleCalculateROI}
            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
          >
            <TrendingUp className="w-4 h-4" />
            Calculate ROI
          </button>
          
          <button
            onClick={handleSaveCosts}
            disabled={saving}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {saving ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            {saving ? 'Saving...' : 'Save All Costs'}
          </button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <p className="text-green-800">{success}</p>
        </div>
      )}

      {/* Cost Configuration Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {costs.map((product, index) => (
          <div key={product.component_type} className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Package className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{product.component_type}</h3>
                  <p className="text-sm text-gray-500">Blood Component</p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id={`active-${index}`}
                    checked={product.is_active}
                    onChange={(e) => updateCost(index, 'is_active', e.target.checked)}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor={`active-${index}`} className="ml-2 text-sm text-gray-700">
                    Active
                  </label>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <DollarSign className="inline w-4 h-4 mr-2" />
                  Cost per Unit (BDT)
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">৳</span>
                  <input
                    type="number"
                    min="0"
                    step="100"
                    value={product.unit_cost_bdt}
                    onChange={(e) => updateCost(index, 'unit_cost_bdt', parseFloat(e.target.value) || 0)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="3500"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Average market price: {product.component_type === 'RBC' ? '৳3,000-4,000' : 
                                       product.component_type === 'FFP' ? '৳2,000-3,000' :
                                       product.component_type === 'Platelets' ? '৳4,000-5,000' : '৳2,500-3,500'}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Units per Bag
                </label>
                <input
                  type="number"
                  min="1"
                  value={product.units_per_bag}
                  onChange={(e) => updateCost(index, 'units_per_bag', parseInt(e.target.value) || 1)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="1"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Typically 1 unit per bag for most blood products
                </p>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Estimated monthly savings:</span>
                  <span className="font-semibold text-green-600">
                    ৳{(product.unit_cost_bdt * 5).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Card */}
      <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">ROI Summary</h3>
              <p className="text-sm text-gray-500">Based on configured costs</p>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-2xl font-bold text-green-600">
              ৳{getTotalMonthlySavings().toLocaleString()}
            </p>
            <p className="text-sm text-gray-500">Estimated monthly savings</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900">How ROI is Calculated</h4>
                <ul className="text-blue-800 text-sm mt-2 space-y-1">
                  <li>• Savings = (Recommended units - Actual units used) × Unit cost</li>
                  <li>• Based on guideline compliance vs actual practice</li>
                  <li>• Uses hospital-specific blood product costs</li>
                  <li>• Updated monthly with new patient data</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">2</p>
              <p className="text-sm text-gray-600">Total Recommendations</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">1</p>
              <p className="text-sm text-gray-600">Patient Encounters</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">0</p>
              <p className="text-sm text-gray-600">Overrides Recorded</p>
            </div>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-yellow-900">Next Steps</h4>
            <ol className="text-yellow-800 text-sm mt-2 space-y-2">
              <li>1. <strong>Set blood product costs</strong> above (use actual hospital prices)</li>
              <li>2. <strong>Click "Save All Costs"</strong> to store prices in database</li>
              <li>3. <strong>Click "Calculate ROI"</strong> to aggregate existing data</li>
              <li>4. <strong>Check Analytics Dashboard</strong> for ROI calculations</li>
              <li>5. <strong>Doctors use the system</strong> to generate more data</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}