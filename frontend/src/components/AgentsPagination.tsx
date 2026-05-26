import { AGENTS_PAGE_SIZE_OPTIONS } from '../hooks/useAgentsPagination';

type AgentsPaginationProps = {
  pageStart: number;
  pageEnd: number;
  totalItems: number;
  totalPages: number;
  currentPage: number;
  agentsPerPage: number;
  onPageSizeChange: (size: number) => void;
  onPageChange: (page: number) => void;
};

export default function AgentsPagination({
  pageStart,
  pageEnd,
  totalItems,
  totalPages,
  currentPage,
  agentsPerPage,
  onPageSizeChange,
  onPageChange,
}: AgentsPaginationProps) {
  return (
    <div className="rounded-2xl border border-slate-700/70 bg-slate-950/55 p-4 shadow-xl shadow-slate-950/20">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-300">
          Showing <span className="text-cyan-300">{pageStart}-{pageEnd}</span> of{' '}
          <span className="text-cyan-300">{totalItems}</span> agents
        </p>

        <label className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">
          <span>Agents per page</span>
          <select
            className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-cyan-400"
            value={agentsPerPage}
            onChange={(event) => onPageSizeChange(Number(event.target.value))}
          >
            {AGENTS_PAGE_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-center gap-2" aria-label="Agent roster pagination">
        <button
          type="button"
          className="rounded-full border border-slate-700 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-slate-200 transition hover:border-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          ← Prev
        </button>

        {Array.from({ length: totalPages }, (_, index) => index + 1).map((page) => (
          <button
            key={page}
            type="button"
            className={`min-w-10 rounded-full border px-3 py-2 text-sm font-bold transition ${
              page === currentPage
                ? 'border-cyan-300 bg-cyan-400/15 text-cyan-200'
                : 'border-slate-700 text-slate-300 hover:border-cyan-400'
            }`}
            onClick={() => onPageChange(page)}
            aria-current={page === currentPage ? 'page' : undefined}
          >
            {page}
          </button>
        ))}

        <button
          type="button"
          className="rounded-full border border-slate-700 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-slate-200 transition hover:border-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next →
        </button>
      </div>
    </div>
  );
}
