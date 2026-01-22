'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, Cell, PieChart, Pie } from 'recharts';
import { TrendingUp, Users, Activity, Banknote, Award } from 'lucide-react';

interface AnalyticsData {
  total_savings_bdt: number;
  avg_compliance_rate: number;
  total_patient_encounters: number;
  total_recommendations: number;
  monthly_trends: {
    month: string;
    savings: number;
    compliance: number;
    encounters: number;
  }[];
  component_distribution: {
    name: string;
    value: number;
  }[];
}

interface LeaderboardItem {
  id: number;
  name: string;
  total_encounters: number;
  total_savings: number;
  compliance_rate: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function SuperAdminAnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState("6");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };

        const [analyticsRes, leaderboardRes] = await Promise.all([
          axios.get(`http://localhost:8000/api/v1/super-admin/analytics/global?months=${period}`, { headers }),
          axios.get('http://localhost:8000/api/v1/super-admin/analytics/leaderboard', { headers })
        ]);

        setData(analyticsRes.data);
        setLeaderboard(leaderboardRes.data);
      } catch (error) {
        console.error("Error fetching analytics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [period]);

  if (loading) {
    return <div className="p-8 flex justify-center text-gray-500">Loading analytics...</div>;
  }

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">System Analytics</h1>
          <p className="text-slate-500">Global performance overview across all hospitals</p>
        </div>
        <Select value={period} onValueChange={setPeriod}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select period" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="3">Last 3 Months</SelectItem>
            <SelectItem value="6">Last 6 Months</SelectItem>
            <SelectItem value="12">Last 12 Months</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">Total Estimated Savings</CardTitle>
            <Banknote className="h-4 w-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">BDT {data?.total_savings_bdt.toLocaleString()}</div>
            <p className="text-xs text-slate-500">System-wide cost reduction</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">Avg Compliance Rate</CardTitle>
            <Award className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.avg_compliance_rate}%</div>
            <p className="text-xs text-slate-500">Adherence to guidelines</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">Total Encounters</CardTitle>
            <Activity className="h-4 w-4 text-indigo-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.total_patient_encounters.toLocaleString()}</div>
            <p className="text-xs text-slate-500">Filtered patient encounters</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">Total Recommendations</CardTitle>
            <TrendingUp className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.total_recommendations.toLocaleString()}</div>
            <p className="text-xs text-slate-500">Generated treatment plans</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-7 gap-6">
        {/* Main Chart */}
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Savings & Compliance Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data?.monthly_trends}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="month" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis yAxisId="left" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `BDT ${value/1000}k`} />
                  <YAxis yAxisId="right" orientation="right" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} unit="%" />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="savings" name="Savings (BDT)" stroke="#10B981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line yAxisId="right" type="monotone" dataKey="compliance" name="Compliance %" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Distribution Chart */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Transfusion Type Mix</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data?.component_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    fill="#8884d8"
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {data?.component_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend layout="horizontal" verticalAlign="bottom" align="center" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Leaderboard */}
      <Card>
        <CardHeader>
          <CardTitle>Hospital Performance Leaderboard</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {leaderboard.map((hospital, index) => (
              <div key={hospital.id} className="flex items-center justify-between p-4 bg-white border rounded-lg hover:shadow-sm transition-shadow">
                <div className="flex items-center gap-4">
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${index < 3 ? 'bg-yellow-100 text-yellow-700' : 'bg-slate-100 text-slate-600'}`}>
                    {index + 1}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">{hospital.name}</h3>
                    <p className="text-sm text-slate-500">{hospital.total_encounters} encounters processed</p>
                  </div>
                </div>
                <div className="flex gap-8 text-right">
                  <div>
                    <p className="text-sm text-slate-500">Compliance</p>
                    <p className={`font-semibold ${hospital.compliance_rate >= 80 ? 'text-green-600' : 'text-amber-600'}`}>
                      {hospital.compliance_rate}%
                    </p>
                  </div>
                  <div className="min-w-[120px]">
                    <p className="text-sm text-slate-500">Savings</p>
                    <p className="font-semibold text-slate-900">BDT {hospital.total_savings.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            ))}
             {leaderboard.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No hospital data available yet.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
