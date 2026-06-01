import React from "react";
import PageHeader from "../components/layout/PageHeader";
import { useTenancy } from "../hooks/useTenancy";
import { useT } from "../hooks/useT";

export default function Workspace() {
  const { t } = useT();
  const { activeWorkspace, loading } = useTenancy();

  return (
    <div className="flex flex-col space-y-6">
      <PageHeader 
        title={t('workspace.title')} 
        subtitle={t('workspace.subtitle')} 
      />
      {loading ? (
        <div className="text-text-dim">{t('workspace.loading')}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-panel-solid border border-border p-6 rounded-card">
            <h3 className="text-lg font-medium text-text-primary mb-2">{t('workspace.current_workspace')}</h3>
            <p className="text-text-secondary">{t('workspace.name')}: <span className="font-semibold">{activeWorkspace?.name || t('common.not_found')}</span></p>
            <p className="text-text-secondary mt-2">
              {t('workspace.environment')}: 
              <span className={`ml-2 px-2 py-1 rounded text-xs uppercase font-medium ${activeWorkspace?.environment === 'production' ? 'bg-accent-violet/10 text-accent-violet' : 'bg-border/50 text-text-secondary'}`}>
                {activeWorkspace?.environment === 'production' ? t('workspace.production') : t('workspace.unknown')}
              </span>
            </p>
          </div>
          <div className="bg-panel-solid border border-border p-6 rounded-card">
            <h3 className="text-lg font-medium text-text-primary mb-2">{t('workspace.safety_state')}</h3>
            <p className="text-sm text-text-dim">{t('workspace.safety_state_desc')}</p>
            <div className="mt-4 px-3 py-2 bg-state-success/10 border border-state-success/20 text-state-success rounded-md text-sm font-medium w-fit">
              {t('workspace.risk_gates_active')}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
