import React from "react";
import type { AlertRule } from "../../api/types";
import { Bell, BellOff } from "lucide-react";

interface Props {
  rules: AlertRule[];
}

export const AlertRuleTable: React.FC<Props> = ({ rules }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
      <table className="min-w-full text-left text-sm text-gray-300">
        <thead className="bg-slate-800 border-b border-slate-700">
          <tr>
            <th className="px-4 py-3 font-medium">Name</th>
            <th className="px-4 py-3 font-medium">Condition</th>
            <th className="px-4 py-3 font-medium">Severity</th>
            <th className="px-4 py-3 font-medium">Channels</th>
            <th className="px-4 py-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {rules.map((rule) => (
            <tr key={rule.id} className="hover:bg-slate-800/50 transition-colors">
              <td className="px-4 py-3 font-medium text-white">{rule.name}</td>
              <td className="px-4 py-3 text-slate-400 font-mono text-xs">{rule.condition}</td>
              <td className="px-4 py-3 capitalize">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  rule.severity === "critical" ? "bg-rose-500/10 text-rose-400" :
                  rule.severity === "error" ? "bg-orange-500/10 text-orange-400" :
                  rule.severity === "warning" ? "bg-amber-500/10 text-amber-400" :
                  "bg-blue-500/10 text-blue-400"
                }`}>
                  {rule.severity}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-400">{rule.channels.length}</td>
              <td className="px-4 py-3">
                {rule.enabled ? (
                  <span className="text-emerald-400 flex items-center gap-1"><Bell className="w-3 h-3"/> Enabled</span>
                ) : (
                  <span className="text-slate-500 flex items-center gap-1"><BellOff className="w-3 h-3"/> Disabled</span>
                )}
              </td>
            </tr>
          ))}
          {rules.length === 0 && (
            <tr>
              <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                No alert rules found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
