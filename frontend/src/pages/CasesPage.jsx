import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2 } from 'lucide-react'
import Card from '../components/Card'
import Table from '../components/Table'
import Modal from '../components/Modal'
import Badge from '../components/Badge'
import Loader from '../components/Loader'
import EmptyState from '../components/EmptyState'
import { getCases, createCase, deleteCase } from '../api/cases'

const CasesPage = () => {
  const navigate = useNavigate()
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({ name: '', description: '' })

  useEffect(() => {
    loadCases()
  }, [])

  const loadCases = async () => {
    try {
      const data = await getCases()
      setCases(data)
    } catch (error) {
      console.error('Failed to load cases:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      await createCase(formData)
      setIsModalOpen(false)
      setFormData({ name: '', description: '' })
      loadCases()
    } catch (error) {
      console.error('Failed to create case:', error)
    }
  }

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (confirm('Delete this case?')) {
      try {
        await deleteCase(id)
        loadCases()
      } catch (error) {
        console.error('Failed to delete case:', error)
      }
    }
  }

  const columns = [
    { header: 'Case Name', accessor: 'name' },
    { header: 'Created', accessor: 'created_at', render: (row) => new Date(row.created_at).toLocaleDateString() },
    { 
      header: 'Status', 
      accessor: 'status',
      render: (row) => <Badge variant={row.status === 'active' ? 'success' : 'default'}>{row.status}</Badge>
    },
    { header: 'Records', accessor: 'records_count', render: (row) => row.records_count || 0 },
    { 
      header: 'Risk', 
      accessor: 'risk_level',
      render: (row) => {
        const variant = row.risk_level === 'high' ? 'danger' : row.risk_level === 'medium' ? 'warning' : 'success'
        return <Badge variant={variant}>{row.risk_level || 'unknown'}</Badge>
      }
    },
    {
      header: 'Actions',
      render: (row) => (
        <button onClick={(e) => handleDelete(row.id, e)} className="text-red-400 hover:text-red-300">
          <Trash2 className="w-4 h-4" />
        </button>
      )
    }
  ]

  if (loading) return <Loader size="lg" />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Case Management</h1>
        <button onClick={() => setIsModalOpen(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Case
        </button>
      </div>

      <Card>
        {cases.length === 0 ? (
          <EmptyState
            title="No cases yet"
            description="Create your first investigation case to get started"
            action={
              <button onClick={() => setIsModalOpen(true)} className="btn-primary">
                Create Case
              </button>
            }
          />
        ) : (
          <Table columns={columns} data={cases} onRowClick={(row) => navigate(`/cases/${row.id}/upload`)} />
        )}
      </Card>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Case">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Case Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div className="flex gap-3 justify-end">
            <button type="button" onClick={() => setIsModalOpen(false)} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export default CasesPage
