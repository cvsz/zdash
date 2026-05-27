type DryRunBannerProps = {
  text?: string;
};

export default function DryRunBanner({
  text = "DRY_RUN enabled: execution is simulation-only.",
}: DryRunBannerProps) {
  return (
    <div className="rounded-lg border border-amber-400/40 bg-amber-500/10 px-4 py-3 text-sm font-semibold text-amber-100">
      {text}
    </div>
  );
}
