import React, { useState } from "react";

interface Props {
  onTest: (id: string) => void;
}

export const NotificationChannelForm: React.FC<Props> = ({ onTest }) => {
  const [type, setType] = useState("slack");
  const [target, setTarget] = useState("");
  const [testing, setTesting] = useState(false);

  const handleTest = () => {
    setTesting(true);
    onTest("chan-1");
    setTimeout(() => setTesting(false), 2000);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex flex-col space-y-4">
      <div>
        <h3 className="text-lg font-medium text-white">Add Notification Channel</h3>
        <p className="text-sm text-slate-400">Configure where alerts should be sent.</p>
      </div>
      <div className="flex items-center space-x-2">
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-white rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
        >
          <option value="slack">Slack</option>
          <option value="email">Email</option>
          <option value="webhook">Webhook</option>
        </select>
        <input
          type="text"
          placeholder="Target (e.g. #alerts)"
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          className="flex-1 bg-slate-800 border border-slate-700 text-white rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
        />
        <button
          onClick={handleTest}
          className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
        >
          {testing ? "Testing..." : "Test Dry-Run"}
        </button>
        <button
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
        >
          Add Channel
        </button>
      </div>
    </div>
  );
};
