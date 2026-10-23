#!/usr/bin/env python3
"""Compatibility entry point for the shared role launcher (including legacy briefs)."""
import os
from pathlib import Path
import sys

ROOT = Path(os.environ.get('AGENT_LAUNCH_ROOT', Path(__file__).resolve().parents[2])).expanduser().resolve()
if not (ROOT / 'scripts/agent_launcher.py').is_file() or not (ROOT / '.codex/agents/scripts/claude_runtime.py').is_file():
    raise SystemExit('Shared launcher unavailable; set AGENT_LAUNCH_ROOT to the configuration checkout containing scripts/agent-launch and both provider folders.')
sys.path.insert(0, str(ROOT / '.codex/agents/scripts'))
from claude_runtime import ensure_runtime
if __name__ == '__main__':
    ensure_runtime()
    sys.path.insert(0, str(ROOT / 'scripts'))
    from agent_launcher import main
    raise SystemExit(main(legacy_brief=True))
