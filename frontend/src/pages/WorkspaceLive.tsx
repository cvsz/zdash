import LiveWorkspaceBanner from "../components/collaboration/LiveWorkspaceBanner";
import { useCollaboration } from "../hooks/useCollaboration";
export default function WorkspaceLive(){ const {connected,events}=useCollaboration("default-workspace"); return <div><h2>Workspace Live</h2><LiveWorkspaceBanner connected={connected}/><pre>{events.length} events</pre></div>; }
