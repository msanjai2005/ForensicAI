import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Play, Clock } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import Card from '../components/Card'
import Table from '../components/Table'
import Badge from '../components/Badge'
import Loader from '../components/Loader'
import { runAnomalyDetection, getAnomalyResults } from '../api/cases'

const AnomalyPage = () => {
  const { id } = useParams()
  const [anomalyData, setAnomalyData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)

  useEffect(() => {
    loadAnomalies()
  }, [id])

  const loadAnomalies = async () => {
    try {
      const data = await getAnomalyResults(id)
      setAnomalyData(data)
    } catch (error) {
      console.error('Failed to load anomalies:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRunAnalysis = async () => {
    setRunning(true)
    try {
      await runAnomalyDetection(id)
      await loadAnomalies()
    } catch (error) {
      console.error('Failed to run analysis:', error)
    } finally {
      setRunning(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-red-500'
    if (score >= 40) return 'text-yellow-500'
    return 'text-green-500'
  }

  const chartData = anomalyData?.baseline_comparison?.map(item => ({
    metric: item.metric,
    baseline: item.baseline,
    current: item.current
  })) || []

  const columns = [
    { header: 'Timestamp', accessor: 'timestamp', render: (row) => new Date(row.timestamp).toLocaleString() },
    { header: 'Deviation Score', accessor: 'deviation_score', render: (row) => `${(row.deviation_score * 100).toFixed(0)}%` },
    { header: 'Description', accessor: 'description' }
  ]

  if (loading) return <Loader size="lg" />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Anomaly Detection</h1>
        <button onClick={handleRunAnalysis} disabled={running} className="btn-primary flex items-center gap-2">
          <Play className="w-4 h-4" />
          {running ? 'Running...' : 'Run Analysis'}
        </button>
      </div>

      {anomalyData && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <Card className="col-span-1">
              <div className="text-center">
                <h3 className="text-sm text-gray-400 mb-4">Anomaly Score</h3>
                <div className={`text-6xl font-bold mb-2 ${getScoreColor(anomalyData.score)}`}>
                  {anomalyData.score}
                </div>
                <div className="text-sm text-gray-500">out of 100</div>
              </div>
            </Card>

            <Card className="col-span-2">
              <h3 className="text-sm text-gray-400 mb-4">Baseline vs Current Behavior</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="metric" stroke="#888" />
                  <YAxis stroke="#888" />
                  <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }} />
                  <Bar dataKey="baseline" fill="#666" name="Baseline" />
                  <Bar dataKey="current" fill="#3b82f6" name="Current" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>

          <Card>
            <div className="flex items-center gap-6 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span>Model Version: {anomalyData.model_version}</span>
              </div>
              <div>Confidence: {(anomalyData.confidence * 100).toFixed(0)}%</div>
            </div>
          </Card>

          <Card>
            <h2 className="text-lg font-semibold mb-4">Anomalous Events</h2>
            <Table columns={columns} data={anomalyData.anomalous_events || []} />
          </Card>
        </>
      )}
    </div>
  )
}

export default AnomalyPage
