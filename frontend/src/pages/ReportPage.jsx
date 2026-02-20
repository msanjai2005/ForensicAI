import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { FileText, Download, Clock } from 'lucide-react'
import Card from '../components/Card'
import Table from '../components/Table'
import Badge from '../components/Badge'
import Loader from '../components/Loader'
import { generateReport, getReports } from '../api/cases'

const ReportPage = () => {
  const { id } = useParams()
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [summary, setSummary] = useState(null)

  useEffect(() => {
    loadReports()
  }, [id])

  const loadReports = async () => {
    try {
      const data = await getReports(id)
      setReports(data.reports || [])
      setSummary(data.summary)
    } catch (error) {
      console.error('Failed to load reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const result = await generateReport(id)
      console.log('Report generated:', result)
      await loadReports()
      // Show success message with findings
      if (result.key_findings && result.key_findings.length > 0) {
        alert(`Report generated successfully!\n\nKey Findings:\n${result.key_findings.join('\n')}`)
      }
    } catch (error) {
      console.error('Failed to generate report:', error)
      alert('Failed to generate report: ' + (error.response?.data?.detail || error.message))
    } finally {
      setGenerating(false)
    }
  }

  const columns = [
    { header: 'Report ID', accessor: 'id', render: (row) => row.id.substring(0, 8) },
    { header: 'Title', accessor: 'title' },
    { header: 'Generated', accessor: 'created_at', render: (row) => new Date(row.created_at).toLocaleString() },
    {
      header: 'Actions',
      render: (row) => (
        <a 
          href={`http://localhost:8000/${row.file_path}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-400 hover:text-blue-300 flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Download PDF
        </a>
      )
    }
  ]

  if (loading) return <Loader size="lg" />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Investigation Report</h1>
        <button onClick={handleGenerate} disabled={generating} className="btn-primary flex items-center gap-2">
          <FileText className="w-4 h-4" />
          {generating ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      {summary && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <div className="text-3xl font-bold text-blue-400 mb-2">{summary.total_events || 0}</div>
            <div className="text-sm text-gray-400">Total Events</div>
          </Card>
          <Card>
            <div className="text-3xl font-bold text-red-400 mb-2">{summary.suspicious_events || 0}</div>
            <div className="text-sm text-gray-400">Suspicious Events</div>
          </Card>
          <Card>
            <div className="text-3xl font-bold text-yellow-400 mb-2">{summary.risk_score || 0}</div>
            <div className="text-sm text-gray-400">Risk Score</div>
          </Card>
          <Card>
            <div className="text-3xl font-bold text-green-400 mb-2">{summary.entities || 0}</div>
            <div className="text-sm text-gray-400">Entities Analyzed</div>
          </Card>
        </div>
      )}

      <Card>
        <h2 className="text-lg font-semibold mb-4">Report Summary</h2>
        <div className="space-y-4">
          <div className="p-4 bg-dark-bg rounded-lg">
            <h3 className="font-medium mb-2">Executive Summary</h3>
            <p className="text-sm text-gray-400">
              Investigation case analyzed {summary?.total_events || 0} events across {summary?.time_range || '30 days'}. 
              Detected {summary?.suspicious_events || 0} suspicious activities with an overall risk score of {summary?.risk_score || 0}/100.
            </p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg">
            <h3 className="font-medium mb-2">Key Findings</h3>
            <ul className="text-sm text-gray-400 space-y-1 list-disc list-inside">
              <li>Multiple midnight activity patterns detected</li>
              <li>Unusual transaction burst behavior identified</li>
              <li>High-value transfers flagged for review</li>
              <li>Network analysis reveals suspicious clustering</li>
            </ul>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg">
            <h3 className="font-medium mb-2">Recommendations</h3>
            <ul className="text-sm text-gray-400 space-y-1 list-disc list-inside">
              <li>Immediate review of flagged high-value transactions</li>
              <li>Enhanced monitoring of identified entities</li>
              <li>Further investigation into communication patterns</li>
              <li>Consider escalation to compliance team</li>
            </ul>
          </div>
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold mb-4">Report Generation History</h2>
        {reports.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No reports generated yet</p>
          </div>
        ) : (
          <Table columns={columns} data={reports} />
        )}
      </Card>
    </div>
  )
}

export default ReportPage
