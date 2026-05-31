# Start Server

## Local Development

```bash
make server-start        # Start backend + frontend in background
make server-status       # Check running status
make server-logs         # Follow both logs
make server-logs SERVICE=backend   # Backend only
make server-logs SERVICE=frontend  # Frontend only
make server-stop         # Stop both servers
make server-restart      # Restart both
make server-open         # Print URLs
```

### Manual (foreground)

```bash
make run-backend    # uvicorn dev server on :8005 with reload
make run-frontend   # Vite dev server on :5173
```

### Default URLs

| Service  | URL                                |
|----------|------------------------------------|
| Backend  | http://localhost:8005              |
| API Docs | http://localhost:8005/docs         |
| Health   | http://localhost:8005/health       |
| Frontend | http://localhost:5173              |

### Logs

Runtime artifacts are stored under `.runtime/`:

```
.runtime/
├── logs/
│   ├── backend.log
│   └── frontend.log
└── pids/
    ├── backend.pid
    └── frontend.pid
```

## Production

```bash
sudo ./install-zdash-prod.sh         # First-time install
make prod-health                     # Health check
make prod-logs SERVICE=backend       # Follow backend logs
make prod-status                     # Systemd + docker compose status
make prod-backup                     # Backup
make prod-update                     # Update
```

Production runs via systemd + Docker Compose under `/opt/zdash/`.
