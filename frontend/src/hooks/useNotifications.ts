import { useState, useEffect } from "react";
import { listAlertRules, listAlertEvents, listNotificationChannels, testNotificationChannel } from "../api/endpoints";
import type { AlertRule, AlertEvent, NotificationChannel } from "../api/types";

export function useNotifications() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [events, setEvents] = useState<AlertEvent[]>([]);
  const [channels, setChannels] = useState<NotificationChannel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const fetchAlerts = async () => {
      try {
        const [r, e, c] = await Promise.all([
          listAlertRules(),
          listAlertEvents(),
          listNotificationChannels()
        ]);
        if (mounted) {
          setRules(r);
          setEvents(e);
          setChannels(c);
        }
      } catch (err) {
        console.error("Failed to load alerts:", err);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchAlerts();
    return () => {
      mounted = false;
    };
  }, []);

  const testChannel = async (id: string) => {
    await testNotificationChannel(id);
  };

  return { rules, events, channels, loading, testChannel };
}
