import { useT } from "../../hooks/useT";
import type { BadgeVariant } from "./Badge";
import Badge from "./Badge";
import SectionCard from "./SectionCard";

type MetricCardProps = {
  label: string;
  value: string | number;
  delta?: string;
  severity?: BadgeVariant;
};

export default function MetricCard({
  label,
  value,
  delta,
  severity = "muted",
}: MetricCardProps) {
  const { t } = useT();
  return (
    <SectionCard className="h-full">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{typeof value === 'number' ? value : (value || t('metric_card_no_value'))}</p>
      {delta ? (
        <div className="mt-3">
          <Badge variant={severity}>{delta}</Badge>
        </div>
      ) : null}
    </SectionCard>
  );
}
