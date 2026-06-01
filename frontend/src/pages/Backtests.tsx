import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  checkPromotion,
  getBacktestingStatus,
  listBacktestResults,
  listStrategies,
  runBacktest,
  runOptimization,
} from "../api/endpoints";
import type { BacktestResult, OptimizationResult } from "../api/types";
import Badge from "../components/common/Badge";
import Button from "../components/common/Button";
import DataTable from "../components/common/DataTable";
import MetricCard from "../components/common/MetricCard";
import PageHeader from "../components/layout/PageHeader";
import { AGENT_NAME_BY_ID } from "../constants/agents";
import { useApi } from "../hooks/useApi";
import { useT } from "../hooks/useT";
import { formatPercent } from "../utils/format";

function getMonthlyRows(result: BacktestResult): Array<{ month: string; value: number }> {
  if (Array.isArray(result.monthly_returns)) {
    return result.monthly_returns;
  }

  const fromMetrics = result.metrics.monthly_return_table;
  if (!fromMetrics) {
    return [];
  }

  return Object.entries(fromMetrics).map(([month, value]) => ({
    month,
    value,
  }));
}

export default function Backtests() {
  const { t } = useT();
  const backtestingStatus = useApi(getBacktestingStatus, []);
  const strategiesState = useApi(listStrategies, []);
  const resultsState = useApi(listBacktestResults, []);

  const [results, setResults] = useState<BacktestResult[]>([]);
  const [selectedResultId, setSelectedResultId] = useState<string | null>(null);
  const [runningBacktest, setRunningBacktest] = useState(false);
  const [runningOptimization, setRunningOptimization] = useState(false);
  const [checkingPromotion, setCheckingPromotion] = useState(false);

  const [runStrategy, setRunStrategy] = useState("ob_aggressive");
  const [runSymbol, setRunSymbol] = useState("XAUUSD");
  const [runTimeframe, setRunTimeframe] = useState("M5");

  const [optimizationMetric, setOptimizationMetric] = useState("profit_factor");
  const [optimization, setOptimization] = useState<OptimizationResult | null>(null);
  const [promotionStatus, setPromotionStatus] = useState<string>("Not checked");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!resultsState.data) {
      return;
    }
    setResults(resultsState.data);
    if (!selectedResultId && resultsState.data.length > 0) {
      setSelectedResultId(resultsState.data[0].id);
    }
  }, [resultsState.data, selectedResultId]);

  const selectedResult =
    results.find((result) => result.id === selectedResultId) ?? results[0] ?? null;

  const monthlyRows = selectedResult ? getMonthlyRows(selectedResult) : [];

  async function onRunBacktest(event: React.FormEvent) {
    event.preventDefault();
    setRunningBacktest(true);
    setMessage(null);
    setError(null);

    try {
      const result = await runBacktest({
        strategy: runStrategy,
        symbol: runSymbol,
        timeframe: runTimeframe,
        initial_balance: 10000,
      });
      setResults((previous) => [result, ...previous]);
      setSelectedResultId(result.id);
      setMessage(`Backtest completed for ${result.strategy}.`);
    } catch (caught) {
      const text = caught instanceof Error ? caught.message : String(caught);
      setError(text);
    } finally {
      setRunningBacktest(false);
    }
  }

  async function onRunOptimization(event: React.FormEvent) {
    event.preventDefault();
    setRunningOptimization(true);
    setMessage(null);
    setError(null);

    try {
      const result = await runOptimization({
        strategy: runStrategy,
        symbol: runSymbol,
        timeframe: runTimeframe,
        sort_metric: optimizationMetric,
      });
      setOptimization(result);
      setMessage(`Optimization completed with ${result.executed_combinations} combinations.`);
    } catch (caught) {
      const text = caught instanceof Error ? caught.message : String(caught);
      setError(text);
    } finally {
      setRunningOptimization(false);
    }
  }

  async function onCheckPromotion() {
    if (!selectedResult) {
      return;
    }

    setCheckingPromotion(true);
    setMessage(null);
    setError(null);

    try {
      const decision = await checkPromotion(selectedResult.id);
      setPromotionStatus(
        decision.approved
          ? "Approved for paper promotion (live trading still disabled)."
          : `Not approved: ${decision.reason}`,
      );
    } catch (caught) {
      const text = caught instanceof Error ? caught.message : String(caught);
      setError(text);
    } finally {
      setCheckingPromotion(false);
    }
  }

  const strategyNames = useMemo(() => {
    const source = strategiesState.data ?? [];
    return source.map((item) => String(item.name ?? "unknown"));
  }, [strategiesState.data]);

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('backtests.backtests')}
        subtitle={t('backtests.backtests_subtitle', { agent: AGENT_NAME_BY_ID.joe })}
        actions={<Badge variant="warning">{t('backtests.live_trading_disabled')}</Badge>}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label={t('backtests.backtesting_enabled')} value={backtestingStatus.data?.enabled ? "YES" : "NO"} />
        <MetricCard label={t('backtests.dataset_source')} value={String(backtestingStatus.data?.dataset_source ?? "unknown")} />
        <MetricCard label={t('backtests.primary_strategy')} value={String(backtestingStatus.data?.primary_strategy ?? "-")} />
        <MetricCard label={t('backtests.stored_results')} value={results.length} />
      </div>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('backtests.strategy_list')}</h3>
        <p className="mt-1 text-xs text-text-dim">{t('backtests.strategy_list_subtitle')}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {strategyNames.length === 0 ? (
            <Badge variant="muted">{t('backtests.no_strategies')}</Badge>
          ) : (
            strategyNames.map((name) => (
              <Badge key={name} variant="normal">
                {name}
              </Badge>
            ))
          )}
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-2">
        <form className="rounded-card border border-border bg-panel p-4" onSubmit={(event) => void onRunBacktest(event)}>
          <h3 className="text-sm font-semibold text-white">{t('backtests.run_backtest')}</h3>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <label className="text-xs text-text-secondary">
              {t('backtests.strategy')}
              <input
                className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
                value={runStrategy}
                onChange={(event) => setRunStrategy(event.target.value)}
              />
            </label>
            <label className="text-xs text-text-secondary">
              {t('backtests.symbol')}
              <input
                className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
                value={runSymbol}
                onChange={(event) => setRunSymbol(event.target.value)}
              />
            </label>
            <label className="text-xs text-text-secondary">
              {t('backtests.timeframe')}
              <input
                className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
                value={runTimeframe}
                onChange={(event) => setRunTimeframe(event.target.value)}
              />
            </label>
          </div>
          <div className="mt-3">
            <Button type="submit" variant="primary" disabled={runningBacktest}>
              {runningBacktest ? t('backtests.running') : t('backtests.run')}
            </Button>
          </div>
        </form>

        <form className="rounded-card border border-border bg-panel p-4" onSubmit={(event) => void onRunOptimization(event)}>
          <h3 className="text-sm font-semibold text-white">{t('backtests.optimization')}</h3>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            <label className="text-xs text-text-secondary">
              {t('backtests.sort_metric')}
              <select
                className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
                value={optimizationMetric}
                onChange={(event) => setOptimizationMetric(event.target.value)}
              >
                <option value="profit_factor">profit_factor</option>
                <option value="net_profit_percent">net_profit_percent</option>
                <option value="max_drawdown_percent">max_drawdown_percent</option>
              </select>
            </label>
          </div>
          <div className="mt-3">
            <Button type="submit" variant="secondary" disabled={runningOptimization}>
              {runningOptimization ? t('backtests.optimizing') : t('backtests.run_optimization')}
            </Button>
          </div>
        </form>
      </div>

      {selectedResult ? (
        <section className="rounded-card border border-border bg-panel p-4">
          <h3 className="text-sm font-semibold text-white">{t('backtests.backtest_results_and_metrics')}</h3>
          <div className="mt-3 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <MetricCard label={t('backtests.win_rate')} value={formatPercent(selectedResult.metrics.win_rate)} />
            <MetricCard label={t('backtests.profit_factor')} value={selectedResult.metrics.profit_factor.toFixed(2)} />
            <MetricCard label={t('backtests.net_profit')} value={formatPercent(selectedResult.metrics.net_profit_percent)} />
            <MetricCard label={t('backtests.max_drawdown')} value={formatPercent(selectedResult.metrics.max_drawdown_percent)} severity="warning" />
            <MetricCard label={t('backtests.total_trades')} value={selectedResult.metrics.total_trades} />
          </div>

          <div className="mt-4 h-64 rounded-md border border-border bg-canvas-lighter/60 p-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={selectedResult.equity_curve ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="x" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Line type="monotone" dataKey="y" stroke="#22d3ee" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-4">
            <DataTable<{ month: string; value: number }>
              rows={monthlyRows}
              rowKey={(row) => row.month}
              emptyMessage={t('backtests.no_monthly_returns')}
              columns={[
                { key: "month", header: t('backtests.month'), render: (row) => row.month },
                { key: "value", header: t('backtests.return'), render: (row) => formatPercent(row.value) },
              ]}
            />
          </div>
        </section>
      ) : null}

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('backtests.result_history')}</h3>
        <div className="mt-3">
          <DataTable<BacktestResult>
            rows={results}
            loading={resultsState.loading}
            error={resultsState.error}
            rowKey={(row) => row.id}
            emptyMessage={t('backtests.no_backtest_results')}
            columns={[
              { key: "id", header: t('backtests.result_id'), render: (row) => row.id },
              { key: "strategy", header: t('backtests.strategy'), render: (row) => row.strategy },
              { key: "symbol", header: t('backtests.symbol'), render: (row) => row.symbol },
              {
                key: "profit",
                header: t('backtests.net_profit_short'),
                render: (row) => formatPercent(row.metrics.net_profit_percent),
              },
              {
                key: "select",
                header: t('backtests.action'),
                render: (row) => (
                  <Button className="px-2 py-1 text-xs" onClick={() => setSelectedResultId(row.id)}>
                    {t('backtests.view')}
                  </Button>
                ),
              },
            ]}
          />
        </div>
      </section>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('backtests.ranked_optimization_results')}</h3>
        {optimization ? (
          <div className="mt-3 space-y-2">
            <p className="text-sm text-text-secondary">
              {t('backtests.best_metric', { metric: optimization.sort_metric })} {t('backtests.combinations_executed', { executed: optimization.executed_combinations, total: optimization.total_combinations })}
            </p>
            <DataTable<BacktestResult>
              rows={optimization.ranked_results}
              rowKey={(row) => row.id}
              emptyMessage={t('backtests.no_ranked_results')}
              columns={[
                { key: "strategy", header: t('backtests.strategy'), render: (row) => row.strategy },
                { key: "profit", header: t('backtests.net_percent'), render: (row) => formatPercent(row.metrics.net_profit_percent) },
                { key: "pf", header: t('backtests.profit_factor_short'), render: (row) => row.metrics.profit_factor.toFixed(2) },
              ]}
            />
          </div>
        ) : (
          <p className="mt-2 text-sm text-text-dim">{t('backtests.run_optimization_to_view')}</p>
        )}
      </section>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('backtests.promotion_check_panel')}</h3>
        <p className="mt-1 text-xs text-text-dim">{t('backtests.promotion_check_subtitle')}</p>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Button
            variant="secondary"
            disabled={!selectedResult || checkingPromotion}
            onClick={() => void onCheckPromotion()}
          >
            {checkingPromotion ? t('backtests.checking') : t('backtests.run_promotion_check')}
          </Button>
          <Badge variant="warning">{promotionStatus}</Badge>
        </div>
      </section>

      {message ? <p className="text-sm text-state-success">{message}</p> : null}
      {error ? <p className="text-sm text-state-danger">{error}</p> : null}

      <div className="rounded-card border border-amber-300/40 bg-amber-400/10 px-4 py-3 text-xs text-state-warning">
        {t('backtests.backtest_disclaimer')}
      </div>
    </div>
  );
}
