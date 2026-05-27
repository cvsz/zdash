import Badge from "../components/common/Badge";
import PageHeader from "../components/layout/PageHeader";

const ownership = [
  { owner: "Victor Hale", module: "Risk" },
  { owner: "Isla Grant", module: "Scheduler + IoT" },
  { owner: "Nathan Cole", module: "Backtesting" },
  { owner: "Elena Voss / Julian Reed / Maya Quinn", module: "Content Pipeline" },
  { owner: "Sophia Lane", module: "Runtime Orchestration" },
  { owner: "Damien Cross", module: "Trading" },
];

export default function OrgMapPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        title="Org Map"
        subtitle="Canonical zDash command structure and module ownership."
      />

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Command Chain</h3>
        <pre className="mt-3 overflow-x-auto rounded-md border border-slate-800 bg-slate-950/70 p-3 text-sm text-slate-200">
{`Alexander Prime
└── Sophia Lane
    ├── Victor Hale
    ├── Isla Grant
    ├── Nathan Cole
    ├── Elena Voss
    ├── Julian Reed
    ├── Maya Quinn
    └── Damien Cross`}
        </pre>
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Module Ownership</h3>
        <div className="mt-3 grid gap-2 md:grid-cols-2">
          {ownership.map((item) => (
            <div key={item.owner} className="rounded-md border border-slate-800 bg-slate-950/70 p-3">
              <p className="text-sm font-semibold text-slate-100">{item.owner}</p>
              <p className="mt-1 text-xs text-slate-400">{item.module}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <h3 className="text-sm font-semibold text-white">Roles</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {[
            "Alexander Prime",
            "Sophia Lane",
            "Victor Hale",
            "Isla Grant",
            "Nathan Cole",
            "Elena Voss",
            "Julian Reed",
            "Maya Quinn",
            "Damien Cross",
          ].map((name) => (
            <Badge key={name} variant="normal">
              {name}
            </Badge>
          ))}
        </div>
      </section>
    </div>
  );
}
