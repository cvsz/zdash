import type {
  Agent,
  BacktestResult,
  ContentItem,
  DrawdownResult,
  EventLog,
  HealthStatus,
  ScheduledJob,
  TradingSignal,
} from "./types";

const nowIso = () => new Date().toISOString();

export const mockTradingOwner = {
  stable_id: "trading",
  name: "Damien Cross",
  title: "Trading Specialist",
  mock: true,
};

export const mockHealth: HealthStatus = {
  app_name: "zDash",
  environment: "mock",
  status: "ok",
  timestamp: nowIso(),
  mock: true,
  services: {
    api: "simulated",
    agents: "simulated",
    risk: "simulated_guarded",
  },
};

export const mockAgents: Agent[] = [
  {
    id: "ceo",
    name: "Alexander Prime",
    role: "CEO • Visionary Leader",
    status: "online",
    health: "mock_ok",
    last_event: "Mock strategic sync completed",
    capabilities: ["strategy", "vision", "approval"],
    metadata: { mock: true },
    mock: true,
  },
  {
    id: "janie",
    name: "Sophia Lane",
    role: "Coordinator • Manager",
    status: "online",
    health: "mock_ok",
    last_event: "Mock orchestration cycle active",
    capabilities: ["coordination", "routing", "management"],
    metadata: { mock: true },
    mock: true,
  },
  {
    id: "guardian",
    name: "Victor Hale",
    role: "Risk Manager",
    status: "online",
    health: "mock_ok",
    last_event: "Mock risk guard active",
    capabilities: ["risk", "halt", "kill-switch"],
    metadata: { mock: true },
    mock: true,
  },
  {
    id: "friday",
    name: "Isla Grant",
    role: "Scheduler • Automation",
    status: "online",
    health: "mock_ok",
    last_event: "Mock scheduler heartbeat",
    capabilities: ["scheduler", "automation", "dry-run"],
    metadata: { mock: true },
    mock: true,
  },
  {
    id: "joe",
    name: "Nathan Cole",
    role: "Analyst • Developer",
    status: "online",
    health: "mock_ok",
    last_event: "Mock strategy lab sync",
    capabilities: ["analysis", "development", "backtesting"],
    metadata: { mock: true },
    mock: true,
  },
  {
    id: "editor",
    name: "Elena Voss",
    role: "Content Specialist",
    status: "online",
    health: "mock_ok",
    last_event: "Mock draft generated",
    capabilities: ["content", "editing", "approval"],
    metadata: { mock: true },
    mock: true,
  },
  {
    id: "graphic",
    name: "Julian Reed",
    role: "Design Specialist",
    status: "online",
    health: "mock_ok",
    last_event: "Mock graphic prompt ready",
    capabilities: ["design", "graphics", "visuals"],
    metadata: { mock: true },
    mock: true,
  },
  {
    id: "social",
    name: "Maya Quinn",
    role: "Social Media Specialist",
    status: "online",
    health: "mock_ok",
    last_event: "Mock approval gate waiting",
    capabilities: ["social", "publishing", "approval"],
    metadata: { mock: true },
    mock: true,
  },
];

export const mockLogs: EventLog[] = [
  {
    id: "log-mock-1",
    type: "system.mock_fallback",
    category: "system",
    source: "mock",
    message:
      "Mock fallback mode active. All outputs are simulated and not live execution.",
    level: "warning",
    created_at: nowIso(),
    ts: nowIso(),
    payload: { mock: true, simulation: true },
  },
];

export const mockSignals: TradingSignal[] = [
  {
    id: "signal-mock-1",
    symbol: "XAUUSD",
    timeframe: "M5",
    strategy: "ob_aggressive",
    direction: "buy",
    side: "buy",
    confidence: 0.71,
    entry: 2356.4,
    stop_loss: 2352.0,
    take_profit: 2364.8,
    reason: "Mock order-block momentum signal",
    ai_summary: "Simulation only: momentum bias positive.",
    validated: true,
    created_at: nowIso(),
    metadata: { mock: true },
  },
];

export const mockDrawdown: DrawdownResult = {
  current_equity: 9950,
  peak_equity: 10000,
  daily_start_equity: 10020,
  total_drawdown_percent: 0.5,
  daily_drawdown_percent: 0.7,
  floating_pnl: -50,
  risk_level: "normal",
  breached: false,
};

export const mockJobs: ScheduledJob[] = [
  {
    id: "job-mock-trading-scan",
    name: "trading_scan",
    job_type: "trading_scan",
    schedule_type: "interval",
    status: "pending",
    enabled: true,
    interval_seconds: 300,
    payload: { symbol: "XAUUSD", timeframe: "M5", dry_run: true, mock: true },
    risk_guarded: true,
    created_at: nowIso(),
    updated_at: nowIso(),
  },
  {
    id: "job-mock-iot",
    name: "iot_power_cycle",
    job_type: "iot_power_cycle",
    schedule_type: "manual",
    status: "disabled",
    enabled: false,
    payload: { dry_run: true, requires_confirmation: true, mock: true },
    created_at: nowIso(),
    updated_at: nowIso(),
  },
];

export const mockBacktests: BacktestResult[] = [
  {
    id: "backtest-mock-1",
    strategy: "ob_aggressive",
    symbol: "XAUUSD",
    timeframe: "M5",
    metrics: {
      total_trades: 100,
      win_rate: 52,
      profit_factor: 1.3,
      max_drawdown_percent: 12,
      net_profit_percent: 18,
      consecutive_losses: 4,
    },
    equity_curve: [
      { x: "W1", y: 10000 },
      { x: "W2", y: 10400 },
    ],
    monthly_returns: [{ month: "2026-04", value: 4.2 }],
    warnings: [
      "Mock dataset used for simulation. Backtest is not guaranteed future performance.",
    ],
  },
];

export const mockContent: ContentItem[] = [
  {
    id: "content-mock-1",
    title: "zDash Educational Market Simulation Brief",
    topic: "Educational simulation for market workflows",
    content_type: "educational",
    status: "draft",
    policy_passed: true,
    policy_notes: ["Mock content pending manual approval before publishing."],
    approval_required: true,
    approved: false,
    social_dry_run: true,
    metadata: { mock: true, simulation: true },
  },
];
