import '@testing-library/jest-dom/vitest';
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '../i18n';
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
  PipelineRunResult,
  IoTActionResult,
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
  AITraderStatus,
  RealtimeConnectionState,
  RealtimeEnvelope,
} from '../api/types';

vi.stubEnv('VITE_REALTIME_ENABLED', 'false');
vi.stubEnv('VITE_ENABLE_MOCK_FALLBACK', 'true');

const now = () => new Date().toISOString();

// Build deterministic mock data + mock endpoints synchronously before test imports
const mocks = vi.hoisted(() => {
  const n = () => new Date().toISOString();

  const mockContentItems: ContentItem[] = [
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
      created_at: n(),
      updated_at: n(),
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
      created_at: n(),
      updated_at: n(),
    },
  ];

  const mockTradingOwner = { stable_id: "trading", name: "Damien Cross", title: "Trading Specialist", mock: true };

  const mockQueueStatuses: QueueStatus[] = [
    { queue_name: "default", workers_active: 3, tasks_pending: 2, tasks_processing: 1, tasks_failed: 0, uptime_seconds: 3600 },
  ];

  const mockTasks: TaskItem[] = [
    { id: "task-1", name: "Data Sync", type: "sync", status: "completed", created_at: n(), retries: 0 },
    { id: "task-2", name: "Report Generation", type: "report", status: "processing", created_at: n(), retries: 0 },
  ];

  const mockOrganizations: Organization[] = [
    { id: "org-1", name: "Zeaz Inc", slug: "zeaz", status: "active", plan: "enterprise", role: "admin", mock: true },
  ];

  const mockWorkspaces: Workspace[] = [
    { id: "ws-1", name: "Production", slug: "prod", environment: "production", is_active: true, mock: true },
    { id: "ws-2", name: "Staging", slug: "staging", environment: "staging", is_active: false, mock: true },
  ];

  const mockSignals = [
    { id: "signal-mock-1", symbol: "XAUUSD", timeframe: "M5", strategy: "ob_aggressive", direction: "buy", side: "buy", confidence: 0.71, entry: 2356.4, stop_loss: 2352.0, take_profit: 2364.8, reason: "Mock signal", validated: true, created_at: n(), metadata: { mock: true } },
  ];

  const mockHealth: HealthStatus = { app_name: "zDash", environment: "mock", status: "ok", timestamp: n(), mock: true, services: { api: "simulated", agents: "simulated", risk: "simulated_guarded" } };
  const mockLogs: EventLog[] = [{ id: "log-mock-1", type: "system.mock_fallback", category: "system", source: "mock", message: "Mock fallback active.", level: "warning", created_at: n(), ts: n(), payload: { mock: true } }];
  const mockAgents: Agent[] = [
    { id: "ceo", name: "Alexander Prime", role: "CEO", status: "online", health: "mock_ok", last_event: "Mock sync", capabilities: ["strategy"], metadata: { mock: true }, mock: true },
    { id: "janie", name: "Sophia Lane", role: "Coordinator", status: "online", health: "mock_ok", last_event: "Mock orchestration", capabilities: ["coordination"], metadata: { mock: true }, mock: true },
  ];
  const mockDrawdown = { current_equity: 9950, peak_equity: 10000, daily_start_equity: 10020, total_drawdown_percent: 0.5, daily_drawdown_percent: 0.7, floating_pnl: -50, risk_level: "normal", breached: false };
  const mockJobs: ScheduledJob[] = [
    { id: "job-trading-scan", name: "trading_scan", job_type: "trading_scan", schedule_type: "interval", status: "pending", enabled: true, interval_seconds: 300, payload: { symbol: "XAUUSD", dry_run: true, mock: true }, risk_guarded: true, created_at: n(), updated_at: n() },
    { id: "job-iot", name: "iot_power_cycle", job_type: "iot_power_cycle", schedule_type: "manual", status: "disabled", enabled: false, payload: { dry_run: true, mock: true }, created_at: n(), updated_at: n() },
  ];
  const mockBacktests: BacktestResult[] = [{ id: "bt-mock-1", strategy: "ob_aggressive", symbol: "XAUUSD", timeframe: "M5", metrics: { total_trades: 100, win_rate: 52, profit_factor: 1.3, max_drawdown_percent: 12, net_profit_percent: 18, consecutive_losses: 4 }, equity_curve: [{ x: "W1", y: 10000 }, { x: "W2", y: 10400 }], warnings: ["Mock dataset."] }];
  const mockOptimization: OptimizationResult = { id: "opt-mock-1", ranked_results: mockBacktests as BacktestResult[], best_result: mockBacktests[0], sort_metric: "profit_factor", total_combinations: 1, executed_combinations: 1, started_at: n(), finished_at: n(), duration_ms: 12 };
  const mockPipelineRunResult: PipelineRunResult = { id: "pipeline-mock-1", content_id: "content-mock-1", ok: true, status: "scheduled", steps: [{ step: "mock", ok: true }], message: "Mock pipeline completed.", started_at: n(), finished_at: n(), duration_ms: 20 };
  const mockIoTActionResult: IoTActionResult = { ok: true, dry_run: true, device_alias: "zdash-power-node", action: "status", message: "Mock IoT status.", output: { mock: true, connected: false } };
  const mockAlertRules: AlertRule[] = [{ id: "rule-1", name: "High Error Rate", condition: "errors > 10", severity: "critical", enabled: true, channels: ["chan-1"], created_at: n() }];
  const mockAlertEvents: AlertEvent[] = [{ id: "evt-1", rule_id: "rule-1", message: "Error rate exceeded 10%", severity: "critical", status: "active", triggered_at: n() }];
  const mockChannels: NotificationChannel[] = [{ id: "chan-1", type: "slack", target: "#alerts", enabled: true, created_at: n() }];
  const mockBillingStatus: BillingStatus = { status: "active", plan_tier: "pro", plan_id: "pro", provider: "mock", cancel_at_period_end: false, current_period_start: n(), current_period_end: n(), trial_ends_at: null };
  const mockPlans: BillingPlan[] = [{ id: "free", tier: "free", name: "Free", description: "Basic", price_monthly: 0, price_yearly: 0, features: [], limits: {} }];
  const mockUsage: UsageSummary = { metrics: { backtest_runs: { limit: 200, usage: 45 } }, reset_timestamp: n() };
  const mockInvoices: Invoice[] = [{ id: "inv-001", number: "INV-2026-001", amount: 49, currency: "USD", status: "paid", created_at: n() }];
  const mockPlugins: PluginManifest[] = [{ id: "plugin-tapo", name: "Tapo Smart Plug", slug: "tapo", version: "1.0", description: "Control smart plugs.", author: "zDash", category: "iot", status: "approved", required_features: ["feature.iot"], required_permissions: ["iot_control"], config_schema: {}, default_config: {}, entrypoint: "main.py", safety_level: "sandbox", metadata_json: {} }];
  const mockInstallations: PluginInstallation[] = [{ id: "inst-tapo", organization_id: "org-1", workspace_id: "ws-1", plugin_id: "plugin-tapo", version: "1.0", status: "enabled", config_json: {}, enabled: true, installed_by: "admin@zeaz.dev", installed_at: n() }];
  const mockLicense: EnterpriseLicense = { organization_id: "org-1", status: "active", tier: "enterprise", seats: 50, features: ["feature.branding"], expires_at: n(), offline_mode: false, issued_to: "Zeaz Inc" };
  const mockBranding: BrandingSettings = { organization_id: "org-1", workspace_id: "ws-1", brand_name: "zDash", logo_url: null, primary_color: "#7c3aed", accent_color: "#22c55e", support_email: "support@zeaz.dev", custom_domain: "dash.zeaz.dev" };
  const mockOnboarding: OnboardingChecklist = { organization_id: "org-1", workspace_id: "ws-1", completed_steps: [], pending_steps: ["invite team", "verify guardian"], progress_percent: 0 };
  const mockCustomer: CustomerHealth = { health_score: 20, status: "poor", active_users: 1, usage_trend: "stable" };
  const mockExports: ExportBundle[] = [{ id: "exp-001", organization_id: "org-1", workspace_id: "ws-1", export_type: "full", status: "completed", file_path: "/exports/bundle.zip", include_audit_logs: true, include_content: true, include_backtests: false, include_scheduler: true, include_secrets: false, created_by: "admin@zeaz.dev", created_at: n(), completed_at: n() }];
  const mockAdminUsers: AdminUser[] = [{ id: "admin-1", email: "admin@zeaz.dev", display_name: "Admin", role: "admin", is_active: true, created_at: n(), updated_at: n() }];
  const mockAuditLogs: AuditLogEntry[] = [{ id: "audit-1", actor_user_id: "admin-1", actor_email: "admin@zeaz.dev", action: "user.login", resource_type: "session", resource_id: "sess-1", result: "success", ip_address: "127.0.0.1", user_agent: "test", metadata: {}, created_at: n() }];
  const mockSafetyCheck: AdminSafetyCheck = { status: "safe", warnings: [], blockers: [], score: 100 };
  const mockAITraderStatus: AITraderStatus = { enabled: false, live_trading_enabled: false, dry_run: true, simulation_only: true, model_version: "v1", safety_notice: "Simulation only." };

  return {
    data: {
      mockContentItems, mockTradingOwner, mockQueueStatuses, mockTasks, mockOrganizations, mockWorkspaces,
      mockHealth, mockLogs, mockAgents, mockDrawdown, mockJobs, mockBacktests, mockOptimization,
      mockPipelineRunResult, mockIoTActionResult, mockSignals, mockAlertRules, mockAlertEvents, mockChannels,
      mockBillingStatus, mockPlans, mockUsage, mockInvoices, mockPlugins, mockInstallations, mockLicense,
      mockBranding, mockOnboarding, mockCustomer, mockExports, mockAdminUsers, mockAuditLogs, mockSafetyCheck,
      mockAITraderStatus,
    },
    buildEndpointMocks() {
      return {
        getHealth: vi.fn().mockResolvedValue(mockHealth),
        getLogs: vi.fn().mockResolvedValue(mockLogs),
        getAgents: vi.fn().mockResolvedValue(mockAgents),
        sendAgentMessage: vi.fn().mockResolvedValue({ ok: true, mock: true, response_text: "Mock response." }),
        getTradingStatus: vi.fn().mockResolvedValue({ enabled: true, dry_run: true, owner: mockTradingOwner, mock: true }),
        runTradingScan: vi.fn().mockResolvedValue({ symbol: "XAUUSD", timeframe: "M5", candles_analyzed: 200, latest_signal: mockSignals[0], ai_summary: "Simulation only", timestamp: n() }),
        dryRunExecution: vi.fn().mockResolvedValue({ ok: true, status: "simulated", dry_run: true, message: "Mock dry-run." }),
        validateSignal: vi.fn().mockResolvedValue({ valid: true, reason: "Mock", warnings: [] }),
        getRiskStatus: vi.fn().mockResolvedValue({ guardian_enabled: true, halt_state: { halted: false }, kill_switch_active: false, risk_level: "normal", mock: true }),
        checkRisk: vi.fn().mockResolvedValue({ approved: true, reason: "Mock risk check", risk_level: "normal", halt_active: false }),
        getDrawdown: vi.fn().mockResolvedValue(mockDrawdown),
        haltRisk: vi.fn().mockResolvedValue({ halted: true, reason: "Mock halt", source: "manual" }),
        resumeRisk: vi.fn().mockResolvedValue({ halted: false, reason: null, source: "manual", resume_reason: "Mock resume" }),
        approveExecution: vi.fn().mockResolvedValue({ approved: true, reason: "Mock approval", risk_level: "normal", halt_active: false }),
        getSchedulerStatus: vi.fn().mockResolvedValue({ enabled: true, running: true, mock: true }),
        listJobs: vi.fn().mockResolvedValue(mockJobs),
        createJob: vi.fn().mockResolvedValue(mockJobs[0]),
        pauseJob: vi.fn().mockResolvedValue({ ...mockJobs[0], status: "paused" }),
        resumeJob: vi.fn().mockResolvedValue({ ...mockJobs[0], status: "pending" }),
        deleteJob: vi.fn().mockResolvedValue({ deleted: true }),
        runJob: vi.fn().mockResolvedValue({ job_id: "mock", status: "completed", ok: true, message: "Mock run", output: {}, started_at: n(), finished_at: n(), duration_ms: 10 }),
        listRuns: vi.fn().mockResolvedValue([]),
        getBacktestingStatus: vi.fn().mockResolvedValue({ enabled: true, dataset_source: "mock", primary_strategy: "ob_aggressive", mock: true }),
        listStrategies: vi.fn().mockResolvedValue([{ name: "ob_aggressive", owner: mockTradingOwner.name, mock: true }]),
        runBacktest: vi.fn().mockResolvedValue(mockBacktests[0]),
        listBacktestResults: vi.fn().mockResolvedValue(mockBacktests),
        getBacktestResult: vi.fn().mockResolvedValue(mockBacktests[0]),
        runOptimization: vi.fn().mockResolvedValue(mockOptimization),
        listOptimizations: vi.fn().mockResolvedValue([mockOptimization]),
        checkPromotion: vi.fn().mockResolvedValue({ approved: false, reason: "Mock gate." }),
        getBacktestReport: vi.fn().mockResolvedValue({ markdown_report: "Mock report.", summary: { mock: true } }),
        getContentStatus: vi.fn().mockResolvedValue({ enabled: true, approval_required: true, social_dry_run: true, mock: true }),
        listContentItems: vi.fn().mockResolvedValue(mockContentItems),
        getContentItem: vi.fn().mockResolvedValue(mockContentItems[0]),
        createContent: vi.fn().mockResolvedValue(mockContentItems[0]),
        editContent: vi.fn().mockResolvedValue(mockContentItems[0]),
        generateGraphic: vi.fn().mockResolvedValue({ ...mockContentItems[0], status: "graphic_ready" }),
        scheduleContent: vi.fn().mockResolvedValue({ ...mockContentItems[0], status: "scheduled" }),
        approveContent: vi.fn().mockResolvedValue({ ...mockContentItems[0], status: "approved", approved: true }),
        publishContent: vi.fn().mockResolvedValue([{ platform: "x", ok: true, dry_run: true, message: "Mock publish." }]),
        runContentPipeline: vi.fn().mockResolvedValue(mockPipelineRunResult),
        listContentRuns: vi.fn().mockResolvedValue([mockPipelineRunResult]),
        getContentReport: vi.fn().mockResolvedValue({ summary: { mock: true }, markdown: "Mock.", logs: mockLogs }),
        getIoTStatus: vi.fn().mockResolvedValue(mockIoTActionResult),
        runIoTAction: vi.fn().mockResolvedValue({ ...mockIoTActionResult, action: "turn_on" }),
        powerCycleIoT: vi.fn().mockResolvedValue({ ...mockIoTActionResult, action: "power_cycle" }),
        listOrganizations: vi.fn().mockResolvedValue(mockOrganizations),
        listWorkspaces: vi.fn().mockResolvedValue(mockWorkspaces),
        getQueueStatus: vi.fn().mockResolvedValue(mockQueueStatuses),
        listTasks: vi.fn().mockResolvedValue(mockTasks),
        enqueueTask: vi.fn().mockResolvedValue(mockTasks[0]),
        listAlertRules: vi.fn().mockResolvedValue(mockAlertRules),
        listAlertEvents: vi.fn().mockResolvedValue(mockAlertEvents),
        listNotificationChannels: vi.fn().mockResolvedValue(mockChannels),
        testNotificationChannel: vi.fn().mockResolvedValue({ ok: true }),
        getBillingStatus: vi.fn().mockResolvedValue(mockBillingStatus),
        getBillingPlans: vi.fn().mockResolvedValue(mockPlans),
        startCheckout: vi.fn().mockResolvedValue({ checkout_url: "https://mock.test/checkout" }),
        openBillingPortal: vi.fn().mockResolvedValue({ portal_url: "https://mock.test/portal" }),
        cancelSubscription: vi.fn().mockResolvedValue({ ok: true }),
        applyMockPlan: vi.fn().mockResolvedValue({ ok: true }),
        getUsageSummary: vi.fn().mockResolvedValue(mockUsage),
        getInvoices: vi.fn().mockResolvedValue(mockInvoices),
        listMarketplacePlugins: vi.fn().mockResolvedValue(mockPlugins),
        getMarketplacePlugin: vi.fn().mockResolvedValue(mockPlugins[0]),
        listPluginInstallations: vi.fn().mockResolvedValue(mockInstallations),
        installMarketplacePlugin: vi.fn().mockResolvedValue({ ok: true, id: "inst-new" }),
        enablePluginInstallation: vi.fn().mockResolvedValue({ ok: true }),
        disablePluginInstallation: vi.fn().mockResolvedValue({ ok: true }),
        uninstallPluginInstallation: vi.fn().mockResolvedValue({ ok: true }),
        runPluginAction: vi.fn().mockResolvedValue({ ok: true, output: { status: "simulated" } }),
        getEnterpriseStatus: vi.fn().mockResolvedValue({ license: mockLicense, branding: mockBranding }),
        getLicenseStatus: vi.fn().mockResolvedValue(mockLicense),
        applyLicense: vi.fn().mockResolvedValue({ ok: true }),
        revokeLicense: vi.fn().mockResolvedValue({ ok: true }),
        getBrandingSettings: vi.fn().mockResolvedValue(mockBranding),
        updateBrandingSettings: vi.fn().mockResolvedValue(mockBranding),
        resetBrandingSettings: vi.fn().mockResolvedValue(mockBranding),
        listExportBundles: vi.fn().mockResolvedValue(mockExports),
        createExportBundle: vi.fn().mockResolvedValue(mockExports[0]),
        getExportBundle: vi.fn().mockResolvedValue(mockExports[0]),
        getOnboardingChecklist: vi.fn().mockResolvedValue(mockOnboarding),
        completeOnboardingStep: vi.fn().mockResolvedValue({ ok: true }),
        resetOnboardingChecklist: vi.fn().mockResolvedValue({ ok: true }),
        getCustomerHealth: vi.fn().mockResolvedValue(mockCustomer),
        listAdminUsers: vi.fn().mockResolvedValue(mockAdminUsers),
        createAdminUser: vi.fn().mockResolvedValue(mockAdminUsers[0]),
        updateAdminUser: vi.fn().mockResolvedValue(mockAdminUsers[0]),
        deactivateAdminUser: vi.fn().mockResolvedValue({ deactivated: true, user_id: "mock" }),
        listAuditLogs: vi.fn().mockResolvedValue(mockAuditLogs),
        getAdminSafetyCheck: vi.fn().mockResolvedValue(mockSafetyCheck),
        getAITraderStatus: vi.fn().mockResolvedValue(mockAITraderStatus),
        generateAITraderSignal: vi.fn().mockResolvedValue({ signal: mockSignals[0], validation: { valid: true, reason: "Mock" }, simulation_only: true }),
        runAITraderPaperTrade: vi.fn().mockResolvedValue({ signal: mockSignals[0], dry_run: true, execution: { ok: true, status: "simulated", dry_run: true } }),
      };
    },
    buildRealtimeHooks() {
      const mockConnection: RealtimeConnectionState = { channel: "content", connected: false, connecting: false, stale: false, online: false, retryAttempt: 0, retryInMs: null, lastMessageAt: null, lastHeartbeatAt: null };
      const mockResult = { events: [] as RealtimeEnvelope[], connection: { ...mockConnection }, lastEvent: null as RealtimeEnvelope | null, clearEvents: vi.fn() };
      return {
        useRealtime: vi.fn(() => ({ ...mockResult, connection: { ...mockConnection, channel: "events" as const } })),
        useRiskRealtime: vi.fn(() => ({ ...mockResult, connection: { ...mockConnection, channel: "risk" as const } })),
        useSchedulerRealtime: vi.fn(() => ({ ...mockResult, connection: { ...mockConnection, channel: "scheduler" as const } })),
        useContentRealtime: vi.fn(() => ({ ...mockResult, connection: { ...mockConnection, channel: "content" as const } })),
      };
    },
  };
});

// Mocks built via vi.hoisted above (data shared across test files)
// NOTE: Individual test files can override vi.mock with their own mocks
vi.mock('../api/endpoints', () => mocks.buildEndpointMocks());
vi.mock('../realtime/useRealtime', () => mocks.buildRealtimeHooks());

afterEach(() => {
  cleanup();
});

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: vi.fn(),
});

class ResizeObserverMock {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}

globalThis.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver;

if (!globalThis.crypto) {
  Object.defineProperty(globalThis, 'crypto', {
    value: {
      randomUUID: () => '00000000-0000-4000-8000-000000000000',
    },
    writable: true,
  });
} else if (!globalThis.crypto.randomUUID) {
  Object.defineProperty(globalThis.crypto, 'randomUUID', {
    value: () => '00000000-0000-4000-8000-000000000000',
    writable: true,
  });
}

if (!globalThis.fetch) {
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input instanceof Request ? input.url : String(input);
    if (url.includes('/api/') || url.includes(':8005')) {
      throw new Error(`Unexpected live API call in frontend test: ${init?.method?.toUpperCase() || 'GET'} ${url}`);
    }
    throw new Error('fetch not mocked');
  }) as unknown as typeof fetch;
}

const originalConsoleWarn = console.warn.bind(console);

console.warn = (...args: unknown[]) => {
  const message = args.map((arg) => String(arg)).join(" ");

  if (
    message.includes("React Router Future Flag Warning") ||
    message.includes("v7_startTransition") ||
    message.includes("v7_relativeSplatPath")
  ) {
    return;
  }

  originalConsoleWarn(...args);
};
