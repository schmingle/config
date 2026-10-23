#!/usr/bin/env bash
# Foreground, role-aware handoff. No automatic Git or publication operations.
set -euo pipefail
exec python3 "$(dirname "$0")/codex_delegate.py" "$@"
