#!/usr/bin/env python3
"""Run one role in its assigned checkout, independently of the calling provider."""
import argparse
from datetime import datetime, timedelta, timezone
import importlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import tomllib
import uuid

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / '.codex/agents'
# These are executor families, not a second model/effort configuration.
NATIVE_ROLES = ('delegate-low', 'delegate-medium', 'delegate-high', 'pr-green',
                'pr-resolve', 'pr-update', 'pr-review', 'pr-risk', 'writer')
CLAUDE_ROLES = ('delegate-xhigh', 'pr-review-high', 'port-to-claude')
READ_ONLY_ROLES = ('pr-green', 'pr-review', 'pr-risk', 'pr-review-high', 'port-to-claude')
ACTIVE = '_SHARED_AGENT_EXECUTOR_ACTIVE'
FIELDS = ('constraints', 'approvals', 'sources', 'verification', 'owned_paths')
# Import the existing ownership implementation once. Specialized reviews use it too.
sys.path.insert(0, str(AGENTS / 'scripts'))
import claude_runner as shared


def assignment(path):
    task = shared.load(path)
    if not isinstance(task, dict):
        raise ValueError('Assignment must be a JSON object')
    for field in ('objective', 'scope', 'expected_result'):
        if not isinstance(task.get(field), str) or not task[field].strip():
            raise ValueError('Missing task string: ' + field)
    for field in FIELDS:
        if not isinstance(task.get(field), list) or any(
                not isinstance(item, str) or not item.strip() for item in task[field]):
            raise ValueError('Task requires a string array: ' + field)
    return task


def schema():
    strings = {'type': 'array', 'items': {'type': 'string'}}
    properties = {'summary': {'type': 'string'}, 'complete': {'type': 'boolean'},
                  **{field: strings for field in ('changes', 'verification', 'gaps')}}
    return {'type': 'object', 'properties': properties, 'required': list(properties),
            'additionalProperties': False}


def valid_report(report):
    return (isinstance(report, dict) and isinstance(report.get('summary'), str)
            and bool(report['summary'].strip()) and isinstance(report.get('complete'), bool)
            and all(isinstance(report.get(field), list)
                    and all(isinstance(item, str) for item in report[field])
                    for field in ('changes', 'verification', 'gaps')))


def git_state(checkout):
    if not checkout.is_dir():
        raise ValueError('Assigned working directory is unavailable')
    probe = subprocess.run(['git', '-C', str(checkout), 'rev-parse', '--is-inside-work-tree'],
                           text=True, capture_output=True, timeout=10)
    if probe.returncode:
        if 'not a git repository' in probe.stderr:
            return {'git': False}
        raise ValueError('Unable to inspect assigned Git state')
    def git(*args):
        result = subprocess.run(['git', '-C', str(checkout), *args], text=True,
                                capture_output=True, timeout=10)
        # A newly initialized repository legitimately has no HEAD yet.
        if result.returncode and args == ('rev-parse', 'HEAD'):
            return None
        result.check_returncode()
        return result.stdout.strip()
    return {'head': git('rev-parse', 'HEAD'), 'branch': git('branch', '--show-current'),
            'status': git('status', '--porcelain=v1', '--untracked-files=all')}


def role_settings(agents, role):
    if role not in NATIVE_ROLES + CLAUDE_ROLES:
        raise ValueError('Unknown executor role: ' + role)
    settings = tomllib.loads((agents / (role + '.toml')).read_text())
    if settings.get('name') != role or not settings.get('developer_instructions'):
        raise ValueError('Canonical role has missing or mismatched settings')
    if role in NATIVE_ROLES and (not settings.get('model') or not settings.get('model_reasoning_effort')):
        raise ValueError('Canonical role has missing execution settings')
    return settings


def deadline_for(task, requested, timeout):
    original = task.get('finish_by')
    if original is not None and (not isinstance(original, str) or not original.strip()):
        raise ValueError('finish_by must be an absolute ISO 8601 string')
    if original:
        shared.bounded_timeout(timeout, original)
    deadline = requested or original or (
        datetime.now(timezone.utc) + timedelta(seconds=timeout)).isoformat()
    shared.bounded_timeout(timeout, deadline)
    if original and requested and datetime.fromisoformat(requested.replace('Z', '+00:00')) > datetime.fromisoformat(original.replace('Z', '+00:00')):
        raise ValueError('Cannot extend the assignment finish-by')
    return deadline


def executor_rules(role):
    review_boundary = (' This generic launch is analysis only: do not publish a PR review or claim review sign-off. '
                       'Use the specialized prepared Claude PR review workflow for its evidence, recovery, and publication gates.'
                       if role == 'pr-review-high' else '')
    return (f'\nYou are the actual {role} executor. Perform the assigned work directly. '
            'Never spawn agents, invoke agent handoff scripts, or route this assignment to another provider. '
            'The shared launcher also rejects nested execution through its inherited environment. '
            'Read applicable global and repository instructions. Preserve unrelated work. '
            'The assignment approvals and owned paths bound all actions; available tools grant no additional authority. '
            'Do not commit, push, publish, or send external communications unless explicitly authorized. '
            'Never bypass hooks or sandbox permissions. Verify actual results and return evidence and gaps. '
            'A supervising agent must verify the report before claiming completion.' + review_boundary + '\n')


def checked_paths(args):
    checkout = Path(args.checkout).expanduser().resolve(strict=True)
    if not checkout.is_dir():
        raise ValueError('Checkout must be a directory')
    output = Path(args.output).expanduser().resolve()
    for root in (checkout, ROOT):
        if output == root or root in output.parents:
            raise ValueError('Task output must be outside the checkout and public configuration repository')
    if output.exists():
        raise FileExistsError('Output directory already exists; inspect the prior result before another launch')
    source = Path(args.assignment or args.brief_file).expanduser().resolve(strict=True)
    for root in (checkout, ROOT):
        if source == root or root in source.parents:
            raise ValueError('Assignment must stay outside the checkout and public configuration repository')
    return checkout, output, source


def run(args):
    if os.environ.get(ACTIVE):
        raise ValueError('Nested agent launch refused: execute the assigned role directly')
    checkout, output, source = checked_paths(args)
    if args.max_turns <= 0:
        raise ValueError('max-turns must be positive')
    brief = None
    if args.assignment:
        task = assignment(source)
    else:
        brief = source.read_text()
        if not brief.strip():
            raise ValueError('Assignment brief must not be empty')
        # Compatibility only: keep the original brief intact, including its scope/approvals.
        task = {'objective': brief, 'scope': 'Exactly the supplied coordinator brief',
                'expected_result': 'A verified report of the assigned work',
                **{field: [] for field in FIELDS}}
    if brief is not None and args.sandbox != 'read-only':
        raise ValueError('Legacy briefs support read-only execution; use --assignment JSON with owned_paths for writes')
    deadline = deadline_for(task, args.finish_by, args.timeout)
    settings = role_settings(AGENTS, args.role)
    if args.role in READ_ONLY_ROLES and args.sandbox != 'read-only':
        raise ValueError('This role requires a read-only filesystem sandbox')
    if args.sandbox == 'workspace-write' and args.assignment and not task['owned_paths']:
        raise ValueError('Writable execution requires explicitly assigned owned_paths')
    adapter = importlib.import_module('agent_codex' if args.role in NATIVE_ROLES else 'agent_claude')
    execution = adapter.execution(settings)
    before = git_state(checkout)
    cli = adapter.executable()
    # A fresh private bundle is required even after a failed or incomplete attempt.
    output.mkdir(parents=True, mode=0o700, exist_ok=False)
    os.chmod(output, 0o700)
    shared.dump(output / 'assignment.json', task)
    if brief is not None:
        (output / 'brief.md').write_text(brief)
    session = str(uuid.uuid4())
    manifest = {'role': args.role, 'provider': adapter.PROVIDER, 'checkout': str(checkout),
                'finish_by': deadline, 'execution': execution, 'before': before,
                'initial_state': before, 'sandbox': args.sandbox, 'dry_run': args.dry_run,
                'model': execution['model'], 'effort': execution['effort'],
                'reviewer_attribution': execution['attribution'],
                'started_at': datetime.now(timezone.utc).isoformat()}
    shared.dump(output / 'manifest.json', manifest)
    started = time.monotonic()
    metrics = {'session': session, 'model': execution['model'], 'effort': execution['effort'],
               'execution_complete': False, 'report_valid': False, 'task_complete_claimed': False,
               'status': 'failed', 'verification': 'Supervisor must verify actual work and checks'}
    try:
        system = adapter.instructions(settings, args.role, executor_rules(args.role))
        (output / 'task-system.md').write_text(system)
        shared.dump(output / 'report-schema.json', schema())
        prompt = (f'Executor role: {args.role}\nCheckout: {checkout}\nAbsolute finish-by: {deadline}\n'
                  f'Executor attribution: {execution["attribution"]}\n'
                  'Use this attribution only for source work completed in this invocation. '
                  'Complete the scoped assignment and return the required structured task report. '
                  'Return complete=false for incomplete work; describe actual verification and gaps.\n'
                  + (f'Assignment: {output / "assignment.json"}\n' if brief is None else
                     'The following is the unchanged compact assignment from the coordinator:\n\n' + brief))
        (output / 'prompt.txt').write_text(prompt)
        command = adapter.launch_args(cli, checkout, output, session, args.max_turns,
                                      execution, args.sandbox, before, system, schema())
        shared.dump(output / 'launch.json', command)
        if args.dry_run:
            metrics['status'] = 'prepared'
            print(json.dumps(manifest, indent=2))
            return 0
        context = adapter.preflight(cli, checkout, output, deadline)
        timeout = shared.bounded_timeout(args.timeout, deadline) - 10
        if timeout <= 0:
            raise ValueError('Insufficient time before finish-by to launch and settle the owned process group')
        state = shared.run_process(command, checkout, prompt, timeout,
                                   lambda name: output / name, session)
        manifest['process'] = state
        result, report, details = adapter.collect(output, context, session, execution)
        shared.dump(output / 'result.json', result)
        if report is not None:
            shared.dump(output / 'report.json', report)
        metrics.update(details)
        metrics['execution_complete'] = (state.get('exit_code') == 0 and not state.get('timed_out')
                                         and not state.get('running') and details['provider_verified'])
        metrics['report_valid'] = valid_report(report)
        metrics['task_complete_claimed'] = report.get('complete', False) if valid_report(report) else False
        if metrics['execution_complete'] and metrics['report_valid']:
            metrics['status'] = 'complete' if report['complete'] else 'incomplete'
        print(json.dumps(metrics))
        if not metrics['execution_complete'] or not metrics['report_valid']:
            print('Executor did not return a verified report; inspect the private bundle and partial work.', file=sys.stderr)
            return 1
        if adapter.PROVIDER == 'codex':
            print(report['summary'])
        return 0
    except BaseException as error:
        metrics['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        manifest['final_state'] = git_state(checkout)
        manifest['finished_at'] = datetime.now(timezone.utc).isoformat()
        if (output / 'process.json').exists():
            manifest['process'] = shared.load(output / 'process.json')
        metrics['after'] = manifest['final_state']
        metrics['elapsed_seconds'] = round(time.monotonic() - started, 2)
        shared.dump(output / 'manifest.json', manifest)
        shared.dump(output / 'metrics.json', metrics)


def main(argv=None, default_role=None, legacy_brief=False):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--role', default=default_role, required=default_role is None,
                        choices=NATIVE_ROLES + CLAUDE_ROLES)
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument('--assignment', type=Path)
    if legacy_brief:
        sources.add_argument('--brief-file', type=Path)
    parser.add_argument('--checkout', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--finish-by', help='Absolute ISO 8601 deadline with explicit timezone')
    parser.add_argument('--sandbox', choices=('read-only', 'workspace-write'), default='read-only',
                        help='Codex filesystem sandbox; workspace-write requires assignment authorization')
    parser.add_argument('--timeout', type=int, default=1800)
    parser.add_argument('--max-turns', type=int, default=120)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    if not hasattr(args, 'brief_file'):
        args.brief_file = None
    def cancel(signum, frame):
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, cancel)
    try:
        return run(args)
    except KeyboardInterrupt:
        return 130
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    finally:
        signal.signal(signal.SIGTERM, previous)
