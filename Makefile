SHELL := /usr/bin/env bash
.SHELLFLAGS := -Eeuo pipefail -c
.DEFAULT_GOAL := help

ROOT_DIR := $(CURDIR)
BACKEND_DIR := backend
FRONTEND_DIR := frontend
NODE_VERSION ?= 20
BACKEND_HOST ?= 0.0.0.0
BACKEND_PORT ?= 8005
FRONTEND_HOST ?= 0.0.0.0
FRONTEND_PORT ?= 5173
PYTHON ?= python3
NPM_INSTALL_FLAGS ?= --legacy-peer-deps --no-audit --fund=false

BACKEND_ACTIVATE := source $(BACKEND_DIR)/.venv/bin/activate
NVM_LOAD := source $$HOME/.nvm/nvm.sh >/dev/null 2>&1 || true; nvm use $(NODE_VERSION) >/dev/null 2>&1 || true
FORBIDDEN_TRACKED_PATTERN := (^\.env$$|^gpg-loopback\.sh$$|^\.agent/|^\.agents/|^\.gemini/|^\.claude/|^\.mcp/|^docs/prompt/codex-runs/|^skill\.sh$$|^scripts/skill\.sh$$)

.PHONY: help
help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"; printf "\nzDash Master Makefile\n\nUsage:\n  make <target>\n\nTargets:\n"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  %-30s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\nCommon flows:\n  make validate-fast\n  make validate\n  make phase10-final\n  make run-backend\n  make run-frontend\n\n"

.PHONY: info
info: ## Print local project/runtime info
	@echo "Repo: cvsz/zdash"
	@echo "Root: $(ROOT_DIR)"
	@echo "Backend: http://localhost:$(BACKEND_PORT)"
	@echo "Frontend: http://localhost:$(FRONTEND_PORT)"
	@git branch --show-current 2>/dev/null || true
	@git rev-parse --short HEAD 2>/dev/null || true
	@$(PYTHON) --version || true
	@node --version || true
	@npm --version || true

.PHONY: pull
pull: ## Pull latest main with rebase
	git pull --rebase

.PHONY: status
status: ## Show normal git status
	git status --short

.PHONY: ignored
ignored: ## Show ignored files summary
	git status --ignored --short | head -160

.PHONY: tracked-forbidden
tracked-forbidden: ## Fail if local-only/secret/tooling files are tracked
	@echo "Checking forbidden tracked files..."
	@if git ls-files | grep -E '$(FORBIDDEN_TRACKED_PATTERN)'; then \
		echo "FAILED: forbidden tracked files found" >&2; \
		exit 1; \
	else \
		echo "PASSED: no forbidden tracked files"; \
	fi

.PHONY: env-check
env-check: ## Validate .env key syntax without printing values
	@$(PYTHON) - <<'PY'
from pathlib import Path
import re
for name in [".env", ".env.production", ".env.production.example", "frontend/.env", "frontend/.env.local"]:
    path = Path(name)
    if not path.exists():
        continue
    ok = True
    for n, raw in enumerate(path.read_text(errors="ignore").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            print(f"{name}:{n}: missing '='")
            ok = False
            continue
        key = line.split("=", 1)[0]
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            print(f"{name}:{n}: invalid key {key!r}")
            ok = False
    if ok:
        print(f"PASSED: {name}")
    else:
        raise SystemExit(1)
PY

.PHONY: port-scan
port-scan: ## Fail if tracked runtime/source files still reference backend port 8000
	@echo "Scanning tracked runtime/source files for old backend port 8000..."
	@tmp=$$(mktemp); \
	git grep -nE 'localhost:8000|BACKEND_PORT=8000' -- . \
		':(exclude)docs/prompt/*.prompt' \
		':(exclude)docs/prompt/codex-runs/**' \
		':(exclude).codex/**' \
		':(exclude).agent/**' \
		':(exclude).agents/**' \
		':(exclude)**/*.md' > $$tmp 2>/dev/null || true; \
	if [ -s $$tmp ]; then \
		cat $$tmp; \
		rm -f $$tmp; \
		echo "FAILED: old backend port 8000 found" >&2; \
		exit 1; \
	else \
		rm -f $$tmp; \
		echo "PASSED: no old backend port 8000 found"; \
	fi

.PHONY: secret-scan
secret-scan: ## Scan tracked files for common secret patterns without reading ignored caches
	@echo "Scanning tracked files for common secret patterns..."
	@tmp=$$(mktemp); \
	git grep -nE 'GPG_PASSPHRASE|sk-[A-Za-z0-9_-]{20,}|api[_-]?key=|password=|private key|BEGIN RSA|BEGIN OPENSSH|STRIPE_SECRET|CLOUDFLARE_API_TOKEN|TUNNEL_TOKEN|ZONE_ID=|ACCOUNT_ID=' -- . \
		':(exclude)docs/prompt/*.prompt' \
		':(exclude)docs/prompt/codex-runs/**' \
		':(exclude).codex/reports/**' \
		':(exclude).codex/runs/**' \
		':(exclude).agent/**' \
		':(exclude).agents/**' > $$tmp 2>/dev/null || true; \
	if [ -s $$tmp ]; then \
		cat $$tmp; \
		rm -f $$tmp; \
		echo "FAILED: possible secret pattern in tracked files" >&2; \
		exit 1; \
	else \
		rm -f $$tmp; \
		echo "PASSED: no common tracked secret patterns"; \
	fi

.PHONY: safety-scan
safety-scan: tracked-forbidden env-check port-scan secret-scan ## Run local safety scans

.PHONY: backend-venv
backend-venv: ## Create backend virtualenv if missing
	@test -d $(BACKEND_DIR)/.venv || $(PYTHON) -m venv $(BACKEND_DIR)/.venv
	@$(BACKEND_ACTIVATE); python -m pip install --upgrade pip setuptools wheel

.PHONY: backend-install
backend-install: backend-venv ## Install backend package and dev tools
	@$(BACKEND_ACTIVATE); cd $(BACKEND_DIR); python -m pip install -e '.[dev]'
	@$(BACKEND_ACTIVATE); cd $(BACKEND_DIR); python -m pip install 'ruff>=0.5.0' 'pytest>=8.1.1'

.PHONY: backend-lint
backend-lint: ## Run backend ruff lint
	@$(BACKEND_ACTIVATE); cd $(BACKEND_DIR); python -m ruff check app tests

.PHONY: backend-lint-fix
backend-lint-fix: ## Run backend ruff auto-fix
	@$(BACKEND_ACTIVATE); cd $(BACKEND_DIR); python -m ruff check app tests --fix

.PHONY: backend-test
backend-test: ## Run backend pytest
	@$(BACKEND_ACTIVATE); cd $(BACKEND_DIR); python -B -m pytest -q

.PHONY: backend-check
backend-check: backend-lint backend-test ## Run backend lint + tests

.PHONY: backend-deps
backend-deps: ## Run Codex backend dependency repair helper
	bash .codex/cloud/repair-backend-deps.sh

.PHONY: frontend-install
frontend-install: ## Install frontend dependencies using Node 20 when nvm is available
	@$(NVM_LOAD); cd $(FRONTEND_DIR); npm install $(NPM_INSTALL_FLAGS)

.PHONY: frontend-test
frontend-test: ## Run frontend tests
	@$(NVM_LOAD); cd $(FRONTEND_DIR); npm test

.PHONY: frontend-build
frontend-build: ## Build frontend production bundle
	@$(NVM_LOAD); cd $(FRONTEND_DIR); npm run build

.PHONY: frontend-check
frontend-check: frontend-test frontend-build ## Run frontend tests + build

.PHONY: docker-build-backend
docker-build-backend: ## Build backend Docker image
	docker build -f infra/docker/backend.Dockerfile .

.PHONY: docker-build-frontend
docker-build-frontend: ## Build frontend Docker image
	docker build -f infra/docker/frontend.Dockerfile .

.PHONY: docker-build-nginx
docker-build-nginx: ## Build nginx Docker image
	docker build -f infra/docker/nginx.Dockerfile .

.PHONY: docker-build
docker-build: docker-build-backend docker-build-frontend docker-build-nginx ## Build all Docker images

.PHONY: compose-config
compose-config: ## Validate default docker compose config
	docker compose config

.PHONY: compose-prod-config
compose-prod-config: ## Validate production docker compose config
	docker compose -f docker-compose.prod.yml config

.PHONY: compose-check
compose-check: compose-config compose-prod-config ## Validate all compose configs

.PHONY: compose-up
compose-up: ## Start local compose stack
	docker compose up --build

.PHONY: compose-up-detached
compose-up-detached: ## Start local compose stack detached
	docker compose up --build -d

.PHONY: compose-prod-up
compose-prod-up: ## Start production compose stack detached
	docker compose -f docker-compose.prod.yml up --build -d

.PHONY: compose-down
compose-down: ## Stop local compose stack
	docker compose down

.PHONY: compose-prod-down
compose-prod-down: ## Stop production compose stack
	docker compose -f docker-compose.prod.yml down

.PHONY: compose-ps
compose-ps: ## Show compose services
	docker compose ps

.PHONY: compose-logs
compose-logs: ## Tail compose logs
	docker compose logs -f --tail=200

.PHONY: maintenance
maintenance: ## Run Codex Cloud maintenance validation
	bash .codex/cloud/maintenance.sh

.PHONY: validate-fast
validate-fast: safety-scan backend-check frontend-check ## Run safety scans + backend/frontend validation

.PHONY: validate
validate: validate-fast docker-build compose-check maintenance ## Run full validation including Docker and maintenance

.PHONY: phase10-final
phase10-final: validate ## Final Phase 10 validation alias

.PHONY: ci-local
ci-local: validate ## Local CI alias

.PHONY: run-backend
run-backend: ## Run backend dev server on port 8005
	@$(BACKEND_ACTIVATE); cd $(BACKEND_DIR); uvicorn app.main:app --host $(BACKEND_HOST) --port $(BACKEND_PORT) --reload

.PHONY: run-frontend
run-frontend: ## Run frontend dev server on port 5173
	@$(NVM_LOAD); cd $(FRONTEND_DIR); npm run dev -- --host $(FRONTEND_HOST) --port $(FRONTEND_PORT)

.PHONY: health
health: ## Check backend health endpoint
	curl -fsS http://localhost:$(BACKEND_PORT)/health

.PHONY: api-docs
api-docs: ## Show local API docs URL
	@echo "OpenAPI: http://localhost:$(BACKEND_PORT)/docs"
	@echo "Health:  http://localhost:$(BACKEND_PORT)/health"

.PHONY: clean-python
clean-python: ## Remove Python caches
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf $(BACKEND_DIR)/.pytest_cache $(BACKEND_DIR)/.ruff_cache .pytest_cache .ruff_cache

.PHONY: clean-frontend
clean-frontend: ## Remove frontend build output only
	rm -rf $(FRONTEND_DIR)/dist $(FRONTEND_DIR)/coverage

.PHONY: clean-codex
clean-codex: ## Remove local Codex runtime reports/logs
	rm -rf .codex/reports .codex/logs .codex/runs .codex/cache .codex/tmp

.PHONY: clean
clean: clean-python clean-frontend ## Remove generated caches/build outputs, but keep venv and node_modules

.PHONY: clean-all
clean-all: clean clean-codex ## Remove generated caches/build outputs and Codex runtime artifacts

.PHONY: phase10-summary
phase10-summary: ## Print Phase 10 documentation map
	@echo "Phase 10 docs:"
	@echo "  docs/architecture/PHASE_10_SAAS_MONETIZATION.md"
	@echo "  docs/architecture/BILLING_MODEL.md"
	@echo "  docs/architecture/MARKETPLACE_MODEL.md"
	@echo "  docs/architecture/ENTERPRISE_PACKAGING.md"
	@echo "  docs/runbooks/BILLING_INCIDENT_RUNBOOK.md"
	@echo "  docs/runbooks/SUBSCRIPTION_SUPPORT_RUNBOOK.md"
	@echo "  docs/runbooks/MARKETPLACE_REVIEW_RUNBOOK.md"
	@echo "  docs/runbooks/ENTERPRISE_CUSTOMER_RUNBOOK.md"
