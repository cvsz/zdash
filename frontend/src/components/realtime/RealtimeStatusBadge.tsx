import Badge from "../common/Badge";
import type { RealtimeConnectionState } from "../../realtime/types";

type RealtimeStatusBadgeProps = {
  connection: RealtimeConnectionState;
  compact?: boolean;
};

export default function RealtimeStatusBadge({ connection, compact = false }: RealtimeStatusBadgeProps) {
  const variant = connection.connected
    ? connection.stale
      ? "warning"
      : "success"
    : "danger";

  const label = connection.connected
    ? connection.stale
      ? "STALE"
      : "CONNECTED"
    : connection.connecting
      ? "CONNECTING"
      : "DISCONNECTED";

  const suffix = compact ? "" : ` · ${connection.channel.toUpperCase()}`;

  return <Badge variant={variant}>{`WS ${label}${suffix}`}</Badge>;
}
