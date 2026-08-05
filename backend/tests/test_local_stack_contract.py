from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_local_compose_uses_one_loopback_entrypoint() -> None:
    compose = read("docker-compose.yml")

    assert "name: ${COMPOSE_PROJECT_NAME:-zdash-local}" in compose
    assert compose.count("ports:") == 1
    assert '${ZDASH_BIND_ADDRESS:-127.0.0.1}:${ZDASH_HTTP_PORT:-18080}:80' in compose
    assert '"80:80"' not in compose
    assert '"443:443"' not in compose
    assert '"8005:8005"' not in compose
    assert '"5432:5432"' not in compose
    assert '"6379:6379"' not in compose


def test_local_backend_uses_postgres_and_health_gated_dependencies() -> None:
    compose = read("docker-compose.yml")

    assert "DATABASE_URL: postgresql+psycopg://" in compose
    assert "postgres:5432" in compose
    assert "condition: service_healthy" in compose
    assert "gateway:" in compose
    assert "backend_data:/app/backend/data" in compose


def test_gateway_proxies_application_health_instead_of_masking_it() -> None:
    gateway = read("infra/nginx/zdash.conf")
    gateway_image = read("infra/docker/nginx.Dockerfile")

    assert "location = /gateway-health" in gateway
    assert "location = /health" in gateway
    assert "proxy_pass http://backend_upstream;" in gateway
    assert "http://localhost/gateway-health" in gateway_image


def test_frontend_container_supports_same_origin_and_spa_routes() -> None:
    dockerfile = read("infra/docker/frontend.Dockerfile")
    frontend_nginx = read("infra/nginx/frontend.conf")
    realtime = read("frontend/src/hooks/useRealtimeEvents.ts")

    assert "ARG VITE_API_BASE_URL=/" in dockerfile
    assert "COPY infra/nginx/frontend.conf" in dockerfile
    assert "try_files $uri $uri/ /index.html;" in frontend_nginx
    assert "window.location.protocol" in realtime
    assert "window.location.host" in realtime
    assert '"ws://localhost:8005"' not in realtime
