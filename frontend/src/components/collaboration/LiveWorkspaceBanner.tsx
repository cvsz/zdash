export default function LiveWorkspaceBanner({ connected }: { connected: boolean }) { return <div>{connected ? "Live collaboration connected" : "Degraded mode"}</div>; }
