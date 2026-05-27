import { useEffect, useState } from "react";
import ActivityTimeline from "../components/realtime/ActivityTimeline";
import PresencePanel from "../components/realtime/PresencePanel";
import WebsocketHealthCard from "../components/system/WebsocketHealthCard";
import { apiClient } from "../api/client";

export default function IncidentCenter() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const load = () => apiClient.get<any[]>("/api/incidents", []).then(setIncidents).catch(() => setIncidents([]));
  useEffect(() => { load(); }, []);
  return <div className="space-y-4"><h1 className="text-xl font-semibold">Incident Ops</h1><WebsocketHealthCard /><PresencePanel /><ul>{incidents.map((i)=><li key={i.id}>{i.title} [{i.status}] <button onClick={()=>apiClient.post(`/api/incidents/${i.id}/ack`,{}).then(load)}>Ack</button> <button onClick={()=>{ if(confirm('Resolve incident?')) apiClient.post(`/api/incidents/${i.id}/resolve`,{notes:'resolved from dashboard'}).then(load); }}>Resolve</button></li>)}</ul><ActivityTimeline /></div>;
}
