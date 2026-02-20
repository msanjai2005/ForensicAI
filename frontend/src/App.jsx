import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import CasesPage from './pages/CasesPage'
import UploadPage from './pages/UploadPage'
import TimelinePage from './pages/TimelinePage'
import RulesPage from './pages/RulesPage'
import AnomalyPage from './pages/AnomalyPage'
import GraphPage from './pages/GraphPage'
import RiskPage from './pages/RiskPage'
import ForensicRiskPage from './pages/ForensicRiskPage'
import AIAssistantPage from './pages/AIAssistantPage'
import ReportPage from './pages/ReportPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/cases" replace />} />
        <Route path="cases" element={<CasesPage />} />
        <Route path="cases/:id/upload" element={<UploadPage />} />
        <Route path="cases/:id/timeline" element={<TimelinePage />} />
        <Route path="cases/:id/rules" element={<RulesPage />} />
        <Route path="cases/:id/anomaly" element={<AnomalyPage />} />
        <Route path="cases/:id/graph" element={<GraphPage />} />
        {/* <Route path="cases/:id/risk" element={<RiskPage />} /> */}
        <Route path="cases/:id/forensic-risk" element={<ForensicRiskPage />} />
        <Route path="cases/:id/ai-assistant" element={<AIAssistantPage />} />
        <Route path="cases/:id/report" element={<ReportPage />} />
      </Route>
    </Routes>
  )
}

export default App
