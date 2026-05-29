export type ApiErrorPayload = {
  code: string;
  message: string;
};

export type ApiResponse<T> = {
  ok: boolean;
  data: T | null;
  error: ApiErrorPayload | null;
  timestamp: string;
};

export class ApiError extends Error {
  code: string;
  status?: number;
  path?: string;
  details?: unknown;

  constructor(
    message: string,
    options: {
      code?: string;
      status?: number;
      path?: string;
      details?: unknown;
      cause?: unknown;
    } = {},
  ) {
    super(message);
    this.name = "ApiError";
    this.code = options.code ?? "API_ERROR";
    this.status = options.status;
    this.path = options.path;
    this.details = options.details;
    if (options.cause !== undefined) {
      (this as Error & { cause?: unknown }).cause = options.cause;
    }
  }
}

export type HealthStatus = {
  app_name?: string;
  environment?: string;
  status: string;
  timestamp?: string;
  services?: Record<string, string>;
  mock?: boolean;
};

export type Agent = {
  id: string;
  name: string;
  role: string;
  status: string;
  metadata?: Record<string, unknown>;
  health?: string;
  last_event?: string;
  capabilities?: string[];
  mock?: boolean;
};

export type EventLog = {
  id: string;
  type?: string;
  category?: string;
  source: string;
  message: string;
  payload?: unknown;
  created_at?: string;
  ts?: string;
  level?: string;
};

export type TradingSignal = {
  id?: string;
  symbol: string;
  timeframe: string;
  strategy?: string;
  direction?: "buy" | "sell" | "hold";
  side?: "buy" | "sell" | "hold";
  confidence: number;
  entry?: number;
  stop_loss?: number;
  take_profit?: number;
  reason?: string;
  metadata?: Record<string, unknown>;
  validated?: boolean;
  ai_summary?: string;
  created_at?: string;
};

export type ExecutionResult = {
  ok: boolean;
  status: string;
  dry_run: boolean;
  signal: TradingSignal;
  message: string;
  simulated_order_id?: string | null;
  risk_decision?: RiskDecision | null;
  timestamp?: string;
};

export type AccountSnapshot = {
  balance: number;
  equity: number;
  peak_equity: number;
  daily_start_equity: number;
  open_positions?: number;
  floating_pnl?: number;
  realized_pnl_today?: number;
  timestamp?: string;
};

export type DrawdownResult = {
  current_equity: number;
  peak_equity: number;
  daily_start_equity: number;
  total_drawdown_percent: number;
  daily_drawdown_percent: number;
  floating_pnl: number;
  risk_level: "normal" | "warning" | "danger" | "emergency";
  breached: boolean;
  breach_reason?: string | null;
};

export type HaltState = {
  halted: boolean;
  reason?: string | null;
  source?: string | null;
  created_at?: string | null;
  resumed_at?: string | null;
  resume_reason?: string | null;
};

export type RiskDecision = {
  approved: boolean;
  reason: string;
  risk_level: "normal" | "warning" | "danger" | "emergency";
  halt_active: boolean;
  drawdown?: DrawdownResult | null;
  timestamp?: string;
};

export type ScheduledJob = {
  id: string;
  name: string;
  job_type: string;
  schedule_type: string;
  status: string;
  enabled: boolean;
  cron?: string | null;
  interval_seconds?: number | null;
  payload?: Record<string, unknown>;
  max_runtime_seconds?: number;
  created_at?: string;
  updated_at?: string;
  last_run_at?: string | null;
  next_run_at?: string | null;
  run_count?: number;
  fail_count?: number;
  risk_guarded?: boolean;
};

export type JobRunResult = {
  job_id: string;
  job_type: string;
  status: string;
  ok: boolean;
  message: string;
  output: Record<string, unknown>;
  started_at: string;
  finished_at: string;
  duration_ms: number;
};

export type BacktestRequest = {
  strategy: string;
  symbol?: string;
  timeframe?: string;
  dataset?: string;
  initial_balance?: number;
  risk_per_trade_percent?: number;
  commission_per_trade?: number;
  spread_points?: number;
  slippage_points?: number;
  parameters?: Record<string, unknown>;
};

export type BacktestMetrics = {
  total_trades: number;
  winning_trades?: number;
  losing_trades?: number;
  win_rate: number;
  gross_profit?: number;
  gross_loss?: number;
  net_profit?: number;
  net_profit_percent: number;
  profit_factor: number;
  max_drawdown_percent: number;
  average_rr?: number;
  expectancy?: number;
  sharpe_like_score?: number;
  consecutive_losses: number;
  monthly_return_table?: Record<string, number>;
};

export type BacktestResult = {
  id: string;
  request?: BacktestRequest;
  strategy: string;
  symbol: string;
  timeframe: string;
  initial_balance?: number;
  final_balance?: number;
  metrics: BacktestMetrics;
  trades?: Array<Record<string, unknown>>;
  parameters?: Record<string, unknown>;
  started_at?: string;
  finished_at?: string;
  duration_ms?: number;
  warnings?: string[];
  equity_curve?: Array<{ x: string; y: number }>;
  monthly_returns?: Array<{ month: string; value: number }>;
};

export type OptimizationResult = {
  id: string;
  request?: Record<string, unknown>;
  ranked_results: BacktestResult[];
  best_result?: BacktestResult | null;
  sort_metric: string;
  total_combinations: number;
  executed_combinations: number;
  started_at: string;
  finished_at: string;
  duration_ms: number;
  warnings?: string[];
};

export type StrategyPromotionDecision = {
  strategy?: string;
  approved: boolean;
  reason: string;
  metrics?: BacktestMetrics | null;
  gates?: Record<string, boolean>;
  timestamp?: string;
};

export type ContentItem = {
  id: string;
  title: string;
  topic?: string;
  content_type?: string;
  status: string;
  brand?: string;
  language?: string;
  tone?: string;
  draft_text?: string | null;
  edited_text?: string | null;
  graphic_prompt?: string | null;
  graphic_asset_url?: string | null;
  platforms?: string[];
  scheduled_at?: string | null;
  approved_at?: string | null;
  posted_at?: string | null;
  policy_passed?: boolean;
  policy_notes?: string[];
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
  approval_required?: boolean;
  approved?: boolean;
  social_dry_run?: boolean;
};

export type PipelineRunResult = {
  id: string;
  content_id: string;
  ok: boolean;
  status: string;
  steps: Array<Record<string, unknown>>;
  message: string;
  started_at: string;
  finished_at: string;
  duration_ms: number;
};

export type SocialPostResult = {
  platform: string;
  ok: boolean;
  dry_run: boolean;
  external_id?: string | null;
  message: string;
  output?: Record<string, unknown>;
  timestamp?: string;
};

export type IoTActionResult = {
  ok: boolean;
  dry_run: boolean;
  device_alias: string;
  action: "status" | "turn_on" | "turn_off" | "power_cycle";
  message: string;
  output?: Record<string, unknown>;
  timestamp?: string;
};

export type TradingScanResult = {
  symbol: string;
  timeframe: string;
  candles_analyzed: number;
  latest_signal: TradingSignal | null;
  validation: {
    valid: boolean;
    reason: string;
    warnings: string[];
    signal?: TradingSignal | null;
    timestamp?: string;
  } | null;
  ai_summary: string;
  timestamp: string;
};

export type BacktestReport = {
  markdown_report: string;
  summary: Record<string, unknown>;
};

export type ContentReport = {
  summary: Record<string, unknown>;
  markdown: string;
  logs: EventLog[];
};

export type AuthTokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role: string;
  username: string;
};

export type AuthUser = {
  username: string;
  role: string;
};

export type StoredAuthSession = {
  accessToken: string;
  refreshToken: string;
};

export type AdminUser = {
  id: string;
  email: string;
  display_name: string;
  role: string;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
};

export type AdminUserCreateInput = {
  email: string;
  password: string;
  role: string;
  display_name: string;
};

export type AdminUserUpdateInput = {
  role?: string;
  display_name?: string;
  is_active?: boolean;
};

export type AuditLogEntry = {
  id: string;
  actor_user_id: string;
  actor_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  result: string;
  ip_address: string;
  user_agent: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type AdminSafetyCheck = {
  status: "safe" | "blocked";
  warnings: string[];
  blockers: string[];
  score: number;
};

export type Organization = {
  id: string;
  name: string;
  slug: string;
  status: string;
  plan: string;
  role: string;
  created_at?: string;
  mock?: boolean;
};

export type Workspace = {
  id: string;
  name: string;
  slug: string;
  environment: string;
  is_active: boolean;
  created_at?: string;
  mock?: boolean;
};

export type QueueStatus = {
  queue_name: string;
  workers_active: number;
  tasks_pending: number;
  tasks_processing: number;
  tasks_failed: number;
  uptime_seconds: number;
};

export type TaskItem = {
  id: string;
  name: string;
  type: string;
  payload?: Record<string, unknown>;
  status: "pending" | "processing" | "completed" | "failed" | "cancelled";
  error?: string | null;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  worker_id?: string | null;
  retries: number;
};

export type AlertRule = {
  id: string;
  name: string;
  condition: string;
  severity: "info" | "warning" | "error" | "critical";
  enabled: boolean;
  channels: string[];
  created_at: string;
};

export type AlertEvent = {
  id: string;
  rule_id: string;
  message: string;
  severity: "info" | "warning" | "error" | "critical";
  status: "active" | "acknowledged" | "resolved";
  triggered_at: string;
  resolved_at?: string | null;
};

export type NotificationChannel = {
  id: string;
  type: "email" | "slack" | "webhook";
  target: string;
  enabled: boolean;
  created_at: string;
};

export type BillingPlan = {
  id: string;
  tier: string;
  name: string;
  description: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  limits: Record<string, number>;
};

export type BillingStatus = {
  status: string;
  plan_tier: string;
  plan_id: string | null;
  provider: string;
  cancel_at_period_end: boolean;
  current_period_start?: string | null;
  current_period_end?: string | null;
  trial_ends_at?: string | null;
  grace_period_ends_at?: string | null;
};

export type UsageMetricValue = {
  limit: number;
  usage: number;
};

export type UsageSummary = {
  metrics: {
    backtest_runs?: UsageMetricValue;
    content_generation_tokens?: UsageMetricValue;
    marketplace_plugins?: UsageMetricValue;
    iot_actions?: UsageMetricValue;
    [key: string]: UsageMetricValue | undefined;
  };
  reset_timestamp: string;
};

export type Invoice = {
  id: string;
  number: string;
  amount: number;
  currency: string;
  status: "paid" | "open" | "uncollectible" | "void";
  created_at: string;
  hosted_invoice_url?: string;
  pdf_url?: string;
};

export type PluginManifest = {
  id: string;
  name: string;
  slug: string;
  version: string;
  description: string;
  author: string;
  category: string;
  status: string;
  required_features: string[];
  required_permissions: string[];
  config_schema: Record<string, unknown>;
  default_config: Record<string, unknown>;
  entrypoint: string;
  safety_level: string;
  metadata_json: Record<string, unknown>;
};

export type PluginInstallation = {
  id: string;
  organization_id: string;
  workspace_id: string;
  plugin_id: string;
  version: string;
  status: string;
  config_json: Record<string, unknown>;
  enabled: boolean;
  installed_by: string;
  installed_at: string;
};

export type EnterpriseLicense = {
  id?: string;
  organization_id: string;
  status: string;
  tier: string;
  seats: number;
  features: string[];
  expires_at?: string | null;
  offline_mode: boolean;
  issued_to?: string;
  metadata_json?: Record<string, unknown>;
};

export type BrandingSettings = {
  id?: string;
  organization_id: string;
  workspace_id: string;
  brand_name: string;
  logo_url?: string | null;
  primary_color: string;
  accent_color: string;
  support_email?: string | null;
  custom_domain?: string | null;
  metadata_json?: Record<string, unknown>;
};

export type ExportBundle = {
  id: string;
  organization_id: string;
  workspace_id: string;
  export_type: string;
  status: string;
  file_path?: string | null;
  include_audit_logs: boolean;
  include_content: boolean;
  include_backtests: boolean;
  include_scheduler: boolean;
  include_secrets: boolean;
  created_by: string;
  created_at: string;
  completed_at?: string | null;
};

export type OnboardingChecklist = {
  id?: string;
  organization_id: string;
  workspace_id?: string | null;
  completed_steps: string[];
  pending_steps: string[];
  progress_percent: number;
  created_at?: string;
  updated_at?: string;
};

export type CustomerHealth = {
  health_score: number;
  status: "poor" | "fair" | "excellent";
  active_users: number;
  usage_trend: string;
};

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
  live_trading_enabled?: boolean;
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
  feature_summary: Record<string, number | string | boolean>;
  model_version: string;
  simulation_only: boolean;
  safety_notice: string;
};

export type AITraderPaperTradeResult = AITraderDecision & {
  dry_run: true;
  execution: ExecutionResult;
};
