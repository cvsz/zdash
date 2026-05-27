import { useMemo, useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import { useRealtimeContext } from "../realtime/context";

export default function EventTimeline() {
  const { events, state } = useRealtimeContext();
  const [search, setSearch] = useState("");
  const filtered = useMemo(() => events.filter((e) => `${e.type} ${e.source} ${e.message}`.toLowerCase().includes(search.toLowerCase())), [events, search]);
  return (
    <div className="space-y-4">
      <PageHeader title="Event Timeline" subtitle={`Realtime state: ${state}`} />
      <input aria-label="Search events" value={search} onChange={(e) => setSearch(e.target.value)} className="rounded border px-2 py-1" />
      <ul className="space-y-2">
        {filtered.map((event) => <li key={event.id} className="rounded border p-2">{event.timestamp} · {event.type} · {event.message || "-"}</li>)}
      </ul>
    </div>
  );
}
