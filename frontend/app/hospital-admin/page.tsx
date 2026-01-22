'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import axios from 'axios'
import { 
  TrendingUp, 
  DollarSign, 
  CheckCircle, 
  AlertTriangle,
  Users,
  Calendar,
  RefreshCw,
  ArrowRight,
  Activity,
  Droplet
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

// --- Interfaces ---

interface ROIResponse {
  hospital_id: number
  period_months: number
  total_encounters: number
  total_recommendations: number
  compliance_rate: number
  estimated_total_savings_bdt: number
  estimated_monthly_savings_bdt: number
  component_usage: {
    [key: string]: { recommended: number; actual: number }
  }
  monthly_trends: Array<{
    month: string
    encounters: number
    recommendations: number
    compliance_rate: number
    savings_bdt: number
  }>
}

interface UserResponse {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
}

export default function HospitalAdminDashboard() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [roiData, setRoiData] = useState<ROIResponse | null>(null)
  const [staffCount, setStaffCount] = useState<number>(0)
  const [selectedPeriod, setSelectedPeriod] = useState(6)

  useEffect(() => {
    fetchDashboardData()
  }, [selectedPeriod])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

      if (!token) {
        router.push('/login')
        return
      }

      const headers = { Authorization: `Bearer ${token}` }

      // Parallel data fetching for speed
      const [roiRes, usersRes] = await Promise.all([
        axios.get(`${apiUrl}/api/v1/analytics/roi-summary?months=${selectedPeriod}`, { headers }),
        axios.get(`${apiUrl}/api/v1/hospital-admin/users`, { headers })
      ])

      setRoiData(roiRes.data)
      // Count active staff
      const activeUsers = usersRes.data.filter((u: UserResponse) => u.is_active).length
      setStaffCount(activeUsers)
      setError(null)

    } catch (err: any) {
      console.error('Dashboard data fetch failed:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-BD', {
      style: 'currency',
      currency: 'BDT',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  if (loading) {
    return <DashboardSkeleton />
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-red-50 p-6 rounded-xl border border-red-200 text-center max-w-md">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-red-800">Data Load Error</h3>
          <p className="text-red-600 mb-6">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 w-full"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
          <p className="text-gray-500">Real-time insights and performance metrics.</p>
        </div>
        
        <div className="flex items-center gap-3">
           <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-lg border shadow-sm">
            <Calendar className="w-4 h-4 text-gray-500" />
            <select 
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(parseInt(e.target.value))}
              className="bg-transparent border-none outline-none text-sm text-gray-700 cursor-pointer focus:ring-0"
            >
              <option value={3}>Last 3 months</option>
              <option value={6}>Last 6 months</option>
              <option value={12}>Last 12 months</option>
            </select>
          </div>
          <button 
            onClick={fetchDashboardData}
            className="p-2 bg-white text-gray-600 border rounded-lg hover:bg-gray-50 shadow-sm transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KpiCard 
          title="Est. Total Savings"
          value={roiData ? formatCurrency(roiData.estimated_total_savings_bdt) : '-'}
          subtext={`Avg ${roiData ? formatCurrency(roiData.estimated_monthly_savings_bdt) : '-'}/mo`}
          icon={DollarSign}
          color="green"
        />
        <KpiCard 
          title="Guideline Compliance"
          value={roiData ? `${roiData.compliance_rate.toFixed(1)}%` : '-'}
          subtext={`${roiData?.total_recommendations} total recommendations`}
          icon={CheckCircle}
          color="blue"
        />
        <KpiCard 
          title="Units Recommended"
          value={roiData ? Object.values(roiData.component_usage).reduce((acc, curr) => acc + curr.recommended, 0).toLocaleString() : '-'}
          subtext="Total blood products"
          icon={Droplet}
          color="red"
        />
        <KpiCard 
          title="Active Staff"
          value={staffCount.toString()}
          subtext="Doctors & Admins"
          icon={Users}
          color="purple"
        />
      </div>

      {/* Visual Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Trend Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-gray-500" />
              Savings & Activity Trend
            </h3>
            <Link href="/hospital-admin/reports" className="text-sm text-blue-600 hover:text-blue-800 flex items-center">
              View Report <ArrowRight className="h-4 w-4 ml-1" />
            </Link>
          </div>
          
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={roiData?.monthly_trends}>
                <defs>
                  <linearGradient id="colorSavings" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRecs" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#9CA3AF', fontSize: 12}} dy={10} />
                <YAxis yAxisId="left" axisLine={false} tickLine={false} tick={{fill: '#9CA3AF', fontSize: 12}} />
                <YAxis yAxisId="right" orientation="right" axisLine={false} tickLine={false} tick={{fill: '#9CA3AF', fontSize: 12}} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  labelStyle={{ fontWeight: 'bold', color: '#111827' }}
                />
                <Area 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="savings_bdt" 
                  name="Savings (BDT)" 
                  stroke="#10B981" 
                  fillOpacity={1} 
                  fill="url(#colorSavings)" 
                  strokeWidth={2}
                />
                 <Area 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="recommendations" 
                  name="Recommendations" 
                  stroke="#3B82F6" 
                  fillOpacity={1} 
                  fill="url(#colorRecs)" 
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Actions / Status */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-6 rounded-xl shadow-md text-white">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-bold text-lg">System Status</h3>
                <p className="text-blue-100 text-sm mt-1">AI Recommendation Engine</p>
              </div>
              <div className="p-2 bg-white/20 rounded-lg">
                <Activity className="h-6 w-6 text-white" />
              </div>
            </div>
            <div className="mt-8">
              <div className="flex items-center gap-2">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
                <span className="font-medium">Operational</span>
              </div>
              <p className="text-xs text-blue-200 mt-2">Running latest clinical guidelines (v2.1)</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border shadow-sm">
             <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
             <div className="space-y-3">
               <Link 
                href="/hospital-admin/reports" 
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors group"
               >
                 <span className="text-sm font-medium text-gray-700">Generate Audit Report</span>
                 <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-blue-600" />
               </Link>
               <Link 
                href="/hospital-admin/users" 
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors group"
               >
                 <span className="text-sm font-medium text-gray-700">Manage Staff Access</span>
                 <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-blue-600" />
               </Link>
               <Link 
                href="/hospital-admin/costs" 
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors group"
               >
                 <span className="text-sm font-medium text-gray-700">Update Unit Costs</span>
                 <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-blue-600" />
               </Link>
             </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function KpiCard({ title, value, subtext, icon: Icon, color }: any) {
  const colorMap = {
    green: 'bg-green-50 text-green-600',
    blue: 'bg-blue-50 text-blue-600',
    red: 'bg-red-50 text-red-600',
    purple: 'bg-purple-50 text-purple-600'
  }

  return (
    <div className="bg-white p-6 rounded-xl border shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <h4 className="text-2xl font-bold text-gray-900 mt-1">{value}</h4>
        </div>
        <div className={`p-2 rounded-lg ${colorMap[color as keyof typeof colorMap]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      <p className="text-xs text-gray-400 font-medium">{subtext}</p>
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div className="space-y-8 animate-pulse p-1">
      <div className="h-8 w-64 bg-gray-200 rounded mb-8"></div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white h-32 rounded-xl border border-gray-100 p-6">
            <div className="flex justify-between">
              <div className="h-10 w-24 bg-gray-100 rounded"></div>
              <div className="h-10 w-10 bg-gray-100 rounded"></div>
            </div>
            <div className="h-6 w-16 bg-gray-100 rounded mt-4"></div>
          </div>
        ))}
      </div>

       <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white h-96 rounded-xl border border-gray-100"></div>
          <div className="bg-white h-96 rounded-xl border border-gray-100"></div>
       </div>
    </div>
  )
}