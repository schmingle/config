"""Codex CLI flags, authentication, and output identity checks."""
import json
import os
from pathlib import Path
import shutil
import subprocess

from agent_launcher import APPROACH_ROLES, capabilities, shared
from reviewer_attribution import native_attribution

PROVIDER = 'codex'


def execution(settings):
    contribution = 'Approach analysis by' if settings['name'] in APPROACH_ROLES else 'Reviewed by'
    return {'model': settings['model'], 'effort': settings['model_reasoning_effort'],
            'attribution': native_attribution(settings, contribution),
            'capabilities': capabilities(settings['name'])}


def executable():
    cli = os.environ.get('CODEX_BIN') or shutil.which('codex')
    if not cli:
        raise ValueError('Codex CLI unavailable; install it or set CODEX_BIN to its executable')
    return cli


def instructions(settings, role, rules):
    # Native Codex instructions already identify the semantic owner and canonical guides.
    return settings['developer_instructions'] + rules


def launch_args(cli, checkout, output, session, max_turns, profile, sandbox, before, system, schema):
    limits = profile['capabilities']
    if sandbox == 'workspace-write' and not limits['source_writes']:
        raise ValueError('This role requires a read-only filesystem sandbox')
    argv = [cli, 'exec', '--strict-config', '--cd', str(checkout), '--sandbox', sandbox,
            '--model', profile['model'],
            '--config', 'model_reasoning_effort=' + json.dumps(profile['effort']),
            '--config', 'developer_instructions=' + json.dumps(system),
            '--config', 'approval_policy=' + json.dumps(limits['approval_policy']),
            '--config', 'approvals_reviewer=' + json.dumps(limits['approvals_reviewer']),
            '--config', 'features.multi_agent=false',
            '--json', '--output-schema', str(output / 'report-schema.json'),
            '--output-last-message', str(output / 'report.md'), '-']
    if before.get('git') is False or before.get('head') is None:
        argv.insert(2, '--skip-git-repo-check')
    return argv


def preflight(cli, checkout, output, deadline):
    for label, action in (('version', ['--version']), ('authentication', ['login', 'status'])):
        result = subprocess.run([cli, *action], cwd=checkout, capture_output=True, text=True,
                                timeout=shared.bounded_timeout(15, deadline))
        (output / (label + '.log')).write_text(result.stdout + result.stderr)
        if result.returncode:
            raise ValueError('Codex ' + label + ' preflight failed; inspect its private log and restore access')
    return {}


def collect(output, context, session, profile):
    events = []
    for line in (output / 'events.jsonl').read_text().splitlines():
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
        except ValueError:
            continue
    report = None
    try:
        report = json.loads((output / 'report.md').read_text())
    except (OSError, ValueError):
        pass
    complete = any(event.get('type') == 'turn.completed' for event in events)
    failed = any(event.get('type') in ('error', 'turn.failed') for event in events)
    return {'events': events}, report, {'provider_verified': complete and not failed}
