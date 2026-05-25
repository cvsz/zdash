#!/usr/bin/env bash
set -euo pipefail
host=$1; port=$2
until nc -z "$host" "$port"; do sleep 1; done
