import AgentsPagination from '../components/AgentsPagination';
import { useAgentsPagination } from '../hooks/useAgentsPagination';

type AgentTier = 'Legendary' | 'Epic' | 'Rare';

type DashboardAgent = {
  id: string;
  name: string;
  tier: AgentTier;
  title: string;
  role: string;
  accent: string;
  summary: string;
};

const agents: DashboardAgent[] = [
  {
    id: 'alexander-prime',
    name: 'Alexander Prime',
    tier: 'Legendary',
    title: 'CEO • Visionary Leader',
    role: 'Strategic command, roadmap, and executive decisions',
    accent: '🏆',
    summary: 'Owns zDash vision, product direction, operating cadence, and final execution approval.',
  },
  {
    id: 'sophia-lane',
    name: 'Sophia Lane',
    tier: 'Epic',
    title: 'Coordinator • Manager',
    role: 'Team orchestration and delivery management',
    accent: '✨',
    summary: 'Coordinates agent workflows, handoffs, priorities, status reporting, and execution flow.',
  },
  {
    id: 'damien-cross',
    name: 'Damien Cross',
    tier: 'Epic',
    title: 'Trading Specialist',
    role: 'XAU trading scanner and dry-run signal operations',
    accent: '✨',
    summary: 'Manages XAU scanner logic, MT5 mock-safe integration, funnel filters, and signal review.',
  },
  {
    id: 'elena-voss',
    name: 'Elena Voss',
    tier: 'Epic',
    title: 'Content Specialist',
    role: 'Editorial pipeline and content production',
    accent: '✨',
    summary: 'Plans, reviews, and prepares campaign-ready content assets across the zDash pipeline.',
  },
  {
    id: 'maya-quinn',
    name: 'Maya Quinn',
    tier: 'Epic',
    title: 'Social Media Specialist',
    role: 'Social workflow and publishing coordination',
    accent: '✨',
    summary: 'Handles social scheduling, channel packaging, distribution, and audience workflow readiness.',
  },
  {
    id: 'julian-reed',
    name: 'Julian Reed',
    tier: 'Epic',
    title: 'Design Specialist',
    role: 'Graphics, visual systems, and dashboard polish',
    accent: '✨',
    summary: 'Builds visual assets, graphic concepts, UI treatments, and design-system consistency.',
  },
  {
    id: 'victor-hale',
    name: 'Victor Hale',
    tier: 'Epic',
    title: 'Risk Manager',
    role: 'Guardian risk, drawdown, and kill-switch oversight',
    accent: '✨',
    summary: 'Monitors risk gates, halt state, drawdown thresholds, and safety-first execution policy.',
  },
  {
    id: 'nathan-cole',
    name: 'Nathan Cole',
    tier: 'Rare',
    title: 'Analyst • Developer',
    role: 'Analysis, implementation, and test support',
    accent: '🎯',
    summary: 'Supports backend/frontend analysis, implementation tasks, validation, and developer workflows.',
  },
  {
    id: 'isla-grant',
    name: 'Isla Grant',
    tier: 'Rare',
    title: 'Scheduler • Automation',
    role: 'Friday-style scheduler and automation operations',
    accent: '🎯',
    summary: 'Owns scheduler jobs, automation safety, dry-run action routing, and operational timing.',
  },
];

const tierStyle: Record<AgentTier, string> = {
  Legendary: 'border-amber-300/60 bg-amber-400/10 text-amber-100',
  Epic: 'border-fuchsia-300/50 bg-fuchsia-400/10 text-fuchsia-100',
  Rare: 'border-cyan-300/50 bg-cyan-400/10 text-cyan-100',
};

function tierLabel(tier: AgentTier) {
  if (tier === 'Legendary') return '🏆 Legendary';
  if (tier === 'Epic') return '✨ Epic';
  return '🎯 Rare';
}

export default function TeamRoster() {
  const {
    agentsPerPage,
    currentPage,
    totalItems,
    totalPages,
    pageItems,
    pageStart,
    pageEnd,
    setAgentsPerPage,
    goToPage,
  } = useAgentsPagination(agents);

  return (
    <section className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8 text-slate-100 sm:px-6 lg:px-8">
      <div className="rounded-3xl border border-slate-700/70 bg-slate-950/60 p-6 shadow-2xl shadow-slate-950/30 backdrop-blur">
        <p className="text-xs font-bold uppercase tracking-[0.32em] text-cyan-300">zDash Command Roster</p>
        <div className="mt-3 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-white md:text-4xl">Team Roster</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              Agent roster renamed into Legendary, Epic, and Rare operating tiers with per-page pagination for cleaner dashboard navigation.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center text-xs font-bold uppercase tracking-[0.18em] text-slate-300">
            <span className="rounded-2xl border border-amber-300/40 bg-amber-400/10 px-3 py-2">1 Legendary</span>
            <span className="rounded-2xl border border-fuchsia-300/40 bg-fuchsia-400/10 px-3 py-2">6 Epic</span>
            <span className="rounded-2xl border border-cyan-300/40 bg-cyan-400/10 px-3 py-2">2 Rare</span>
          </div>
        </div>
      </div>

      <AgentsPagination
        pageStart={pageStart}
        pageEnd={pageEnd}
        totalItems={totalItems}
        totalPages={totalPages}
        currentPage={currentPage}
        agentsPerPage={agentsPerPage}
        onPageSizeChange={setAgentsPerPage}
        onPageChange={goToPage}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {pageItems.map((agent) => (
          <article
            key={agent.id}
            className="rounded-3xl border border-slate-700/70 bg-slate-950/55 p-5 shadow-xl shadow-slate-950/25 transition hover:-translate-y-1 hover:border-cyan-300/60"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-3xl" aria-hidden="true">{agent.accent}</p>
                <h2 className="mt-3 text-2xl font-black text-white">{agent.name}</h2>
                <p className="mt-1 text-sm font-semibold text-cyan-200">{agent.title}</p>
              </div>
              <span className={`rounded-full border px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] ${tierStyle[agent.tier]}`}>
                {tierLabel(agent.tier)}
              </span>
            </div>

            <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Primary Role</p>
              <p className="mt-2 text-sm text-slate-200">{agent.role}</p>
            </div>

            <p className="mt-4 text-sm leading-6 text-slate-300">{agent.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
