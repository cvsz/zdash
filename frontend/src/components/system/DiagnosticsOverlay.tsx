import { useState } from "react";
import { useLiveMetrics } from "../../realtime/hooks";

export default function DiagnosticsOverlay() {
  const [open, setOpen] = useState(false);
  const metrics = useLiveMetrics();
  return <div className="fixed bottom-2 right-2"><button onClick={()=>setOpen((x)=>!x)}>Diagnostics</button>{open && <div className="rounded bg-slate-900 p-2 text-xs">events: {metrics.length}</div>}</div>;
}
