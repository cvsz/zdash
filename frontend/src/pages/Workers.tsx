import React from "react";
import PageHeader from "../components/layout/PageHeader";
import { QueueStatusCard } from "../components/workers/QueueStatusCard";
import { WorkerRunTable } from "../components/workers/WorkerRunTable";
import { TaskDispatchPanel } from "../components/workers/TaskDispatchPanel";
import { useWorkers } from "../hooks/useWorkers";
import { useT } from "../hooks/useT";

export default function Workers() {
  const { t } = useT();
  const { queueStatus, tasks, loading, enqueue } = useWorkers();

  return (
    <div className="flex flex-col space-y-6">
      <PageHeader 
        title={t('workers.title')} 
        subtitle={t('workers.subtitle')} 
      />
      {loading ? (
        <div className="text-text-dim">{t('workers.loading')}</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {queueStatus.map((status) => (
              <QueueStatusCard key={status.queue_name} status={status} />
            ))}
            {queueStatus.length === 0 && (
              <div className="text-text-dim">{t('workers.no_queues')}</div>
            )}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="lg:col-span-2 flex flex-col space-y-4">
              <h3 className="text-xl font-medium text-white">{t('workers.recent_tasks')}</h3>
              <WorkerRunTable tasks={tasks} />
            </div>
            <div>
              <TaskDispatchPanel onEnqueue={enqueue} />
            </div>
          </div>
        </>
      )}
    </div>
  );
};
