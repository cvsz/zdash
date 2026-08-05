# Local Docker Stack

This workflow builds and starts the complete zDash stack without taking over host ports 80, 443, 8005, 5432, or 6379.

## Architecture

```text
Browser
  -> 127.0.0.1:18080
  -> zDash gateway (Nginx)
     -> frontend:80
     -> backend:8005
        -> postgres:5432
        -> redis:6379
```

Only the gateway is published to the host. The default bind address is loopback, so the stack is not exposed to the LAN or public Internet.

## Start and verify

```bash
bash scripts/local/stack.sh up
```

The command:

1. validates that the selected host port is available;
2. builds backend, frontend, and gateway images;
3. starts PostgreSQL and Redis;
4. waits for the backend and frontend health checks;
5. starts the gateway;
6. verifies `/gateway-health` and the backend `/health` endpoint through the gateway.

Open:

```text
http://127.0.0.1:18080
```

## Commands

```bash
bash scripts/local/stack.sh status
bash scripts/local/stack.sh logs
bash scripts/local/stack.sh logs backend
bash scripts/local/stack.sh restart
bash scripts/local/stack.sh down
```

Use a different loopback port when 18080 is occupied:

```bash
ZDASH_HTTP_PORT=18081 bash scripts/local/stack.sh up
```

To delete local containers and data volumes explicitly:

```bash
CONFIRM_RESET=yes bash scripts/local/stack.sh reset
```

## Existing production/runtime stack

The local stack uses the Compose project name `zdash-local`, so it does not reuse the containers or volumes created under `/opt/zdash/runtime`. It can coexist with an existing stack as long as `127.0.0.1:18080` is free.

To stop the generated runtime stack before local testing:

```bash
sudo docker compose \
  --env-file /opt/zdash/runtime/.env.production \
  -f /opt/zdash/runtime/docker-compose.yml \
  down --remove-orphans
```

This does not delete volumes unless `--volumes` is supplied.

## Host Caddy or Cloudflare Tunnel

Keep the local gateway bound to loopback and point the host proxy or tunnel origin to:

```text
http://127.0.0.1:18080
```

The gateway supports normal HTTP requests, backend API routes, health checks, and WebSocket upgrades through the same origin.
