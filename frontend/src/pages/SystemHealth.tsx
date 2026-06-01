import PageHeader from '../components/layout/PageHeader';
import SectionCard from '../components/common/SectionCard';
import { apiClientConfig, mockFallbackActive } from '../api/client';
import { getHealth } from '../api/endpoints';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../hooks/useAuth';
import { useRealtimeContext } from '../realtime/context';
import { useT } from '../hooks/useT';

export default function SystemHealth() {
  const { t } = useT();
  const health = useApi(getHealth, []);
  const { user } = useAuth();
  const mode = import.meta.env.MODE;
  const { state, events } = useRealtimeContext();
  const lastEvent = events[0];

  return (
    <div className="space-y-6">
      <PageHeader title={t('system_health.title')} subtitle={t('system_health.subtitle')} />
      <SectionCard title={t('health.diagnostics')}>
        <ul className="space-y-2 text-sm text-text-secondary">
          <li>{t('health.build_mode')}: <strong>{mode}</strong></li>
          <li>{t('health.api_base_url')}: <strong>{apiClientConfig.baseUrl}</strong></li>
          <li>{t('health.mock_fallback_enabled')}: <strong>{String(apiClientConfig.mockFallbackEnabled)}</strong></li>
          <li>{t('health.mock_fallback_active')}: <strong>{String(mockFallbackActive)}</strong></li>
          <li>{t('health.auth_enabled')}: <strong>{String(import.meta.env.VITE_AUTH_ENABLED ?? false)}</strong></li>
          <li>{t('health.router_status')}: <strong>{t('common.enabled')}</strong></li>
          <li>{t('health.backend_reachable')}: <strong>{health.error ? t('common.no') : t('common.yes')}</strong></li>
          <li>{t('health.last_api_response_time')}: <strong>{health.data?.timestamp ?? t('common.none')}</strong></li>
          <li>{t('health.current_user_role')}: <strong>{user?.role ?? t('settings.anonymous')}</strong></li>
          <li>{t('health.websocket_status')}: <strong>{state}</strong></li>
          <li>{t('health.reconnect_attempts')}: <strong>0</strong></li>
          <li>{t('health.last_event_timestamp')}: <strong>{lastEvent?.timestamp ?? t('common.none')}</strong></li>
          <li>{t('health.heartbeat_latency')}: <strong>{lastEvent?.type === 'system.heartbeat' ? t('common.active') : t('common.none')}</strong></li>
          <li>{t('health.mock_realtime_fallback')}: <strong>{state !== 'connected' ? t('health.simulated_realtime_mode') : t('common.no')}</strong></li>
        </ul>
      </SectionCard>
    </div>
  );
}
