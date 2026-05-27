import type { ReactNode } from "react";

type SectionCardProps = {
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
};

export default function SectionCard({
  title,
  subtitle,
  actions,
  children,
  footer,
  className = "",
}: SectionCardProps) {
  return (
    <section
      className={`rounded-lg border border-slate-800 bg-slate-900/70 p-4 shadow-lg shadow-slate-950/20 ${className}`}
    >
      {(title || subtitle || actions) && (
        <header className="mb-3 flex items-start justify-between gap-3">
          <div>
            {title ? <h3 className="text-sm font-semibold text-slate-100">{title}</h3> : null}
            {subtitle ? <p className="mt-1 text-xs text-slate-400">{subtitle}</p> : null}
          </div>
          {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
        </header>
      )}

      <div>{children}</div>

      {footer ? <footer className="mt-3 border-t border-slate-800 pt-3">{footer}</footer> : null}
    </section>
  );
}
