import { useT } from "../../hooks/useT";
import Badge from "../common/Badge";
import type { RealtimeConnectionState } from "../../realtime/types";

type RealtimeStatusBadgeProps = {
  connection: RealtimeConnectionState;
  compact?: boolean;
};

export default function RealtimeStatusBadge({ connection, compact = false }: RealtimeStatusBadgeProps) {
  const { t } = useT();
  const variant = connection.connected
    ? connection.stale
      ? "warning"
      : "success"
    : "danger";

  const label = connection.connected
    ? connection.stale
      ? t('realtime.stale')
      : t('realtime.status_badge_connected')
    : connection.connecting
      ? t('realtime.live_indicator_connecting')
      : t('realtime.status_badge_disconnected');

  const suffix = compact ? "" : ` · ${connection.channel.toUpperCase()}`;

  return <Badge variant={variant}>{`WS ${label}${suffix}`}</Badge>;
}
