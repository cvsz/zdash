import React from "react";
import PageHeader from "../components/layout/PageHeader";
import { QueueStatusCard } from "../components/workers/QueueStatusCard";
import { WorkerRunTable } from "../components/workers/WorkerRunTable";
import { TaskDispatchPanel } from "../components/workers/TaskDispatchPanel";
import { useWorkers } from "../hooks/useWorkers";

export default function Workers() {
  const { queueStatus, tasks, loading, enqueue } = useWorkers();

  return (
    <div className="flex flex-col space-y-6">
      <PageHeader 
        title="Workers & Queues" 
        subtitle="Monitor background tasks, async queues, and dispatched workloads." 
      />
      {loading ? (
        <div className="text-slate-400">Loading workers data...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {queueStatus.map((status) => (
              <QueueStatusCard key={status.queue_name} status={status} />
            ))}
            {queueStatus.length === 0 && (
              <div className="text-slate-500">No active queues found.</div>
            )}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="lg:col-span-2 flex flex-col space-y-4">
              <h3 className="text-xl font-medium text-white">Recent Tasks</h3>
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
