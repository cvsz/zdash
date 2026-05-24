import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Layout from './components/Layout'
import { ErrorBoundary } from './components/ErrorBoundary'
import Dashboard from './pages/Dashboard'
import TeamRoster from './pages/TeamRoster'
import XauDashboard from './pages/XauDashboard'
import Scheduler from './pages/Scheduler'
import Backtests from './pages/Backtests'
import OrgMap from './pages/OrgMap'
import SessionLogs from './pages/SessionLogs'
import RiskPanel from './pages/RiskPanel'
import ContentPipeline from './pages/ContentPipeline'
import Login from './pages/Login'
import AuditLogs from './pages/AuditLogs'
import { apiGet, clearSession, getToken } from './api/client'

function Protected({ token, children }: { token: string; children: JSX.Element }) {
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const [token, setToken] = useState(getToken())
  const [role, setRole] = useState(localStorage.getItem('zdash_role') || 'viewer')
  const [warning, setWarning] = useState(true)
  const [liveActive, setLiveActive] = useState(false)
  const [offline, setOffline] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    setToken(getToken())
    setRole(localStorage.getItem('zdash_role') || 'viewer')
  }, [])

  useEffect(() => {
    if (!token) return
    apiGet<{ gates: { all_enabled: boolean } }>('/api/trading/live-gates', { gates: { all_enabled: false } }).then((d) => {
      setWarning(!d.gates.all_enabled)
      setLiveActive(d.gates.all_enabled)
      setOffline(false)
    }).catch(() => {
      setOffline(true)
    })
  }, [token])

  useEffect(() => {
    const handler = () => {
      clearSession()
      setToken('')
      setRole('viewer')
      navigate('/login')
    }
    window.addEventListener('auth:unauthorized', handler)
    return () => window.removeEventListener('auth:unauthorized', handler)
  }, [navigate])

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="*"
        element={
          <Protected token={token}>
            <ErrorBoundary>
              <Layout
                role={role}
                liveWarning={warning}
                liveActive={liveActive}
                offline={offline}
                onLogout={() => {
                  clearSession()
                  setToken('')
                  setRole('viewer')
                  navigate('/login')
                }}
              >
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/team" element={<TeamRoster />} />
                  <Route path="/xau" element={<XauDashboard />} />
                  <Route path="/scheduler" element={<Scheduler />} />
                  <Route path="/backtests" element={<Backtests />} />
                  <Route path="/org" element={<OrgMap />} />
                  <Route path="/logs" element={<SessionLogs />} />
                  <Route path="/risk" element={<RiskPanel />} />
                  <Route path="/content" element={<ContentPipeline />} />
                  <Route path="/audit" element={<AuditLogs />} />
                </Routes>
              </Layout>
            </ErrorBoundary>
          </Protected>
        }
      />
    </Routes>
  )
}
