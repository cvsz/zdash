import React from "react";
import PageHeader from "../components/layout/PageHeader";
import { OrganizationTable } from "../components/tenancy/OrganizationTable";
import { WorkspaceTable } from "../components/tenancy/WorkspaceTable";
import { InviteUserForm } from "../components/tenancy/InviteUserForm";
import { useTenancy } from "../hooks/useTenancy";

export default function Organizations() {
  const { organizations, workspaces, loading } = useTenancy();

  return (
    <div className="flex flex-col space-y-6">
      <PageHeader 
        title="Organizations" 
        subtitle="Manage your enterprise organizations, workspaces, and team members." 
      />
      {loading ? (
        <div className="text-slate-400">Loading tenancy data...</div>
      ) : (
        <>
          <OrganizationTable organizations={organizations} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <div className="flex flex-col space-y-4">
              <h3 className="text-xl font-medium text-white">Workspaces</h3>
              <WorkspaceTable workspaces={workspaces} />
            </div>
            <div className="flex flex-col space-y-4">
              <InviteUserForm />
            </div>
          </div>
        </>
      )}
    </div>
  );
};
