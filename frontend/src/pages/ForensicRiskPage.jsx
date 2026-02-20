import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Shield, AlertTriangle, CheckCircle, Info } from 'lucide-react'
import Card from '../components/Card'
import Badge from '../components/Badge'
import Loader from '../components/Loader'
import axios from 'axios'

const ForensicRiskPage = () => {
  const { id } = useParams()
  const [riskData, setRiskData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRisk()
  }, [id])

  const loadRisk = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/cases/${id}/forensic-risk`)
      setRiskData(response.data)
    } catch (error) {
      console.error('Failed to load forensic risk:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: 'text-red-500',
      HIGH: 'text-orange-500',
      MEDIUM: 'text-yellow-500',
      LOW: 'text-green-500'
    }
    return colors[severity] || 'text-gray-500'
  }

  const getSeverityBadge = (severity) => {
    const variants = {
      critical: 'danger',
      high: 'warning',
      medium: 'info',
      low: 'success'
    }
    return variants[severity] || 'default'
  }

  const getCategoryIcon = (category) => {
    if (category === 'Rule Detection') return <AlertTriangle className="w-5 h-5 text-red-400" />
    if (category === 'Correlation') return <Shield className="w-5 h-5 text-orange-400" />
    if (category === 'Anomaly Detection') return <Info className="w-5 h-5 text-yellow-400" />
    if (category === 'Network Analysis') return <CheckCircle className="w-5 h-5 text-blue-400" />
    return <Info className="w-5 h-5 text-gray-400" />
  }

  if (loading) return <Loader size="lg" />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Forensic Risk Assessment</h1>
        <Badge variant={getSeverityBadge(riskData?.severity?.toLowerCase())}>
          {riskData?.severity}
        </Badge>
      </div>

      {/* Risk Score Card */}
      <Card>
        <div className="text-center py-8">
          <div className="mb-4">
            <Shield className={`w-20 h-20 mx-auto ${getSeverityColor(riskData?.severity)}`} />
          </div>
          <div className="text-6xl font-bold mb-2">
            <span className={getSeverityColor(riskData?.severity)}>
              {riskData?.risk_score_100 || 0}
            </span>
            <span className="text-2xl text-gray-400">/100</span>
          </div>
          <div className="text-xl text-gray-400 mb-4">Overall Risk Score</div>
          <div className="text-sm text-gray-500">{riskData?.summary}</div>
        </div>

        {/* Risk Bar */}
        <div className="mt-6">
          <div className="w-full bg-gray-700 rounded-full h-4">
            <div 
              className={`h-4 rounded-full transition-all ${
                riskData?.severity === 'CRITICAL' ? 'bg-red-500' :
                riskData?.severity === 'HIGH' ? 'bg-orange-500' :
                riskData?.severity === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${riskData?.risk_score_100 || 0}%` }}
            />
          </div>
        </div>
      </Card>

      {/* Justifications */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Risk Justifications</h2>
        <div className="space-y-4">
          {riskData?.justifications?.length === 0 ? (
            <p className="text-center text-gray-400 py-8">No risk indicators found</p>
          ) : (
            riskData?.justifications?.map((item, idx) => (
              <div 
                key={idx} 
                className="flex items-start gap-4 p-4 bg-dark-bg rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
              >
                <div className="mt-1">
                  {getCategoryIcon(item.category)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold">{item.type}</h3>
                      <Badge variant={getSeverityBadge(item.severity)}>
                        {item.severity}
                      </Badge>
                    </div>
                    <span className="text-sm font-mono text-orange-400">
                      +{item.score.toFixed(1)} points
                    </span>
                  </div>
                  <p className="text-sm text-gray-400">{item.description}</p>
                  <div className="mt-2 text-xs text-gray-500">
                    Category: {item.category}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400 mb-2">
              {riskData?.justifications?.length || 0}
            </div>
            <div className="text-sm text-gray-400">Total Indicators</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-400 mb-2">
              {riskData?.total_points?.toFixed(1) || 0}
            </div>
            <div className="text-sm text-gray-400">Total Points</div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400 mb-2">
              {riskData?.justifications?.filter(j => j.severity === 'critical' || j.severity === 'high').length || 0}
            </div>
            <div className="text-sm text-gray-400">High Priority</div>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default ForensicRiskPage
