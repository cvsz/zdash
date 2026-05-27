type EmptyStateProps = {
  message: string;
  hint?: string;
};

export default function EmptyState({ message, hint }: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-300">
      <p>{message}</p>
      {hint ? <p className="mt-1 text-xs text-slate-400">{hint}</p> : null}
    </div>
  );
}
