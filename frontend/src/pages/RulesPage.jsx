import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Moon, Zap, DollarSign, Trash } from 'lucide-react'
import Card from '../components/Card'
import Table from '../components/Table'
import Badge from '../components/Badge'
import Loader from '../components/Loader'
import { getRuleResults } from '../api/cases'

const RulesPage = () => {
  const { id } = useParams()
  const [ruleData, setRuleData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRules()
  }, [id])

  const loadRules = async () => {
    try {
      const data = await getRuleResults(id)
      setRuleData(data)
    } catch (error) {
      console.error('Failed to load rules:', error)
    } finally {
      setLoading(false)
    }
  }

  const ruleCards = [
    { icon: Moon, title: 'Midnight Activity', count: ruleData?.rules?.find(r => r.name === 'Midnight Activity')?.violations || 0, risk: 15, color: 'text-purple-400', ruleName: 'Midnight Activity' },
    { icon: Zap, title: 'Transaction Burst', count: ruleData?.rules?.find(r => r.name === 'Transaction Burst')?.violations || 0, risk: 25, color: 'text-yellow-400', ruleName: 'Transaction Burst' },
    { icon: DollarSign, title: 'High Value Transfer', count: ruleData?.rules?.find(r => r.name === 'High Value Transfer')?.violations || 0, risk: 35, color: 'text-green-400', ruleName: 'High Value Transfer' },
    { icon: Trash, title: 'Deleted Messages', count: ruleData?.rules?.find(r => r.name === 'Deleted Messages')?.violations || 0, risk: 20, color: 'text-red-400', ruleName: 'Deleted Messages' },
  ]

  const columns = [
    { header: 'Rule', accessor: 'rule_type' },
    { header: 'Timestamp', accessor: 'created_at', render: (row) => new Date(row.created_at).toLocaleString() },
    { 
      header: 'Severity', 
      accessor: 'severity',
      render: (row) => <Badge variant={row.severity === 'critical' ? 'danger' : row.severity === 'high' ? 'warning' : 'info'}>{row.severity}</Badge>
    },
    { header: 'Description', accessor: 'description' },
    { header: 'Score', accessor: 'score_contribution' }
  ]

  if (loading) return <Loader size="lg" />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Rule Engine Dashboard</h1>

      <div className="grid grid-cols-4 gap-4">
        {ruleCards.map((rule, idx) => {
          const Icon = rule.icon
          return (
            <Card key={idx}>
              <div className="flex items-start justify-between mb-4">
                <Icon className={`w-8 h-8 ${rule.color}`} />
                <span className="text-2xl font-bold">{rule.count}</span>
              </div>
              <h3 className="font-medium mb-2">{rule.title}</h3>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Risk Contribution</span>
                <span className="text-orange-400 font-medium">{rule.risk}%</span>
              </div>
            </Card>
          )
        })}
      </div>

      <Card>
        <h2 className="text-lg font-semibold mb-4">Suspicious Events</h2>
        <Table columns={columns} data={ruleData?.events || []} />
      </Card>
    </div>
  )
}

export default RulesPage
