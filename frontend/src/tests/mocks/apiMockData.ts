import type {
  HealthStatus,
  EventLog,
  Agent,
  ContentItem,
  QueueStatus,
  TaskItem,
  Organization,
  Workspace,
  ScheduledJob,
  BacktestResult,
  OptimizationResult,
  DrawdownResult,
  AlertRule,
  AlertEvent,
  NotificationChannel,
  BillingStatus,
  BillingPlan,
  UsageSummary,
  Invoice,
  PluginManifest,
  PluginInstallation,
  EnterpriseLicense,
  BrandingSettings,
  OnboardingChecklist,
  CustomerHealth,
  ExportBundle,
  AdminUser,
  AuditLogEntry,
  AdminSafetyCheck,
  PipelineRunResult,
  IoTActionResult,
  TradingSignal,
  AITraderStatus,
} from "../../api/types";

const now = () => new Date().toISOString();

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
  timestamp: now(),
  mock: true,
  services: {
    api: "simulated",
    agents: "simulated",
    risk: "simulated_guarded",
  },
};

export const mockLogs: EventLog[] = [
  {
    id: "log-mock-1",
    type: "system.mock_fallback",
    category: "system",
    source: "mock",
    message: "Mock fallback mode active. All outputs are simulated.",
    level: "warning",
    created_at: now(),
    ts: now(),
    payload: { mock: true },
  },
];

export const mockAgents: Agent[] = [
  { id: "ceo", name: "Alexander Prime", role: "CEO", status: "online", health: "mock_ok", last_event: "Mock sync", capabilities: ["strategy"], metadata: { mock: true }, mock: true },
  { id: "janie", name: "Sophia Lane", role: "Coordinator", status: "online", health: "mock_ok", last_event: "Mock orchestration", capabilities: ["coordination"], metadata: { mock: true }, mock: true },
  { id: "guardian", name: "Victor Hale", role: "Risk Manager", status: "online", health: "mock_ok", last_event: "Mock risk guard", capabilities: ["risk"], metadata: { mock: true }, mock: true },
  { id: "friday", name: "Isla Grant", role: "Scheduler", status: "online", health: "mock_ok", last_event: "Mock heartbeat", capabilities: ["scheduler"], metadata: { mock: true }, mock: true },
  { id: "joe", name: "Nathan Cole", role: "Analyst", status: "online", health: "mock_ok", last_event: "Mock analysis", capabilities: ["analysis"], metadata: { mock: true }, mock: true },
  { id: "editor", name: "Elena Voss", role: "Content Specialist", status: "online", health: "mock_ok", last_event: "Mock draft", capabilities: ["content"], metadata: { mock: true }, mock: true },
  { id: "graphic", name: "Julian Reed", role: "Design Specialist", status: "online", health: "mock_ok", last_event: "Mock graphic", capabilities: ["design"], metadata: { mock: true }, mock: true },
  { id: "social", name: "Maya Quinn", role: "Social Media Specialist", status: "online", health: "mock_ok", last_event: "Mock approval", capabilities: ["social"], metadata: { mock: true }, mock: true },
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
    validated: true,
    created_at: now(),
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
    created_at: now(),
    updated_at: now(),
  },
  {
    id: "job-mock-iot",
    name: "iot_power_cycle",
    job_type: "iot_power_cycle",
    schedule_type: "manual",
    status: "disabled",
    enabled: false,
    payload: { dry_run: true, requires_confirmation: true, mock: true },
    created_at: now(),
    updated_at: now(),
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
    equity_curve: [{ x: "W1", y: 10000 }, { x: "W2", y: 10400 }],
    monthly_returns: [{ month: "2026-04", value: 4.2 }],
    warnings: ["Mock dataset used for simulation."],
  },
];

export const mockOptimization: OptimizationResult = {
  id: "opt-mock-1",
  ranked_results: mockBacktests,
  best_result: mockBacktests[0],
  sort_metric: "profit_factor",
  total_combinations: 1,
  executed_combinations: 1,
  started_at: now(),
  finished_at: now(),
  duration_ms: 12,
};

export const mockContentItems: ContentItem[] = [
  {
    id: "content-mock-1",
    title: "zDash Educational Market Simulation Brief",
    topic: "Educational simulation for market workflows",
    content_type: "educational",
    status: "draft",
    policy_passed: true,
    policy_notes: ["Policy notes: approval required before publishing."],
    approval_required: true,
    approved: false,
    social_dry_run: true,
    platforms: ["x"],
    created_at: now(),
    updated_at: now(),
    metadata: { mock: true, simulation: true },
  },
  {
    id: "content-mock-2",
    title: "Weekly Market Analysis",
    topic: "Market trends and analysis",
    content_type: "analysis",
    status: "approved",
    policy_passed: true,
    policy_notes: [],
    approval_required: true,
    approved: true,
    social_dry_run: true,
    platforms: ["x", "linkedin"],
    created_at: now(),
    updated_at: now(),
  },
];

export const mockPipelineRunResult: PipelineRunResult = {
  id: "pipeline-mock-1",
  content_id: "content-mock-1",
  ok: true,
  status: "scheduled",
  steps: [{ step: "mock_pipeline", ok: true }],
  message: "Mock content pipeline completed in simulation mode.",
  started_at: now(),
  finished_at: now(),
  duration_ms: 20,
};

export const mockQueueStatuses: QueueStatus[] = [
  {
    queue_name: "default",
    workers_active: 3,
    tasks_pending: 2,
    tasks_processing: 1,
    tasks_failed: 0,
    uptime_seconds: 3600,
  },
];

export const mockTasks: TaskItem[] = [
  {
    id: "task-1",
    name: "Data Sync",
    type: "sync",
    status: "completed",
    created_at: now(),
    retries: 0,
  },
  {
    id: "task-2",
    name: "Report Generation",
    type: "report",
    status: "processing",
    created_at: now(),
    retries: 0,
  },
];

export const mockOrganizations: Organization[] = [
  {
    id: "org-1",
    name: "Zeaz Inc",
    slug: "zeaz",
    status: "active",
    plan: "enterprise",
    role: "admin",
    mock: true,
  },
];

export const mockWorkspaces: Workspace[] = [
  {
    id: "ws-1",
    name: "Production",
    slug: "prod",
    environment: "production",
    is_active: true,
    mock: true,
  },
  {
    id: "ws-2",
    name: "Staging",
    slug: "staging",
    environment: "staging",
    is_active: false,
    mock: true,
  },
];

export const mockAlertRules: AlertRule[] = [
  {
    id: "rule-1",
    name: "High Error Rate",
    condition: "errors > 10",
    severity: "critical",
    enabled: true,
    channels: ["chan-1"],
    created_at: now(),
  },
];

export const mockAlertEvents: AlertEvent[] = [
  {
    id: "evt-1",
    rule_id: "rule-1",
    message: "Error rate exceeded 10%",
    severity: "critical",
    status: "active",
    triggered_at: now(),
  },
];

export const mockNotificationChannels: NotificationChannel[] = [
  {
    id: "chan-1",
    type: "slack",
    target: "#alerts",
    enabled: true,
    created_at: now(),
  },
];

export const mockBillingStatus: BillingStatus = {
  status: "active",
  plan_tier: "pro",
  plan_id: "pro",
  provider: "mock",
  cancel_at_period_end: false,
  current_period_start: now(),
  current_period_end: new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString(),
  trial_ends_at: null,
};

export const mockBillingPlans: BillingPlan[] = [
  { id: "free", tier: "free", name: "Free", description: "Basic operations", price_monthly: 0, price_yearly: 0, features: [], limits: {} },
  { id: "pro", tier: "pro", name: "Pro", description: "Advanced", price_monthly: 49, price_yearly: 490, features: ["Backtest runs", "Guardian"], limits: { backtest_runs: 200, marketplace_plugins: 5 } },
];

export const mockUsageSummary: UsageSummary = {
  metrics: {
    backtest_runs: { limit: 200, usage: 45 },
    marketplace_plugins: { limit: 5, usage: 2 },
  },
  reset_timestamp: new Date(Date.now() + 15 * 24 * 3600 * 1000).toISOString(),
};

export const mockInvoices: Invoice[] = [
  { id: "inv-001", number: "INV-2026-001", amount: 49.0, currency: "USD", status: "paid", created_at: now() },
];

export const mockPlugins: PluginManifest[] = [
  {
    id: "plugin-tapo", name: "Tapo Smart Plug Controller", slug: "tapo-controller", version: "1.0.2",
    description: "Control smart plugs.", author: "zDash Team", category: "iot",
    status: "approved", required_features: ["feature.iot"], required_permissions: ["iot_control"],
    config_schema: {}, default_config: {}, entrypoint: "main.py", safety_level: "sandbox", metadata_json: {},
  },
  {
    id: "plugin-slack", name: "Slack Webhook Notifier", slug: "slack-notifier", version: "2.1.0",
    description: "Send alerts to Slack.", author: "Slack Inc.", category: "notifications",
    status: "approved", required_features: [], required_permissions: [],
    config_schema: {}, default_config: {}, entrypoint: "slack.py", safety_level: "restricted", metadata_json: {},
  },
];

export const mockPluginInstallations: PluginInstallation[] = [
  {
    id: "inst-tapo", organization_id: "org-1", workspace_id: "ws-1", plugin_id: "plugin-tapo",
    version: "1.0.2", status: "enabled", config_json: {}, enabled: true,
    installed_by: "admin@zeaz.dev", installed_at: now(),
  },
];

export const mockEnterpriseLicense: EnterpriseLicense = {
  organization_id: "org-1",
  status: "active",
  tier: "enterprise",
  seats: 50,
  features: ["feature.branding", "feature.exports"],
  expires_at: new Date(Date.now() + 365 * 24 * 3600 * 1000).toISOString(),
  offline_mode: false,
  issued_to: "Zeaz Inc",
};

export const mockBrandingSettings: BrandingSettings = {
  organization_id: "org-1",
  workspace_id: "ws-1",
  brand_name: "zDash Custom",
  logo_url: null,
  primary_color: "#7c3aed",
  accent_color: "#22c55e",
  support_email: "support@zeaz.dev",
  custom_domain: "dash.zeaz.dev",
};

export const mockOnboardingChecklist: OnboardingChecklist = {
  organization_id: "org-1",
  workspace_id: "ws-1",
  completed_steps: ["create organization", "create workspace"],
  pending_steps: ["invite team", "verify risk guardian", "run first dry-run scan"],
  progress_percent: 20.0,
};

export const mockCustomerHealth: CustomerHealth = {
  health_score: 20.0,
  status: "poor",
  active_users: 1,
  usage_trend: "stable",
};

export const mockExportBundles: ExportBundle[] = [
  {
    id: "exp-001", organization_id: "org-1", workspace_id: "ws-1",
    export_type: "full", status: "completed", file_path: "/exports/bundle_001.zip",
    include_audit_logs: true, include_content: true, include_backtests: false, include_scheduler: true, include_secrets: false,
    created_by: "admin@zeaz.dev", created_at: now(), completed_at: now(),
  },
];

export const mockAdminUsers: AdminUser[] = [
  {
    id: "admin-1", email: "admin@zeaz.dev", display_name: "Admin User",
    role: "admin", is_active: true, created_at: now(), updated_at: now(),
  },
];

export const mockAuditLogs: AuditLogEntry[] = [
  {
    id: "audit-1", actor_user_id: "admin-1", actor_email: "admin@zeaz.dev",
    action: "user.login", resource_type: "session", resource_id: "sess-1",
    result: "success", ip_address: "127.0.0.1", user_agent: "test",
    metadata: {}, created_at: now(),
  },
];

export const mockAdminSafetyCheck: AdminSafetyCheck = {
  status: "safe",
  warnings: [],
  blockers: [],
  score: 100,
};

export const mockIoTActionResult: IoTActionResult = {
  ok: true,
  dry_run: true,
  device_alias: "zdash-power-node",
  action: "status",
  message: "Mock IoT status simulated.",
  output: { mock: true, connected: false },
};

export const mockAITraderStatus: AITraderStatus = {
  enabled: false,
  live_trading_enabled: false,
  dry_run: true,
  simulation_only: true,
  model_version: "phase33-deterministic-ai-trader-v1",
  safety_notice: "Simulation only. Not financial advice. No live execution.",
};
