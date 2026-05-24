# RBAC Matrix

## Roles
- `admin`
- `operator`
- `analyst`
- `viewer`

## Endpoint Access

| Area | Endpoint | admin | operator | analyst | viewer |
|---|---|---:|---:|---:|---:|
| Auth | `POST /api/auth/login` | ✅ | ✅ | ✅ | ✅ |
| Agents | `GET /api/agents` | ✅ | ✅ | ✅ | ✅ |
| Agents | `POST /api/agents/message` | ✅ | ✅ | ✅ | ❌ |
| Trading | `GET /api/trading/status` | ✅ | ✅ | ✅ | ✅ |
| Trading | `POST /api/trading/scan` | ✅ | ✅ | ✅ | ✅ |
| Trading | `POST /api/trading/dry-run` | ✅ | ✅ | ✅ | ❌ |
| Trading | `POST /api/trading/live-mode/confirm` | ✅ | ❌ | ❌ | ❌ |
| Trading | `POST /api/trading/live-execute` | ✅ | ✅ | ❌ | ❌ |
| Risk | `POST /api/risk/halt` | ✅ | ✅ | ❌ | ❌ |
| Risk | `POST /api/risk/emergency-halt` | ✅ | ❌ | ❌ | ❌ |
| Risk | `POST /api/risk/resume` | ✅ | ❌ | ❌ | ❌ |
| Risk | `POST /api/risk/kill-switch-reset` | ✅ | ❌ | ❌ | ❌ |
| Scheduler | `POST /api/scheduler/jobs*` | ✅ | ✅ | ❌ | ❌ |
| Scheduler | `POST /api/scheduler/iot/power-cycle` | ✅ | ✅ | ❌ | ❌ |
| Content | `POST /api/content/approve` | ✅ | ✅ | ❌ | ❌ |
| Content | `POST /api/content/post` | ✅ | ✅ | ❌ | ❌ |
| Audit | `GET /api/audit` | ✅ | ✅ | ❌ | ❌ |

## Notes
- Viewer role is read-only.
- Mutating endpoints are blocked for `viewer`.
- Dangerous actions always emit audit logs.
