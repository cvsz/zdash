import { useOperatorPresence } from "../../realtime/hooks";

export default function PresencePanel() {
  const presence = useOperatorPresence();
  return <div><h3>Operator Presence</h3>{presence.length===0?<p>No active operators</p>:<ul>{presence.map((p)=><li key={p.id}>{String(p.payload.operator ?? "operator")} ({String(p.payload.role ?? "viewer")})</li>)}</ul>}</div>;
}
