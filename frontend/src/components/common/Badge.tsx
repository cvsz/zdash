import type { ReactNode } from "react";

export type BadgeVariant = "normal" | "warning" | "danger" | "success" | "muted";

type BadgeProps = {
  children: ReactNode;
  variant?: BadgeVariant;
  className?: string;
};

const variantStyles: Record<BadgeVariant, string> = {
  normal: "border-slate-700 bg-slate-800/70 text-slate-200",
  warning: "border-amber-400/40 bg-amber-500/15 text-amber-100",
  danger: "border-rose-500/40 bg-rose-500/20 text-rose-100",
  success: "border-emerald-500/40 bg-emerald-500/15 text-emerald-100",
  muted: "border-slate-800 bg-slate-900 text-slate-300",
};

export default function Badge({ children, variant = "normal", className = "" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-semibold ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
