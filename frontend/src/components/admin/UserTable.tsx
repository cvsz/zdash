import { FormEvent, useState } from "react";

import type { AdminUser } from "../../api/types";

type CreateUserInput = {
  email: string;
  password: string;
  role: string;
  display_name: string;
};

type UserTableProps = {
  currentUsername: string;
  users: AdminUser[];
  loading?: boolean;
  error?: string | null;
  onCreateUser: (payload: CreateUserInput) => Promise<void>;
  onSetActive: (user: AdminUser, isActive: boolean) => Promise<void>;
};

export default function UserTable({
  currentUsername,
  users,
  loading = false,
  error,
  onCreateUser,
  onSetActive,
}: UserTableProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("viewer");
  const [displayName, setDisplayName] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleCreateUser = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitError(null);

    try {
      await onCreateUser({
        email,
        password,
        role,
        display_name: displayName,
      });
      setEmail("");
      setPassword("");
      setRole("viewer");
      setDisplayName("");
    } catch (caught) {
      setSubmitError(caught instanceof Error ? caught.message : "Failed to create user");
    }
  };

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
      <h3 className="text-sm font-semibold text-white">Users</h3>
      <p className="mt-1 text-xs text-slate-400">Current user: {currentUsername}</p>

      <form className="mt-3 grid gap-2 md:grid-cols-5" onSubmit={handleCreateUser}>
        <input
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Email"
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
          required
        />
        <input
          value={password}
          type="password"
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Password"
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
          required
        />
        <input
          value={displayName}
          onChange={(event) => setDisplayName(event.target.value)}
          placeholder="Display name"
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
        />
        <select
          value={role}
          onChange={(event) => setRole(event.target.value)}
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
        >
          <option value="viewer">viewer</option>
          <option value="analyst">analyst</option>
          <option value="operator">operator</option>
          <option value="admin">admin</option>
        </select>
        <button
          type="submit"
          className="rounded-md bg-cyan-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-cyan-500"
        >
          Create User
        </button>
      </form>

      {(error || submitError) && (
        <p className="mt-3 rounded-md border border-rose-400/30 bg-rose-500/10 p-2 text-xs text-rose-100">
          {error ?? submitError}
        </p>
      )}

      <div className="mt-3 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800 text-sm">
          <thead className="bg-slate-950/50 text-left text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-3 py-2">Email</th>
              <th className="px-3 py-2">Display Name</th>
              <th className="px-3 py-2">Role</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {loading && (
              <tr>
                <td className="px-3 py-3 text-slate-400" colSpan={5}>
                  Loading users...
                </td>
              </tr>
            )}
            {!loading && users.length === 0 && (
              <tr>
                <td className="px-3 py-3 text-slate-400" colSpan={5}>
                  No users found.
                </td>
              </tr>
            )}
            {!loading &&
              users.map((user) => {
                const canDeactivateCurrentAdmin = !(
                  user.email === currentUsername && user.role === "admin"
                );
                return (
                  <tr key={user.id}>
                    <td className="px-3 py-2 text-slate-200">{user.email}</td>
                    <td className="px-3 py-2 text-slate-300">
                      {user.display_name || "-"}
                    </td>
                    <td className="px-3 py-2 text-slate-300">{user.role}</td>
                    <td className="px-3 py-2 text-slate-300">
                      {user.is_active ? "active" : "inactive"}
                    </td>
                    <td className="px-3 py-2">
                      {user.is_active ? (
                        <button
                          type="button"
                          disabled={!canDeactivateCurrentAdmin}
                          onClick={() => {
                            void onSetActive(user, false);
                          }}
                          className="rounded-md border border-rose-700 px-3 py-1 text-xs text-rose-200 transition hover:bg-rose-800/30 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          Deactivate
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => {
                            void onSetActive(user, true);
                          }}
                          className="rounded-md border border-emerald-700 px-3 py-1 text-xs text-emerald-200 transition hover:bg-emerald-800/30"
                        >
                          Activate
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
