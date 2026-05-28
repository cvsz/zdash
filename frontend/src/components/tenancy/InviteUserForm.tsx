import React, { useState } from "react";

export const InviteUserForm: React.FC = () => {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("member");
  const [invited, setInvited] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setInvited(true);
    setTimeout(() => {
      setInvited(false);
      setEmail("");
    }, 3000);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex flex-col space-y-4">
      <div>
        <h3 className="text-lg font-medium text-white">Invite User</h3>
        <p className="text-sm text-slate-400">Invite a new member to this organization.</p>
      </div>
      <div className="flex items-center space-x-2">
        <input
          type="email"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="flex-1 bg-slate-800 border border-slate-700 text-white rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
          required
        />
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-white rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
        >
          <option value="admin">Admin</option>
          <option value="member">Member</option>
          <option value="viewer">Viewer</option>
        </select>
        <button
          type="submit"
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
        >
          {invited ? "Invited!" : "Invite"}
        </button>
      </div>
    </form>
  );
};
