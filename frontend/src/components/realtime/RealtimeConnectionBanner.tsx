import { useT } from "../../hooks/useT";
import type { RealtimeConnectionState } from "../../realtime/types";

type RealtimeConnectionBannerProps = {
  connection: RealtimeConnectionState;
};

function formatRetryMs(ms: number | null): string {
  if (ms === null) {
    return "-";
  }
  return `${Math.max(0, Math.ceil(ms / 1000))}s`;
}

export default function RealtimeConnectionBanner({ connection }: RealtimeConnectionBannerProps) {
  const { t } = useT();
  if (connection.connected && !connection.stale) {
    return null;
  }

  return (
    <div className="rounded-lg border border-amber-400/40 bg-amber-500/10 px-4 py-3 text-xs text-amber-100">
      <p className="font-semibold">{t('realtime.stream_degraded')}</p>
      <p className="mt-1">
        {t('realtime.channel')}: {connection.channel} · {t('realtime.presence_online')}: {connection.online ? t('common.yes') : t('common.no')} · {t('realtime.retry_attempt')}: {connection.retryAttempt}
        {" · "}
        {t('realtime.next_reconnect')}: {formatRetryMs(connection.retryInMs)}
      </p>
    </div>
  );
}
