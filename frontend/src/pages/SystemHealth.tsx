import PageHeader from '../components/layout/PageHeader';
import SectionCard from '../components/common/SectionCard';
import { apiClientConfig, mockFallbackActive } from '../api/client';
import { getHealth } from '../api/endpoints';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../hooks/useAuth';

export default function SystemHealth() {
  const health = useApi(getHealth, []);
  const { user } = useAuth();
  const mode = import.meta.env.MODE;

  return (
    <div className="space-y-6">
      <PageHeader title="System Health" subtitle="Frontend and backend diagnostic summary (safe, no secrets)." />
      <SectionCard title="Diagnostics">
        <ul className="space-y-2 text-sm text-slate-200">
          <li>Build mode: <strong>{mode}</strong></li>
          <li>API base URL: <strong>{apiClientConfig.baseUrl}</strong></li>
          <li>Mock fallback enabled: <strong>{String(apiClientConfig.mockFallbackEnabled)}</strong></li>
          <li>Mock fallback active: <strong>{String(mockFallbackActive)}</strong></li>
          <li>Auth enabled: <strong>{String(import.meta.env.VITE_AUTH_ENABLED ?? false)}</strong></li>
          <li>Router status: <strong>BrowserRouter active</strong></li>
          <li>Backend reachable: <strong>{health.error ? 'false' : 'true'}</strong></li>
          <li>Last API response time: <strong>{health.data?.timestamp ?? 'n/a'}</strong></li>
          <li>Current user role: <strong>{user?.role ?? 'anonymous'}</strong></li>
        </ul>
      </SectionCard>
    </div>
  );
}
