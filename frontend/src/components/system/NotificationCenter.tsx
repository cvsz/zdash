import { useMemo, useState } from "react";
import { useRealtimeContext } from "../../realtime/context";

const MAX_ITEMS = 30;

export default function NotificationCenter() {
  const { events, unread, clearUnread } = useRealtimeContext();
  const [open, setOpen] = useState(false);
  const items = useMemo(() => events.slice(0, MAX_ITEMS), [events]);
  return (
    <div>
      <button aria-label="Notifications" onClick={() => { setOpen(!open); clearUnread(); }}>
        Notifications ({unread})
      </button>
      {open ? (
        <div role="region" aria-label="Notification center" className="rounded border p-2 bg-slate-900 max-h-80 overflow-auto">
          {items.length === 0 ? <p>No notifications.</p> : items.map((event) => (
            <div key={event.id} className="mb-1 rounded border border-slate-700 px-2 py-1">
              <p className="text-xs text-slate-400">{new Date(event.timestamp).toLocaleTimeString()} · {event.severity} · {event.source}</p>
              <p>{event.message || event.type}</p>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
