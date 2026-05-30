import React, { useState } from "react";
import { ExportBundle } from "../../api/types";

interface ExportImportPanelProps {
  exportsList: ExportBundle[];
  onCreateExport: (req: {
    export_type: string;
    include_audit_logs: boolean;
    include_content: boolean;
    include_backtests: boolean;
    include_scheduler: boolean;
    include_secrets: boolean;
    secret_export_confirmation?: string;
  }) => Promise<any>;
}

export function ExportImportPanel({ exportsList, onCreateExport }: ExportImportPanelProps) {
  const [exportType, setExportType] = useState("full");
  const [includeAuditLogs, setIncludeAuditLogs] = useState(true);
  const [includeContent, setIncludeContent] = useState(true);
  const [includeBacktests, setIncludeBacktests] = useState(false);
  const [includeScheduler, setIncludeScheduler] = useState(true);
  const [includeSecrets, setIncludeSecrets] = useState(false);
  const [secretConfirmInput, setSecretConfirmInput] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (includeSecrets && secretConfirmInput !== "CONFIRM_SECRET_EXPORT") {
      setErrorMsg("You must confirm secret export by typing CONFIRM_SECRET_EXPORT");
      return;
    }

    setSubmitting(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      await onCreateExport({
        export_type: exportType,
        include_audit_logs: includeAuditLogs,
        include_content: includeContent,
        include_backtests: includeBacktests,
        include_scheduler: includeScheduler,
        include_secrets: includeSecrets,
        secret_export_confirmation: includeSecrets ? secretConfirmInput : undefined,
      });
      setSuccessMsg("System configuration bundle generated successfully.");
      setSecretConfirmInput("");
      setIncludeSecrets(false);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to generate bundle.");
    } finally {
      setSubmitting(false);
    }
  };

  const isButtonDisabled = submitting || (includeSecrets && secretConfirmInput !== "CONFIRM_SECRET_EXPORT");

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Configuration Builder */}
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-4">
        <h4 className="text-lg font-bold text-white mb-1">Export Configuration Package</h4>
        <p className="text-xs text-neutral-500 mb-4">Pack up database logs, schedules, and assets for backup or migrations.</p>

        {successMsg && (
          <div className="p-3 bg-green-500/10 border border-green-500/20 text-green-400 rounded-lg text-xs font-semibold">
            {successMsg}
          </div>
        )}

        {errorMsg && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg text-xs font-semibold">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleGenerate} className="space-y-4 text-sm text-neutral-300">
          <div>
            <label className="block text-xs font-medium text-neutral-400 mb-1">Export Type</label>
            <select
              value={exportType}
              onChange={(e) => setExportType(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-850 text-neutral-250 focus:outline-none focus:border-violet-500 text-sm font-medium"
            >
              <option value="full">Full Backup (All Selected Databases)</option>
              <option value="partial">Metadata & Schedules Only</option>
            </select>
          </div>

          <div className="space-y-2 pt-2">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="auditCheck"
                checked={includeAuditLogs}
                onChange={(e) => setIncludeAuditLogs(e.target.checked)}
                className="rounded border-neutral-800 text-violet-600 focus:ring-violet-500 h-4 w-4 bg-neutral-950"
              />
              <label htmlFor="auditCheck" className="text-xs text-neutral-300">Include Audit Logs & User Sessions</label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="contentCheck"
                checked={includeContent}
                onChange={(e) => setIncludeContent(e.target.checked)}
                className="rounded border-neutral-800 text-violet-600 focus:ring-violet-500 h-4 w-4 bg-neutral-950"
              />
              <label htmlFor="contentCheck" className="text-xs text-neutral-300">Include Generated Content Items & Media Prompts</label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="backtestCheck"
                checked={includeBacktests}
                onChange={(e) => setIncludeBacktests(e.target.checked)}
                className="rounded border-neutral-800 text-violet-600 focus:ring-violet-500 h-4 w-4 bg-neutral-950"
              />
              <label htmlFor="backtestCheck" className="text-xs text-neutral-300">Include Backtesting Runs & Optimization Charts</label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="schedCheck"
                checked={includeScheduler}
                onChange={(e) => setIncludeScheduler(e.target.checked)}
                className="rounded border-neutral-800 text-violet-600 focus:ring-violet-500 h-4 w-4 bg-neutral-950"
              />
              <label htmlFor="schedCheck" className="text-xs text-neutral-300">Include Automation Scheduler Tasks & Chronology</label>
            </div>

            <div className="flex items-center gap-2 border-t border-neutral-900 pt-3">
              <input
                type="checkbox"
                id="secretsCheck"
                checked={includeSecrets}
                onChange={(e) => setIncludeSecrets(e.target.checked)}
                className="rounded border-neutral-800 text-violet-600 focus:ring-violet-500 h-4 w-4 bg-neutral-950"
              />
              <label htmlFor="secretsCheck" className="text-xs text-amber-400 font-semibold">
                Include Encryption Keys & Private API Credentials
              </label>
            </div>
          </div>

          {/* Safety Typed Confirmation Input */}
          {includeSecrets && (
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg space-y-2 mt-2">
              <div className="text-xs text-amber-300 font-semibold">
                ⚠ WARNING: Exporting raw secrets and keys is high-risk. Please confirm you have correct credentials by typing exactly: <span className="font-mono text-white select-all">CONFIRM_SECRET_EXPORT</span>
              </div>
              <input
                type="text"
                required
                placeholder="Type CONFIRM_SECRET_EXPORT"
                value={secretConfirmInput}
                onChange={(e) => setSecretConfirmInput(e.target.value)}
                className="w-full px-3 py-1.5 rounded bg-neutral-900 border border-neutral-800 text-neutral-200 placeholder-neutral-700 text-xs font-mono"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isButtonDisabled}
            className="w-full py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs border border-violet-500/20 transition disabled:opacity-50"
          >
            {submitting ? "Exporting..." : "Generate Export Bundle"}
          </button>
        </form>
      </div>

      {/* Export Bundles List */}
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-4 flex flex-col justify-between">
        <div>
          <h4 className="text-lg font-bold text-white mb-4">Available Bundles</h4>
          {exportsList.length === 0 ? (
            <div className="p-8 text-center text-neutral-500 text-xs italic">No bundles available.</div>
          ) : (
            <div className="space-y-3">
              {exportsList.map((bundle) => (
                <div key={bundle.id} className="p-3 bg-neutral-900/40 border border-neutral-850 rounded-lg flex items-center justify-between text-xs">
                  <div>
                    <span className="font-mono font-bold text-neutral-200">{bundle.id}</span>
                    <span className="text-neutral-500 block mt-1">
                      {new Date(bundle.created_at).toLocaleString()} • Type: <span className="capitalize">{bundle.export_type}</span>
                    </span>
                    <span className="text-neutral-500 block mt-0.5">
                      Secrets included: <span className="font-semibold">{bundle.include_secrets ? "Yes" : "No"}</span>
                    </span>
                  </div>

                  <div className="flex gap-2">
                    {bundle.file_path ? (
                      <a
                        href={bundle.file_path}
                        className="px-2.5 py-1 bg-violet-600/10 hover:bg-violet-600/20 text-violet-400 border border-violet-500/20 rounded font-semibold text-[11px] transition"
                      >
                        Download
                      </a>
                    ) : (
                      <span className="text-neutral-500 font-semibold px-2">Pending</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="border-t border-neutral-900 pt-4 text-[11px] text-neutral-500">
          💡 System restores can be triggered via CLI. Backups are fully encrypted using AES-GCM standards.
        </div>
      </div>
    </div>
  );
}
export default ExportImportPanel;
