'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Printer, 
  Download, 
  FileText,
  AlertCircle,
  Calendar
} from 'lucide-react'

// --- Interfaces ---

interface MonthlyTrend {
  month: string
  encounters: number
  recommendations: number
  compliance_rate: number
  savings_bdt: number
}

interface ComponentUsageStats {
  recommendations_count: number
  recommended_units: number
  actual_units: number
  overrides_count: number
  common_override_reasons: string[]
}

interface ComponentUsageResponse {
  hospital_id: number
  period_start: string
  period_end: string
  component_stats: {
    [key: string]: ComponentUsageStats
  }
  total_recommendations: number
  total_overrides: number
  override_rate: number
}

interface HospitalROIResponse {
  hospital_id: number
  period_months: number
  total_encounters: number
  total_recommendations: number
  compliance_rate: number
  estimated_total_savings_bdt: number
  estimated_monthly_savings_bdt: number
  component_usage: {
    [key: string]: {
      recommended: number
      actual: number
    }
  }
  monthly_trends: MonthlyTrend[]
}

export default function ReportsPage() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [roiData, setRoiData] = useState<HospitalROIResponse | null>(null)
  const [usageData, setUsageData] = useState<ComponentUsageResponse | null>(null)
  const [generatedDate, setGeneratedDate] = useState<string>('')

  useEffect(() => {
    fetchReportData()
  }, [])

  const fetchReportData = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

      if (!token) {
        throw new Error('No authentication token found. Please login.')
      }

      const headers = { Authorization: `Bearer ${token}` }

      // Parallel requests for summary and usage details
      // By default asking for 6 months ROI summary
      const roiPromise = axios.get(`${apiUrl}/api/v1/analytics/roi-summary?months=6`, { headers })
      const usagePromise = axios.get(`${apiUrl}/api/v1/analytics/component-usage`, { headers })

      const [roiRes, usageRes] = await Promise.all([roiPromise, usagePromise])

      setRoiData(roiRes.data)
      setUsageData(usageRes.data)
      setGeneratedDate(new Date().toLocaleDateString('en-US', { 
        year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' 
      }))
      setError(null)

    } catch (err: any) {
      console.error('Failed to fetch report data:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load report data.')
    } finally {
      setLoading(false)
    }
  }

  const handlePrint = () => {
    window.print()
  }

  if (loading) {
    return (
      <div className="h-96 flex flex-col items-center justify-center space-y-4">
        <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-500 font-medium">Generating Comprehensive Report...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-bold text-red-800 mb-2">Error Loading Report</h3>
        <p className="text-red-600 mb-4">{error}</p>
        <button 
          onClick={fetchReportData}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in pb-12 print:p-0 print:max-w-none">
      
      {/* Action Bar - Hidden when printing */}
      <div className="flex justify-between items-center print:hidden">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Hospital Analytics Report</h1>
          <p className="text-gray-500">Comprehensive utilization and efficiency audit</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={fetchReportData}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            {/* Refresh Icon */}
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg>
            <span>Refresh</span>
          </button>
          <button 
            onClick={handlePrint}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-sm"
          >
            <Printer className="h-5 w-5" />
            <span>Print / Save PDF</span>
          </button>
        </div>
      </div>

      {/* Report Container */}
      <div className="bg-white p-8 md:p-12 shadow-sm border print:shadow-none print:border-none print:p-0">
        
        {/* Report Header */}
        <div className="border-b pb-8 mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Confidential Analytics Report</h1>
              <p className="text-gray-500 mt-2">Blood Product Management & Utilization Audit</p>
            </div>
            <div className="text-right">
              <div className="inline-flex items-center px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-600 mb-2">
                <Calendar className="h-4 w-4 mr-2" />
                {generatedDate}
              </div>
              <p className="text-sm text-gray-400">Report ID: #{Math.floor(Math.random() * 1000000)}</p>
            </div>
          </div>
        </div>

        {/* Executive Summary */}
        <section className="mb-10">
          <h3 className="text-lg font-bold text-gray-900 uppercase tracking-wider mb-6 border-l-4 border-blue-600 pl-3">
            Executive Summary (Last {roiData?.period_months} Months)
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <SummaryStat 
              label="Total Recommendations" 
              value={roiData?.total_recommendations.toLocaleString()} 
            />
             <SummaryStat 
              label="Guideline Compliance" 
              value={`${roiData?.compliance_rate}%`} 
              highlight={roiData && roiData.compliance_rate > 90}
            />
            <SummaryStat 
              label="Est. Total Savings" 
              value={`৳${roiData?.estimated_total_savings_bdt.toLocaleString()}`} 
              subtext={`Avg ৳${roiData?.estimated_monthly_savings_bdt.toLocaleString()}/mo`}
            />
            <SummaryStat 
              label="Override Rate" 
              value={`${usageData?.override_rate.toFixed(1)}%`} 
              highlight={usageData && usageData.override_rate < 5}
            />
          </div>
        </section>


        {/* Component Usage Details */}
        <section className="mb-10 page-break-inside-avoid">
           <h3 className="text-lg font-bold text-gray-900 uppercase tracking-wider mb-6 border-l-4 border-blue-600 pl-3">
            Component Utilization Breakdown
          </h3>
          <div className="overflow-hidden border rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Component</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Rec. Units</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Actual Use (Est)</th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Overrides</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Common Override Reasons</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(usageData?.component_stats || {}).map(([key, stats]) => (
                  <tr key={key}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{key}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">{stats.recommended_units}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">{stats.actual_units}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-red-600 font-medium">{stats.overrides_count}</td>
                    <td className="px-6 py-4 text-sm text-gray-500 italic">
                      {stats.common_override_reasons.length > 0 
                        ? stats.common_override_reasons.join(', ') 
                        : 'N/A'
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Monthly Trends Table */}
        <section className="mb-8 page-break-inside-avoid">
           <h3 className="text-lg font-bold text-gray-900 uppercase tracking-wider mb-6 border-l-4 border-blue-600 pl-3">
            Monthly Performance Trends
          </h3>
          <div className="overflow-hidden border rounded-lg">
             <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Month</th>
                  <th className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase">Encounters</th>
                  <th className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase">Recommendations</th>
                  <th className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase">Compliance</th>
                  <th className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase">Est. Savings</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {roiData?.monthly_trends.map((trend) => (
                  <tr key={trend.month}>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{trend.month}</td>
                    <td className="px-6 py-4 text-sm text-right text-gray-500">{trend.encounters}</td>
                    <td className="px-6 py-4 text-sm text-right text-gray-500">{trend.recommendations}</td>
                    <td className="px-6 py-4 text-sm text-right text-gray-900">
                      <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                        trend.compliance_rate >= 90 ? 'bg-green-100 text-green-800' : 
                        trend.compliance_rate >= 70 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {trend.compliance_rate}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-right text-green-600 font-medium">
                      ৳{trend.savings_bdt.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
             </table>
          </div>
        </section>

        {/* Footer */}
        <div className="mt-16 pt-8 border-t text-center text-xs text-gray-400">
          <p>Generated by TransfusionIQ Clinical Decision Support System</p>
          <p>Confidential Medical Record Audit - Not for external distribution</p>
        </div>

      </div>
    </div>
  )
}

function SummaryStat({ label, value, subtext, highlight }: any) {
  let valueColor = 'text-gray-900'
  if (highlight === true) valueColor = 'text-green-600'
  if (highlight === false) {} // Default
  // We can add logic for 'bad' highlights if needed

  return (
    <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
      <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className={`text-2xl font-bold ${valueColor}`}>{value}</p>
      {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
    </div>
  )
}
