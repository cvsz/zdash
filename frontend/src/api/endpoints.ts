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
