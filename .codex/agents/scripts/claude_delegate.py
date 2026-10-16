#!/usr/bin/env python3
"""Run one scoped Claude task in its assigned checkout. Never grants publication."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
import signal
import subprocess
import time
import uuid

import claude_runner as shared

FIELDS = ('constraints', 'approvals', 'sources', 'verification', 'owned_paths')


def assignment(path):
    task = shared.load(path)
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
    return {'type': 'object', 'properties': properties, 'required': list(properties)}


def valid_report(report):
    return (isinstance(report, dict) and isinstance(report.get('summary'), str)
            and isinstance(report.get('complete'), bool)
            and all(isinstance(report.get(field), list)
                    and all(isinstance(item, str) for item in report[field])
                    for field in ('changes', 'verification', 'gaps')))


def git_state(checkout):
    if not checkout.is_dir():
        raise ValueError('Assigned working directory is unavailable')
    probe = subprocess.run(['git', '-C', str(checkout), 'rev-parse', '--is-inside-work-tree'],
                           text=True, capture_output=True)
    if probe.returncode:
        if 'not a git repository' in probe.stderr:
            return {'git': False}
        raise ValueError('Unable to inspect assigned Git state')
    return {'head': shared.git(checkout, 'rev-parse', 'HEAD'),
            'branch': shared.git(checkout, 'branch', '--show-current'),
            'status': shared.git(checkout, 'status', '--porcelain')}


def launch_args(cli, output, session, max_turns, profile):
    return shared.launch_args(cli, output, session, max_turns, profile,
                              schema(), 'task-system.md')


def run(args):
    task = assignment(args.assignment)
    checkout = Path(args.checkout).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    config_repo = Path(__file__).resolve().parents[3]
    if any(output == root or root in output.parents for root in (checkout, config_repo)):
        raise ValueError('Task output must be outside the checkout and public configuration repository')
    if args.max_turns <= 0:
        raise ValueError('max-turns must be positive')
    deadline = args.finish_by or task.get('finish_by') or (
        datetime.now(timezone.utc) + timedelta(seconds=args.timeout)).isoformat()
    if args.finish_by and task.get('finish_by'):
        original = datetime.fromisoformat(task['finish_by'].replace('Z', '+00:00'))
        requested = datetime.fromisoformat(args.finish_by.replace('Z', '+00:00'))
        if original.tzinfo is None or requested.tzinfo is None:
            raise ValueError('finish-by must include an explicit timezone')
        if requested > original:
            raise ValueError('Cannot extend the assignment finish-by')
    shared.bounded_timeout(args.timeout, deadline)
    before = git_state(checkout)
    cli = shutil.which('claude')
    if not cli:
        raise ValueError('Claude CLI is unavailable; restore the installed CLI without substituting a model')
    profile = shared.execution_profile()
    # A fresh bundle prevents accidental retries after partially completed edits.
    output.mkdir(parents=True, exist_ok=False)
    shared.dump(output / 'assignment.json', task)
    shared.dump(output / 'manifest.json', {'checkout': str(checkout), 'finish_by': deadline,
                                          'execution': profile, 'before': before})
    storage = shared.persistence_preflight(cli, checkout)
    shared.dump(output / 'persistence.json', storage)
    (output / 'task-system.md').write_text(
        (shared.AGENTS / 'context.md').read_text() + '\n\n'
        + (shared.AGENTS / 'claude.md').read_text() + '\n\n'
        + (shared.AGENTS / 'delegate-claude.md').read_text() + '\n\n'
        + 'You are the Claude task executor, not the Codex wrapper. Perform the task directly. '
        + 'Do not invoke the task runner or spawn agents. Read applicable global and repository '
        + 'instructions before acting. Preserve unrelated changes and obey the assignment approvals.\n')
    session = str(uuid.uuid4())
    argv = launch_args(cli, output, session, args.max_turns, profile)
    shared.dump(output / 'launch.json', argv)
    prompt = ('Complete the scoped assignment in ' + str(output / 'assignment.json')
              + '. Work in the assigned current checkout. Absolute finish-by: ' + deadline
              + '. Select applicable guidance and gather needed evidence; do not expand ownership '
              + 'or authorization. No additional agents. Return the structured task report, with '
              + 'actual verification evidence and gaps. Never claim unverified completion.\n')
    (output / 'prompt.txt').write_text(prompt)
    started = time.monotonic()
    state = shared.run_process(argv, checkout, prompt,
                               shared.bounded_timeout(args.timeout, deadline),
                               lambda name: output / name, session)
    events = []
    for line in (output / 'events.jsonl').read_text().splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    result = next((event for event in reversed(events) if event.get('type') == 'result'), {})
    report = result.get('structured_output')
    execution_complete = (state.get('exit_code') == 0 and not state['timed_out']
                          and not result.get('is_error', True)
                          and profile['model'] in result.get('modelUsage', {}))
    transcript = shared.saved_transcript(storage, session)
    storage.update(session=session, transcript=transcript, transcript_persisted=bool(transcript))
    shared.dump(output / 'persistence.json', storage)
    metrics = {'session': session, 'model': profile['model'], 'effort': profile['effort'],
               'execution_complete': execution_complete, 'report_valid': valid_report(report),
               'task_complete_claimed': report.get('complete', False) if valid_report(report) else False,
               'transcript_persisted': bool(transcript), 'after': git_state(checkout),
               'elapsed_seconds': round(time.monotonic() - started, 2),
               'model_usage': result.get('modelUsage', {}), 'usage': result.get('usage', {}),
               'permission_denials': result.get('permission_denials', []),
               'verification': 'Wrapper must verify actual changes and checks before completion'}
    shared.dump(output / 'result.json', result)
    shared.dump(output / 'metrics.json', metrics)
    if report is not None:
        shared.dump(output / 'report.json', report)
    print(json.dumps(metrics))
    if not execution_complete or not valid_report(report) or not transcript:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assignment', required=True)
    parser.add_argument('--checkout', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--timeout', type=int, default=1800)
    parser.add_argument('--max-turns', type=int, default=120)
    parser.add_argument('--finish-by', help='ISO 8601 deadline with timezone')
    args = parser.parse_args()

    def cancel(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, cancel)
    try:
        run(args)
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == '__main__':
    main()
