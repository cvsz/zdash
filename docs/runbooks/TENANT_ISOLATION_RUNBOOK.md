# Tenant Isolation Runbook

## Overview
zDash uses logical separation for multi-tenancy. Every request must be scoped to an `organization_id` and `workspace_id`.

## Auditing
1. Review tenant access logs in the event bus.
2. Ensure no cross-tenant queries exist in the database by checking repository patterns.

## Incident Response
If cross-tenant data leakage is suspected:
1. Immediately trigger a global halt.
2. Identify and patch the leaky query or endpoint.
3. Notify affected tenants.
