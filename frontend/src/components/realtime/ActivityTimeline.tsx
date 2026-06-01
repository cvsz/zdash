import { useState } from "react";
import { useT } from "../../hooks/useT";
import { useRealtime } from "../../realtime/useRealtime";

export default function ActivityTimeline() {
  const { t } = useT();
  const { events } = useRealtime();
  const [paused, setPaused] = useState(false);
  const list = paused ? events.slice(0, 25) : events;
  return <div><button onClick={() => setPaused((p) => !p)}>{paused ? t('activity_timeline.resume') : t('activity_timeline.pause')}</button><ul>{list.slice(-30).reverse().map((e) => <li key={e.id}>{e.type} - {e.source}</li>)}</ul></div>;
}
