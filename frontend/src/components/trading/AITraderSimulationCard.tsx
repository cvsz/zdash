import { useMemo, useState } from "react";

import {
  compareAITraderStrategies,
  generateAITraderSignal,
  getAITraderStatus,
  listAITraderStrategies,
  runAITraderPaperTrade,
  type AITraderCompareResponse,
  type AITraderPaperTradeResponse,
  type AITraderSignalResponse,
  type Candle,
} from "../../api/aiTrader";
import { useApi } from "../../hooks/useApi";
import Badge from "../common/Badge";
import Button from "../common/Button";
import SectionCard from "../common/SectionCard";

function buildDemoCandles(): Candle[] {
  const now = Date.now();
  return Array.from({ length: 34 }, (_, index) => {
    const close = 2300 + index * 0.9;
    const open = close - 0.35;
    return {
      timestamp: new Date(now + index * 5 * 60_000).toISOString(),
      open,
      high: close + 0.8,
      low: open - 0.8,
      close,
      volume: 100 + index,
    };
  });
}

export default function AITraderSimulationCard() {
  const status = useApi(getAITraderStatus, []);
  const strategies = useApi(listAITraderStrategies, []);
  const candles = useMemo(() => buildDemoCandles(), []);
  const [symbol, setSymbol] = useState("XAUUSD");
  const [timeframe, setTimeframe] = useState("M5");
  const [strategyId, setStrategyId] = useState("trend_momentum_v1");
  const [minConfidence, setMinConfidence] = useState(0.55);
  const [decision, setDecision] = useState<AITraderSignalResponse | null>(null);
  const [comparison, setComparison] = useState<AITraderCompareResponse | null>(null);
  const [paperResult, setPaperResult] = useState<AITraderPaperTradeResponse | null>(null);
  const [loading, setLoading] = useState<"signal" | "compare" | "paper" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const strategyOptions = strategies.data?.strategies ?? status.data?.strategies ?? [];

  async function onGenerateSignal() {
    setLoading("signal");
    setError(null);
    try {
      const result = await generateAITraderSignal({
        symbol,
        timeframe,
        strategy_id: strategyId,
        candles,
        min_confidence: minConfidence,
      });
      setDecision(result);
      setPaperResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(null);
    }
  }

  async function onCompareStrategies() {
    setLoading("compare");
    setError(null);
    try {
      const result = await compareAITraderStrategies({
        symbol,
        timeframe,
        candles,
        strategy_ids: strategyOptions.map((strategy) => strategy.id),
      });
      setComparison(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(null);
    }
  }

  async function onPaperTrade() {
    setLoading("paper");
    setError(null);
    try {
      const result = await runAITraderPaperTrade({
        symbol,
        timeframe,
        strategy_id: strategyId,
        candles,
        min_confidence: minConfidence,
        snapshot: {
          balance: 10000,
          equity: 10000,
          peak_equity: 10000,
          daily_start_equity: 10000,
          open_positions: 0,
          floating_pnl: 0,
          realized_pnl_today: 0,
        },
      });
      setDecision(result);
      setPaperResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(null);
    }
  }

  const signal = decision?.signal;
  const validation = decision?.validation;
  const execution = paperResult?.execution;

  return (
    <SectionCard
      title="AI Trader Control Plane"
      subtitle="Phase 34 multi-strategy simulation control plane with Guardian-gated dry-run execution."
      actions={<Badge variant="warning">SIMULATION ONLY</Badge>}
    >
      <div className="space-y-5">
        <div className="rounded-lg border border-amber-400/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
          Simulation only. No live broker execution. Not financial advice. Every paper-trade request forces dry-run execution.
        </div>

        <div className="grid gap-3 md:grid-cols-4">
          <label className="space-y-1 text-sm">
            <span className="text-xs text-slate-400">Strategy</span>
            <select
              className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
              value={strategyId}
              onChange={(event) => setStrategyId(event.target.value)}
            >
              {strategyOptions.map((strategy) => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-1 text-sm">
            <span className="text-xs text-slate-400">Symbol</span>
            <input
              className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
              value={symbol}
              onChange={(event) => setSymbol(event.target.value.toUpperCase())}
            />
          </label>
          <label className="space-y-1 text-sm">
            <span className="text-xs text-slate-400">Timeframe</span>
            <input
              className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
              value={timeframe}
              onChange={(event) => setTimeframe(event.target.value.toUpperCase())}
            />
          </label>
          <label className="space-y-1 text-sm">
            <span className="text-xs text-slate-400">Min confidence</span>
            <input
              className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
              min="0"
              max="1"
              step="0.01"
              type="number"
              value={minConfidence}
              onChange={(event) => setMinConfidence(Number(event.target.value))}
            />
          </label>
        </div>

        <div className="grid gap-3 md:grid-cols-5">
          <div>
            <p className="text-xs text-slate-400">Model</p>
            <p className="text-sm font-semibold text-slate-100">{status.data?.model_version ?? decision?.model_version ?? "-"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Direction</p>
            <p className="text-sm font-semibold text-slate-100">{signal?.direction?.toUpperCase() ?? "PENDING"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Confidence</p>
            <p className="text-sm font-semibold text-slate-100">{signal ? `${(signal.confidence * 100).toFixed(1)}%` : "-"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Validation</p>
            <p className="text-sm font-semibold text-slate-100">{validation ? (validation.valid ? "VALID" : "BLOCKED") : "PENDING"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Execution</p>
            <p className="text-sm font-semibold text-slate-100">{execution?.status?.toUpperCase() ?? "NOT RUN"}</p>
          </div>
        </div>

        {decision ? (
          <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3 text-sm text-slate-300">
            <p className="font-semibold text-slate-100">Decision explanation</p>
            <p className="mt-1">{decision.explanation}</p>
            {decision.warnings.length > 0 ? (
              <ul className="mt-2 list-disc pl-5 text-amber-200">
                {decision.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : null}

        {execution ? (
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <Badge variant={execution.dry_run ? "success" : "danger"}>{execution.dry_run ? "DRY RUN" : "BLOCKED"}</Badge>
            <span className="text-slate-300">{execution.message}</span>
          </div>
        ) : null}

        {comparison ? (
          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="min-w-full divide-y divide-slate-800 text-sm">
              <thead className="bg-slate-950/70 text-left text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-3 py-2">Strategy</th>
                  <th className="px-3 py-2">Direction</th>
                  <th className="px-3 py-2">Confidence</th>
                  <th className="px-3 py-2">Validation</th>
                  <th className="px-3 py-2">Safety</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {comparison.ranked_decisions.map((item) => (
                  <tr key={item.signal.strategy}>
                    <td className="px-3 py-2 text-slate-100">{item.signal.strategy}</td>
                    <td className="px-3 py-2 text-slate-300">{item.signal.direction}</td>
                    <td className="px-3 py-2 text-slate-300">{(item.signal.confidence * 100).toFixed(1)}%</td>
                    <td className="px-3 py-2 text-slate-300">{item.validation.valid ? "valid" : "blocked"}</td>
                    <td className="px-3 py-2 text-emerald-200">simulation-only</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}

        {error ? <p className="text-sm text-rose-300">{error}</p> : null}

        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" disabled={loading !== null} onClick={() => void onGenerateSignal()}>
            {loading === "signal" ? "Generating..." : "Generate simulation signal"}
          </Button>
          <Button variant="secondary" disabled={loading !== null} onClick={() => void onCompareStrategies()}>
            {loading === "compare" ? "Comparing..." : "Compare simulation strategies"}
          </Button>
          <Button variant="primary" disabled={loading !== null} onClick={() => void onPaperTrade()}>
            {loading === "paper" ? "Simulating..." : "Run dry-run paper trade only"}
          </Button>
        </div>

        <p className="text-xs text-slate-400">
          Live trading button intentionally does not exist. Guardian risk checks, signal validation, RBAC, audit/event logging,
          and dry-run mode remain mandatory.
        </p>
      </div>
    </SectionCard>
  );
}
