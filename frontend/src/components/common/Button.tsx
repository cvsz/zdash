import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost" | "disabled";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: ButtonVariant;
};

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "border-cyan-500/40 bg-cyan-500/20 text-cyan-50 hover:bg-cyan-500/30",
  secondary:
    "border-slate-700 bg-slate-800 text-slate-100 hover:bg-slate-700/80",
  danger:
    "border-rose-500/40 bg-rose-500/25 text-rose-50 hover:bg-rose-500/35",
  ghost: "border-transparent bg-transparent text-slate-200 hover:bg-slate-800",
  disabled: "border-slate-800 bg-slate-900 text-slate-500",
};

export default function Button({
  children,
  variant = "secondary",
  className = "",
  disabled = false,
  type = "button",
  ...rest
}: ButtonProps) {
  const appliedVariant = disabled ? "disabled" : variant;

  return (
    <button
      type={type}
      disabled={disabled}
      className={`inline-flex items-center justify-center rounded-md border px-3 py-2 text-sm font-semibold transition ${variantStyles[appliedVariant]} ${
        disabled ? "cursor-not-allowed" : ""
      } ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
