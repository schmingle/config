"""Claude CLI profile, authentication, persistence, and output identity checks."""
import json
import os
import shutil

from agent_launcher import ROOT, shared

PROVIDER = 'claude'


def execution(settings):
    profile = shared.execution_profile(settings.get("name"))
    return {**profile, 'attribution': 'Reviewed by ' + profile['label'] + ' ' + profile['effort'] + '.'}


def executable():
    cli = os.environ.get('CLAUDE_BIN') or shutil.which('claude')
    if not cli:
        raise ValueError('Claude CLI unavailable; restore the installed CLI without substituting a model')
    return cli


def instructions(settings, role, rules):
    # Claude counterparts contain actual executor instructions, not Codex orchestration.
    text = (ROOT / '.claude/agents' / (role + '.md')).read_text()
    parts = text.split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError('Claude role requires frontmatter and an executor body')
    fields = dict(line.split(': ', 1) for line in parts[1].splitlines() if ': ' in line)
    profile = shared.execution_profile(settings.get("name"))
    if fields.get('name') != role or fields.get('model') != profile['model'] or fields.get('effort') != profile['effort']:
        raise ValueError('Claude counterpart does not match its canonical execution profile')
    return parts[2].strip() + '\n' + rules


def launch_args(cli, checkout, output, session, max_turns, profile, sandbox, before, system, schema):
    return shared.launch_args(cli, output, session, max_turns, profile, schema, 'task-system.md')


def preflight(cli, checkout, output, deadline):
    # The shared provider helper authenticates and checks the real writable session store.
    storage = shared.persistence_preflight(cli, checkout, timeout=shared.bounded_timeout(15, deadline))
    shared.dump(output / 'persistence.json', storage)
    shared.bounded_timeout(15, deadline)
    return storage


def collect(output, storage, session, profile):
    events = []
    for line in (output / 'events.jsonl').read_text().splitlines():
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
        except ValueError:
            continue
    result = next((event for event in reversed(events) if event.get('type') == 'result'), {})
    transcript = shared.saved_transcript(storage, session)
    storage.update(session=session, transcript=transcript, transcript_persisted=bool(transcript))
    shared.dump(output / 'persistence.json', storage)
    return result, result.get('structured_output'), {
        'provider_verified': (not result.get('is_error', True)
                              and profile['model'] in result.get('modelUsage', {}) and bool(transcript)),
        'transcript_persisted': bool(transcript), 'model_usage': result.get('modelUsage', {}),
        'usage': result.get('usage', {}), 'permission_denials': result.get('permission_denials', [])}
