import React, { useState } from "react";
import { useT } from '../../hooks/useT';

interface Props {
  onTest: (id: string) => void;
}

export const NotificationChannelForm: React.FC<Props> = ({ onTest }) => {
  const { t } = useT();
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
        <h3 className="text-lg font-medium text-white">{t('alerts.add_channel')}</h3>
        <p className="text-sm text-slate-400">{t('alerts.channel_form_config')}</p>
      </div>
      <div className="flex items-center space-x-2">
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-white rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
        >
          <option value="slack">{t('alerts.slack')}</option>
          <option value="email">{t('alerts.email')}</option>
          <option value="webhook">{t('alerts.webhook')}</option>
        </select>
        <input
          type="text"
          placeholder={t('alerts.channel_form_config')}
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          className="flex-1 bg-slate-800 border border-slate-700 text-white rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
        />
        <button
          onClick={handleTest}
          className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
        >
          {testing ? t('common.loading') : t('alerts.test_channel')}
        </button>
        <button
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
        >
          {t('alerts.add_channel')}
        </button>
      </div>
    </div>
  );
};
