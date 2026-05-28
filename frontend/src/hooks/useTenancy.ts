import { useState, useEffect } from "react";
import { listOrganizations, listWorkspaces } from "../api/endpoints";
import { setTenant, setWorkspace } from "../api/client";
import type { Organization, Workspace } from "../api/types";

export function useTenancy() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeOrg, setActiveOrg] = useState<Organization | null>(null);
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const fetchOrgs = async () => {
      try {
        const orgs = await listOrganizations();
        if (mounted) {
          setOrganizations(orgs);
          if (orgs.length > 0) {
            const org = orgs[0];
            setActiveOrg(org);
            setTenant(org.id);
            const wss = await listWorkspaces(org.id);
            if (mounted) {
              setWorkspaces(wss);
              if (wss.length > 0) {
                setActiveWorkspace(wss[0]);
                setWorkspace(wss[0].id);
              }
            }
          }
        }
      } catch (err) {
        console.error("Failed to load tenancy:", err);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchOrgs();
    return () => {
      mounted = false;
    };
  }, []);

  const switchOrganization = async (orgId: string) => {
    const org = organizations.find((o) => o.id === orgId);
    if (org) {
      setActiveOrg(org);
      setTenant(org.id);
      const wss = await listWorkspaces(org.id);
      setWorkspaces(wss);
      if (wss.length > 0) {
        setActiveWorkspace(wss[0]);
        setWorkspace(wss[0].id);
      } else {
        setActiveWorkspace(null);
        setWorkspace(undefined);
      }
    }
  };

  const switchWorkspace = (wsId: string) => {
    const ws = workspaces.find((w) => w.id === wsId);
    if (ws) {
      setActiveWorkspace(ws);
      setWorkspace(ws.id);
    }
  };

  return {
    organizations,
    workspaces,
    activeOrg,
    activeWorkspace,
    switchOrganization,
    switchWorkspace,
    loading,
  };
}
