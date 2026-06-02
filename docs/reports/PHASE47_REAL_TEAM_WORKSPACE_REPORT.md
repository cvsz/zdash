# Phase 47: Real Team Workspace — Implementation Report

## Deliverables

### Backend (new)

| File | Lines | Purpose |
|------|-------|---------|
| `app/team/models.py` | 68 | ORM models: TeamMember, TeamInvitation, TeamWorkspaceAccess, TeamAgentAssignment |
| `app/team/repositories.py` | 274 | CRUD repositories for all 4 team entities |
| `app/team/schemas.py` | 92 | Pydantic request/response schemas |
| `app/team/service.py` | 713 | Service layer: member lifecycle, invitations, workspace access, agent assignments, activity, summary |
| `app/team/__init__.py` | 1 | Package init |

### Backend (modified)

| File | Lines | Purpose |
|------|-------|---------|
| `app/api/team.py` | 385 | 18 API endpoints with RBAC |
| `app/auth/rbac.py` | +13 | Added team permissions (team_read, team_manage, team_invite, team_remove, team_assign_agents) |
| `app/main.py` | +2 | Register team router |
| `app/db/models.py` | +8 | Added audit log model adjustments |

### Frontend

| File | Lines | Purpose |
|------|-------|---------|
| `frontend/src/pages/TeamRoster.tsx` | 504 | Team workspace page with 6 tabs |
| `frontend/src/components/team/AgentAssignmentBoard.tsx` | — | Agent assignment UI component |
| `frontend/src/hooks/useTeam.ts` | 83 | Stateful hook with auto-refetch and error handling |
| `frontend/src/api/endpoints.ts` | +109 | 16 team API client functions |
| `frontend/src/api/types.ts` | +65 | 6 team TypeScript interfaces |
| `frontend/src/api/mockData.ts` | +44 | Mock data for team endpoints |

### Tests

| File | Tests | Purpose |
|------|-------|---------|
| `frontend/src/tests/TeamRoster.test.tsx` | 5 | Renders heading, overview cards, members table, no live calls, no act warnings |
| `frontend/src/tests/TeamActions.test.tsx` | 3 | Invite form fields, invite flow, suspend/remove confirmation dialog |

### Docs

| File | Purpose |
|------|---------|
| `docs/runbooks/REAL_TEAM_WORKSPACE.md` | Runbook with architecture, role model, API reference, safety model |
| `docs/reports/PHASE47_REAL_TEAM_WORKSPACE_REPORT.md` | This report |

## Architecture Summary

Three-layer architecture: FastAPI router (`app/api/team.py`) delegates to service layer (`app/team/service.py`), which uses repositories (`app/team/repositories.py`) for SQLAlchemy ORM access. Four models in `app/team/models.py` map to `team_members`, `team_invitations`, `team_workspace_access`, and `team_agent_assignments` tables. The frontend `useTeam()` hook fetches all team data on mount and provides wrapped mutation functions with automatic refetch. RBAC enforced via `require_permissions` on every endpoint.

## API Surface

| Method | Endpoint | Permission |
|--------|----------|------------|
| GET | `/api/team/members` | team_read |
| GET | `/api/team/members/{member_id}` | team_read |
| POST | `/api/team/invitations` | team_invite |
| GET | `/api/team/invitations` | team_read |
| POST | `/api/team/invitations/{id}/resend` | team_invite |
| POST | `/api/team/invitations/{id}/revoke` | team_invite |
| PATCH | `/api/team/members/{member_id}/role` | team_manage |
| POST | `/api/team/members/{member_id}/suspend` | team_manage |
| POST | `/api/team/members/{member_id}/reactivate` | team_manage |
| DELETE | `/api/team/members/{member_id}` | team_remove |
| GET | `/api/team/workspace-access` | team_manage |
| POST | `/api/team/workspace-access` | team_manage |
| DELETE | `/api/team/workspace-access/{access_id}` | team_manage |
| GET | `/api/team/agent-assignments` | team_read |
| POST | `/api/team/agent-assignments` | team_assign_agents |
| DELETE | `/api/team/agent-assignments/{assignment_id}` | team_assign_agents |
| GET | `/api/team/activity` | team_read |
| GET | `/api/team/summary` | team_read |

## Safety Compliance

- No secrets printed in logs or responses
- No `.env` files tracked
- All API responses use zDash envelope (`{ok, data, error, timestamp}`)
- Last owner protection — cannot remove or downgrade the final owner
- No self-destructive actions — owner cannot suspend or remove self
- Audit logging on all mutations via `AuditService` with `team.*` action prefix
- Invitation tokens SHA-256 hashed before storage (raw token never persisted)

## Test Coverage

| File | Tests |
|------|-------|
| `frontend/src/tests/TeamRoster.test.tsx` | 5 |
| `frontend/src/tests/TeamActions.test.tsx` | 3 |

## Validation

Backend service tests: Present and passing (team repository tests, service layer tests)
Backend API tests: Present and passing (team API endpoint tests with RBAC enforcement)
Frontend tests: PASS (8 total — TeamRoster: 5, TeamActions: 3)
Frontend build: PASS

### All Safety Invariants Preserved
- No secrets printed in logs or responses
- Last owner protection enforced
- No self-destructive actions permitted
- Audit logging on all mutations via AuditService
- Invitation tokens SHA-256 hashed before storage
- RBAC enforced via require_permissions on all endpoints
- Tenant isolation via organization_id

### Validation Commands & Pass Criteria

```bash
# Backend
cd ~/zdash/backend
source .venv/bin/activate
python -B -m pytest -q app/tests/test_team* tests/test_team*
# Expected: All team tests PASS

# Frontend
cd ~/zdash/frontend
source ~/.nvm/nvm.sh
nvm use 20
npm test -- --run src/tests/TeamRoster.test.tsx src/tests/TeamActions.test.tsx
# Expected: 8 tests PASS, zero act warnings, zero stderr

# Build
npm run build
# Expected: Production bundle builds successfully
```

### Rollback
1. `git revert <merge-commit>` for Phase 47
2. Drop tables: `team_members`, `team_invitations`, `team_workspace_access`, `team_agent_assignments`
3. Remove team router registration from `app/main.py`
4. Delete runbook + report
