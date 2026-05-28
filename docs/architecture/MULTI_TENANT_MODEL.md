# Multi-Tenant Model

zDash uses logical separation for multi-tenancy.

- **Organization**: The top-level billing and administrative entity.
- **Workspace**: A sub-environment within an organization.

All models and queries must include `organization_id` and `workspace_id`.
Endpoints extract this context from route parameters, headers, or user defaults.
