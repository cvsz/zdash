import SectionCard from "../common/SectionCard";
import Badge from "../common/Badge";

type RiskStatusCardProps = {
  guardianEnabled: boolean;
  riskLevel: string;
  halted: boolean;
};

export default function RiskStatusCard({
  guardianEnabled,
  riskLevel,
  halted,
}: RiskStatusCardProps) {
  return (
    <SectionCard
      title="Victor Hale Risk Manager"
      actions={
        <Badge
          variant={
            halted || riskLevel === "danger" || riskLevel === "emergency"
              ? "danger"
              : riskLevel === "warning"
                ? "warning"
                : "success"
          }
        >
          {riskLevel.toUpperCase()}
        </Badge>
      }
    >
      <div className="space-y-2 text-sm text-slate-300">
        <p>Guardian Enabled: {guardianEnabled ? "Yes" : "No"}</p>
        <p>Halt Active: {halted ? "Yes" : "No"}</p>
      </div>
    </SectionCard>
  );
}
