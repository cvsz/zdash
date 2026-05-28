import React from "react";
import type { TaskItem } from "../../api/types";

interface Props {
  tasks: TaskItem[];
}

export const WorkerRunTable: React.FC<Props> = ({ tasks }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
      <table className="min-w-full text-left text-sm text-gray-300">
        <thead className="bg-slate-800 border-b border-slate-700">
          <tr>
            <th className="px-4 py-3 font-medium">Task ID</th>
            <th className="px-4 py-3 font-medium">Type</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">Created At</th>
            <th className="px-4 py-3 font-medium">Retries</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {tasks.map((task) => (
            <tr key={task.id} className="hover:bg-slate-800/50 transition-colors">
              <td className="px-4 py-3 text-slate-400 font-mono text-xs">{task.id}</td>
              <td className="px-4 py-3 font-medium text-white">{task.type}</td>
              <td className="px-4 py-3 capitalize">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  task.status === "completed" ? "bg-emerald-500/10 text-emerald-400" :
                  task.status === "failed" ? "bg-rose-500/10 text-rose-400" :
                  task.status === "processing" ? "bg-blue-500/10 text-blue-400" :
                  "bg-amber-500/10 text-amber-400"
                }`}>
                  {task.status}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-400">{new Date(task.created_at).toLocaleString()}</td>
              <td className="px-4 py-3 text-slate-400">{task.retries}</td>
            </tr>
          ))}
          {tasks.length === 0 && (
            <tr>
              <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                No tasks found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
