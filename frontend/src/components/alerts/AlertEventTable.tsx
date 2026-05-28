import React from "react";
import type { AlertEvent } from "../../api/types";

interface Props {
  events: AlertEvent[];
}

export const AlertEventTable: React.FC<Props> = ({ events }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
      <table className="min-w-full text-left text-sm text-gray-300">
        <thead className="bg-slate-800 border-b border-slate-700">
          <tr>
            <th className="px-4 py-3 font-medium">Message</th>
            <th className="px-4 py-3 font-medium">Severity</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">Triggered At</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {events.map((event) => (
            <tr key={event.id} className="hover:bg-slate-800/50 transition-colors">
              <td className="px-4 py-3 font-medium text-white">{event.message}</td>
              <td className="px-4 py-3 capitalize">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  event.severity === "critical" ? "bg-rose-500/10 text-rose-400" :
                  event.severity === "error" ? "bg-orange-500/10 text-orange-400" :
                  event.severity === "warning" ? "bg-amber-500/10 text-amber-400" :
                  "bg-blue-500/10 text-blue-400"
                }`}>
                  {event.severity}
                </span>
              </td>
              <td className="px-4 py-3 capitalize">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  event.status === "resolved" ? "bg-emerald-500/10 text-emerald-400" :
                  event.status === "acknowledged" ? "bg-amber-500/10 text-amber-400" :
                  "bg-rose-500/10 text-rose-400"
                }`}>
                  {event.status}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-400">{new Date(event.triggered_at).toLocaleString()}</td>
            </tr>
          ))}
          {events.length === 0 && (
            <tr>
              <td colSpan={4} className="px-4 py-8 text-center text-slate-500">
                No alert events found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
