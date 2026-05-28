import React from "react";
import type { QueueStatus } from "../../api/types";
import { Activity, Clock, AlertTriangle, CheckCircle } from "lucide-react";

interface Props {
  status: QueueStatus;
}

export const QueueStatusCard: React.FC<Props> = ({ status }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-white capitalize">{status.queue_name} Queue</h3>
        <span className="flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
        </span>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col">
          <span className="text-sm text-slate-400 flex items-center gap-1"><Activity className="w-4 h-4"/> Active Workers</span>
          <span className="text-2xl font-semibold text-white">{status.workers_active}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-sm text-slate-400 flex items-center gap-1"><Clock className="w-4 h-4"/> Pending</span>
          <span className="text-2xl font-semibold text-amber-400">{status.tasks_pending}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-sm text-slate-400 flex items-center gap-1"><CheckCircle className="w-4 h-4"/> Processing</span>
          <span className="text-2xl font-semibold text-blue-400">{status.tasks_processing}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-sm text-slate-400 flex items-center gap-1"><AlertTriangle className="w-4 h-4"/> Failed</span>
          <span className="text-2xl font-semibold text-rose-400">{status.tasks_failed}</span>
        </div>
      </div>
    </div>
  );
};
