import { useEffect, useState } from "react";
import ActivityTimeline from "../components/realtime/ActivityTimeline";
import PresencePanel from "../components/realtime/PresencePanel";
import WebsocketHealthCard from "../components/system/WebsocketHealthCard";
import { apiClient } from "../api/client";
import { useT } from "../hooks/useT";

type IncidentItem = {
  id: string;
  title: string;
  status: string;
};

function normalizeIncidents(value: unknown): IncidentItem[] {
  if (Array.isArray(value)) {
    return value as IncidentItem[];
  }

  if (value && typeof value === "object") {
    const candidate = value as { items?: unknown };
    if (Array.isArray(candidate.items)) {
      return candidate.items as IncidentItem[];
    }
  }

  return [];
}

export default function IncidentCenter() {
  const { t } = useT();
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);

  const load = () =>
    apiClient
      .get<IncidentItem[] | { items?: IncidentItem[] }>("/api/incidents", { items: [] })
      .then((data) => setIncidents(normalizeIncidents(data)))
      .catch(() => setIncidents([]));

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">{t('incidents.title')}</h1>
      <WebsocketHealthCard />
      <PresencePanel />
      <ul>
        {incidents.map((incident) => (
          <li key={incident.id}>
            {incident.title} [{incident.status}]{" "}
            <button onClick={() => apiClient.post(`/api/incidents/${incident.id}/ack`, {}).then(load)}>
              {t('incidents.ack')}
            </button>{" "}
            <button
              onClick={() => {
                if (confirm(t('incidents.resolve_incident_confirm'))) {
                  apiClient
                    .post(`/api/incidents/${incident.id}/resolve`, {
                      notes: t('incidents.resolved_from_dashboard'),
                    })
                    .then(load);
                }
              }}
            >
              {t('incidents.resolve')}
            </button>
          </li>
        ))}
      </ul>
      <ActivityTimeline />
    </div>
  );
}
