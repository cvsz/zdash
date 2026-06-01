import { useEffect, useMemo, useState } from "react";

import {
  approveExecution,
  dryRunExecution,
  getTradingStatus,
  runTradingScan,
  validateSignal,
} from "../api/endpoints";
import type { RiskDecision, TradingScanResult, TradingSignal } from "../api/types";
import Button from "../components/common/Button";
import MetricCard from "../components/common/MetricCard";
import SectionCard from "../components/common/SectionCard";
import Badge from "../components/common/Badge";
import PageHeader from "../components/layout/PageHeader";
import AITraderSimulationCard from "../components/trading/AITraderSimulationCard";
import DryRunBanner from "../components/trading/DryRunBanner";
import SignalTable from "../components/trading/SignalTable";
import XauScannerPanel from "../components/trading/XauScannerPanel";
import { AGENT_NAME_BY_ID } from "../constants/agents";
import { useApi } from "../hooks/useApi";
import { useT } from "../hooks/useT";

const defaultSnapshot = {
  balance: 10000,
  equity: 9950,
  peak_equity: 10000,
  daily_start_equity: 10020,
  open_positions: 0,
  floating_pnl: -50,
  realized_pnl_today: 0,
};

export default function XauDashboard() {
  const { t } = useT();
  const tradingStatus = useApi(getTradingStatus, []);
  const [scanLoading, setScanLoading] = useState(false);
  const [executionLoading, setExecutionLoading] = useState(false);
  const [riskLoading, setRiskLoading] = useState(false);
  const [scanResult, setScanResult] = useState<TradingScanResult | null>(null);

  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [selectedSignal, setSelectedSignal] = useState<TradingSignal | null>(null);
  const [validation, setValidation] = useState<{
    valid: boolean;
    reason: string;
    warnings: string[];
  } | null>(null);
  const [riskDecision, setRiskDecision] = useState<RiskDecision | null>(null);
  const [executionMessage, setExecutionMessage] = useState<string | null>(null);
  const [executionStatus, setExecutionStatus] = useState<string>("idle");
  const [scanSummary, setScanSummary] = useState<string>("Scan not run yet.");
  const [scanTimestamp, setScanTimestamp] = useState<string>("-");
  const [lastError, setLastError] = useState<string | null>(null);

  const dryRunEnabled = tradingStatus.data?.dry_run !== false;

  async function performScan() {
    setScanLoading(true);
    setLastError(null);
    try {
      const result = await runTradingScan({ symbol: "XAUUSD", timeframe: "M5" });
      setScanResult(result);
      const nextSignals = result.latest_signal ? [result.latest_signal] : [];
      setSignals(nextSignals);
      setScanSummary(result.ai_summary || "No AI summary returned.");
      setScanTimestamp(result.timestamp);

      if (nextSignals.length > 0) {
        const primary = nextSignals[0];
        setSelectedSignal(primary);
        const validationResult = await validateSignal(primary);
        setValidation({
          valid: validationResult.valid,
          reason: validationResult.reason,
          warnings: validationResult.warnings,
        });
      } else {
        setSelectedSignal(null);
        setValidation(null);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setLastError(message);
    } finally {
      setScanLoading(false);
    }
  }

  async function onSelectSignal(signal: TradingSignal) {
    setSelectedSignal(signal);
    setLastError(null);
    try {
      const validationResult = await validateSignal(signal);
      setValidation({
        valid: validationResult.valid,
        reason: validationResult.reason,
        warnings: validationResult.warnings,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setLastError(message);
    }
  }

  async function onCheckRiskApproval() {
    if (!selectedSignal) {
      return;
    }

    setRiskLoading(true);
    setLastError(null);
    try {
      const decision = await approveExecution({ signal: selectedSignal, snapshot: defaultSnapshot });
      setRiskDecision(decision);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setLastError(message);
    } finally {
      setRiskLoading(false);
    }
  }

  async function onDryRunExecute() {
    if (!selectedSignal) {
      return;
    }

    setExecutionLoading(true);
    setExecutionStatus("running");
    setLastError(null);
    try {
      const result = await dryRunExecution({ signal: selectedSignal, dry_run: true, confirmation: true });
      setExecutionStatus(result.status);
      setExecutionMessage(result.message);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setExecutionStatus("failed");
      setExecutionMessage(null);
      setLastError(message);
    } finally {
      setExecutionLoading(false);
    }
  }

  useEffect(() => {
    void performScan();
  }, []);

  const validationVariant = validation?.valid ? "success" : validation ? "danger" : "muted";
  const riskVariant = riskDecision?.approved ? "success" : riskDecision ? "warning" : "muted";

  const signalStats = useMemo(() => {
    const count = signals.length;
    const averageConfidence =
      count === 0
        ? 0
        : signals.reduce((total, signal) => total + signal.confidence, 0) / count;
    return { count, averageConfidence };
  }, [signals]);

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('trading.xau_title')}
        subtitle={`${AGENT_NAME_BY_ID.trading} ${t('trading.subtitle')}`}
        actions={
          <Badge variant={dryRunEnabled ? "success" : "danger"}>
            {dryRunEnabled ? t('trading.dry_run') : t('trading.live_mode_banner')}
          </Badge>
        }
      />

      <DryRunBanner text={t('trading.dry_run_banner')} />

      <AITraderSimulationCard />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label={t('trading.scanner_status')} value={scanLoading ? t('trading.scanner_status_scanning') : t('trading.scanner_status_ready')} />
        <MetricCard label={t('trading.signals')} value={signalStats.count} />
        <MetricCard
          label={t('trading.avg_confidence')}
          value={`${(signalStats.averageConfidence * 100).toFixed(1)}%`}
        />
        <MetricCard label={t('trading.funnel_filter')} value="21/10/3 ACTIVE" delta="Order block + trend confirmation" />
      </div>

      <XauScannerPanel scanResult={scanResult} loading={scanLoading} onScan={() => void performScan()} />

      <SectionCard
        title={t('trading.signal_validation')}
        subtitle={t('trading.signal_validation_subtitle')}
        actions={<Badge variant={validationVariant}>{validation ? (validation.valid ? t('trading.valid') : t('trading.invalid')) : t('trading.pending')}</Badge>}
      >
        <div className="space-y-3 text-sm text-text-secondary">
          <p>
            <span className="font-semibold text-text-primary">{t('trading.ai_summary')}:</span> {scanSummary}
          </p>
          <p>
            <span className="font-semibold text-text-primary">{t('trading.latest_scan')}:</span> {scanTimestamp}
          </p>
          <p>
            <span className="font-semibold text-text-primary">{t('trading.validation_reason')}:</span> {validation?.reason ?? t('trading.no_signal_selected')}
          </p>
          {validation?.warnings?.length ? (
            <ul className="list-disc space-y-1 pl-5 text-amber-200">
              {validation.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : null}
        </div>
      </SectionCard>

      <SectionCard
        title={t('trading.latest_signals')}
        subtitle={t('trading.latest_signals_subtitle')}
        actions={selectedSignal ? <Badge variant="normal">{t('trading.selected')}: {selectedSignal.symbol}</Badge> : null}
      >
        <SignalTable signals={signals} onSelect={onSelectSignal} />
      </SectionCard>

      <SectionCard title={t('trading.risk_approval')} subtitle={t('trading.risk_approval_subtitle')}>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="secondary"
            disabled={!selectedSignal || riskLoading}
            onClick={() => void onCheckRiskApproval()}
          >
            {riskLoading ? t('trading.checking') : t('trading.check_risk_approval')}
          </Button>
          <Badge variant={riskVariant}>
            {riskDecision ? (riskDecision.approved ? t('trading.approved') : t('trading.not_approved')) : t('trading.not_checked')}
          </Badge>
          {riskDecision ? <span className="text-sm text-text-secondary">{riskDecision.reason}</span> : null}
        </div>
      </SectionCard>

      <SectionCard title={t('trading.dry_run_execution')} subtitle={t('trading.dry_run_execution_subtitle')}>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="primary"
            disabled={!selectedSignal || executionLoading}
            onClick={() => void onDryRunExecute()}
          >
            {executionLoading ? t('trading.executing') : t('trading.dry_run_execute')}
          </Button>
          <Badge variant={executionStatus === "failed" ? "danger" : executionStatus === "idle" ? "muted" : "success"}>
            {executionStatus.toUpperCase()}
          </Badge>
          {executionMessage ? <span className="text-sm text-text-secondary">{executionMessage}</span> : null}
        </div>
      </SectionCard>

      {lastError ? (
        <div className="rounded-card border border-state-danger/20 bg-state-danger/10 px-4 py-3 text-sm text-state-danger">
          {lastError}
        </div>
      ) : null}

      <p className="rounded-card border border-border bg-panel/50 px-4 py-3 text-xs text-text-secondary">
        {t('trading.disclaimer')}
      </p>
    </div>
  );
}
