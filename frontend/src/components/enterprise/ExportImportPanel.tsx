import React, { useState } from "react";
import { ExportBundle } from "../../api/types";
import { useT } from '../../hooks/useT';

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
  const { t } = useT();
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
      setErrorMsg(t('enterprise.confirm_secret_export_required'));
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
      setSuccessMsg(t('enterprise.export_complete'));
      setSecretConfirmInput("");
      setIncludeSecrets(false);
    } catch (err: any) {
      setErrorMsg(err.message || t('enterprise.export_failed'));
    } finally {
      setSubmitting(false);
    }
  };

  const isButtonDisabled = submitting || (includeSecrets && secretConfirmInput !== "CONFIRM_SECRET_EXPORT");

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Configuration Builder */}
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-4">
        <h4 className="text-lg font-bold text-white mb-1">{t('enterprise.export_config_title')}</h4>
        <p className="text-xs text-neutral-500 mb-4">{t('enterprise.export_config_desc')}</p>

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
            <label className="block text-xs font-medium text-neutral-400 mb-1">{t('enterprise.export_type')}</label>
            <select
              value={exportType}
              onChange={(e) => setExportType(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-850 text-neutral-250 focus:outline-none focus:border-violet-500 text-sm font-medium"
            >
              <option value="full">{t('enterprise.full_backup')}</option>
              <option value="partial">{t('enterprise.metadata_only')}</option>
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
              <label htmlFor="auditCheck" className="text-xs text-neutral-300">{t('enterprise.include_audit_logs')}</label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="contentCheck"
                checked={includeContent}
                onChange={(e) => setIncludeContent(e.target.checked)}
                className="rounded border-neutral-800 text-violet-600 focus:ring-violet-500 h-4 w-4 bg-neutral-950"
              />
              <label htmlFor="contentCheck" className="text-xs text-neutral-300">{t('enterprise.include_content')}</label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="backtestCheck"
                checked={includeBacktests}
                onChange={(e) => setIncludeBacktests(e.target.checked)}
                className="rounded border-neutral-800 text-violet-600 focus:ring-violet-500 h-4 w-4 bg-neutral-950"
              />
              <label htmlFor="backtestCheck" className="text-xs text-neutral-300">{t('enterprise.include_backtests')}</label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="schedCheck"
                checked={includeScheduler}
                onChange={(e) => setIncludeScheduler(e.target.checked)}
                className="rounded border-neutral-800 text-violet-600 focus:ring-violet-500 h-4 w-4 bg-neutral-950"
              />
              <label htmlFor="schedCheck" className="text-xs text-neutral-300">{t('enterprise.include_scheduler')}</label>
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
                {t('enterprise.include_secrets')}
              </label>
            </div>
          </div>

          {/* Safety Typed Confirmation Input */}
          {includeSecrets && (
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg space-y-2 mt-2">
              <div className="text-xs text-amber-300 font-semibold">
                {t('enterprise.export_secret_warning_text')} <span className="font-mono text-white select-all">CONFIRM_SECRET_EXPORT</span>
              </div>
              <input
                type="text"
                required
                placeholder={t('enterprise.confirm_secret_export_placeholder')}
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
            {submitting ? t('enterprise.exporting') : t('enterprise.generate_export')}
          </button>
        </form>
      </div>

      {/* Export Bundles List */}
      <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-4 flex flex-col justify-between">
        <div>
          <h4 className="text-lg font-bold text-white mb-4">{t('enterprise.available_bundles')}</h4>
          {exportsList.length === 0 ? (
            <div className="p-8 text-center text-neutral-500 text-xs italic">{t('enterprise.no_bundles')}</div>
          ) : (
            <div className="space-y-3">
              {exportsList.map((bundle) => (
                <div key={bundle.id} className="p-3 bg-neutral-900/40 border border-neutral-850 rounded-lg flex items-center justify-between text-xs">
                  <div>
                    <span className="font-mono font-bold text-neutral-200">{bundle.id}</span>
                    <span className="text-neutral-500 block mt-1">
                      {new Date(bundle.created_at).toLocaleString()} • {t('common.type')}: <span className="capitalize">{bundle.export_type}</span>
                    </span>
                    <span className="text-neutral-500 block mt-0.5">
                      {t('enterprise.secrets_included')}: {bundle.include_secrets ? t('common.yes') : t('common.no')}
                    </span>
                  </div>

                  <div className="flex gap-2">
                    {bundle.file_path ? (
                      <a
                        href={bundle.file_path}
                        className="px-2.5 py-1 bg-violet-600/10 hover:bg-violet-600/20 text-violet-400 border border-violet-500/20 rounded font-semibold text-[11px] transition"
                      >
                        {t('common.download')}
                      </a>
                    ) : (
                      <span className="text-neutral-500 font-semibold px-2">{t('common.pending')}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="border-t border-neutral-900 pt-4 text-[11px] text-neutral-500">
          {t('enterprise.export_restore_note_text')}
        </div>
      </div>
    </div>
  );
}
export default ExportImportPanel;
