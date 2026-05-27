import type { RealtimeEnvelope } from "../../realtime/types";
import { formatDateTime } from "../../utils/format";

const severityStyle: Record<string, string> = {
  info: "border-cyan-400/30 bg-cyan-500/10 text-cyan-100",
  success: "border-emerald-400/30 bg-emerald-500/10 text-emerald-100",
  warning: "border-amber-400/30 bg-amber-500/10 text-amber-100",
  danger: "border-rose-400/30 bg-rose-500/10 text-rose-100",
};

type RealtimeEventFeedProps = {
  title: string;
  events: RealtimeEnvelope[];
  maxItems?: number;
  emptyMessage?: string;
};

function readMessage(event: RealtimeEnvelope): string {
  const payloadMessage = event.payload?.message;
  if (typeof payloadMessage === "string" && payloadMessage.trim().length > 0) {
    return payloadMessage;
  }
  return event.type;
}

export default function RealtimeEventFeed({
  title,
  events,
  maxItems = 8,
  emptyMessage = "No realtime events yet.",
}: RealtimeEventFeedProps) {
  const visible = events.slice(0, maxItems);

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
      <h3 className="text-sm font-semibold text-white">{title}</h3>
      {visible.length === 0 ? (
        <p className="mt-2 text-xs text-slate-400">{emptyMessage}</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {visible.map((event, index) => {
            const style = severityStyle[event.severity] ?? severityStyle.info;
            return (
              <li
                key={`${event.type}-${event.timestamp}-${index}`}
                className={`rounded-md border p-3 transition duration-300 ${style} ${index === 0 ? "animate-pulse" : ""}`}
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="text-xs font-semibold uppercase tracking-wide">{event.type}</p>
                  <span className="text-[11px] opacity-90">{event.severity.toUpperCase()}</span>
                </div>
                <p className="mt-1 text-sm font-medium">{readMessage(event)}</p>
                <p className="mt-1 text-[11px] opacity-90">
                  {event.source} · {formatDateTime(event.timestamp)}
                </p>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
