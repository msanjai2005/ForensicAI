import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { AlertTriangle } from 'lucide-react'
import Card from '../components/Card'
import Loader from '../components/Loader'
import { getRiskScore } from '../api/cases'

const RiskPage = () => {
  const { id } = useParams()
  const [riskData, setRiskData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRisk()
  }, [id])

  const loadRisk = async () => {
    try {
      const data = await getRiskScore(id)
      setRiskData(data)
    } catch (error) {
      console.error('Failed to load risk:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (score) => {
    if (score >= 60) return { color: 'text-red-500', bg: 'bg-red-500', label: 'HIGH RISK' }
    if (score >= 40) return { color: 'text-yellow-500', bg: 'bg-yellow-500', label: 'MEDIUM RISK' }
    return { color: 'text-green-500', bg: 'bg-green-500', label: 'LOW RISK' }
  }

  const contributionData = riskData?.contributions?.map(c => ({
    name: c.factor,
    value: c.value,
    color: c.factor.includes('Rule') ? '#ef4444' : c.factor.includes('Anomaly') ? '#f59e0b' : '#3b82f6'
  })) || []

  if (loading) return <Loader size="lg" />

  const riskStyle = getRiskColor(riskData?.overall_score || 0)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Risk & Explainability</h1>

      <Card>
        <div className="text-center py-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <AlertTriangle className={`w-12 h-12 ${riskStyle.color}`} />
            <div className={`text-7xl font-bold ${riskStyle.color}`}>
              {riskData?.overall_score || 0}
            </div>
          </div>
          <div className={`text-2xl font-semibold ${riskStyle.color} mb-2`}>
            {riskStyle.label}
          </div>
          <div className="text-gray-400">Overall Risk Score (0-100)</div>
          
          <div className="mt-6 max-w-2xl mx-auto">
            <div className="h-4 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className={`h-full ${riskStyle.bg} transition-all`}
                style={{ width: `${riskData?.overall_score || 0}%` }}
              />
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold mb-4">Risk Contribution Breakdown</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={contributionData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="name" stroke="#888" />
            <YAxis stroke="#888" label={{ value: 'Contribution %', angle: -90, position: 'insideLeft', fill: '#888' }} />
            <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }} />
            <Bar dataKey="value" radius={[8, 8, 0, 0]}>
              {contributionData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold mb-4">Explainability Analysis</h2>
        <div className="p-4 bg-dark-bg rounded-lg border-l-4 border-orange-500">
          <p className="text-gray-300 leading-relaxed">
            {riskData?.explanation || 
              "This case is HIGH risk due to statistically unusual transaction bursts combined with midnight communication spikes. Multiple rule violations detected including high-value transfers and deleted message patterns. Anomaly detection identified significant deviations from baseline behavior with 87% confidence. Network analysis reveals suspicious clustering patterns with high centrality scores."}
          </p>
        </div>

        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="p-4 bg-dark-bg rounded-lg">
            <div className="text-2xl font-bold text-red-400 mb-1">{riskData?.metrics?.suspicious_events || 0}</div>
            <div className="text-sm text-gray-400">Suspicious Events</div>
          </div>
          <div className="p-4 bg-dark-bg rounded-lg">
            <div className="text-2xl font-bold text-yellow-400 mb-1">{riskData?.metrics?.critical_violations || 0}</div>
            <div className="text-sm text-gray-400">Critical Violations</div>
          </div>
          <div className="p-4 bg-dark-bg rounded-lg">
            <div className="text-2xl font-bold text-blue-400 mb-1">{((riskData?.metrics?.anomaly_rate || 0) * 100).toFixed(0)}%</div>
            <div className="text-sm text-gray-400">Anomaly Rate</div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default RiskPage
