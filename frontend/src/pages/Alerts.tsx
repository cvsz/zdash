import React from "react";
import PageHeader from "../components/layout/PageHeader";
import { AlertRuleTable } from "../components/alerts/AlertRuleTable";
import { AlertEventTable } from "../components/alerts/AlertEventTable";
import { NotificationChannelForm } from "../components/alerts/NotificationChannelForm";
import { useNotifications } from "../hooks/useNotifications";
import { useT } from "../hooks/useT";

export default function Alerts() {
  const { t } = useT();
  const { rules, events, loading, testChannel } = useNotifications();

  return (
    <div className="flex flex-col space-y-6">
      <PageHeader 
        title={t('alerts.title')} 
        subtitle={t('alerts.subtitle')} 
      />
      {loading ? (
        <div className="text-text-dim">{t('alerts.loading')}</div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="flex flex-col space-y-4">
              <h3 className="text-xl font-medium text-white">{t('alerts.alert_rules')}</h3>
              <AlertRuleTable rules={rules} />
            </div>
            <div className="flex flex-col space-y-4">
              <NotificationChannelForm onTest={testChannel} />
            </div>
          </div>
          <div className="mt-6 flex flex-col space-y-4">
            <h3 className="text-xl font-medium text-white">{t('alerts.active_events')}</h3>
            <AlertEventTable events={events} />
          </div>
        </>
      )}
    </div>
  );
};
