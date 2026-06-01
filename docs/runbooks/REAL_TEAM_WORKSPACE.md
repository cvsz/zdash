# Real Team Workspace Runbook

## Overview

Phase 47 adds a full-featured team workspace with role-based access control, invitation management, workspace-level permissions, and agent assignment. The feature supports 6 roles, 4 workspace access levels, and 4 agent assignment roles, all audit-logged and safety-gated.

## Architecture

- **Backend**: FastAPI routes at `/api/team/*`, service layer in `app/team/service.py` (713 lines), repositories in `app/team/repositories.py` (274 lines), schemas in `app/team/schemas.py` (92 lines)
- **Database**: 4 tables — `team_members`, `team_invitations`, `team_workspace_access`, `team_agent_assignments` (models in `app/team/models.py`)
- **Frontend**: `/team` page (`TeamRoster.tsx`, 504 lines) with 6 tabs (Overview, Members, Invitations, Workspace Access, Agent Assignments, Activity)
- **Hook**: `useTeam()` in `frontend/src/hooks/useTeam.ts` — fetches all team data, provides mutation wrappers with auto-refetch
- **Auth**: RBAC via `Permission.team_read`, `Permission.team_manage`, `Permission.team_invite`, `Permission.team_remove`, `Permission.team_assign_agents`

## Role Model

| Role | Description |
|------|-------------|
| owner | Full control, including billing and team management |
| admin | Manage team members, roles, workspace access |
| operator | Daily operations, run agents, monitor activity |
| analyst | Read-only access to team data and analytics |
| developer | Technical operations, agent assignments |
| viewer | Read-only access |

## Invitation Flow

1. Admin sends invitation via `POST /api/team/invitations`
2. System creates invitation record with `token_hash` (SHA-256)
3. Invitation expires after 7 days
4. Admin can resend or revoke pending invitations via `POST .../resend` and `POST .../revoke`
5. Invited member must have separate account to accept

## Workspace Access Model

| Level | Permissions |
|-------|-------------|
| owner | Full workspace control, manage access |
| manage | Modify workspace settings |
| write | Add/edit workspace content |
| read | View workspace content |

## Agent Assignment Model

| Role | Description |
|------|-------------|
| owner | Full control over agent behavior |
| reviewer | Review agent outputs before execution |
| runner | Execute agent actions |
| observer | Read-only agent monitoring |

## API Reference

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/team/members` | team_read | List members (optional `workspace_id`) |
| GET | `/api/team/members/{member_id}` | team_read | Get a single member |
| POST | `/api/team/invitations` | team_invite | Invite a new member |
| GET | `/api/team/invitations` | team_read | List invitations (optional `workspace_id`) |
| POST | `/api/team/invitations/{id}/resend` | team_invite | Resend invitation, reset expiry |
| POST | `/api/team/invitations/{id}/revoke` | team_invite | Revoke a pending invitation |
| PATCH | `/api/team/members/{member_id}/role` | team_manage | Update member role |
| POST | `/api/team/members/{member_id}/suspend` | team_manage | Suspend a member |
| POST | `/api/team/members/{member_id}/reactivate` | team_manage | Reactivate a suspended member |
| DELETE | `/api/team/members/{member_id}` | team_remove | Remove a member |
| GET | `/api/team/workspace-access` | team_manage | List workspace access entries |
| POST | `/api/team/workspace-access` | team_manage | Grant or update workspace access |
| DELETE | `/api/team/workspace-access/{access_id}` | team_manage | Revoke workspace access |
| GET | `/api/team/agent-assignments` | team_read | List agent assignments (optional `workspace_id`) |
| POST | `/api/team/agent-assignments` | team_assign_agents | Assign agent to member |
| DELETE | `/api/team/agent-assignments/{assignment_id}` | team_assign_agents | Unassign agent |
| GET | `/api/team/activity` | team_read | Get filtered activity log (`limit`) |
| GET | `/api/team/summary` | team_read | Get team summary counts |

## Audit / Safety Model

- All mutations are audit-logged via `AuditService` with action prefix `team.*`
- Last owner cannot be removed or downgraded (enforced in `update_member_role` and `remove_member`)
- Owner cannot suspend or remove self (enforced in `suspend_member` and `remove_member`)
- Invitation tokens are SHA-256 hashed before storage
- Secrets redacted in audit logs (standard metadata filtering)

## Local Development

- Uses SQLite by default
- `auth_enabled=false` mode provides dev-user
- No external dependencies required

## Validation

Backend services (if tests exist):
```bash
cd backend && python -m pytest app/tests/test_team_service.py
cd backend && python -m pytest app/tests/test_team_api.py
```

Frontend tests:
```bash
cd frontend && npm test -- src/tests/TeamRoster.test.tsx
cd frontend && npm test
```
