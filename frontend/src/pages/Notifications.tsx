import PageHeader from "../components/layout/PageHeader";
import SectionCard from "../components/common/SectionCard";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import { useRealtimeContext } from "../realtime/context";

export default function Notifications() {
  const { events } = useRealtimeContext();
  return (
    <div className="space-y-6">
      <PageHeader title="Notifications" subtitle="Live notification center (simulation-safe)." />
      <SectionCard title="Recent Notifications">
        <RealtimeEventFeed title="Realtime Notifications" events={events.slice(0, 50)} />
      </SectionCard>
    </div>
  );
}
