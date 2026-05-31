# Quick Start

## Prerequisites

- Git
- Python 3.11+
- Node.js 20 LTS (via nvm)
- Docker + Docker Compose (optional, for production)

## Clone and Install

```bash
git clone https://github.com/cvsz/zdash.git
cd zdash
make install-local
```

## Start the App

```bash
make server-start
```

## Check Status

```bash
make server-status
```

## View Logs

```bash
make server-logs
```

## Stop the App

```bash
make server-stop
```

## Access the App

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend health | http://localhost:8005/health |
| API docs | http://localhost:8005/docs |

## Run Validation

```bash
make validate-fast
```

## Production Install

```bash
sudo ./install-zdash-prod.sh
```

## Next Steps

- See `docs/runbooks/INSTALLATION.md` for detailed setup options
- See `docs/runbooks/OPERATIONS_INDEX.md` for all operations runbooks
- See `docs/runbooks/GO_LIVE_CHECKLIST.md` for production deployment
