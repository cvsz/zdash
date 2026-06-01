import { useT } from "../../hooks/useT";
import { useOperatorPresence } from "../../realtime/hooks";

export default function PresencePanel() {
  const { t } = useT();
  const presence = useOperatorPresence();
  return <div><h3>{t('realtime.operator_presence')}</h3>{presence.length===0?<p>{t('realtime.no_active_operators')}</p>:<ul>{presence.map((p)=><li key={p.id}>{String(p.payload.operator ?? t('common.unnamed'))} ({String(p.payload.role ?? t('common.unknown'))})</li>)}</ul>}</div>;
}
