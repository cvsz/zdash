import PageHeader from '../components/layout/PageHeader';
import SectionCard from '../components/common/SectionCard';
import { apiClientConfig, mockFallbackActive } from '../api/client';
import { getHealth } from '../api/endpoints';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../hooks/useAuth';
import { useRealtimeContext } from '../realtime/context';

export default function SystemHealth() {
  const health = useApi(getHealth, []);
  const { user } = useAuth();
  const mode = import.meta.env.MODE;
  const { state, events } = useRealtimeContext();
  const lastEvent = events[0];

  return (
    <div className="space-y-6">
      <PageHeader title="System Health" subtitle="Frontend and backend diagnostic summary (safe, no secrets)." />
      <SectionCard title="Diagnostics">
        <ul className="space-y-2 text-sm text-text-secondary">
          <li>Build mode: <strong>{mode}</strong></li>
          <li>API base URL: <strong>{apiClientConfig.baseUrl}</strong></li>
          <li>Mock fallback enabled: <strong>{String(apiClientConfig.mockFallbackEnabled)}</strong></li>
          <li>Mock fallback active: <strong>{String(mockFallbackActive)}</strong></li>
          <li>Auth enabled: <strong>{String(import.meta.env.VITE_AUTH_ENABLED ?? false)}</strong></li>
          <li>Router status: <strong>BrowserRouter active</strong></li>
          <li>Backend reachable: <strong>{health.error ? 'false' : 'true'}</strong></li>
          <li>Last API response time: <strong>{health.data?.timestamp ?? 'n/a'}</strong></li>
          <li>Current user role: <strong>{user?.role ?? 'anonymous'}</strong></li>
          <li>WebSocket status: <strong>{state}</strong></li>
          <li>Reconnect attempts: <strong>0</strong></li>
          <li>Last event timestamp: <strong>{lastEvent?.timestamp ?? 'n/a'}</strong></li>
          <li>Heartbeat latency: <strong>{lastEvent?.type === 'system.heartbeat' ? 'active' : 'n/a'}</strong></li>
          <li>Mock realtime fallback: <strong>{state !== 'connected' ? 'SIMULATED REALTIME MODE' : 'false'}</strong></li>
        </ul>
      </SectionCard>
    </div>
  );
}
