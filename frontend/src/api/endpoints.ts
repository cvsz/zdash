import { apiClient } from "./client";
import {
  mockAgents,
  mockBacktests,
  mockContent,
  mockDrawdown,
  mockHealth,
  mockJobs,
  mockLogs,
  mockSignals,
  mockTradingOwner,
} from "./mockData";
import type {
  AccountSnapshot,
  AdminSafetyCheck,
  AdminUser,
  AdminUserCreateInput,
  AdminUserUpdateInput,
  Agent,
  AuditLogEntry,
  BacktestReport,
  BacktestRequest,
  BacktestResult,
  ContentItem,
  ContentReport,
  DrawdownResult,
  EventLog,
  ExecutionResult,
  HaltState,
  HealthStatus,
  IoTActionResult,
  JobRunResult,
  OptimizationResult,
  PipelineRunResult,
  RiskDecision,
  ScheduledJob,
  SocialPostResult,
  StrategyPromotionDecision,
  TradingScanResult,
  TradingSignal,
  Organization,
  Workspace,
  QueueStatus,
  TaskItem,
  AlertRule,
  AlertEvent,
  NotificationChannel,
  BillingPlan,
  BillingStatus,
  UsageSummary,
  Invoice,
  PluginManifest,
  PluginInstallation,
  EnterpriseLicense,
  BrandingSettings,
  ExportBundle,
  OnboardingChecklist,
  CustomerHealth,
} from "./types";

type AgentMessagePayload = {
  from_agent: string;
  to_agent: string;
  message: string;
  context?: Record<string, unknown>;
};

export const getHealth = () => apiClient.getHealth() as Promise<HealthStatus>;

export const getLogs = async () => {
  const data = await apiClient.get<{ events: EventLog[] }>("/api/logs", {
    events: mockLogs,
  });
  return data.events;
};

export const getAgents = async () => {
  const data = await apiClient.get<{ agents: Agent[] }>("/api/agents", {
    agents: mockAgents,
  });
  return data.agents;
};

export const sendAgentMessage = (payload: AgentMessagePayload) =>
  apiClient.post<Record<string, unknown>>("/api/agents/message", payload, {
    ok: true,
    mock: true,
    response_text:
      "Mock response: Sophia Lane received coordination message in simulation mode.",
  });

export const getTradingStatus = () =>
  apiClient.get<Record<string, unknown>>("/api/trading/status", {
    enabled: true,
    dry_run: true,
    owner: mockTradingOwner,
    mock: true,
  });

export const runTradingScan = async (payload?: { symbol?: string; timeframe?: string }) => {
  const data = await apiClient.post<TradingScanResult>(
    "/api/trading/scan",
    {
      symbol: payload?.symbol ?? "XAUUSD",
      timeframe: payload?.timeframe ?? "M5",
    },
    {
      symbol: "XAUUSD",
      timeframe: "M5",
      candles_analyzed: 200,
      latest_signal: mockSignals[0],
      validation: {
        valid: true,
        reason: "Mock validation passed",
        warnings: ["Simulation only"],
        signal: mockSignals[0],
      },
      ai_summary: "Simulation only",
      timestamp: new Date().toISOString(),
    },
  );
  return data;
};

export const validateSignal = (payload: TradingSignal) =>
  apiClient.post<{
    valid: boolean;
    reason: string;
    warnings: string[];
    signal?: TradingSignal | null;
    timestamp?: string;
  }>(
    "/api/trading/validate-signal",
    payload,
    {
      valid: true,
      reason: "Mock validation",
      warnings: ["Simulation only"],
      signal: payload,
      timestamp: new Date().toISOString(),
    },
  );

export const dryRunExecution = (payload: { signal: TradingSignal; dry_run?: boolean; confirmation?: boolean }) =>
  apiClient.post<ExecutionResult>(
    "/api/trading/dry-run-execute",
    payload,
    {
      ok: true,
      status: "simulated",
      dry_run: true,
      signal: payload.signal,
      message: "Mock dry-run execution completed.",
      simulated_order_id: "mock-order-1",
      timestamp: new Date().toISOString(),
    },
  );

export const getRiskStatus = () =>
  apiClient.get<Record<string, unknown>>("/api/risk/status", {
    guardian_enabled: true,
    halt_state: { halted: false },
    kill_switch_active: false,
    risk_level: "normal",
    mock: true,
  });

export const checkRisk = async (snapshot: AccountSnapshot) => {
  const data = await apiClient.post<{ decision: RiskDecision }>(
    "/api/risk/check",
    snapshot,
    {
      decision: {
        approved: true,
        reason: "Mock risk check passed",
        risk_level: "normal",
        halt_active: false,
      },
    },
  );
  return data.decision;
};

export const getDrawdown = async () => {
  const data = await apiClient.get<{ drawdown: DrawdownResult | null }>(
    "/api/risk/drawdown",
    { drawdown: mockDrawdown },
  );
  return data.drawdown;
};

export const haltRisk = async (reason: string) => {
  const data = await apiClient.post<{ halt_state: HaltState }>(
    "/api/risk/halt",
    { reason },
    {
      halt_state: {
        halted: true,
        reason: reason || "Mock manual halt",
        source: "manual",
      },
    },
  );
  return data.halt_state;
};

export const resumeRisk = async (reason: string, approved = true) => {
  const data = await apiClient.post<{ halt_state: HaltState }>(
    "/api/risk/resume",
    { reason, approved },
    {
      halt_state: {
        halted: false,
        reason: null,
        source: "manual",
        resume_reason: reason,
      },
    },
  );
  return data.halt_state;
};

export const approveExecution = async (payload: { signal: Record<string, unknown>; snapshot: AccountSnapshot }) => {
  const data = await apiClient.post<{ decision: RiskDecision }>(
    "/api/risk/approve-execution",
    payload,
    {
      decision: {
        approved: true,
        reason: "Mock approval granted",
        risk_level: "normal",
        halt_active: false,
      },
    },
  );
  return data.decision;
};

export const getSchedulerStatus = async () => {
  const data = await apiClient.get<{ scheduler: Record<string, unknown> }>(
    "/api/scheduler/status",
    {
      scheduler: { enabled: true, running: true, mock: true },
    },
  );
  return data.scheduler;
};

export const listJobs = async () => {
  const data = await apiClient.get<{ jobs: ScheduledJob[] }>("/api/scheduler/jobs", {
    jobs: mockJobs,
  });
  return data.jobs;
};

export const createJob = async (payload: Record<string, unknown>) => {
  const data = await apiClient.post<{ job: ScheduledJob }>(
    "/api/scheduler/jobs",
    payload,
    { job: mockJobs[0] },
  );
  return data.job;
};

export const runJob = async (jobId: string) => {
  const data = await apiClient.post<{ result: JobRunResult }>(
    `/api/scheduler/jobs/${jobId}/run`,
    {},
    {
      result: {
        job_id: jobId,
        job_type: "custom",
        status: "completed",
        ok: true,
        message: "Mock scheduler run completed",
        output: { mock: true },
        started_at: new Date().toISOString(),
        finished_at: new Date().toISOString(),
        duration_ms: 10,
      },
    },
  );
  return data.result;
};

export const listAdminUsers = async () => {
  const data = await apiClient.get<{ users: AdminUser[] }>("/api/admin/users", {
    users: [],
  });
  return data.users;
};

export const createAdminUser = async (payload: AdminUserCreateInput) => {
  const data = await apiClient.post<{ user: AdminUser }>(
    "/api/admin/users",
    payload,
    {
      user: {
        id: "mock-user",
        email: payload.email,
        display_name: payload.display_name,
        role: payload.role,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    },
  );
  return data.user;
};

export const updateAdminUser = async (
  userId: string,
  payload: AdminUserUpdateInput,
) => {
  const data = await apiClient.patch<{ user: AdminUser }>(
    `/api/admin/users/${userId}`,
    payload,
    {
      user: {
        id: userId,
        email: "mock@example.com",
        display_name: payload.display_name ?? "Mock User",
        role: payload.role ?? "viewer",
        is_active: payload.is_active ?? true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    },
  );
  return data.user;
};

export const deactivateAdminUser = async (userId: string) => {
  const data = await apiClient.delete<{ deactivated: boolean; user_id: string }>(
    `/api/admin/users/${userId}`,
    { deactivated: true, user_id: userId },
  );
  return data;
};

export const listAuditLogs = async (limit = 100, offset = 0) => {
  const query = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  const data = await apiClient.get<{ items: AuditLogEntry[] }>(
    `/api/admin/audit-logs?${query.toString()}`,
    { items: [] },
  );
  return data.items;
};

export const getAdminSafetyCheck = () =>
  apiClient.get<AdminSafetyCheck>("/api/admin/safety-check", {
    status: "safe",
    warnings: [],
    blockers: [],
    score: 100,
  });

export const pauseJob = async (jobId: string) => {
  const data = await apiClient.post<{ job: ScheduledJob }>(
    `/api/scheduler/jobs/${jobId}/pause`,
    {},
    { job: { ...mockJobs[0], id: jobId, status: "paused" } },
  );
  return data.job;
};

export const resumeJob = async (jobId: string) => {
  const data = await apiClient.post<{ job: ScheduledJob }>(
    `/api/scheduler/jobs/${jobId}/resume`,
    {},
    { job: { ...mockJobs[0], id: jobId, status: "pending" } },
  );
  return data.job;
};

export const deleteJob = (jobId: string) =>
  apiClient.delete<{ deleted: boolean; job_id: string }>(
    `/api/scheduler/jobs/${jobId}`,
    { deleted: true, job_id: jobId },
  );

export const listRuns = async (jobId?: string) => {
  const path = jobId ? `/api/scheduler/runs/${jobId}` : "/api/scheduler/runs";
  const data = await apiClient.get<{ runs: JobRunResult[] }>(path, { runs: [] });
  return data.runs;
};

export const getBacktestingStatus = () =>
  apiClient.get<Record<string, unknown>>("/api/backtesting/status", {
    enabled: true,
    dataset_source: "mock",
    primary_strategy: "ob_aggressive",
    mock: true,
  });

export const listStrategies = async () => {
  const data = await apiClient.get<{ strategies: Array<Record<string, unknown>> }>(
    "/api/backtesting/strategies",
    {
      strategies: [
        { name: "ob_aggressive", owner: mockTradingOwner.name, mock: true },
        { name: "ob_conservative", owner: mockTradingOwner.name, mock: true },
        { name: "trend_follow", owner: mockTradingOwner.name, mock: true },
      ],
    },
  );
  return data.strategies;
};

export const runBacktest = async (payload: BacktestRequest) => {
  const data = await apiClient.post<{ result: BacktestResult }>(
    "/api/backtesting/run",
    payload,
    { result: mockBacktests[0] },
  );
  return data.result;
};

export const listBacktestResults = async () => {
  const data = await apiClient.get<{ results: BacktestResult[] }>(
    "/api/backtesting/results",
    { results: mockBacktests },
  );
  return data.results;
};

export const getBacktestResult = async (resultId: string) => {
  const data = await apiClient.get<{ result: BacktestResult }>(
    `/api/backtesting/results/${resultId}`,
    { result: { ...mockBacktests[0], id: resultId } },
  );
  return data.result;
};

export const runOptimization = async (payload: Record<string, unknown>) => {
  const data = await apiClient.post<{ optimization: OptimizationResult }>(
    "/api/backtesting/optimize",
    payload,
    {
      optimization: {
        id: "opt-mock-1",
        ranked_results: mockBacktests,
        best_result: mockBacktests[0],
        sort_metric: "profit_factor",
        total_combinations: 1,
        executed_combinations: 1,
        started_at: new Date().toISOString(),
        finished_at: new Date().toISOString(),
        duration_ms: 12,
      },
    },
  );
  return data.optimization;
};

export const listOptimizations = async () => {
  const data = await apiClient.get<{ optimizations: OptimizationResult[] }>(
    "/api/backtesting/optimizations",
    { optimizations: [] },
  );
  return data.optimizations;
};

export const checkPromotion = async (resultId: string) => {
  const data = await apiClient.post<{ decision: StrategyPromotionDecision }>(
    `/api/backtesting/results/${resultId}/promotion-check`,
    {},
    {
      decision: {
        approved: false,
        reason: "Mock gate: promotion disabled in simulation mode.",
      },
    },
  );
  return data.decision;
};

export const getBacktestReport = async (resultId: string) => {
  const data = await apiClient.get<BacktestReport>(
    `/api/backtesting/results/${resultId}/report`,
    {
      markdown_report:
        "Mock report only. Backtest results are not guaranteed future performance.",
      summary: { result_id: resultId, mock: true },
    },
  );
  return data;
};

export const getContentStatus = () =>
  apiClient.get<Record<string, unknown>>("/api/content/status", {
    enabled: true,
    approval_required: true,
    social_dry_run: true,
    mock: true,
  });

export const createContent = async (payload: Record<string, unknown>) => {
  const data = await apiClient.post<{ item: ContentItem }>(
    "/api/content/create",
    payload,
    { item: mockContent[0] },
  );
  return data.item;
};

export const editContent = async (payload: { content_id: string; instructions?: string }) => {
  const data = await apiClient.post<{ item: ContentItem }>(
    "/api/content/edit",
    payload,
    { item: { ...mockContent[0], id: payload.content_id } },
  );
  return data.item;
};

export const generateGraphic = async (payload: { content_id: string; style?: string; aspect_ratio?: string }) => {
  const data = await apiClient.post<{ item: ContentItem }>(
    "/api/content/generate-graphic",
    payload,
    { item: { ...mockContent[0], id: payload.content_id, status: "graphic_ready" } },
  );
  return data.item;
};

export const scheduleContent = async (payload: { content_id: string; scheduled_at: string; platforms?: string[] }) => {
  const data = await apiClient.post<{ item: ContentItem }>(
    "/api/content/schedule",
    payload,
    { item: { ...mockContent[0], id: payload.content_id, status: "scheduled" } },
  );
  return data.item;
};

export const approveContent = async (payload: { content_id: string; approved_by?: string; notes?: string }) => {
  const data = await apiClient.post<{ item: ContentItem }>(
    "/api/content/approve",
    payload,
    {
      item: {
        ...mockContent[0],
        id: payload.content_id,
        status: "approved",
        approved: true,
      },
    },
  );
  return data.item;
};

export const publishContent = async (payload: { content_id: string; platforms?: string[]; confirmation?: boolean }) => {
  const data = await apiClient.post<{ results: SocialPostResult[] }>(
    "/api/content/post",
    payload,
    {
      results: [
        {
          platform: "x",
          ok: true,
          dry_run: true,
          message: "Mock publish simulated. No real post created.",
        },
      ],
    },
  );
  return data.results;
};

export const runContentPipeline = async (payload: Record<string, unknown>) => {
  const data = await apiClient.post<{ run: PipelineRunResult }>(
    "/api/content/pipeline/run",
    payload,
    {
      run: {
        id: "pipeline-mock-1",
        content_id: mockContent[0].id,
        ok: true,
        status: "scheduled",
        steps: [{ step: "mock_pipeline", ok: true }],
        message: "Mock content pipeline completed in simulation mode.",
        started_at: new Date().toISOString(),
        finished_at: new Date().toISOString(),
        duration_ms: 20,
      },
    },
  );
  return data.run;
};

export const listContentItems = async () => {
  const data = await apiClient.get<{ items: ContentItem[] }>("/api/content/items", {
    items: mockContent,
  });
  return data.items;
};

export const getContentItem = async (contentId: string) => {
  const data = await apiClient.get<{ item: ContentItem }>(
    `/api/content/items/${contentId}`,
    { item: { ...mockContent[0], id: contentId } },
  );
  return data.item;
};

export const listContentRuns = async () => {
  const data = await apiClient.get<{ runs: PipelineRunResult[] }>(
    "/api/content/runs",
    { runs: [] },
  );
  return data.runs;
};

export const getContentReport = async (contentId: string) => {
  const data = await apiClient.get<ContentReport>(
    `/api/content/items/${contentId}/report`,
    {
      summary: { content_id: contentId, mock: true },
      markdown: "Mock report. Publishing is simulation-only unless explicitly enabled.",
      logs: mockLogs,
    },
  );
  return data;
};

export const getIoTStatus = async () => {
  const data = await apiClient.get<{ result: IoTActionResult }>("/api/iot/status", {
    result: {
      ok: true,
      dry_run: true,
      device_alias: "zdash-power-node",
      action: "status",
      message: "Mock IoT status simulated.",
      output: { mock: true, connected: false },
    },
  });
  return data.result;
};

export const runIoTAction = async (payload: {
  device_alias?: string;
  action: "status" | "turn_on" | "turn_off" | "power_cycle";
  confirmation?: boolean;
  payload?: Record<string, unknown>;
}) => {
  const data = await apiClient.post<{ result: IoTActionResult }>(
    "/api/iot/action",
    payload,
    {
      result: {
        ok: true,
        dry_run: true,
        device_alias: payload.device_alias ?? "zdash-power-node",
        action: payload.action,
        message: "Mock IoT action simulated.",
        output: { mock: true },
      },
    },
  );
  return data.result;
};

export const powerCycleIoT = async (deviceAlias = "zdash-power-node", confirmation = false) => {
  const data = await apiClient.post<{ result: IoTActionResult }>(
    "/api/iot/power-cycle",
    {
      device_alias: deviceAlias,
      confirmation,
    },
    {
      result: {
        ok: true,
        dry_run: true,
        device_alias: deviceAlias,
        action: "power_cycle",
        message: "Mock IoT power-cycle simulated.",
        output: { mock: true, requires_confirmation: true },
      },
    },
  );
  return data.result;
};

export const listOrganizations = async () => {
  const data = await apiClient.get<{ organizations: Organization[] }>("/api/tenancy/organizations", {
    organizations: [{ id: "org-1", name: "Zeaz Inc", slug: "zeaz", status: "active", plan: "enterprise", role: "admin", mock: true }],
  });
  return data.organizations;
};

export const listWorkspaces = async (orgId: string) => {
  const data = await apiClient.get<{ workspaces: Workspace[] }>(`/api/tenancy/organizations/${orgId}/workspaces`, {
    workspaces: [{ id: "ws-1", name: "Production", slug: "prod", environment: "production", is_active: true, mock: true }],
  });
  return data.workspaces;
};

export const getQueueStatus = async () => {
  const data = await apiClient.get<{ status: QueueStatus[] }>("/api/workers/queues", {
    status: [{ queue_name: "default", workers_active: 3, tasks_pending: 0, tasks_processing: 1, tasks_failed: 0, uptime_seconds: 3600 }],
  });
  return data.status;
};

export const listTasks = async () => {
  const data = await apiClient.get<{ tasks: TaskItem[] }>("/api/workers/tasks", {
    tasks: [{ id: "task-1", name: "Data Sync", type: "sync", status: "completed", created_at: new Date().toISOString(), retries: 0 }],
  });
  return data.tasks;
};

export const enqueueTask = async (payload: { type: string; payload?: Record<string, unknown> }) => {
  const data = await apiClient.post<{ task: TaskItem }>("/api/workers/enqueue", payload, {
    task: { id: "task-2", name: payload.type, type: payload.type, payload: payload.payload, status: "pending", created_at: new Date().toISOString(), retries: 0 },
  });
  return data.task;
};

export const listAlertRules = async () => {
  const data = await apiClient.get<{ rules: AlertRule[] }>("/api/alerts/rules", {
    rules: [{ id: "rule-1", name: "High Error Rate", condition: "errors > 10", severity: "critical", enabled: true, channels: ["chan-1"], created_at: new Date().toISOString() }],
  });
  return data.rules;
};

export const listAlertEvents = async () => {
  const data = await apiClient.get<{ events: AlertEvent[] }>("/api/alerts/events", {
    events: [{ id: "evt-1", rule_id: "rule-1", message: "Error rate exceeded 10%", severity: "critical", status: "active", triggered_at: new Date().toISOString() }],
  });
  return data.events;
};

export const listNotificationChannels = async () => {
  const data = await apiClient.get<{ channels: NotificationChannel[] }>("/api/alerts/channels", {
    channels: [{ id: "chan-1", type: "slack", target: "#alerts", enabled: true, created_at: new Date().toISOString() }],
  });
  return data.channels;
};

export const testNotificationChannel = async (channelId: string) => {
  const data = await apiClient.post<{ ok: boolean }>("/api/alerts/channels/" + channelId + "/test", {}, { ok: true });
  return data;
};

// Billing API
export const getBillingStatus = async () => {
  return apiClient.get<BillingStatus>("/api/billing/status", {
    status: "active",
    plan_tier: "pro",
    plan_id: "pro",
    provider: "mock",
    cancel_at_period_end: false,
    current_period_start: new Date().toISOString(),
    current_period_end: new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString(),
    trial_ends_at: null,
  });
};

export const getBillingPlans = async () => {
  const data = await apiClient.get<{ plans: BillingPlan[] }>("/api/billing/plans", {
    plans: [
      {
        id: "free",
        tier: "free",
        name: "Free",
        description: "Basic trading operations",
        price_monthly: 0,
        price_yearly: 0,
        features: ["Backtest runs", "Basic signals"],
        limits: { backtest_runs: 10, content_generation_tokens: 0, marketplace_plugins: 0, iot_actions: 0 },
      },
      {
        id: "starter",
        tier: "starter",
        name: "Starter",
        description: "For individual traders",
        price_monthly: 19,
        price_yearly: 190,
        features: ["Backtest runs", "Basic signals", "1 Marketplace plugin"],
        limits: { backtest_runs: 50, content_generation_tokens: 10000, marketplace_plugins: 1, iot_actions: 10 },
      },
      {
        id: "pro",
        tier: "pro",
        name: "Pro",
        description: "Advanced automation and safety",
        price_monthly: 49,
        price_yearly: 490,
        features: ["Backtest runs", "Advanced signals", "5 Marketplace plugins", "IoT control", "Guardian risk guards"],
        limits: { backtest_runs: 200, content_generation_tokens: 50000, marketplace_plugins: 5, iot_actions: 100 },
      },
      {
        id: "enterprise",
        tier: "enterprise",
        name: "Enterprise",
        description: "White-label and custom scale",
        price_monthly: 199,
        price_yearly: 1990,
        features: ["Unlimited backtests", "Priority execution", "Unlimited plugins", "Custom branding", "Exports"],
        limits: { backtest_runs: 999999, content_generation_tokens: 999999, marketplace_plugins: 999999, iot_actions: 999999 },
      },
    ],
  });
  return data.plans;
};

export const startCheckout = async (planId: string) => {
  return apiClient.post<{ checkout_url: string }>("/api/billing/checkout", { plan_id: planId }, {
    checkout_url: "https://mock-billing.test/checkout?plan=" + planId,
  });
};

export const openBillingPortal = async () => {
  return apiClient.post<{ portal_url: string }>("/api/billing/portal", {}, {
    portal_url: "https://mock-billing.test/portal",
  });
};

export const cancelSubscription = async () => {
  return apiClient.post<{ ok: boolean }>("/api/billing/cancel", {}, { ok: true });
};

export const applyMockPlan = async (planTier: string) => {
  return apiClient.post<{ ok: boolean }>("/api/billing/mock/apply-plan", { plan_tier: planTier }, { ok: true });
};

export const getUsageSummary = async () => {
  return apiClient.get<UsageSummary>("/api/billing/usage", {
    metrics: {
      backtest_runs: { limit: 200, usage: 45 },
      content_generation_tokens: { limit: 50000, usage: 12000 },
      marketplace_plugins: { limit: 5, usage: 2 },
      iot_actions: { limit: 100, usage: 85 },
    },
    reset_timestamp: new Date(Date.now() + 15 * 24 * 3600 * 1000).toISOString(),
  });
};

export const getInvoices = async () => {
  const data = await apiClient.get<{ invoices: Invoice[] }>("/api/billing/invoices", {
    invoices: [
      { id: "inv-001", number: "INV-2026-001", amount: 49.00, currency: "USD", status: "paid", created_at: new Date(Date.now() - 30 * 24 * 3600 * 1000).toISOString() },
      { id: "inv-002", number: "INV-2026-002", amount: 49.00, currency: "USD", status: "paid", created_at: new Date(Date.now() - 60 * 24 * 3600 * 1000).toISOString() },
    ],
  });
  return data.invoices;
};

// Marketplace API
export const listMarketplacePlugins = async () => {
  const data = await apiClient.get<{ plugins: PluginManifest[] }>("/api/marketplace/plugins", {
    plugins: [
      {
        id: "plugin-tapo",
        name: "Tapo Smart Plug Controller",
        slug: "tapo-controller",
        version: "1.0.2",
        description: "Control smart plugs and devices automatically based on risk events.",
        author: "zDash Team",
        category: "iot",
        status: "approved",
        required_features: ["feature.iot"],
        required_permissions: ["iot_control"],
        config_schema: {},
        default_config: {},
        entrypoint: "main.py",
        safety_level: "sandbox",
        metadata_json: {},
      },
      {
        id: "plugin-slack",
        name: "Slack Webhook Notifier",
        slug: "slack-notifier",
        version: "2.1.0",
        description: "Send system alerts and trading summaries to Slack channels.",
        author: "Slack Inc.",
        category: "notifications",
        status: "approved",
        required_features: [],
        required_permissions: [],
        config_schema: {},
        default_config: {},
        entrypoint: "slack.py",
        safety_level: "restricted",
        metadata_json: {},
      },
    ],
  });
  return data.plugins;
};

export const getMarketplacePlugin = async (pluginId: string) => {
  const data = await apiClient.get<{ plugin: PluginManifest }>("/api/marketplace/plugins/" + pluginId, {
    plugin: {
      id: pluginId,
      name: pluginId === "plugin-tapo" ? "Tapo Smart Plug Controller" : "Slack Webhook Notifier",
      slug: "plugin-slug",
      version: "1.0.0",
      description: "Plugin description",
      author: "Author",
      category: "general",
      status: "approved",
      required_features: [],
      required_permissions: [],
      config_schema: {},
      default_config: {},
      entrypoint: "main.py",
      safety_level: "sandbox",
      metadata_json: {},
    },
  });
  return data.plugin;
};

export const listPluginInstallations = async () => {
  const data = await apiClient.get<{ installations: PluginInstallation[] }>("/api/marketplace/installations", {
    installations: [
      {
        id: "inst-tapo",
        organization_id: "org-1",
        workspace_id: "ws-1",
        plugin_id: "plugin-tapo",
        version: "1.0.2",
        status: "enabled",
        config_json: {},
        enabled: true,
        installed_by: "admin@zeaz.dev",
        installed_at: new Date(Date.now() - 5 * 24 * 3600 * 1000).toISOString(),
      },
    ],
  });
  return data.installations;
};

export const installMarketplacePlugin = async (pluginId: string, workspaceId: string, config: Record<string, any> = {}) => {
  return apiClient.post<{ ok: boolean, id: string }>("/api/marketplace/install", { plugin_id: pluginId, workspace_id: workspaceId, config }, {
    ok: true,
    id: "inst-tapo",
  });
};

export const enablePluginInstallation = async (installationId: string) => {
  return apiClient.post<{ ok: boolean }>("/api/marketplace/installations/" + installationId + "/enable", {}, { ok: true });
};

export const disablePluginInstallation = async (installationId: string) => {
  return apiClient.post<{ ok: boolean }>("/api/marketplace/installations/" + installationId + "/disable", {}, { ok: true });
};

export const uninstallPluginInstallation = async (installationId: string) => {
  return apiClient.delete<{ ok: boolean }>("/api/marketplace/installations/" + installationId, { ok: true });
};

export const runPluginAction = async (installationId: string, action: string, payload: Record<string, any> = {}) => {
  return apiClient.post<{ ok: boolean, output: any }>("/api/marketplace/installations/" + installationId + "/run", { action, payload }, {
    ok: true,
    output: { status: "simulated_success" },
  });
};

// Enterprise API
export const getEnterpriseStatus = async () => {
  return apiClient.get<{ license: EnterpriseLicense, branding: BrandingSettings }>("/status", {
    license: {
      organization_id: "org-1",
      status: "active",
      tier: "enterprise",
      seats: 50,
      features: ["feature.branding", "feature.exports", "feature.unlimited_backtests"],
      expires_at: new Date(Date.now() + 365 * 24 * 3600 * 1000).toISOString(),
      offline_mode: false,
      issued_to: "Zeaz Inc",
    },
    branding: {
      organization_id: "org-1",
      workspace_id: "ws-1",
      brand_name: "zDash Custom",
      logo_url: null,
      primary_color: "#7c3aed",
      accent_color: "#22c55e",
      support_email: "support@zeaz.dev",
      custom_domain: "dash.zeaz.dev",
    },
  });
};

export const getLicenseStatus = async () => {
  return apiClient.get<EnterpriseLicense>("/license", {
    organization_id: "org-1",
    status: "active",
    tier: "enterprise",
    seats: 50,
    features: ["feature.branding", "feature.exports", "feature.unlimited_backtests"],
    expires_at: new Date(Date.now() + 365 * 24 * 3600 * 1000).toISOString(),
    offline_mode: false,
    issued_to: "Zeaz Inc",
  });
};

export const applyLicense = async (licenseKey: string) => {
  return apiClient.post<{ ok: boolean }>("/license/apply", { license_key: licenseKey }, { ok: true });
};

export const revokeLicense = async () => {
  return apiClient.post<{ ok: boolean }>("/license/revoke", {}, { ok: true });
};

export const getBrandingSettings = async () => {
  return apiClient.get<BrandingSettings>("/branding", {
    organization_id: "org-1",
    workspace_id: "ws-1",
    brand_name: "zDash",
    logo_url: null,
    primary_color: "#7c3aed",
    accent_color: "#22c55e",
    support_email: "support@zeaz.dev",
    custom_domain: "dash.zeaz.dev",
  });
};

export const updateBrandingSettings = async (settings: Partial<BrandingSettings>) => {
  return apiClient.patch<BrandingSettings>("/branding", settings, {
    organization_id: "org-1",
    workspace_id: "ws-1",
    brand_name: settings.brand_name ?? "zDash",
    logo_url: settings.logo_url ?? null,
    primary_color: settings.primary_color ?? "#7c3aed",
    accent_color: settings.accent_color ?? "#22c55e",
    support_email: settings.support_email ?? "support@zeaz.dev",
    custom_domain: settings.custom_domain ?? "dash.zeaz.dev",
  });
};

export const resetBrandingSettings = async () => {
  return apiClient.post<BrandingSettings>("/branding/reset", {}, {
    organization_id: "org-1",
    workspace_id: "ws-1",
    brand_name: "zDash",
    logo_url: null,
    primary_color: "#7c3aed",
    accent_color: "#22c55e",
    support_email: "support@zeaz.dev",
    custom_domain: null,
  });
};

export const listExportBundles = async () => {
  const data = await apiClient.get<{ exports: ExportBundle[] }>("/exports", {
    exports: [
      {
        id: "exp-001",
        organization_id: "org-1",
        workspace_id: "ws-1",
        export_type: "full",
        status: "completed",
        file_path: "/exports/bundle_001.zip",
        include_audit_logs: true,
        include_content: true,
        include_backtests: false,
        include_scheduler: true,
        include_secrets: false,
        created_by: "admin@zeaz.dev",
        created_at: new Date(Date.now() - 2 * 24 * 3600 * 1000).toISOString(),
        completed_at: new Date(Date.now() - 2 * 24 * 3600 * 1000).toISOString(),
      },
    ],
  });
  return data.exports;
};

export const createExportBundle = async (req: {
  export_type: string;
  include_audit_logs: boolean;
  include_content: boolean;
  include_backtests: boolean;
  include_scheduler: boolean;
  include_secrets: boolean;
}) => {
  return apiClient.post<ExportBundle>("/exports", req, {
    id: "exp-new",
    organization_id: "org-1",
    workspace_id: "ws-1",
    export_type: req.export_type,
    status: "completed",
    file_path: "/exports/bundle_new.zip",
    include_audit_logs: req.include_audit_logs,
    include_content: req.include_content,
    include_backtests: req.include_backtests,
    include_scheduler: req.include_scheduler,
    include_secrets: req.include_secrets,
    created_by: "admin@zeaz.dev",
    created_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
  });
};

export const getExportBundle = async (bundleId: string) => {
  return apiClient.get<ExportBundle>("/exports/" + bundleId, {
    id: bundleId,
    organization_id: "org-1",
    workspace_id: "ws-1",
    export_type: "full",
    status: "completed",
    file_path: "/exports/" + bundleId + ".zip",
    include_audit_logs: true,
    include_content: true,
    include_backtests: false,
    include_scheduler: true,
    include_secrets: false,
    created_by: "admin@zeaz.dev",
    created_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
  });
};

export const getOnboardingChecklist = async () => {
  return apiClient.get<OnboardingChecklist>("/onboarding", {
    organization_id: "org-1",
    workspace_id: "ws-1",
    completed_steps: ["create organization", "create workspace"],
    pending_steps: [
      "invite team",
      "verify risk guardian",
      "run first dry-run scan",
      "run first backtest",
      "create first content item",
      "review scheduler jobs",
      "configure billing",
      "review production safety check",
    ],
    progress_percent: 20.0,
  });
};

export const completeOnboardingStep = async (step: string) => {
  return apiClient.post<{ ok: boolean }>("/onboarding/complete-step", { step }, { ok: true });
};

export const resetOnboardingChecklist = async () => {
  return apiClient.post<{ ok: boolean }>("/onboarding/reset", {}, { ok: true });
};

export const getCustomerHealth = async () => {
  return apiClient.get<CustomerHealth>("/customer-health", {
    health_score: 20.0,
    status: "poor",
    active_users: 1,
    usage_trend: "stable",
  });
};

