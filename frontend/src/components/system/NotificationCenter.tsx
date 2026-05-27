import { useState } from "react";
import { useRealtimeContext } from "../../realtime/context";

export default function NotificationCenter() {
  const { events, unread, clearUnread } = useRealtimeContext();
  const [open, setOpen] = useState(false);
  const items = events.slice(0, 20);
  return (
    <div>
      <button aria-label="Notifications" onClick={() => { setOpen(!open); clearUnread(); }}>
        Notifications ({unread})
      </button>
      {open ? (
        <div role="region" aria-label="Notification center" className="rounded border p-2 bg-slate-900">
          {items.length === 0 ? <p>No notifications.</p> : items.map((event) => <p key={event.id}>{event.message || event.type}</p>)}
        </div>
      ) : null}
    </div>
  );
}
