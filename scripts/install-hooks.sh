#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

chmod +x scripts/scan-secrets.sh
chmod +x .githooks/pre-push

git config core.hooksPath .githooks

echo "[hooks] Installed. pre-push secret scan is now active."
