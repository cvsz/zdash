# Realtime Gateway Runbook

## Channel Paths

| Channel    | WebSocket path                    |
|------------|-----------------------------------|
| events     | `/api/realtime/ws/events`         |
| risk       | `/api/realtime/ws/risk`           |
| scheduler  | `/api/realtime/ws/scheduler`      |
| content    | `/api/realtime/ws/content`        |

The generic `/api/realtime/ws/{channel}` endpoint validates against these 4 channels. Unknown channels are rejected with close code `4003` and reason `CHANNEL_NOT_ALLOWED`.

A compatibility endpoint `/api/realtime/ws/events` is preserved for clients using the legacy path.

## Local Dev WebSocket Setup

The realtime gateway runs as part of the backend process (uvicorn on port 8005). No additional server is needed.

```bash
make run-backend
```

The frontend connects via the configured `VITE_API_BASE_URL` (or `VITE_WS_BASE_URL` if set). The realtime client in `frontend/src/realtime/client.ts` derives the WebSocket URL from the API base URL:

- `http://localhost:8005` → `ws://localhost:8005`
- `https://zdash.zeaz.dev` → `wss://zdash.zeaz.dev`

## Test Isolation Rules

- Frontend tests must not depend on a running backend.
- `frontend/.env.test` sets `VITE_ENABLE_MOCK_FALLBACK=true` and `VITE_REALTIME_ENABLED=false`.
- The `RealtimeClientManager` respects `VITE_REALTIME_ENABLED` — when `false`, no WebSocket is opened and state returns `connected=false`, `connecting=false`, `retryInMs=null`.
- Run isolated frontend tests:

```bash
make test-frontend-isolated
```

## Common 403 Causes

| Cause | What to check |
|---|---|
| Unknown channel | Use only `events`, `risk`, `scheduler`, `content` |
| Feature entitlement | `VITE_REALTIME_ENABLED=true` and backend billing check may block |
| Quota exceeded | Check `realtime_connections` quota for the tenant |
| Auth required | If `AUTH_ENABLED=true`, WebSocket may need bearer token subprotocol |

## Disabling Realtime Locally

```bash
VITE_REALTIME_ENABLED=false npm run dev
```

Or set in `frontend/.env`:

```
VITE_REALTIME_ENABLED=false
```

## Server Management

```bash
make server-stop     # Stop local backend
make server-start    # Start local backend
make server-status   # Check backend health
```
