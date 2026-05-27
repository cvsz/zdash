import { apiClientConfig } from "../api/client";
import {
  getBacktestingStatus,
  getContentStatus,
  getIoTStatus,
  getTradingStatus,
} from "../api/endpoints";
import DataTable from "../components/common/DataTable";
import PageHeader from "../components/layout/PageHeader";
import { useApi } from "../hooks/useApi";

type SettingRow = {
  key: string;
  value: string;
};

export default function Settings() {
  const tradingStatus = useApi(getTradingStatus, []);
  const contentStatus = useApi(getContentStatus, []);
  const iotStatus = useApi(getIoTStatus, []);
  const backtestingStatus = useApi(getBacktestingStatus, []);

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
        <div className="mt-3">
          <DataTable<SettingRow>
            rows={rows}
            loading={
              tradingStatus.loading ||
              contentStatus.loading ||
              iotStatus.loading ||
              backtestingStatus.loading
            }
            error={
              tradingStatus.error ||
              contentStatus.error ||
              iotStatus.error ||
              backtestingStatus.error
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
