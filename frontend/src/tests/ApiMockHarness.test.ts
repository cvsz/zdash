import { describe, expect, it } from "vitest";
import {
  listContentItems,
  getQueueStatus,
  listOrganizations,
  listWorkspaces,
} from "../api/endpoints";

describe("ApiMockHarness", () => {
  it("listContentItems returns at least one item with required fields", async () => {
    const items = await listContentItems();
    expect(items.length).toBeGreaterThan(0);
    expect(items[0].id).toBeDefined();
    expect(items[0].title).toBeDefined();
  });

  it("getQueueStatus returns at least one queue with required fields", async () => {
    const queues = await getQueueStatus();
    expect(queues.length).toBeGreaterThan(0);
    expect(queues[0].queue_name).toBeDefined();
    expect(typeof queues[0].workers_active).toBe("number");
  });

  it("listOrganizations returns at least one org", async () => {
    const orgs = await listOrganizations();
    expect(orgs.length).toBeGreaterThan(0);
    expect(orgs[0].id).toBeDefined();
  });

  it("listWorkspaces returns at least one workspace", async () => {
    const workspaces = await listWorkspaces("org-1");
    expect(workspaces.length).toBeGreaterThan(0);
    expect(workspaces[0].id).toBeDefined();
  });
});
