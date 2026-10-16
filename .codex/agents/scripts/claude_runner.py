#!/usr/bin/env python3
"""Shared Claude execution, authentication, persistence, and process ownership."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time
import tomllib

AGENTS = Path(__file__).resolve().parents[1]
PROFILE = Path(__file__).with_name('claude-review.toml')


def execution_profile():
    return tomllib.loads(PROFILE.read_text())


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(checkout, *args):
    return subprocess.check_output(['git', '-C', str(checkout), *args], text=True).strip()


def persistence_preflight(cli, checkout):
    """Probe the real authenticated config directory under these launch permissions."""
    if os.environ.get('CLAUDE_CODE_SKIP_PROMPT_HISTORY', '').lower() in ('1', 'true', 'yes'):
        raise ValueError('Claude session persistence is disabled by CLAUDE_CODE_SKIP_PROMPT_HISTORY')
    status = subprocess.run([cli, 'auth', 'status'], cwd=checkout, capture_output=True, text=True, timeout=15)
    try:
        identity = json.loads(status.stdout)
    except ValueError:
        raise ValueError('Claude authentication preflight returned no valid status; check launch permissions/login') from None
    if status.returncode or not identity.get('loggedIn') or not identity.get('configDirectory'):
        raise ValueError('Claude login/config directory unavailable under launch permissions; use authorized escalation or restore login')
    config = Path(identity['configDirectory']).expanduser().resolve()
    projects = config / 'projects'
    project = projects / re.sub(r'[^a-zA-Z0-9]', '-', str(checkout.resolve()))
    try:
        for directory in (projects, project):
            directory.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=directory) as probe:
                probe.write(b'persistence probe')
                probe.flush()
    except OSError:
        raise ValueError('Claude session storage is not writable under launch permissions; use authorized escalation') from None
    return {'config_directory': str(config), 'projects_directory': str(projects)}


def saved_transcript(storage, session):
    matches = [path for path in Path(storage['projects_directory']).glob('*/' + session + '.jsonl')
               if path.is_file() and path.stat().st_size]
    if len(matches) > 1:
        raise ValueError('Ambiguous persisted Claude session; reconcile transcript paths before resuming')
    return str(matches[0]) if matches else None


def assignment_deadline(bundle, requested, timeout):
    """Continuations/recovery may shorten, but never reset, the original deadline."""
    path = bundle / 'assignment.json'
    deadline = requested or (datetime.now(timezone.utc) + timedelta(seconds=timeout)).isoformat()
    bounded_timeout(timeout, deadline)
    if path.exists():
        original = load(path)['finish_by']
        if requested and datetime.fromisoformat(deadline.replace('Z', '+00:00')) > datetime.fromisoformat(original.replace('Z', '+00:00')):
            raise ValueError('Continuation/replacement cannot extend the original assignment deadline')
        if requested and deadline != original:
            dump(path, {'finish_by': deadline})
        return original if not requested else deadline
    dump(path, {'finish_by': deadline})
    return deadline


def ensure_settled(bundle):
    for path in bundle.glob('process*.json'):
        if load(path).get('running'):
            raise ValueError('An owned Claude process is not settled; reconcile it before another launch')


def bounded_timeout(requested, finish_by):
    if requested <= 0:
        raise ValueError('timeout must be positive')
    if not finish_by:
        return requested
    deadline = datetime.fromisoformat(finish_by.replace('Z', '+00:00'))
    if deadline.tzinfo is None:
        raise ValueError('finish-by must include an explicit timezone')
    remaining = (deadline - datetime.now(timezone.utc)).total_seconds()
    if remaining <= 0:
        raise ValueError('Absolute assignment finish-by has passed')
    return min(requested, remaining)


def stop_process(proc):
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=3)


def run_process(argv, checkout, prompt, timeout, artifact, session, cleanup=None):
    """Always settle the owned process, including input failures and interruption."""
    proc = None
    state = {'session': session, 'running': False, 'timed_out': False, 'interrupted': False}
    with artifact('events.jsonl').open('w') as stdout, artifact('stderr.log').open('w') as stderr:
        try:
            env = os.environ.copy()
            env['ENABLE_TOOL_SEARCH'] = 'true'
            proc = subprocess.Popen(argv, cwd=checkout, env=env, stdin=subprocess.PIPE,
                                    stdout=stdout, stderr=stderr, start_new_session=True)
            state.update(pid=proc.pid, running=True)
            dump(artifact('process.json'), state)
            proc.communicate(input=prompt.encode(), timeout=timeout)
        except subprocess.TimeoutExpired:
            state['timed_out'] = True
        except BaseException:
            state['interrupted'] = True
            raise
        finally:
            try:
                if proc is not None:
                    (cleanup or stop_process)(proc)
            finally:
                if proc is not None:
                    state.update(running=proc.poll() is None, exit_code=proc.poll())
                dump(artifact('process.json'), state)
    return state


def launch_args(cli, bundle, session, max_turns, profile, schema, system_file, settings=None):
    argv = [cli, '--print', '--model', profile['model'], '--effort', profile['effort'],
            '--session-id', session, '--output-format', 'stream-json',
            '--json-schema', json.dumps(schema), '--verbose', '--permission-mode', 'dontAsk',
            '--setting-sources', '']
    if settings is not None:
        argv += ['--settings', json.dumps(settings)]
    return argv + ['--disable-slash-commands', '--tools', 'default', '--add-dir', str(bundle),
                   '--append-system-prompt-file', str(bundle / system_file),
                   '--max-turns', str(max_turns), '--allowedTools', *profile['allowed_tools'],
                   '--disallowedTools', 'Agent']
