import PageHeader from "../components/layout/PageHeader";
import LiveIndicator from "../components/realtime/LiveIndicator";
import RealtimeConnectionBanner from "../components/realtime/RealtimeConnectionBanner";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import RealtimeStatusBadge from "../components/realtime/RealtimeStatusBadge";
import { useRealtime } from "../realtime/useRealtime";

export default function Alerts() {
  const realtime = useRealtime({ maxEvents: 12 });

  return (
    <div className="space-y-5">
      <PageHeader
        title="Alerts"
        subtitle="Realtime alert stream for risk, scheduler, and content pipeline notifications."
        actions={
          <>
            <RealtimeStatusBadge connection={realtime.connection} compact />
            <LiveIndicator connection={realtime.connection} label="Alerts WS" />
          </>
        }
      />

      <RealtimeConnectionBanner connection={realtime.connection} />

      <RealtimeEventFeed
        title="Live Alert Feed"
        events={realtime.events}
        maxItems={12}
        emptyMessage="No live alerts yet."
      />
    </div>
  );
}
