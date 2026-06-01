import { useMemo, useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import { useRealtimeContext } from "../realtime/context";
import { useT } from "../hooks/useT";

export default function EventTimeline() {
  const { t } = useT();
  const { events, state } = useRealtimeContext();
  const [search, setSearch] = useState("");
  const filtered = useMemo(() => events.filter((e) => `${e.type} ${e.source} ${e.message}`.toLowerCase().includes(search.toLowerCase())), [events, search]);
  return (
    <div className="space-y-4">
      <PageHeader title={t('event_timeline.title')} subtitle={`Realtime state: ${state}`} />
      <input aria-label={t('event_timeline.search_events')} value={search} onChange={(e) => setSearch(e.target.value)} className="rounded border px-2 py-1" />
      <ul className="space-y-2">
        {filtered.length === 0 ? <li className="rounded border p-2 text-text-dim">{t('event_timeline.no_events')}</li> : filtered.map((event) => <li key={event.id} className="rounded border p-2">{event.timestamp} · {event.type} · {event.message || "-"}</li>)}
      </ul>
    </div>
  );
}
