type ErrorStateProps = {
  message: string;
  retryLabel?: string;
  onRetry?: () => void;
};

export default function ErrorState({
  message,
  retryLabel = "Retry",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-100">
      <p>{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 rounded-md border border-rose-400/60 px-3 py-1.5 text-xs font-semibold text-rose-100 transition hover:bg-rose-500/20"
        >
          {retryLabel}
        </button>
      ) : null}
    </div>
  );
}
