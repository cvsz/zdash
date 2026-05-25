#!/usr/bin/env bash
set -euo pipefail
curl -fsS http://localhost/ >/dev/null
curl -fsS http://localhost/api/health >/dev/null
echo ok
