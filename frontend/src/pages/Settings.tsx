import { apiClientConfig } from "../api/client";
import { DEFAULT_ADMIN_USERNAME } from "../api/auth";
import {
  getBacktestingStatus,
  getBillingStatus,
  getContentStatus,
  getEnterpriseStatus,
  getIoTStatus,
  getTradingStatus,
} from "../api/endpoints";
import DataTable from "../components/common/DataTable";
import PageHeader from "../components/layout/PageHeader";
import { useAuth } from "../hooks/useAuth";
import { useApi } from "../hooks/useApi";

type SettingRow = {
  key: string;
  value: string;
};

export default function Settings() {
  const { user, mode } = useAuth();
  const tradingStatus = useApi(getTradingStatus, []);
  const contentStatus = useApi(getContentStatus, []);
  const iotStatus = useApi(getIoTStatus, []);
  const backtestingStatus = useApi(getBacktestingStatus, []);
  const billingStatus = useApi(getBillingStatus, []);
  const enterpriseStatus = useApi(getEnterpriseStatus, []);

  const pollIntervalMs = Number(import.meta.env.VITE_POLL_INTERVAL_MS ?? 5000);
  const appVersion = import.meta.env.VITE_APP_VERSION ?? "0.1.0-placeholder";

  const rows: SettingRow[] = [
    {
      key: "API base URL",
      value: apiClientConfig.baseUrl,
    },
    {
      key: "Mock fallback enabled",
      value: apiClientConfig.mockFallbackEnabled ? "true" : "false",
    },
    {
      key: "Poll interval",
      value: `${pollIntervalMs}ms`,
    },
    {
      key: "Dry-run state",
      value: tradingStatus.data?.dry_run === false ? "REAL_MODE" : "DRY_RUN",
    },
    {
      key: "Social approval required",
      value: contentStatus.data?.approval_required === false ? "false" : "true",
    },
    {
      key: "IoT dry-run state",
      value: iotStatus.data?.dry_run === false ? "REAL_MODE" : "IOT_DRY_RUN",
    },
    {
      key: "Primary strategy",
      value: String(backtestingStatus.data?.primary_strategy ?? "ob_aggressive"),
    },
    {
      key: "App version",
      value: appVersion,
    },
    {
      key: "Auth mode",
      value: mode === "dev" ? "DEV_BYPASS" : mode.toUpperCase(),
    },
    {
      key: "Current user",
      value: user ? `${user.username} (${user.role})` : "anonymous",
    },
    {
      key: "Billing provider",
      value: String(billingStatus.data?.provider ?? "N/A"),
    },
    {
      key: "Current plan tier",
      value: String(billingStatus.data?.plan_tier ?? "N/A"),
    },
    {
      key: "Enterprise license tier",
      value: String(enterpriseStatus.data?.license?.tier ?? "N/A"),
    },
    {
      key: "Whitelabel brand name",
      value: String(enterpriseStatus.data?.branding?.brand_name ?? "N/A"),
    },
    {
      key: "Whitelabel support contact",
      value: String(enterpriseStatus.data?.branding?.support_email ?? "N/A"),
    },
    {
      key: "Whitelabel custom domain",
      value: String(enterpriseStatus.data?.branding?.custom_domain ?? "N/A"),
    },
  ];

  return (
    <div className="space-y-5">
      <PageHeader
        title="Settings"
        subtitle="Read-only runtime and safety configuration summary."
      />

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Configuration Summary</h3>
        <p className="mt-1 text-xs text-slate-400">
          This view is read-only and intentionally excludes API keys, tokens, or secret values.
        </p>
        {user?.username === DEFAULT_ADMIN_USERNAME && (
          <p className="mt-2 rounded-md border border-amber-400/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-100">
            Warning: default admin username detected. Rotate credentials before production use.
          </p>
        )}
        <div className="mt-3">
          <DataTable<SettingRow>
            rows={rows}
            loading={
              tradingStatus.loading ||
              contentStatus.loading ||
              iotStatus.loading ||
              backtestingStatus.loading ||
              billingStatus.loading ||
              enterpriseStatus.loading
            }
            error={
              tradingStatus.error ||
              contentStatus.error ||
              iotStatus.error ||
              backtestingStatus.error ||
              billingStatus.error ||
              enterpriseStatus.error
            }
            rowKey={(row) => row.key}
            columns={[
              { key: "key", header: "Setting", render: (row) => row.key },
              { key: "value", header: "Value", render: (row) => row.value },
            ]}
          />
        </div>
      </section>
    </div>
  );
}
