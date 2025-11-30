import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Cases from './pages/Cases'
import CaseNew from './pages/CaseNew'
import CaseDetail from './pages/CaseDetail'
import Observations from './pages/Observations'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import ReportPreview from './pages/ReportPreview'
import DocumentUpload from './pages/DocumentUpload'
import DataFlow from './pages/DataFlow'
import { useAuthStore } from './stores/authStore'

function App() {
  const { login, isAuthenticated } = useAuthStore()

  // デモモード: 自動的にログイン状態にする
  useEffect(() => {
    if (!isAuthenticated) {
      login('demo-token', {
        user_id: 'demo-1',
        email: 'demo@fund-ic.com',
        full_name: 'デモユーザー',
        role: 'analyst',
        permissions: ['view:dashboard', 'view:cases'],
      })
    }
  }, [isAuthenticated, login])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/cases" element={<Cases />} />
        <Route path="/cases/new" element={<CaseNew />} />
        <Route path="/cases/:caseId" element={<CaseDetail />} />
        <Route path="/observations" element={<Observations />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
        {/* デモ用新規ページ */}
        <Route path="/report-preview" element={<ReportPreview />} />
        <Route path="/upload" element={<DocumentUpload />} />
        <Route path="/data-flow" element={<DataFlow />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
