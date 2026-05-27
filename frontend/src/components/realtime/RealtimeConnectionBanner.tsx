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
  if (connection.connected && !connection.stale) {
    return null;
  }

  return (
    <div className="rounded-lg border border-amber-400/40 bg-amber-500/10 px-4 py-3 text-xs text-amber-100">
      <p className="font-semibold">Realtime stream is degraded.</p>
      <p className="mt-1">
        Channel: {connection.channel} · Online: {connection.online ? "yes" : "no"} · Retry attempt: {connection.retryAttempt}
        {" · "}
        Next reconnect: {formatRetryMs(connection.retryInMs)}
      </p>
    </div>
  );
}
