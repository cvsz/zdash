import { vi } from "vitest";
import * as mockData from "./apiMockData";

export function buildMockEndpoints() {
  return {
    getHealth: vi.fn().mockResolvedValue(mockData.mockHealth),
    getLogs: vi.fn().mockResolvedValue(mockData.mockLogs),
    getAgents: vi.fn().mockResolvedValue(mockData.mockAgents),
    sendAgentMessage: vi.fn().mockResolvedValue({ ok: true, mock: true, response_text: "Mock response." }),

    getTradingStatus: vi.fn().mockResolvedValue({
      enabled: true, dry_run: true, owner: mockData.mockTradingOwner, mock: true,
    }),
    runTradingScan: vi.fn().mockResolvedValue({
      symbol: "XAUUSD", timeframe: "M5", candles_analyzed: 200,
      latest_signal: mockData.mockSignals[0],
      ai_summary: "Simulation only", timestamp: new Date().toISOString(),
    }),
    dryRunExecution: vi.fn().mockResolvedValue({
      ok: true, status: "simulated", dry_run: true, message: "Mock dry-run completed.",
    }),
    validateSignal: vi.fn().mockResolvedValue({
      valid: true, reason: "Mock validation", warnings: ["Simulation only"],
    }),

    getRiskStatus: vi.fn().mockResolvedValue({
      guardian_enabled: true, halt_state: { halted: false }, kill_switch_active: false,
      risk_level: "normal", mock: true,
    }),
    checkRisk: vi.fn().mockResolvedValue({
      approved: true, reason: "Mock risk check passed", risk_level: "normal", halt_active: false,
    }),
    getDrawdown: vi.fn().mockResolvedValue(mockData.mockDrawdown),
    haltRisk: vi.fn().mockResolvedValue({ halted: true, reason: "Mock halt", source: "manual" }),
    resumeRisk: vi.fn().mockResolvedValue({
      halted: false, reason: null, source: "manual", resume_reason: "Mock resume",
    }),
    approveExecution: vi.fn().mockResolvedValue({
      approved: true, reason: "Mock approval", risk_level: "normal", halt_active: false,
    }),

    getSchedulerStatus: vi.fn().mockResolvedValue({ enabled: true, running: true, mock: true }),
    listJobs: vi.fn().mockResolvedValue(mockData.mockJobs),
    createJob: vi.fn().mockResolvedValue(mockData.mockJobs[0]),
    pauseJob: vi.fn().mockResolvedValue({ ...mockData.mockJobs[0], status: "paused" }),
    resumeJob: vi.fn().mockResolvedValue({ ...mockData.mockJobs[0], status: "pending" }),
    deleteJob: vi.fn().mockResolvedValue({ deleted: true }),
    runJob: vi.fn().mockResolvedValue({
      job_id: "mock", status: "completed", ok: true, message: "Mock scheduler run completed",
      output: {}, started_at: new Date().toISOString(), finished_at: new Date().toISOString(), duration_ms: 10,
    }),
    listRuns: vi.fn().mockResolvedValue([]),

    getBacktestingStatus: vi.fn().mockResolvedValue({
      enabled: true, dataset_source: "mock", primary_strategy: "ob_aggressive", mock: true,
    }),
    listStrategies: vi.fn().mockResolvedValue([
      { name: "ob_aggressive", owner: mockData.mockTradingOwner.name, mock: true },
    ]),
    runBacktest: vi.fn().mockResolvedValue(mockData.mockBacktests[0]),
    listBacktestResults: vi.fn().mockResolvedValue(mockData.mockBacktests),
    getBacktestResult: vi.fn().mockResolvedValue(mockData.mockBacktests[0]),
    runOptimization: vi.fn().mockResolvedValue(mockData.mockOptimization),
    listOptimizations: vi.fn().mockResolvedValue([mockData.mockOptimization]),
    checkPromotion: vi.fn().mockResolvedValue({
      approved: false, reason: "Mock gate: promotion disabled.",
    }),
    getBacktestReport: vi.fn().mockResolvedValue({
      markdown_report: "Mock report.", summary: { mock: true },
    }),

    getContentStatus: vi.fn().mockResolvedValue({
      enabled: true, approval_required: true, social_dry_run: true, mock: true,
    }),
    listContentItems: vi.fn().mockResolvedValue(mockData.mockContentItems),
    getContentItem: vi.fn().mockResolvedValue(mockData.mockContentItems[0]),
    createContent: vi.fn().mockResolvedValue(mockData.mockContentItems[0]),
    editContent: vi.fn().mockResolvedValue(mockData.mockContentItems[0]),
    generateGraphic: vi.fn().mockResolvedValue({ ...mockData.mockContentItems[0], status: "graphic_ready" }),
    scheduleContent: vi.fn().mockResolvedValue({ ...mockData.mockContentItems[0], status: "scheduled" }),
    approveContent: vi.fn().mockResolvedValue({ ...mockData.mockContentItems[0], status: "approved", approved: true }),
    publishContent: vi.fn().mockResolvedValue([
      { platform: "x", ok: true, dry_run: true, message: "Mock publish simulated." },
    ]),
    runContentPipeline: vi.fn().mockResolvedValue(mockData.mockPipelineRunResult),
    listContentRuns: vi.fn().mockResolvedValue([mockData.mockPipelineRunResult]),
    getContentReport: vi.fn().mockResolvedValue({
      summary: { mock: true }, markdown: "Mock report.", logs: mockData.mockLogs,
    }),

    getIoTStatus: vi.fn().mockResolvedValue(mockData.mockIoTActionResult),
    runIoTAction: vi.fn().mockResolvedValue({ ...mockData.mockIoTActionResult, action: "turn_on" }),
    powerCycleIoT: vi.fn().mockResolvedValue({ ...mockData.mockIoTActionResult, action: "power_cycle" }),

    listOrganizations: vi.fn().mockResolvedValue(mockData.mockOrganizations),
    listWorkspaces: vi.fn().mockResolvedValue(mockData.mockWorkspaces),

    getQueueStatus: vi.fn().mockResolvedValue(mockData.mockQueueStatuses),
    listTasks: vi.fn().mockResolvedValue(mockData.mockTasks),
    enqueueTask: vi.fn().mockResolvedValue(mockData.mockTasks[0]),

    listAlertRules: vi.fn().mockResolvedValue(mockData.mockAlertRules),
    listAlertEvents: vi.fn().mockResolvedValue(mockData.mockAlertEvents),
    listNotificationChannels: vi.fn().mockResolvedValue(mockData.mockNotificationChannels),
    testNotificationChannel: vi.fn().mockResolvedValue({ ok: true }),

    getBillingStatus: vi.fn().mockResolvedValue(mockData.mockBillingStatus),
    getBillingPlans: vi.fn().mockResolvedValue(mockData.mockBillingPlans),
    startCheckout: vi.fn().mockResolvedValue({ checkout_url: "https://mock.test/checkout" }),
    openBillingPortal: vi.fn().mockResolvedValue({ portal_url: "https://mock.test/portal" }),
    cancelSubscription: vi.fn().mockResolvedValue({ ok: true }),
    applyMockPlan: vi.fn().mockResolvedValue({ ok: true }),
    getUsageSummary: vi.fn().mockResolvedValue(mockData.mockUsageSummary),
    getInvoices: vi.fn().mockResolvedValue(mockData.mockInvoices),

    listMarketplacePlugins: vi.fn().mockResolvedValue(mockData.mockPlugins),
    getMarketplacePlugin: vi.fn().mockResolvedValue(mockData.mockPlugins[0]),
    listPluginInstallations: vi.fn().mockResolvedValue(mockData.mockPluginInstallations),
    installMarketplacePlugin: vi.fn().mockResolvedValue({ ok: true, id: "inst-new" }),
    enablePluginInstallation: vi.fn().mockResolvedValue({ ok: true }),
    disablePluginInstallation: vi.fn().mockResolvedValue({ ok: true }),
    uninstallPluginInstallation: vi.fn().mockResolvedValue({ ok: true }),
    runPluginAction: vi.fn().mockResolvedValue({ ok: true, output: { status: "simulated" } }),

    getEnterpriseStatus: vi.fn().mockResolvedValue({
      license: mockData.mockEnterpriseLicense, branding: mockData.mockBrandingSettings,
    }),
    getLicenseStatus: vi.fn().mockResolvedValue(mockData.mockEnterpriseLicense),
    applyLicense: vi.fn().mockResolvedValue({ ok: true }),
    revokeLicense: vi.fn().mockResolvedValue({ ok: true }),
    getBrandingSettings: vi.fn().mockResolvedValue(mockData.mockBrandingSettings),
    updateBrandingSettings: vi.fn().mockResolvedValue(mockData.mockBrandingSettings),
    resetBrandingSettings: vi.fn().mockResolvedValue(mockData.mockBrandingSettings),
    listExportBundles: vi.fn().mockResolvedValue(mockData.mockExportBundles),
    createExportBundle: vi.fn().mockResolvedValue(mockData.mockExportBundles[0]),
    getExportBundle: vi.fn().mockResolvedValue(mockData.mockExportBundles[0]),
    getOnboardingChecklist: vi.fn().mockResolvedValue(mockData.mockOnboardingChecklist),
    completeOnboardingStep: vi.fn().mockResolvedValue({ ok: true }),
    resetOnboardingChecklist: vi.fn().mockResolvedValue({ ok: true }),
    getCustomerHealth: vi.fn().mockResolvedValue(mockData.mockCustomerHealth),

    listAdminUsers: vi.fn().mockResolvedValue(mockData.mockAdminUsers),
    createAdminUser: vi.fn().mockResolvedValue(mockData.mockAdminUsers[0]),
    updateAdminUser: vi.fn().mockResolvedValue(mockData.mockAdminUsers[0]),
    deactivateAdminUser: vi.fn().mockResolvedValue({ deactivated: true, user_id: "mock" }),
    listAuditLogs: vi.fn().mockResolvedValue(mockData.mockAuditLogs),
    getAdminSafetyCheck: vi.fn().mockResolvedValue(mockData.mockAdminSafetyCheck),

    getAITraderStatus: vi.fn().mockResolvedValue(mockData.mockAITraderStatus),
    generateAITraderSignal: vi.fn().mockResolvedValue({
      signal: mockData.mockSignals[0],
      validation: { valid: true, reason: "Mock AI trader signal." },
      simulation_only: true,
    }),
    runAITraderPaperTrade: vi.fn().mockResolvedValue({
      signal: mockData.mockSignals[0],
      dry_run: true,
      execution: { ok: true, status: "simulated", dry_run: true },
    }),
  };
}
