import { Link } from "react-router-dom";
import { useT } from "../hooks/useT";

export default function NotFound() {
  const { t } = useT();
  return (
    <div className="rounded-card border border-border bg-panel p-6">
      <h2 className="text-xl font-semibold text-white">{t('page_not_found.title')}</h2>
      <p className="mt-2 text-sm text-text-dim">
        {t('page_not_found.description')}
      </p>
      <Link
        to="/"
        className="mt-4 inline-flex rounded-md border border-accent-cyan/40 bg-accent-cyan/20 px-3 py-2 text-sm font-semibold text-accent-cyan transition hover:bg-cyan-500/30"
      >
        {t('common.back_to_dashboard')}
      </Link>
    </div>
  );
}
