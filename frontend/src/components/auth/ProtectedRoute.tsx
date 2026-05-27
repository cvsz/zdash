import { Navigate, useLocation } from "react-router-dom";
import type { ReactNode } from "react";

import { useAuth } from "../../hooks/useAuth";

type ProtectedRouteProps = {
  children: ReactNode;
  allowRoles?: string[];
};

export default function ProtectedRoute({
  children,
  allowRoles,
}: ProtectedRouteProps) {
  const location = useLocation();
  const { loading, isAuthenticated, user } = useAuth();

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-300">
        Checking authentication...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (allowRoles && allowRoles.length > 0 && !allowRoles.includes(user?.role ?? "")) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
