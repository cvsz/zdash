import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-6">
      <h2 className="text-xl font-semibold text-white">Page not found</h2>
      <p className="mt-2 text-sm text-slate-400">
        The requested route does not exist in this dashboard shell.
      </p>
      <Link
        to="/"
        className="mt-4 inline-flex rounded-md border border-cyan-500/40 bg-cyan-500/20 px-3 py-2 text-sm font-semibold text-cyan-50 transition hover:bg-cyan-500/30"
      >
        Back to Dashboard
      </Link>
    </div>
  );
}
