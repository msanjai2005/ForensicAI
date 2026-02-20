import { useParams } from 'react-router-dom'
import { User } from 'lucide-react'
import Badge from './Badge'
import { useState, useEffect } from 'react'
import { getCaseById } from '../api/cases'

const Topbar = () => {
  const { id } = useParams()
  const [caseData, setCaseData] = useState(null)

  useEffect(() => {
    if (id) {
      getCaseById(id).then(setCaseData).catch(() => {})
    }
  }, [id])

  return (
    <div className="h-16 bg-dark-card border-b border-dark-border px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        {caseData && (
          <>
            <h1 className="text-lg font-semibold">{caseData.name}</h1>
            <Badge variant={caseData.status === 'active' ? 'success' : 'default'}>
              {caseData.status}
            </Badge>
          </>
        )}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-2 bg-dark-bg rounded-lg">
          <User className="w-4 h-4" />
          <span className="text-sm">Investigator</span>
        </div>
      </div>
    </div>
  )
}

export default Topbar
