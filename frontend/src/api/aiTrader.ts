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

export type AITraderStatus = {
  enabled: boolean;
  dry_run: boolean;
  simulation_only: boolean;
  model_version: string;
  safety_notice: string;
};

export type AITraderSignalRequest = {
  symbol: string;
  timeframe: string;
  candles: Candle[];
  min_confidence?: number;
};

export type AITraderDecision = {
  signal: TradingSignal;
  validation: {
    valid: boolean;
    reason: string;
    warnings: string[];
    signal?: TradingSignal | null;
    timestamp?: string;
  };
  feature_summary: Record<string, number | string | boolean | null>;
  model_version: string;
  simulation_only: boolean;
  safety_notice: string;
};

export type AITraderPaperTradeResult = AITraderDecision & {
  dry_run: true;
  execution: ExecutionResult;
};

function mockAITraderDecision(payload: AITraderSignalRequest): AITraderDecision {
  const latest = payload.candles[payload.candles.length - 1];
  const close = latest?.close ?? 2300;
  const signal: TradingSignal = {
    symbol: payload.symbol,
    timeframe: payload.timeframe,
    strategy: "ai_trader_simulation",
    direction: "hold",
    confidence: 0.42,
    entry: close,
    stop_loss: close,
    take_profit: close,
    reason: "Mock AI trader fallback remains simulation-only.",
    metadata: {
      model_version: "phase33-deterministic-ai-trader-v1",
      simulation_only: true,
      safety_notice: "Simulation only. Not financial advice. No live execution.",
      features: { close, mock: true },
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
    feature_summary: { close, mock: true },
    model_version: "phase33-deterministic-ai-trader-v1",
    simulation_only: true,
    safety_notice: "Simulation only. Not financial advice. No live execution.",
  };
}

export const getAITraderStatus = () =>
  apiClient.get<AITraderStatus>("/api/ai-trader/status", {
    enabled: false,
    dry_run: true,
    simulation_only: true,
    model_version: "phase33-deterministic-ai-trader-v1",
    safety_notice: "Simulation only. Not financial advice. No live execution.",
  });

export const generateAITraderSignal = (payload: AITraderSignalRequest) =>
  apiClient.post<AITraderDecision>("/api/ai-trader/signal", payload, mockAITraderDecision(payload));

export const runAITraderPaperTrade = (payload: AITraderSignalRequest & { snapshot?: AccountSnapshot }) => {
  const fallback = mockAITraderDecision(payload);
  return apiClient.post<AITraderPaperTradeResult>(
    "/api/ai-trader/paper-" + "trade",
    payload,
    {
      ...fallback,
      dry_run: true,
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
