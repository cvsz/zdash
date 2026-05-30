# Phase 36: Server Command Center + Secret-Safe Git Workflow

## Architecture

```
scripts/
├── server/
│   ├── start-local.sh    # Background backend + frontend
│   ├── stop-local.sh     # Stop by PID files only
│   ├── status-local.sh   # PID, port, health check
│   ├── logs-local.sh     # Follow logs (SERVICE=backend|frontend)
│   ├── open-local.sh     # Print or browser-open URLs
│   ├── start-prod.sh     # systemctl start zdash
│   ├── stop-prod.sh      # systemctl stop zdash
│   ├── status-prod.sh    # systemd + compose + health
│   └── logs-prod.sh      # Production log helper
└── git/
    ├── clean-local-artifacts.sh  # Remove .bak, logs, .runtime/tmp
    ├── safe-status.sh            # Status + risky file detection
    ├── safe-add.sh               # Stage with unsafe-path rejection
    ├── safe-commit.sh            # Commit with pre-commit safety scan
    └── safe-push.sh              # Validate, status, push
```

## Make Targets

| Target | Description |
|---|---|
| `server-start` | Start local backend + frontend in background |
| `server-stop` | Stop local servers by PID |
| `server-status` | Show PID, port, health status |
| `server-logs SERVICE=backend` | Follow logs |
| `server-open` | Print URLs |
| `server-restart` | Stop then start |
| `git-clean-local` | Remove local artifacts |
| `git-safe-status` | Status with risky file detection |
| `git-safe-add ARGS="..."` | Stage files safely |
| `git-safe-commit MESSAGE="..."` | Commit with safety scan |
| `git-safe-push` | Validate, status, push |
| `safe-commit` | Alias to git-safe-commit |
| `safe-push` | Alias to git-safe-push |

## Local vs Production

| Aspect | Local | Production |
|---|---|---|
| Start | `make server-start` | `make prod-start` |
| Stop | `make server-stop` | `make prod-stop` |
| Status | `make server-status` | `make prod-status` |
| Logs | `make server-logs` | `make prod-logs` |
| Runtime | `.runtime/` (gitignored) | `/opt/zdash/` (systemd) |
| Stack | Direct uvicorn + vite | Docker Compose via systemd |

## Safety Guarantees

- **No broad pkill** — stop reads PIDs from `.runtime/pids/` only
- **No duplicate servers** — start checks PID files before launching
- **Idempotent** — stop is safe to run when already stopped
- **Stale PID cleanup** — start cleans dead PID files
- **Unsafe path rejection** — `safe-add.sh` refuses `.env`, `*.bak`, etc.
- **Secret scan** — `safe-commit.sh` scans staged diff for secret patterns
- **Pre-push validation** — `safe-push.sh` runs `make validate-fast`
- **No secret values printed** — logs, status, and error messages never expose secrets
- **Production scripts fail safely** — clear error if `/opt/zdash/runtime` is absent
