import { useRealtimeContext } from "../../realtime/context";

export default function ConnectionStatus() {
  const { state } = useRealtimeContext();
  return <span className="text-xs text-slate-300">Connection: {state}</span>;
}
