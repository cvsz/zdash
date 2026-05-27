import { useRealtime } from "../../realtime/useRealtime";

export default function WebsocketHealthCard() {
  const { connection } = useRealtime();
  return <div><h3>Websocket Health</h3><p>state: {connection.connected ? "connected" : connection.connecting ? "connecting" : "offline"}</p><p>retries: {connection.retryAttempt}</p></div>;
}
