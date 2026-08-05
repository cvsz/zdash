import { apiClient } from "./client";

export type DataSource = "live" | "sample";
export type StageStatus = "ready" | "attention" | "planned";

export type MarketingMetric = {
  key: string;
  label: string;
  value: number | string;
  detail: string;
  source: DataSource;
};

export type MarketingStage = {
  key: string;
  label: string;
  description: string;
  status: StageStatus;
  route?: string | null;
};

export type HookInsight = {
  id: string;
  hook: string;
  category: string;
  usage_count: number;
  performance_note: string;
  source: DataSource;
};

export type CompetitorInsight = {
  id: string;
  name: string;
  platform: string;
  momentum: string;
  opportunity: string;
  source: DataSource;
};

export type TrendInsight = {
  id: string;
  topic: string;
  signal: string;
  recommended_angle: string;
  source: DataSource;
};

export type ScheduleItem = {
  id: string;
  title: string;
  platform: string;
  scheduled_for: string;
  status: string;
  source: DataSource;
};

export type CampaignRecommendation = {
  id: string;
  campaign: string;
  recommendation: string;
  rationale: string;
  approval_required: boolean;
  source: DataSource;
};

export type MarketingDashboard = {
  generated_at: string;
  source_mode: string;
  disclaimer: string;
  metrics: MarketingMetric[];
  system_map: MarketingStage[];
  hooks: HookInsight[];
  competitors: CompetitorInsight[];
  trends: TrendInsight[];
  schedule: ScheduleItem[];
  campaign_recommendations: CampaignRecommendation[];
};

const sampleFallback: MarketingDashboard = {
  generated_at: new Date().toISOString(),
  source_mode: "offline_sample",
  disclaimer:
    "The API is unavailable. Every value on this page is labelled sample and no live platform analytics are being represented.",
  metrics: [
    { key: "content_assets", label: "Content assets", value: 0, detail: "API unavailable", source: "sample" },
    { key: "awaiting_approval", label: "Awaiting approval", value: 0, detail: "API unavailable", source: "sample" },
    { key: "scheduled", label: "Scheduled", value: 0, detail: "API unavailable", source: "sample" },
    { key: "published", label: "Published", value: 0, detail: "API unavailable", source: "sample" },
  ],
  system_map: [
    { key: "sources", label: "Sources & connectors", description: "Connect brand and platform data", status: "attention", route: "/settings" },
    { key: "intelligence", label: "Marketing intelligence", description: "Convert signals into opportunities", status: "ready", route: "/marketing" },
    { key: "production", label: "Content production", description: "Create and review content", status: "ready", route: "/content" },
    { key: "distribution", label: "Scheduling & distribution", description: "Queue approved content", status: "ready", route: "/scheduler" },
  ],
  hooks: [
    {
      id: "offline-hook",
      hook: "Connect the zDash API to load the governed hook workspace.",
      category: "system",
      usage_count: 0,
      performance_note: "Offline sample",
      source: "sample",
    },
  ],
  competitors: [],
  trends: [],
  schedule: [],
  campaign_recommendations: [
    {
      id: "offline-campaign",
      campaign: "No connected campaign",
      recommendation: "Keep mutations disabled",
      rationale: "The dashboard API is unavailable",
      approval_required: true,
      source: "sample",
    },
  ],
};

export const getMarketingDashboard = () =>
  apiClient.get<MarketingDashboard>("/api/marketing/overview", sampleFallback);
