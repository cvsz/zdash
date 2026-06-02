import React, { useState } from "react";
import { EnterpriseLicense } from "../../api/types";
import { useT } from '../../hooks/useT';

interface LicenseStatusCardProps {
  license: EnterpriseLicense | null;
  onApply: (key: string) => Promise<any>;
  onRevoke: () => Promise<any>;
}

export function LicenseStatusCard({ license, onApply, onRevoke }: LicenseStatusCardProps) {
  const { t } = useT();
  const [licenseKey, setLicenseKey] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!licenseKey.trim()) return;

    setSubmitting(true);
    setErrorMsg(null);

    try {
      const res = await onApply(licenseKey);
      if (res && res.ok === false) {
        setErrorMsg(res.error || t('enterprise.invalid_license_key'));
      } else {
        setLicenseKey("");
      }
    } catch (err: any) {
      setErrorMsg(err.message || t('enterprise.failed_to_activate'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevoke = async () => {
    if (!window.confirm(t('enterprise.deactivate_license_confirm'))) {
      return;
    }
    setSubmitting(true);
    setErrorMsg(null);
    try {
      await onRevoke();
    } catch (err: any) {
      setErrorMsg(err.message || t('enterprise.failed_to_revoke'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 rounded-xl border border-neutral-800 bg-neutral-950/20 space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">{t('enterprise.licensing')}</div>
          <h4 className="text-xl font-bold text-white mt-1">{t('enterprise.enterprise_licensing_status')}</h4>
        </div>

        <div className="flex gap-2">
          {license && (
            <span
              className={`px-3 py-1 text-xs font-semibold rounded-full border ${
                license.status === "active"
                  ? "text-green-400 bg-green-500/10 border-green-500/20"
                  : "text-rose-400 bg-rose-500/10 border-rose-500/20"
              }`}
            >
              {t('common.status')}: <span className="capitalize">{license.status || "none"}</span>
            </span>
          )}
        </div>
      </div>

      {errorMsg && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg text-xs font-semibold">
          {errorMsg}
        </div>
      )}

      {license && license.status === "active" ? (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-neutral-300 border-b border-neutral-900 pb-4">
            <div>
              <span className="text-neutral-500 block text-xs uppercase tracking-wider font-semibold">{t('enterprise.tier')}</span>
              <span className="font-semibold text-white capitalize mt-1 block">{license.tier}</span>
            </div>
            <div>
              <span className="text-neutral-500 block text-xs uppercase tracking-wider font-semibold">{t('enterprise.seats')}</span>
              <span className="font-semibold text-white mt-1 block">{license.seats} {t('enterprise.operators')}</span>
            </div>
            <div>
              <span className="text-neutral-500 block text-xs uppercase tracking-wider font-semibold">{t('enterprise.issued_to')}</span>
              <span className="font-semibold text-white mt-1 block">{license.issued_to || "Zeaz Enterprise Partner"}</span>
            </div>
            <div>
              <span className="text-neutral-500 block text-xs uppercase tracking-wider font-semibold">{t('enterprise.expiration')}</span>
              <span className="font-semibold text-white mt-1 block">
                {license.expires_at ? new Date(license.expires_at).toLocaleDateString() : t('enterprise.never')}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              <span className="text-xs text-neutral-400">
                {license.offline_mode ? t('enterprise.offline_activation') : t('enterprise.connected_online')}
              </span>
            </div>

            <button
              onClick={handleRevoke}
              disabled={submitting}
              className="py-2 px-4 rounded-lg bg-rose-950/20 hover:bg-rose-950/40 text-rose-400 border border-rose-900/30 hover:border-rose-900/50 text-xs font-semibold transition"
            >
              {t('enterprise.revoke_license')}
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleApply} className="space-y-4">
          <div className="space-y-2">
            <label className="block text-xs font-medium text-neutral-400">{t('enterprise.enter_license_key')}</label>
            <input
              type="password"
              placeholder={t('enterprise.license_key_placeholder')}
              value={licenseKey}
              onChange={(e) => setLicenseKey(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-200 placeholder-neutral-600 focus:outline-none focus:border-violet-500 text-sm font-mono"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs border border-violet-500/20 transition disabled:opacity-50"
          >
            {submitting ? t('enterprise.activating') : t('enterprise.activate_license')}
          </button>
        </form>
      )}
    </div>
  );
}
export default LicenseStatusCard;
