export type AgentTier = "Legendary" | "Epic" | "Rare";

export type CanonicalAgent = {
  id:
    | "ceo"
    | "janie"
    | "guardian"
    | "friday"
    | "joe"
    | "editor"
    | "graphic"
    | "social"
    | "trading";
  name: string;
  title: string;
  tier: AgentTier;
  role: string;
  summary: string;
};

export const CANONICAL_AGENTS: CanonicalAgent[] = [
  {
    id: "ceo",
    name: "Alexander Prime",
    title: "CEO - Visionary Leader",
    tier: "Legendary",
    role: "Strategic command, roadmap, and executive decisions",
    summary:
      "Owns zDash vision, product direction, operating cadence, and final execution approval.",
  },
  {
    id: "janie",
    name: "Sophia Lane",
    title: "Coordinator - Manager",
    tier: "Epic",
    role: "Team orchestration and delivery management",
    summary:
      "Coordinates agent workflows, handoffs, priorities, status reporting, and execution flow.",
  },
  {
    id: "guardian",
    name: "Victor Hale",
    title: "Risk Manager",
    tier: "Epic",
    role: "Guardian risk, drawdown, and kill-switch oversight",
    summary:
      "Monitors risk gates, halt state, drawdown thresholds, and safety-first execution policy.",
  },
  {
    id: "friday",
    name: "Isla Grant",
    title: "Scheduler - Automation",
    tier: "Rare",
    role: "Scheduler, IoT safety routing, and automation operations",
    summary:
      "Owns scheduler jobs, automation safety, dry-run routing, and operational timing.",
  },
  {
    id: "joe",
    name: "Nathan Cole",
    title: "Analyst - Developer",
    tier: "Rare",
    role: "Backtesting, strategy lab analysis, and optimization support",
    summary:
      "Leads simulation-first strategy validation, performance diagnostics, and promotion gates.",
  },
  {
    id: "editor",
    name: "Elena Voss",
    title: "Content Specialist",
    tier: "Epic",
    role: "Editorial pipeline and content production",
    summary:
      "Plans, reviews, and prepares campaign-ready content assets across the zDash pipeline.",
  },
  {
    id: "graphic",
    name: "Julian Reed",
    title: "Design Specialist",
    tier: "Epic",
    role: "Graphics, visual systems, and creative quality",
    summary:
      "Builds visual assets, graphic concepts, and design system consistency.",
  },
  {
    id: "social",
    name: "Maya Quinn",
    title: "Social Media Specialist",
    tier: "Epic",
    role: "Social workflow and publishing coordination",
    summary:
      "Handles social scheduling, channel packaging, distribution, and approval-gated publishing.",
  },
  {
    id: "trading",
    name: "Damien Cross",
    title: "Trading Specialist",
    tier: "Epic",
    role: "XAU scanner operations and dry-run execution",
    summary:
      "Manages XAU scanner logic, funnel filters, risk-gated review, and dry-run trade execution.",
  },
];

export const AGENT_NAME_BY_ID = CANONICAL_AGENTS.reduce<Record<string, string>>(
  (accumulator, agent) => {
    accumulator[agent.id] = agent.name;
    return accumulator;
  },
  {},
);

export const AGENT_TITLE_BY_ID = CANONICAL_AGENTS.reduce<Record<string, string>>(
  (accumulator, agent) => {
    accumulator[agent.id] = agent.title;
    return accumulator;
  },
  {},
);
