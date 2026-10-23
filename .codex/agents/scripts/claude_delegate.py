#!/usr/bin/env python3
"""Compatibility entry point for shared role execution; defaults to delegate-xhigh."""
import os
from pathlib import Path
import sys

ROOT = Path(os.environ.get('AGENT_LAUNCH_ROOT', Path(__file__).resolve().parents[3])).expanduser().resolve()
if not (ROOT / 'scripts/agent_launcher.py').is_file() or not (ROOT / '.codex/agents/scripts/claude_runtime.py').is_file():
    raise SystemExit('Shared launcher unavailable; set AGENT_LAUNCH_ROOT to the configuration checkout containing scripts/agent-launch and both provider folders.')
sys.path.insert(0, str(ROOT / '.codex/agents/scripts'))
from claude_runtime import ensure_runtime
if __name__ == '__main__':
    ensure_runtime()
sys.path.insert(0, str(ROOT / 'scripts'))
from agent_launcher import assignment, git_state, schema, valid_report, main as shared_main
from agent_launcher import run as shared_run
from agent_claude import launch_args as command
import claude_runner as shared


def launch_args(cli, output, session, max_turns, profile):
    return command(cli, None, output, session, max_turns, profile, 'read-only', {}, '', schema())


def run(args):
    # Preserve the original Python API while sharing the only launch engine.
    from types import SimpleNamespace
    options = vars(args).copy()
    options.setdefault('role', 'delegate-xhigh')
    options.setdefault('brief_file', None)
    options.setdefault('sandbox', 'read-only')
    options.setdefault('dry_run', False)
    code = shared_run(SimpleNamespace(**options))
    if code:
        raise SystemExit(code)


def main():
    return shared_main(default_role='delegate-xhigh')


if __name__ == '__main__':
    raise SystemExit(main())
