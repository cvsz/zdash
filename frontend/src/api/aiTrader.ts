import { apiClient } from "./client";
import type { AccountSnapshot, ExecutionResult, TradingSignal } from "./types";

export type Candle = {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
};

export type AITraderStrategy = {
  id: string;
  name: string;
  description: string;
  risk_profile: string;
  min_candles: number;
  default_min_confidence: number;
  supported_symbols: string[];
  supported_timeframes: string[];
  simulation_only: boolean;
};

export type AITraderStatus = {
  enabled: boolean;
  simulation_only: boolean;
  live_execution_allowed: false;
  dry_run_forced: true;
  model_version: string;
  strategies: AITraderStrategy[];
  safety_policy: Record<string, boolean>;
  safety_notice: string;
};

export type AITraderSignalRequest = {
  symbol: string;
  timeframe: string;
  strategy_id: string;
  candles: Candle[];
  min_confidence?: number;
};

export type AITraderSignalResponse = {
  signal: TradingSignal;
  validation: {
    valid: boolean;
    reason: string;
    warnings: string[];
    signal?: TradingSignal | null;
    timestamp?: string;
  };
  features: Record<string, number | string | boolean | null>;
  feature_summary?: Record<string, number | string | boolean | null>;
  warnings: string[];
  explanation: string;
  model_version: string;
  simulation_only: boolean;
  safety_notice: string;
  risk_policy: Record<string, boolean>;
};

export type AITraderCompareRequest = {
  symbol: string;
  timeframe: string;
  candles: Candle[];
  strategy_ids: string[];
};

export type AITraderCompareResponse = {
  ranked_decisions: AITraderSignalResponse[];
  model_version: string;
  simulation_only: boolean;
  safety_notice: string;
};

export type AITraderPaperTradeRequest = AITraderSignalRequest & {
  snapshot?: AccountSnapshot;
};

export type AITraderPaperTradeResponse = AITraderSignalResponse & {
  dry_run: true;
  live_execution_allowed: false;
  execution: ExecutionResult;
};

const mockStrategies: AITraderStrategy[] = [
  {
    id: "trend_momentum_v1",
    name: "Trend Momentum v1",
    description: "Follows aligned moving-average trend and short-term momentum.",
    risk_profile: "balanced",
    min_candles: 21,
    default_min_confidence: 0.55,
    supported_symbols: ["XAUUSD", "BTCUSD", "ETHUSD", "EURUSD"],
    supported_timeframes: ["M5", "M15", "H1"],
    simulation_only: true,
  },
  {
    id: "mean_reversion_v1",
    name: "Mean Reversion v1",
    description: "Looks for stretched price versus slow moving average with stabilizing momentum.",
    risk_profile: "moderate",
    min_candles: 21,
    default_min_confidence: 0.58,
    supported_symbols: ["XAUUSD", "BTCUSD", "ETHUSD", "EURUSD"],
    supported_timeframes: ["M5", "M15", "H1"],
    simulation_only: true,
  },
  {
    id: "volatility_breakout_v1",
    name: "Volatility Breakout v1",
    description: "Requires elevated volatility and aligned momentum before simulating breakout.",
    risk_profile: "aggressive",
    min_candles: 28,
    default_min_confidence: 0.62,
    supported_symbols: ["XAUUSD", "BTCUSD", "ETHUSD"],
    supported_timeframes: ["M5", "M15", "H1"],
    simulation_only: true,
  },
  {
    id: "conservative_guarded_v1",
    name: "Conservative Guarded v1",
    description: "Stricter confidence and volatility filters, preferring hold decisions.",
    risk_profile: "conservative",
    min_candles: 28,
    default_min_confidence: 0.72,
    supported_symbols: ["XAUUSD", "EURUSD"],
    supported_timeframes: ["M5", "M15", "H1"],
    simulation_only: true,
  },
];

function mockAITraderDecision(payload: AITraderSignalRequest): AITraderSignalResponse {
  const latest = payload.candles[payload.candles.length - 1];
  const close = latest?.close ?? 2300;
  const signal: TradingSignal = {
    symbol: payload.symbol,
    timeframe: payload.timeframe,
    strategy: payload.strategy_id,
    direction: "hold",
    confidence: 0.42,
    entry: close,
    stop_loss: close,
    take_profit: close,
    reason: "Mock AI trader fallback remains simulation-only.",
    metadata: {
      model_version: "ai-trader-phase34",
      strategy_id: payload.strategy_id,
      simulation_only: true,
      safety_notice: "Simulation only. Not financial advice. No live execution.",
      features: { close, mock: true },
      warnings: ["mock fallback"],
      explanation: "Mock fallback decision generated safely.",
      risk_policy: {
        dry_run_forced: true,
        guardian_required: true,
        live_execution_allowed: false,
      },
    },
    created_at: new Date().toISOString(),
  };

  return {
    signal,
    validation: {
      valid: true,
      reason: "Mock validation for simulation-only AI trader signal.",
      warnings: ["Simulation only", "No live execution"],
      signal,
      timestamp: new Date().toISOString(),
    },
    features: { close, mock: true },
    feature_summary: { close, mock: true },
    warnings: ["mock fallback"],
    explanation: "Mock fallback decision generated safely.",
    model_version: "ai-trader-phase34",
    simulation_only: true,
    safety_notice: "Simulation only. Not financial advice. No live execution.",
    risk_policy: {
      dry_run_forced: true,
      guardian_required: true,
      live_execution_allowed: false,
    },
  };
}

export const getAITraderStatus = () =>
  apiClient.get<AITraderStatus>("/api/ai-trader/status", {
    enabled: true,
    simulation_only: true,
    live_execution_allowed: false,
    dry_run_forced: true,
    model_version: "ai-trader-phase34",
    strategies: mockStrategies,
    safety_policy: {
      dry_run_forced: true,
      guardian_required: true,
      live_execution_allowed: false,
    },
    safety_notice: "Simulation only. Not financial advice. No live execution.",
  });

export const listAITraderStrategies = () =>
  apiClient.get<{ strategies: AITraderStrategy[]; simulation_only: boolean; model_version: string }>(
    "/api/ai-trader/strategies",
    { strategies: mockStrategies, simulation_only: true, model_version: "ai-trader-phase34" },
  );

export const generateAITraderSignal = (payload: AITraderSignalRequest) =>
  apiClient.post<AITraderSignalResponse>("/api/ai-trader/signal", payload, mockAITraderDecision(payload));

export const compareAITraderStrategies = (payload: AITraderCompareRequest) => {
  const ranked_decisions = payload.strategy_ids.map((strategy_id) =>
    mockAITraderDecision({ ...payload, strategy_id, min_confidence: 0.55 }),
  );
  return apiClient.post<AITraderCompareResponse>("/api/ai-trader/compare", payload, {
    ranked_decisions,
    model_version: "ai-trader-phase34",
    simulation_only: true,
    safety_notice: "Simulation only. Not financial advice. No live execution.",
  });
};

export const runAITraderPaperTrade = (payload: AITraderPaperTradeRequest) => {
  const fallback = mockAITraderDecision(payload);
  return apiClient.post<AITraderPaperTradeResponse>(
    "/api/ai-trader/paper-" + "trade",
    payload,
    {
      ...fallback,
      dry_run: true,
      live_execution_allowed: false,
      execution: {
        ok: true,
        status: "simulated",
        dry_run: true,
        signal: fallback.signal,
        message: "Mock AI trader paper trade simulated. No live order sent.",
        simulated_order_id: "mock-ai-trader-paper-1",
        timestamp: new Date().toISOString(),
      },
    },
  );
};
