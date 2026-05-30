import { BrowserRouter, Route, Routes } from "react-router-dom";
import ErrorBoundary from "./components/system/ErrorBoundary";

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
import Organizations from "./pages/Organizations";
import Workspace from "./pages/Workspace";
import Workers from "./pages/Workers";
import OrgMapPage from "./pages/OrgMapPage";
import RiskPanel from "./pages/RiskPanel";
import Scheduler from "./pages/Scheduler";
import SessionLogs from "./pages/SessionLogs";
import Settings from "./pages/Settings";
import TeamRoster from "./pages/TeamRoster";
import XauDashboard from "./pages/XauDashboard";
import SystemHealth from "./pages/SystemHealth";
import EventTimeline from "./pages/EventTimeline";
import ZFinance from "./pages/ZFinance";
import Notifications from "./pages/Notifications";
import WorkspaceLive from "./pages/WorkspaceLive";
import WorkspaceTimeline from "./pages/WorkspaceTimeline";
import WorkspaceNotes from "./pages/WorkspaceNotes";
import IncidentCenter from "./pages/IncidentCenter";
import Billing from "./pages/Billing";
import Usage from "./pages/Usage";
import Marketplace from "./pages/Marketplace";
import Enterprise from "./pages/Enterprise";
import Onboarding from "./pages/Onboarding";
import { RealtimeProvider } from "./realtime/context";

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
          <Route path="/incidents" element={<IncidentCenter />} />
          <Route path="/scheduler" element={<Scheduler />} />
          <Route path="/backtests" element={<Backtests />} />
          <Route path="/content" element={<ContentPipeline />} />
          <Route path="/iot" element={<IoTControl />} />
          <Route path="/org" element={<OrgMapPage />} />
          <Route path="/organizations" element={<Organizations />} />
          <Route path="/workspace" element={<Workspace />} />
          <Route path="/workers" element={<Workers />} />
          <Route path="/logs" element={<SessionLogs />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="/usage" element={<Usage />} />
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/enterprise" element={<Enterprise />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/zfinance" element={<ZFinance />} />
          <Route path="/system/health" element={<SystemHealth />} />
          <Route path="/events" element={<EventTimeline />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/workspace/live" element={<WorkspaceLive />} />
          <Route path="/workspace/timeline" element={<WorkspaceTimeline />} />
          <Route path="/workspace/notes" element={<WorkspaceNotes />} />
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
      <ErrorBoundary>
        <RealtimeProvider>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="*" element={<ProtectedDashboardRoutes />} />
            </Routes>
          </AuthProvider>
        </RealtimeProvider>
      </ErrorBoundary>
    </BrowserRouter>
  );
}
