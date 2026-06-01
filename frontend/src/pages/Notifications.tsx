import PageHeader from "../components/layout/PageHeader";
import SectionCard from "../components/common/SectionCard";
import RealtimeEventFeed from "../components/realtime/RealtimeEventFeed";
import { useRealtimeContext } from "../realtime/context";
import { useT } from "../hooks/useT";

export default function Notifications() {
  const { t } = useT();
  const { events } = useRealtimeContext();
  return (
    <div className="space-y-6">
      <PageHeader title={t('notifications.title')} subtitle={t('notifications.subtitle')} />
      <SectionCard title={t('notifications.recent_notifications')}>
        <RealtimeEventFeed title={t('notifications.title')} events={events.slice(0, 50)} />
      </SectionCard>
    </div>
  );
}
