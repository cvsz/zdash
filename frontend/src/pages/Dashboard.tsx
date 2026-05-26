import { mockFallbackActive } from '../api/client';
import PageHeader from '../components/layout/PageHeader';
import TeamRoster from './TeamRoster';

export default function Dashboard() {
  return (
    <div>
      <PageHeader title="Dashboard" />

      {mockFallbackActive && (
        <div className="mx-auto mb-4 max-w-7xl rounded-2xl border border-amber-300/40 bg-amber-400/10 px-4 py-3 text-sm font-semibold text-amber-100">
          Mock fallback mode
        </div>
      )}

      <TeamRoster />
    </div>
  );
}
