import { BrowserRouter, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/auth/ProtectedRoute";
import AppLayout from "./components/layout/AppLayout";
import { AuthProvider } from "./hooks/useAuth";
import Admin from "./pages/Admin";
import Alerts from "./pages/Alerts";
import Backtests from "./pages/Backtests";
import ContentPipeline from "./pages/ContentPipeline";
import Dashboard from "./pages/Dashboard";
import IoTControl from "./pages/IoTControl";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import OrgMapPage from "./pages/OrgMapPage";
import RiskPanel from "./pages/RiskPanel";
import Scheduler from "./pages/Scheduler";
import SessionLogs from "./pages/SessionLogs";
import Settings from "./pages/Settings";
import TeamRoster from "./pages/TeamRoster";
import XauDashboard from "./pages/XauDashboard";

function ProtectedDashboardRoutes() {
  return (
    <ProtectedRoute>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/team" element={<TeamRoster />} />
          <Route path="/xau" element={<XauDashboard />} />
          <Route path="/risk" element={<RiskPanel />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/scheduler" element={<Scheduler />} />
          <Route path="/backtests" element={<Backtests />} />
          <Route path="/content" element={<ContentPipeline />} />
          <Route path="/iot" element={<IoTControl />} />
          <Route path="/org" element={<OrgMapPage />} />
          <Route path="/logs" element={<SessionLogs />} />
          <Route path="/settings" element={<Settings />} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowRoles={["admin"]}>
                <Admin />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AppLayout>
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<ProtectedDashboardRoutes />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
