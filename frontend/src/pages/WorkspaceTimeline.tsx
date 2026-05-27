import { useCollaboration } from "../hooks/useCollaboration";
export default function WorkspaceTimeline(){ const {events}=useCollaboration("default-workspace"); return <div><h2>Workspace Timeline</h2>{events.map((e,i)=><div key={i}>{e.type||"event"}</div>)}</div>; }
