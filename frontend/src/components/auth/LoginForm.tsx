import { FormEvent, useState } from "react";

import {
  DEFAULT_ADMIN_PASSWORD,
  DEFAULT_ADMIN_USERNAME,
  isDefaultAdminCredentials,
} from "../../api/auth";
import { useAuth } from "../../hooks/useAuth";

type LoginFormProps = {
  onAuthenticated?: () => void;
};

export default function LoginForm({ onAuthenticated }: LoginFormProps) {
  const { login, loading, mode } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const defaultCredentialWarning = isDefaultAdminCredentials(username, password);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    try {
      await login(username, password);
      onAuthenticated?.();
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : "Login failed";
      setError(message);
    }
  };

  return (
    <div className="mx-auto w-full max-w-md rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-lg">
      <h1 className="text-xl font-semibold text-white">Sign in to zDash</h1>
      <p className="mt-1 text-sm text-slate-400">
        Session tokens are stored locally and never exposed in the UI.
      </p>

      {mode === "dev" && (
        <div className="mt-4 rounded-md border border-emerald-400/30 bg-emerald-500/10 p-3 text-xs text-emerald-100">
          Authentication is disabled in backend dev mode. Dashboard access is available
          without credentials.
        </div>
      )}

      {defaultCredentialWarning && (
        <div className="mt-4 rounded-md border border-amber-400/30 bg-amber-500/10 p-3 text-xs text-amber-100">
          Default admin credentials detected ({DEFAULT_ADMIN_USERNAME} / {DEFAULT_ADMIN_PASSWORD}).
          Rotate credentials before production use.
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-md border border-rose-400/30 bg-rose-500/10 p-3 text-xs text-rose-100">
          {error}
        </div>
      )}

      <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
        <label className="block text-sm text-slate-200" htmlFor="zdash-login-username">
          Username / Email
          <input
            id="zdash-login-username"
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none ring-cyan-500/30 transition focus:ring"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
          />
        </label>

        <label className="block text-sm text-slate-200" htmlFor="zdash-login-password">
          Password
          <input
            id="zdash-login-password"
            type="password"
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none ring-cyan-500/30 transition focus:ring"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-cyan-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-cyan-500 disabled:cursor-not-allowed disabled:bg-cyan-800"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </div>
  );
}
