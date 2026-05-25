#!/usr/bin/env bash
set -euo pipefail
curl -s http://127.0.0.1:8000/api/scheduler/jobs || true
