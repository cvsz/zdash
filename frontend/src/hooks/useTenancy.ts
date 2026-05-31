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

        if (!mounted) return;

        const safeOrgs = Array.isArray(orgs) ? orgs : [];
        setOrganizations(safeOrgs);

        if (safeOrgs.length > 0) {
          const org = safeOrgs[0];
          setActiveOrg(org);
          setTenant(org.id);

          const loadedWorkspaces = await listWorkspaces(org.id);
          if (!mounted) return;

          const safeWorkspaces = Array.isArray(loadedWorkspaces)
            ? loadedWorkspaces
            : [];
          setWorkspaces(safeWorkspaces);

          if (safeWorkspaces.length > 0) {
            setActiveWorkspace(safeWorkspaces[0]);
            setWorkspace(safeWorkspaces[0].id);
          } else {
            setActiveWorkspace(null);
            setWorkspace(undefined);
          }
        }
      } catch (err) {
        console.error("Failed to load tenancy:", err);
        if (mounted) {
          setOrganizations([]);
          setWorkspaces([]);
          setActiveOrg(null);
          setActiveWorkspace(null);
        }
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
    if (!org) return;

    setActiveOrg(org);
    setTenant(org.id);

    const loadedWorkspaces = await listWorkspaces(org.id);
    const safeWorkspaces = Array.isArray(loadedWorkspaces)
      ? loadedWorkspaces
      : [];

    setWorkspaces(safeWorkspaces);

    if (safeWorkspaces.length > 0) {
      setActiveWorkspace(safeWorkspaces[0]);
      setWorkspace(safeWorkspaces[0].id);
    } else {
      setActiveWorkspace(null);
      setWorkspace(undefined);
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
