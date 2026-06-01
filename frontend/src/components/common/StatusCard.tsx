import type { ReactNode } from "react";

import { useT } from "../../hooks/useT";
import Badge, { type BadgeVariant } from "./Badge";
import SectionCard from "./SectionCard";

type StatusCardProps = {
  title: string;
  status: string;
  description?: string;
  icon?: ReactNode;
  severity?: BadgeVariant;
};

export default function StatusCard({
  title,
  status,
  description,
  icon,
  severity = "normal",
}: StatusCardProps) {
  const { t } = useT();
  return (
    <SectionCard
      title={title}
      actions={<Badge variant={severity}>{status}</Badge>}
      className="h-full"
    >
      <div className="flex items-start gap-3">
        {icon ? <div className="pt-0.5 text-slate-300">{icon}</div> : null}
        <p className="text-sm text-slate-300">{description || t('status_card.no_details')}</p>
      </div>
    </SectionCard>
  );
}
