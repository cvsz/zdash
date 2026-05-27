type LoadingStateProps = {
  label?: string;
};

export default function LoadingState({ label = "Loading data..." }: LoadingStateProps) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-300">
      {label}
    </div>
  );
}
