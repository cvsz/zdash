import type { RealtimeConnectionState } from "../../realtime/types";

type LiveIndicatorProps = {
  connection: RealtimeConnectionState;
  label?: string;
};

export default function LiveIndicator({ connection, label = "Realtime" }: LiveIndicatorProps) {
  const isLive = connection.connected && !connection.stale;
  const statusLabel = isLive ? "LIVE" : connection.stale ? "STALE" : "OFFLINE";
  const colorClass = isLive
    ? "bg-emerald-400"
    : connection.stale
      ? "bg-amber-400"
      : "bg-rose-400";

  return (
    <div className="inline-flex items-center gap-2 rounded-md border border-slate-700 bg-slate-900/80 px-2 py-1 text-xs font-semibold text-slate-200">
      <span className="text-slate-300">{label}</span>
      <span className="relative flex h-2 w-2">
        {isLive ? <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-300 opacity-75" /> : null}
        <span className={`relative inline-flex h-2 w-2 rounded-full ${colorClass}`} />
      </span>
      <span>{statusLabel}</span>
    </div>
  );
}
