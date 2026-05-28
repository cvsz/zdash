import { useMemo, useState } from "react";

import {
  generateAITraderSignal,
  getAITraderStatus,
  runAITraderPaperTrade,
  type AITraderDecision,
  type AITraderPaperTradeResult,
  type Candle,
} from "../../api/aiTrader";
import { useApi } from "../../hooks/useApi";
import Badge from "../common/Badge";
import Button from "../common/Button";
import SectionCard from "../common/SectionCard";

function buildDemoCandles(): Candle[] {
  const now = Date.now();
  return Array.from({ length: 30 }, (_, index) => {
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
  const candles = useMemo(() => buildDemoCandles(), []);
  const [decision, setDecision] = useState<AITraderDecision | null>(null);
  const [paperResult, setPaperResult] = useState<AITraderPaperTradeResult | null>(null);
  const [loading, setLoading] = useState<"signal" | "paper" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onGenerateSignal() {
    setLoading("signal");
    setError(null);
    try {
      const result = await generateAITraderSignal({
        symbol: "XAUUSD",
        timeframe: "M5",
        candles,
        min_confidence: 0.55,
      });
      setDecision(result);
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
        symbol: "XAUUSD",
        timeframe: "M5",
        candles,
        min_confidence: 0.55,
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
      title="AI Trader Simulation"
      subtitle="Deterministic Phase 33 signal generation routed through zDash validation, Guardian checks, and dry-run execution."
      actions={<Badge variant="warning">SIMULATION ONLY</Badge>}
    >
      <div className="space-y-4">
        <div className="rounded-lg border border-amber-400/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
          Simulation only / Not financial advice / No live execution. All AI trader execution is forced through dry-run paper trading.
        </div>

        <div className="grid gap-3 md:grid-cols-4">
          <div>
            <p className="text-xs text-slate-400">Model</p>
            <p className="text-sm font-semibold text-slate-100">
              {status.data?.model_version ?? decision?.model_version ?? "-"}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Direction</p>
            <p className="text-sm font-semibold text-slate-100">{signal?.direction?.toUpperCase() ?? "PENDING"}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Confidence</p>
            <p className="text-sm font-semibold text-slate-100">
              {signal ? `${(signal.confidence * 100).toFixed(1)}%` : "-"}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Execution</p>
            <p className="text-sm font-semibold text-slate-100">{execution?.status?.toUpperCase() ?? "NOT RUN"}</p>
          </div>
        </div>

        {validation ? (
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <Badge variant={validation.valid ? "success" : "danger"}>{validation.valid ? "VALID" : "BLOCKED"}</Badge>
            <span className="text-slate-300">{validation.reason}</span>
          </div>
        ) : null}

        {execution ? (
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <Badge variant={execution.dry_run ? "success" : "danger"}>{execution.dry_run ? "DRY RUN" : "BLOCKED"}</Badge>
            <span className="text-slate-300">{execution.message}</span>
          </div>
        ) : null}

        {signal ? (
          <div className="grid gap-3 text-sm text-slate-300 md:grid-cols-3">
            <p>Entry: <span className="text-slate-100">{signal.entry ?? "-"}</span></p>
            <p>Stop: <span className="text-slate-100">{signal.stop_loss ?? "-"}</span></p>
            <p>Target: <span className="text-slate-100">{signal.take_profit ?? "-"}</span></p>
          </div>
        ) : null}

        {error ? <p className="text-sm text-rose-300">{error}</p> : null}

        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" disabled={loading !== null} onClick={() => void onGenerateSignal()}>
            {loading === "signal" ? "Generating..." : "Generate AI signal"}
          </Button>
          <Button variant="primary" disabled={loading !== null} onClick={() => void onPaperTrade()}>
            {loading === "paper" ? "Simulating..." : "Run dry-run paper trade"}
          </Button>
        </div>
      </div>
    </SectionCard>
  );
}
