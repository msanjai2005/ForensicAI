import { Link, useLocation, useParams } from 'react-router-dom'
import { Shield, FolderOpen, Upload, Clock, AlertTriangle, Activity, Network, AlertCircle, FileText, Scale, Brain } from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()
  const { id } = useParams()

  const navItems = [
    { path: '/cases', label: 'Cases', icon: FolderOpen },
    ...(id ? [
      { path: `/cases/${id}/upload`, label: 'Upload', icon: Upload },
      { path: `/cases/${id}/timeline`, label: 'Timeline', icon: Clock },
      { path: `/cases/${id}/rules`, label: 'Rules', icon: AlertTriangle },
      { path: `/cases/${id}/anomaly`, label: 'Anomaly', icon: Activity },
      { path: `/cases/${id}/graph`, label: 'Graph', icon: Network },
      { path: `/cases/${id}/forensic-risk`, label: 'Forensic Risk', icon: Scale },
      { path: `/cases/${id}/ai-assistant`, label: 'AI Assistant', icon: Brain },
      { path: `/cases/${id}/report`, label: 'Report', icon: FileText },
    ] : [])
  ]

  return (
    <div className="w-64 bg-dark-card border-r border-dark-border h-screen flex flex-col">
      <div className="p-6 border-b border-dark-border">
        <div className="flex items-center gap-2">
          <Shield className="w-8 h-8 text-blue-500" />
          <span className="text-xl font-bold">SecureIntel</span>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:bg-dark-hover hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

export default Sidebar
