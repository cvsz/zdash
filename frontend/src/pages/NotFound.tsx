import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="rounded-card border border-border bg-panel p-6">
      <h2 className="text-xl font-semibold text-white">Page not found</h2>
      <p className="mt-2 text-sm text-text-dim">
        The requested route does not exist in this dashboard shell.
      </p>
      <Link
        to="/"
        className="mt-4 inline-flex rounded-md border border-accent-cyan/40 bg-accent-cyan/20 px-3 py-2 text-sm font-semibold text-accent-cyan transition hover:bg-cyan-500/30"
      >
        Back to Dashboard
      </Link>
    </div>
  );
}
