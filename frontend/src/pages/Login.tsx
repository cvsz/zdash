import { Navigate, useLocation, useNavigate } from "react-router-dom";

import LoginForm from "../components/auth/LoginForm";
import { useAuth } from "../hooks/useAuth";

type LoginRouteState = {
  from?: string;
};

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, loading } = useAuth();

  if (!loading && isAuthenticated) {
    const from = (location.state as LoginRouteState | null)?.from ?? "/";
    return <Navigate to={from} replace />;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4 py-10">
      <LoginForm onAuthenticated={() => navigate("/", { replace: true })} />
    </div>
  );
}
