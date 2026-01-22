// frontend/app/hospital-admin/analytics/page.tsx
'use client'

import { useState } from 'react'
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import { 
  TrendingUp, 
  AlertCircle, 
  Droplet,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  Activity
} from 'lucide-react'

// Mock Data
const usageData = [
  { month: 'Jan', rbc: 450, platelets: 200, plasma: 150 },
  { month: 'Feb', rbc: 420, platelets: 210, plasma: 160 },
  { month: 'Mar', rbc: 480, platelets: 250, plasma: 140 },
  { month: 'Apr', rbc: 510, platelets: 230, plasma: 180 },
  { month: 'May', rbc: 490, platelets: 240, plasma: 190 },
  { month: 'Jun', rbc: 550, platelets: 280, plasma: 210 },
]

const deptEfficiencyData = [
  { name: 'Surgery', ratio: 1.8, target: 2.0 },
  { name: 'ICU', ratio: 2.4, target: 2.0 },
  { name: 'ER', ratio: 3.1, target: 2.5 },
  { name: 'Oncology', ratio: 1.2, target: 1.5 },
  { name: 'Ob/Gyn', ratio: 1.5, target: 2.0 },
]

const wastageData = [
  { name: 'Expired', value: 45, color: '#EF4444' }, // Red
  { name: 'Temp Excursion', value: 25, color: '#F59E0B' }, // Amber
  { name: 'Handling', value: 15, color: '#3B82F6' }, // Blue
  { name: 'Other', value: 15, color: '#6B7280' }, // Gray
]

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('6m')

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics Overview</h2>
          <p className="text-gray-500">Monitor usage trends, efficiency, and wastage metrics.</p>
        </div>
        <div className="flex bg-white rounded-lg border shadow-sm p-1">
          {['1m', '3m', '6m', '1y'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                timeRange === range
                  ? 'bg-blue-50 text-blue-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {range.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KpiCard
          title="Total Transfusions"
          value="2,845"
          change="+12.5%"
          trend="up"
          icon={Droplet}
          color="blue"
        />
        <KpiCard
          title="Avg C:T Ratio"
          value="2.1"
          change="-0.3"
          trend="down"
          trendLabel="Improved"
          icon={Activity}
          color="green"
        />
        <KpiCard
          title="Wastage Rate"
          value="3.2%"
          change="+0.4%"
          trend="up"
          trendLabel="worsened"
          icon={AlertCircle}
          color="red"
        />
        <KpiCard
          title="Est. Cost Savings"
          value="$14.2k"
          change="+8.1%"
          trend="up"
          icon={DollarSign}
          color="emerald"
        />
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Usage Trends */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-900">Blood Product Usage Trends</h3>
            <span className="text-sm text-gray-500">Last 6 Months</span>
          </div>
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={usageData}>
                <defs>
                  <linearGradient id="colorRbc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorPlatelets" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#6B7280'}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#6B7280'}} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend iconType="circle" />
                <Area 
                  type="monotone" 
                  dataKey="rbc" 
                  name="RBC Units" 
                  stroke="#EF4444" 
                  fillOpacity={1} 
                  fill="url(#colorRbc)" 
                  strokeWidth={2}
                />
                <Area 
                  type="monotone" 
                  dataKey="platelets" 
                  name="Platelets" 
                  stroke="#F59E0B" 
                  fillOpacity={1} 
                  fill="url(#colorPlatelets)" 
                  strokeWidth={2}
                />
                <Area 
                  type="monotone" 
                  dataKey="plasma" 
                  name="Plasma" 
                  stroke="#3B82F6" 
                  fillOpacity={1} 
                  fill="#EBF5FF" 
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Wastage Breakdown */}
        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-6">Wastage by Reason</h3>
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={wastageData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={110}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {wastageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend 
                  layout="horizontal" 
                  verticalAlign="bottom" 
                  align="center"
                  wrapperStyle={{ paddingTop: '20px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Secondary Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department Efficiency */}
        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-900">Crossmatch to Transfusion (C:T) Ratio</h3>
            <span className="text-sm text-gray-500">By Department</span>
          </div>
          <div className="h-[300px]">
             <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptEfficiencyData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E5E7EB" />
                <XAxis type="number" domain={[0, 4]} axisLine={false} tickLine={false} />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} width={80} />
                <Tooltip 
                   cursor={{fill: '#F3F4F6'}}
                   contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend />
                <Bar dataKey="ratio" name="Current Ratio" fill="#3B82F6" radius={[0, 4, 4, 0]} barSize={20} />
                <Bar dataKey="target" name="Target Ratio" fill="#E5E7EB" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Alerts / Insights */}
        <div className="bg-white p-6 rounded-xl border shadow-sm">
           <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-900">AI Insights & Alerts</h3>
            <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">New</span>
          </div>
          <div className="space-y-4">
            <InsightItem 
              type="warning" 
              message="ER C:T Ratio exceeded 3.0 for 3 consecutive days." 
              time="2 hours ago"
            />
            <InsightItem 
              type="success" 
              message="Wastage due to expiration dropped by 5% this month." 
              time="1 day ago"
            />
            <InsightItem 
              type="info" 
              message="O-Negative inventory levels are optimal." 
              time="2 days ago"
            />
             <InsightItem 
              type="warning" 
              message="Platelet utilization in Oncology showing unusual spike." 
              time="3 days ago"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function KpiCard({ title, value, change, trend, trendLabel, icon: Icon, color }: any) {
  const isPositive = trend === 'up'
  // Logic for "worsened" metrics where up is bad
  
  // Correction: If trendLabel is 'worsened', then 'up' is BAD (red).
  // If trendLabel is 'Improved', then 'down' (for ratio) is GOOD (green).
  
  // Let's simplify color logic for visual clarity
  const trendColor = trend === 'up' 
    ? (trendLabel === 'worsened' ? 'text-red-600' : 'text-green-600')
    : (trendLabel === 'Improved' ? 'text-green-600' : 'text-red-600')

  const TrendIcon = trend === 'up' ? ArrowUpRight : ArrowDownRight

  return (
    <div className="bg-white p-6 rounded-xl border shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <h4 className="text-2xl font-bold text-gray-900 mt-1">{value}</h4>
        </div>
        <div className={`p-2 rounded-lg bg-${color}-50`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
      </div>
      <div className="flex items-center mt-4">
        <span className={`flex items-center text-sm font-medium ${trendColor}`}>
          <TrendIcon className="h-4 w-4 mr-1" />
          {change}
        </span>
        <span className="text-sm text-gray-500 ml-2">vs last month</span>
      </div>
    </div>
  )
}

function InsightItem({ type, message, time }: any) {
  const styles = {
    warning: { bg: 'bg-amber-50', border: 'border-amber-200', icon: AlertCircle, color: 'text-amber-600' },
    success: { bg: 'bg-green-50', border: 'border-green-200', icon: TrendingUp, color: 'text-green-600' },
    info: { bg: 'bg-blue-50', border: 'border-blue-200', icon: Activity, color: 'text-blue-600' }
  }
  
  const style = styles[type as keyof typeof styles]
  const Icon = style.icon

  return (
    <div className={`flex gap-3 p-3 rounded-lg border ${style.bg} ${style.border}`}>
      <Icon className={`h-5 w-5 shrink-0 ${style.color} mt-0.5`} />
      <div>
        <p className="text-sm text-gray-800">{message}</p>
        <p className="text-xs text-gray-500 mt-1">{time}</p>
      </div>
    </div>
  )
}
