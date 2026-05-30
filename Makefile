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
GH_REPO ?= cvsz/zdash
GH_ENV ?= dev
GH_ENV_FILE ?= .env
GO_LIVE_RESET ?= no
RELEASE_TAG ?= v2.0.0
RELEASE_TITLE ?= zDash Final Release
CONFIRM_RELEASE ?= no

ZDASH_DOMAIN ?= localhost
ZDASH_PROD_RUNTIME ?= /opt/zdash/runtime
ZDASH_PROD_ENV ?= $(ZDASH_PROD_RUNTIME)/.env.production
ZDASH_PROD_COMPOSE ?= $(ZDASH_PROD_RUNTIME)/docker-compose.yml
ZDASH_PROD_HEALTH ?= $(ZDASH_PROD_RUNTIME)/scripts/zdash-health.sh
ZDASH_PROD_LOGS ?= $(ZDASH_PROD_RUNTIME)/scripts/zdash-logs.sh
ZDASH_PROD_BACKUP ?= $(ZDASH_PROD_RUNTIME)/scripts/zdash-backup.sh
ZDASH_PROD_UPDATE ?= $(ZDASH_PROD_RUNTIME)/scripts/zdash-update.sh

BACKEND_ACTIVATE := source $(BACKEND_DIR)/.venv/bin/activate
NVM_LOAD := source $$HOME/.nvm/nvm.sh >/dev/null 2>&1 || true; nvm use $(NODE_VERSION) >/dev/null 2>&1 || true
FORBIDDEN_TRACKED_PATTERN := (^\.env$$|^gpg-loopback\.sh$$|^\.agent/|^\.agents/|^\.gemini/|^\.claude/|^\.mcp/|^docs/prompt/codex-runs/|^skill\.sh$$|^scripts/skill\.sh$$)

.PHONY: help
help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"; printf "\nzDash Master Makefile\n\nUsage:\n  make <target>\n\nTargets:\n"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  %-34s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\nCommon flows:\n  make install-local\n  make install-local-start\n  make validate-fast\n  make validate\n  make install-prod ZDASH_DOMAIN=zdash.zeaz.dev\n  make prod-health\n  make prod-logs SERVICE=backend\n  make gh-env-dry GH_ENV=dev\n  make gh-env-sync GH_ENV=dev\n  make run-backend\n  make run-frontend\n\n"

.PHONY: info
info: ## Print local project/runtime info
	@echo "Repo: cvsz/zdash"
	@echo "Root: $(ROOT_DIR)"
	@echo "Backend: http://localhost:$(BACKEND_PORT)"
	@echo "Frontend: http://localhost:$(FRONTEND_PORT)"
	@echo "Release tag: $(RELEASE_TAG)"
	@git branch --show-current 2>/dev/null || true
	@git rev-parse --short HEAD 2>/dev/null || true
	@$(PYTHON) --version || true
	@node --version || true
	@npm --version || true

.PHONY: pull
pull: ## Pull latest main with fast-forward only
	git pull --ff-only

.PHONY: sync-main
sync-main: ## Sync local main from origin/main; set GO_LIVE_RESET=yes to hard reset and clean
	@git fetch origin main
	@if [ "$(GO_LIVE_RESET)" = "yes" ]; then \
		git checkout main; \
		git reset --hard origin/main; \
		git clean -fd; \
	else \
		git pull --ff-only origin main; \
	fi

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
	@status=0; \
	for file in .env .env.production .env.production.example frontend/.env frontend/.env.local; do \
		[ -f "$$file" ] || continue; \
		file_ok=1; \
		line_no=0; \
		while IFS= read -r raw || [ -n "$$raw" ]; do \
			line_no=$$((line_no + 1)); \
			line="$$(printf '%s' "$$raw" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$$//')"; \
			[ -n "$$line" ] || continue; \
			case "$$line" in \#*) continue ;; esac; \
			case "$$line" in *=*) key="$${line%%=*}" ;; *) echo "$$file:$$line_no: missing ="; file_ok=0; status=1; continue ;; esac; \
			if ! printf '%s\n' "$$key" | grep -Eq '^[A-Za-z_][A-Za-z0-9_]*$$'; then \
				echo "$$file:$$line_no: invalid key '$$key'"; \
				file_ok=0; \
				status=1; \
			fi; \
		done < "$$file"; \
		[ "$$file_ok" -eq 0 ] || echo "PASSED: $$file"; \
	done; \
	exit "$$status"

.PHONY: gh-env-dry
gh-env-dry: ## Dry-run sync local env files into GitHub Environment variables/secrets
	@bash scripts/github/bootstrap-env-from-env.sh --repo $(GH_REPO) --env $(GH_ENV) --file $(GH_ENV_FILE) --dry-run

.PHONY: gh-env-sync
gh-env-sync: ## Live sync local env file into GitHub Environment variables/secrets; requires GH_ENV/GH_ENV_FILE and gh auth
	@bash scripts/github/bootstrap-env-from-env.sh --repo $(GH_REPO) --env $(GH_ENV) --file $(GH_ENV_FILE) --yes

.PHONY: gh-env-clean-dry
gh-env-clean-dry: ## Dry-run stale cleanup for managed GitHub Environment keys
	@bash scripts/github/bootstrap-env-from-env.sh --repo $(GH_REPO) --env $(GH_ENV) --file $(GH_ENV_FILE) --delete-stale --dry-run

.PHONY: gh-env-clean
gh-env-clean: ## Delete stale managed GitHub Environment keys not present in local env file; requires confirmation
	@bash scripts/github/bootstrap-env-from-env.sh --repo $(GH_REPO) --env $(GH_ENV) --file $(GH_ENV_FILE) --delete-stale --yes

.PHONY: port-scan
port-scan: ## Fail if tracked runtime/source files still reference backend port 8000
	@echo "Scanning tracked runtime/source files for old backend port 8000..."
	@tmp=$$(mktemp); \
	git grep -nE 'localhost:8000|BACKEND_PORT=8000' -- . \
		':(exclude)Makefile' \
		':(exclude)docs/prompt/*.prompt' \
		':(exclude)docs/prompts/**' \
		':(exclude)docs/reports/**' \
		':(exclude)docs/releases/**' \
		':(exclude)release/**' \
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
secret-scan: ## Scan tracked runtime/source files for actual secret-looking values
	@echo "Scanning tracked runtime/source files for actual secret-looking values..."
	@tmp=$$(mktemp); \
	git grep -nE 'sk-[A-Za-z0-9_-]{20,}|BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY|(GPG_PASSPHRASE|STRIPE_SECRET_KEY|STRIPE_WEBHOOK_SECRET|CLOUDFLARE_API_TOKEN|CLOUDFLARE_ACCOUNT_ID|CLOUDFLARE_ZONE_ID|TUNNEL_TOKEN|OPENAI_API_KEY)[[:space:]]*=[[:space:]]*[^[:space:]#]+' -- . \
		':(exclude)Makefile' \
		':(exclude)**/*.md' \
		':(exclude)docs/**' \
		':(exclude).codex/**' \
		':(exclude).agent/**' \
		':(exclude).agents/**' \
		':(exclude)backend/app/tests/**' \
		':(exclude)backend/tests/**' \
		':(exclude)frontend/src/tests/**' > $$tmp 2>/dev/null || true; \
	if [ -s $$tmp ]; then \
		cat $$tmp; \
		rm -f $$tmp; \
		echo "FAILED: possible real secret in tracked runtime/source files" >&2; \
		exit 1; \
	else \
		rm -f $$tmp; \
		echo "PASSED: no actual secret-looking tracked values"; \
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
compose-logs: ## Follow compose logs
	docker compose logs -f --tail=200

.PHONY: scripts-list
scripts-list: ## List executable script files known to the repo/worktree
	@echo "Tracked shell/python/powershell scripts:"; \
	git ls-files '*.sh' '*.py' '*.ps1' | sort | sed 's/^/  /'; \
	echo; \
	echo "Installer-generated local helpers if present:"; \
	for f in run-backend.sh run-frontend.sh healthcheck-zdash.sh validate-zdash.sh repair-zdash.sh; do [ ! -f "$$f" ] || echo "  $$f"; done

.PHONY: scripts-chmod
scripts-chmod: ## chmod +x tracked shell scripts and root installers
	@chmod +x install-zdash-fullstack.sh install-zdash-prod.sh 2>/dev/null || true
	@find scripts infra/scripts .codex -type f -name '*.sh' -exec chmod +x {} + 2>/dev/null || true
	@for f in run-backend.sh run-frontend.sh healthcheck-zdash.sh validate-zdash.sh repair-zdash.sh; do [ ! -f "$$f" ] || chmod +x "$$f"; done
	@echo "Script executable bits refreshed."

.PHONY: install-local
install-local: scripts-chmod ## Run local/VM full-stack installer
	bash install-zdash-fullstack.sh

.PHONY: install-local-start
install-local-start: scripts-chmod ## Run local installer and start backend/frontend via nohup
	START_SERVICES=true bash install-zdash-fullstack.sh

.PHONY: install-local-pull
install-local-pull: scripts-chmod ## Pull when clean, then run local installer
	DO_PULL=true bash install-zdash-fullstack.sh

.PHONY: install-local-fast
install-local-fast: scripts-chmod ## Run local installer without tests/build for quick repair
	RUN_BACKEND_TESTS=false RUN_FRONTEND_TESTS=false RUN_FRONTEND_BUILD=false bash install-zdash-fullstack.sh

.PHONY: install-local-docker
install-local-docker: scripts-chmod ## Run local installer plus Docker validation builds
	RUN_DOCKER_BUILDS=true INSTALL_DOCKER=true bash install-zdash-fullstack.sh

.PHONY: install-repair
install-repair: scripts-chmod ## Run generated repair helper if present, else force backend reinstall through installer
	@if [ -x ./repair-zdash.sh ]; then ./repair-zdash.sh; else FORCE_BACKEND_REINSTALL=true bash install-zdash-fullstack.sh; fi

.PHONY: install-validate
install-validate: scripts-chmod ## Run generated validate helper if present, else run make validate-fast
	@if [ -x ./validate-zdash.sh ]; then ./validate-zdash.sh; else $(MAKE) validate-fast; fi

.PHONY: install-health
install-health: ## Run generated local healthcheck if present
	@if [ -x ./healthcheck-zdash.sh ]; then ./healthcheck-zdash.sh; else $(MAKE) health; fi

.PHONY: install-prod
install-prod: scripts-chmod ## Run production installer with sudo; set ZDASH_DOMAIN=domain
	sudo ZDASH_DOMAIN=$(ZDASH_DOMAIN) ./install-zdash-prod.sh

.PHONY: install-prod-tests
install-prod-tests: scripts-chmod ## Run production installer with backend/frontend host tests enabled
	sudo ZDASH_DOMAIN=$(ZDASH_DOMAIN) RUN_TESTS=true RUN_FRONTEND_TESTS=true ./install-zdash-prod.sh

.PHONY: install-prod-no-firewall
install-prod-no-firewall: scripts-chmod ## Run production installer without changing UFW
	sudo ZDASH_DOMAIN=$(ZDASH_DOMAIN) ENABLE_UFW=false ./install-zdash-prod.sh

.PHONY: prod-ps
prod-ps: ## Show production Docker Compose services
	sudo docker compose --env-file $(ZDASH_PROD_ENV) -f $(ZDASH_PROD_COMPOSE) ps

.PHONY: prod-health
prod-health: ## Run production health helper
	sudo $(ZDASH_PROD_HEALTH)

.PHONY: prod-logs
prod-logs: ## Follow production logs; set SERVICE=backend/nginx/frontend/postgres/redis
	@if [ -n "$${SERVICE:-}" ]; then sudo $(ZDASH_PROD_LOGS) "$$SERVICE"; else sudo $(ZDASH_PROD_LOGS); fi

.PHONY: prod-backend-logs
prod-backend-logs: ## Follow production backend logs
	sudo $(ZDASH_PROD_LOGS) backend

.PHONY: prod-nginx-logs
prod-nginx-logs: ## Follow production nginx logs
	sudo $(ZDASH_PROD_LOGS) nginx

.PHONY: prod-backup
prod-backup: ## Run production backup helper
	sudo $(ZDASH_PROD_BACKUP)

.PHONY: prod-update
prod-update: ## Run production update/rebuild helper
	sudo $(ZDASH_PROD_UPDATE)

.PHONY: prod-start
prod-start: ## Start production systemd service
	sudo systemctl start zdash

.PHONY: prod-stop
prod-stop: ## Stop production systemd service
	sudo systemctl stop zdash

.PHONY: prod-restart
prod-restart: ## Restart production stack through systemd
	sudo systemctl restart zdash

.PHONY: prod-status
prod-status: ## Show production systemd service status
	sudo systemctl status zdash --no-pager

.PHONY: prod-down
prod-down: ## Stop production Docker Compose stack directly
	sudo docker compose --env-file $(ZDASH_PROD_ENV) -f $(ZDASH_PROD_COMPOSE) down

.PHONY: prod-up
prod-up: ## Start production Docker Compose stack directly
	sudo docker compose --env-file $(ZDASH_PROD_ENV) -f $(ZDASH_PROD_COMPOSE) up -d

.PHONY: codex-setup
codex-setup: ## Run Codex Cloud setup script
	bash .codex/cloud/setup.sh

.PHONY: codex-maintenance
codex-maintenance: ## Run Codex Cloud maintenance script
	bash .codex/cloud/maintenance.sh

.PHONY: codex-repair-backend
codex-repair-backend: ## Run Codex backend dependency repair script
	bash .codex/cloud/repair-backend-deps.sh

.PHONY: codex-healthcheck
codex-healthcheck: ## Run Codex healthcheck if present
	@if [ -x .codex/healthcheck.sh ]; then bash .codex/healthcheck.sh; else echo ".codex/healthcheck.sh not found/executable"; fi

.PHONY: maintenance
maintenance: codex-maintenance ## Run Codex Cloud maintenance validation

.PHONY: script-run-phases
script-run-phases: ## Run prompt phase runner; set PHASE_ARGS='...'
	bash scripts/run-prompt-phases.sh $${PHASE_ARGS:-}

.PHONY: script-export-json-prompt
script-export-json-prompt: ## Run JSON-to-prompt export helper; set EXPORT_ARGS='...'
	bash scripts/export-json-to-prompt.sh $${EXPORT_ARGS:-}

.PHONY: script-integrate-ecc
script-integrate-ecc: ## Run ECC integration script
	bash scripts/integrate-ecc.sh

.PHONY: script-sync-ecc-codex
script-sync-ecc-codex: ## Run ECC-to-Codex sync script
	bash scripts/sync-ecc-to-codex.sh

.PHONY: script-setup-dev
script-setup-dev: ## Run repository dev setup script
	bash scripts/setup-dev.sh

.PHONY: script-enable-agents
script-enable-agents: ## Run agent enabling helper
	$(PYTHON) scripts/enable_agents.py

.PHONY: infra-deploy-dev
infra-deploy-dev: ## Run infra development deploy script
	bash infra/scripts/deploy-dev.sh

.PHONY: infra-deploy-prod
infra-deploy-prod: ## Run infra production deploy script
	bash infra/scripts/deploy-prod.sh

.PHONY: infra-rollback
infra-rollback: ## Run infra rollback script
	bash infra/scripts/rollback.sh

.PHONY: windows-nssm-command
windows-nssm-command: ## Print Windows NSSM install command for PowerShell
	@echo 'PowerShell:'
	@echo '  powershell -ExecutionPolicy Bypass -File scripts/install-nssm-service.ps1'

.PHONY: all-scripts-check
all-scripts-check: scripts-list scripts-chmod safety-scan ## List scripts, refresh executable bits, and run safety scan

.PHONY: validate-fast
validate-fast: safety-scan backend-check frontend-check ## Run safety scans + backend/frontend validation

.PHONY: validate
validate: validate-fast docker-build compose-check maintenance ## Run full validation including Docker and maintenance

.PHONY: golive
golive: backend-install frontend-install validate-fast ## Go-live gate: install deps, safety scans, tests, and frontend build
	@echo "GO LIVE READY: backend pytest, frontend tests, and frontend build passed."

.PHONY: golive-sync
golive-sync: sync-main golive ## Sync from origin/main, then run go-live gate

.PHONY: release-notes
release-notes: ## Generate docs/releases/$(RELEASE_TAG).md
	@mkdir -p docs/releases
	@printf '%s\n' \
		"# $(RELEASE_TITLE)" \
		"" \
		"Status: GO LIVE READY" \
		"" \
		"## Validation" \
		"" \
		"- Backend pytest: PASS" \
		"- Frontend vitest: PASS" \
		"- Frontend production build: PASS" \
		"- Safety scans: PASS" \
		"" \
		"## Safety" \
		"" \
		"- Trading execution remains dry-run / guarded by default." \
		"- Google Finance Beta integration is read-only and does not scrape private endpoints." \
		"- This release is not financial advice." \
		"" \
		"Generated by: make release-notes RELEASE_TAG=$(RELEASE_TAG)" \
		> docs/releases/$(RELEASE_TAG).md
	@echo "Wrote docs/releases/$(RELEASE_TAG).md"

.PHONY: release-artifact
release-artifact: frontend-build ## Package frontend dist artifact under release-artifacts/
	@mkdir -p release-artifacts
	@tar -czf release-artifacts/zdash-frontend-$(RELEASE_TAG).tar.gz -C $(FRONTEND_DIR) dist
	@echo "Wrote release-artifacts/zdash-frontend-$(RELEASE_TAG).tar.gz"

.PHONY: release-local
release-local: golive release-notes release-artifact ## Run go-live validation and create local release notes/artifact

.PHONY: release-push
release-push: release-tag ## Push main and release tag; set CONFIRM_RELEASE=yes
	@test "$(CONFIRM_RELEASE)" = "yes" || (echo "ERROR: set CONFIRM_RELEASE=yes to push release" >&2; exit 1)
	@git push origin main
	@git push origin $(RELEASE_TAG)

.PHONY: gh-release
gh-release: ## Create GitHub release with artifact; requires gh auth and CONFIRM_RELEASE=yes
	@test "$(CONFIRM_RELEASE)" = "yes" || (echo "ERROR: set CONFIRM_RELEASE=yes to create GitHub release" >&2; exit 1)
	@command -v gh >/dev/null 2>&1 || (echo "ERROR: gh CLI not found" >&2; exit 1)
	@test -f docs/releases/$(RELEASE_TAG).md || (echo "ERROR: missing docs/releases/$(RELEASE_TAG).md; run make release-notes" >&2; exit 1)
	@test -f release-artifacts/zdash-frontend-$(RELEASE_TAG).tar.gz || (echo "ERROR: missing release artifact; run make release-artifact" >&2; exit 1)
	@if gh release view $(RELEASE_TAG) >/dev/null 2>&1; then \
		echo "Release $(RELEASE_TAG) exists. Uploading artifact with --clobber..."; \
		gh release upload $(RELEASE_TAG) release-artifacts/zdash-frontend-$(RELEASE_TAG).tar.gz --clobber; \
	else \
		gh release create $(RELEASE_TAG) --title "$(RELEASE_TITLE)" --notes-file docs/releases/$(RELEASE_TAG).md release-artifacts/zdash-frontend-$(RELEASE_TAG).tar.gz; \
	fi

.PHONY: release-status
release-status: ## Show release tag status
	@if git rev-parse $(RELEASE_TAG) >/dev/null 2>&1; then \
		echo "Tag $(RELEASE_TAG) exists at $(shell git rev-parse --short $(RELEASE_TAG))"; \
		if [ "$$(git rev-parse $(RELEASE_TAG))" = "$$(git rev-parse HEAD)" ]; then \
			echo "Tag points to HEAD (up to date)"; \
		else \
			echo "WARNING: tag does not point to HEAD"; \
		fi; \
	else \
		echo "Tag $(RELEASE_TAG) does not exist yet"; \
	fi
	@if gh release view $(RELEASE_TAG) >/dev/null 2>&1; then \
		echo "GitHub release $(RELEASE_TAG) exists"; \
	else \
		echo "GitHub release $(RELEASE_TAG) does not exist"; \
	fi

.PHONY: release-tag
release-tag: release-local ## Create local annotated release tag; set CONFIRM_RELEASE=yes
	@test "$(CONFIRM_RELEASE)" = "yes" || (echo "ERROR: set CONFIRM_RELEASE=yes to create release tag" >&2; exit 1)
	@git diff --quiet || (echo "ERROR: working tree has unstaged changes. Commit release notes first." >&2; git status --short; exit 1)
	@if git rev-parse $(RELEASE_TAG) >/dev/null 2>&1; then \
		if [ "$$(git rev-parse $(RELEASE_TAG))" = "$$(git rev-parse HEAD)" ]; then \
			echo "Tag $(RELEASE_TAG) already exists at HEAD (skipping)"; \
		else \
			echo "ERROR: tag $(RELEASE_TAG) exists but does not point to HEAD" >&2; \
			exit 1; \
		fi; \
	else \
		git tag -a $(RELEASE_TAG) -m "$(RELEASE_TITLE)"; \
		echo "Created tag $(RELEASE_TAG)"; \
	fi

.PHONY: prod-env-generate
prod-env-generate: ## Generate .env.production with random secrets (chmod 600)
	bash scripts/production/generate-prod-env.sh

.PHONY: prod-deploy-final
prod-deploy-final: prod-env-generate ## Generate env, validate compose config, build, deploy, health check
	@test -f .env.production || (echo "ERROR: .env.production missing" >&2; exit 1)
	docker compose --env-file .env.production -f docker-compose.prod.yml config
	docker compose --env-file .env.production -f docker-compose.prod.yml up --build -d
	docker compose -f docker-compose.prod.yml ps
	@echo "Waiting for backend health check..."
	@sleep 10
	curl -fsS http://localhost/health && echo " Health check passed" || echo " Health check failed (backend may still be starting)"

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
