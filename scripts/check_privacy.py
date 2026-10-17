#!/usr/bin/env python3
"""Fail-closed publication checks using only Python's standard library and Git.

Git snapshots, rather than working-tree files, are authoritative for hooks/CI.
This detects mechanical privacy hazards; manual content review remains required.
"""
import argparse
import json
import os
from pathlib import PurePosixPath
import re
import subprocess
import sys

PRIVATE_DIRS = {
    'private', 'writing', 'sessions', 'memories', 'automations', 'worktrees', 'backups',
    'logs', 'cache', 'caches', 'tmp', 'temp', 'shell_snapshots', 'sqlite',
    'archived_sessions', 'benchmark-evidence', 'benchmark_evidence',
}
PRIVATE_FILES = {
    'agents-private.md', 'auth.json', 'history.jsonl', 'history.ndjson',
    'credentials.json', 'credentials', '.ds_store', '.env', '.netrc',
    'cookies.txt', 'cookies.json',
}
TOKENS = re.compile(
    r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|'
    r'sk-(?:proj-|ant-)?[A-Za-z0-9_-]{30,}|(?:AKIA|ASIA)[A-Z0-9]{16}|'
    r'xox[baprs]-[A-Za-z0-9-]{20,}|'
    r'-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----)'
)
CREDENTIAL_URL = re.compile(r'\b[a-z][a-z0-9+.-]*://([^\s/<>:@]+):([^\s/<>@]+)@', re.I)
WEBHOOK = re.compile(r'https://(?:hooks\.slack\.com/(?:services|triggers)/|(?:\w+\.)?discord(?:app)?\.com/api/webhooks/)\S+', re.I)
ASSIGNMENT = re.compile(
    r'''(?ix)^\s*(?:(?:export|const|let|var)\s+)?["']?(?:[\w.-]*[_-])?
    (?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|client[_-]?secret)
    ["']?\s*[:=]\s*(.+?)\s*[,;]?\s*$'''
)
QUERY_TOKEN = re.compile(r'[?&](?:access_token|api_key|token|password)=([^\s&#]+)', re.I)
PERSONAL_PATH = re.compile(r'/' + r'Users' + r'/[^/\s]+/')
PLACEHOLDER = re.compile(
    r'(?ix)(?:\$\{?[A-Z_][A-Z0-9_]*\}?|<[^<>]+>|'
    r'(?:example|placeholder|changeme|redacted|dummy|fake|test)(?:[-_].*)?|'
    r'your[-_].*|(?:none|null|true|false))'
)


class PrivacyError(ValueError):
    pass


def git(*args):
    result = subprocess.run(['git', *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        # Git stderr may include sensitive ref/path content; do not echo it.
        raise PrivacyError('Git snapshot unavailable; fetch missing refs or repair the index, then retry')
    return result.stdout


def placeholder(value):
    return not value or bool(PLACEHOLDER.fullmatch(value))


def inspect_blob(name, mode, payload):
    """Raise without printing content; symlinks are never dereferenced."""
    inspect_text(name, 'Git filename (value omitted)')
    parts = tuple(part.casefold() for part in PurePosixPath(name).parts)
    basename = parts[-1]
    if (basename in PRIVATE_FILES or basename.startswith('.env.') and basename not in {'.env.example', '.env.sample', '.env.template'}
            or any(part in PRIVATE_DIRS for part in parts)
            or '.system' in parts
            or '.codex' in parts and basename == 'config.toml'
            or basename.endswith(('.sqlite', '.sqlite3', '.db', '.db-wal', '.db-shm', '.log', '.bak'))):
        raise PrivacyError(name + ': private/local-only filename')
    if mode not in {'100644', '100755'}:
        raise PrivacyError(name + ': symlink or unsupported Git entry needs explicit review')
    try:
        text = payload.decode('utf-8')
    except UnicodeError:
        raise PrivacyError(name + ': binary content needs explicit review') from None
    if '\0' in text:
        raise PrivacyError(name + ': binary content needs explicit review')
    inspect_text(text, name)


def inspect_text(text, label):
    for number, line in enumerate(text.splitlines(), 1):
        reason = None
        if TOKENS.search(line):
            reason = 'possible credential or private key'
        for match in CREDENTIAL_URL.finditer(line):
            if not placeholder(match[2]):
                reason = 'credential-bearing URL'
        for match in WEBHOOK.finditer(line):
            suffix = re.split(r'/(?:services|triggers|webhooks)/', match[0], maxsplit=1, flags=re.I)[-1]
            if not all(placeholder(part) for part in suffix.split('/')):
                reason = 'possible private webhook URL'
        for match in QUERY_TOKEN.finditer(line):
            if not placeholder(match[1]):
                reason = 'credential-bearing URL parameter'
        assignment = ASSIGNMENT.match(line)
        if assignment:
            value = assignment[1].rstrip(',;').strip()
            quoted_value = re.fullmatch(r"""(["'])(.*?)\1\s*[,;]?\s*(?:(?:#|//).*)?""", value)
            quoted = quoted_value is not None
            literal = quoted_value[2] if quoted else value.split(' #', 1)[0].strip()
            # Bare source expressions/reference names are not literal credentials.
            reference = not quoted and bool(re.fullmatch(r'[A-Z_][A-Z0-9_]*|(?:os\.(?:getenv|environ)|process\.env|env\.|getenv\().*', literal))
            source_expression = not quoted and PurePosixPath(label).suffix in {'.py', '.js', '.ts', '.mjs', '.cjs', '.tsx', '.jsx'}
            if not placeholder(literal) and not reference and not source_expression:
                reason = 'possible literal credential assignment'
        if PERSONAL_PATH.search(line):
            reason = 'personal absolute path'
        if reason:
            raise PrivacyError(f'{label}:{number}: {reason}; value omitted')


def scan_entries(entries, context, seen=None):
    if seen is None:
        seen = set()
    count = 0
    for name, mode, oid in entries:
        key = (name, mode, oid)
        if key in seen:
            continue
        seen.add(key)
        count += 1
        try:
            inspect_blob(name, mode, git('cat-file', 'blob', oid))
        except PrivacyError as error:
            raise PrivacyError(context + ': ' + str(error)) from None
    return count


def index_entries():
    for record in git('ls-files', '--stage', '-z').split(b'\0'):
        if not record:
            continue
        metadata, name = record.split(b'\t', 1)
        mode, oid, stage = metadata.decode('ascii').split()
        if stage != '0':
            raise PrivacyError('Unmerged index; resolve conflicts before publishing')
        yield name.decode('utf-8'), mode, oid


def commit_entries(commit):
    for record in git('ls-tree', '-r', '-z', '--full-tree', commit).split(b'\0'):
        if not record:
            continue
        metadata, name = record.split(b'\t', 1)
        mode, kind, oid = metadata.decode('ascii').split()
        yield name.decode('utf-8'), mode, oid


def valid_oid(value):
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', value):
        raise PrivacyError('Unsupported Git object ID; publication check stopped')
    return value


def zero_oid(value):
    return set(valid_oid(value)) == {'0'}


def inspect_tag_messages(oid):
    # Annotated tags can carry secrets even if their commit is already remote.
    while git('cat-file', '-t', oid).strip() == b'tag':
        tag = git('cat-file', 'tag', oid)
        headers, separator, message = tag.partition(b'\n\n')
        if not separator:
            raise PrivacyError('Unsupported annotated tag; publication check stopped')
        inspect_text(message.decode('utf-8'), 'outgoing tag ' + oid[:12] + ' message')
        target = headers.splitlines()[0].split()
        if len(target) != 2 or target[0] != b'object':
            raise PrivacyError('Unsupported annotated tag target; publication check stopped')
        oid = valid_oid(target[1].decode('ascii'))


def outgoing(local, remote):
    if zero_oid(local):
        return set()  # Deleting a remote ref publishes no objects.
    inspect_tag_messages(local)
    git('rev-parse', '--verify', local + '^{commit}')
    revisions = [local]
    if not zero_oid(remote):
        git('rev-parse', '--verify', remote + '^{commit}')
        revisions.append('^' + remote)
    return set(git('rev-list', *revisions).decode('ascii').splitlines())


def push_commits(stream):
    commits = set()
    for line in stream:
        fields = line.split()
        if len(fields) != 4:
            raise PrivacyError('Unsupported pre-push input; publication check stopped')
        commits.update(outgoing(fields[1], fields[3]))
    return commits


def ci_commits():
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    if not event_path:
        raise PrivacyError('CI event payload is required')
    with open(event_path, encoding='utf-8') as stream:
        event = json.load(stream)
    if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request':
        return outgoing(event['pull_request']['head']['sha'], event['pull_request']['base']['sha'])
    if os.environ.get('GITHUB_EVENT_NAME') == 'push':
        return outgoing(event['after'], event['before'])
    raise PrivacyError('Unsupported CI event; publication check stopped')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--staged', action='store_true', help='scan the complete Git index')
    modes.add_argument('--pre-push', action='store_true', help='read Git ref updates from stdin')
    modes.add_argument('--ci', action='store_true', help='scan outgoing commits in the GitHub event')
    modes.add_argument('--commit-message', metavar='PATH', help='scan the Git-provided commit message file')
    args = parser.parse_args()
    git('rev-parse', '--show-toplevel')
    if args.commit_message:
        with open(args.commit_message, encoding='utf-8') as stream:
            inspect_text(stream.read(), 'commit message')
        print('Privacy check passed: commit message.')
    elif args.staged:
        count = scan_entries(index_entries(), 'staged snapshot')
        print(f'Privacy check passed: {count} staged files.')
    else:
        commits = ci_commits() if args.ci else push_commits(sys.stdin)
        seen = set()
        for commit in sorted(commits):
            inspect_text(git('show', '-s', '--format=%B', commit).decode('utf-8'),
                         'outgoing commit ' + commit[:12] + ' message')
            scan_entries(commit_entries(commit), 'outgoing commit ' + commit[:12], seen)
        print(f'Privacy check passed: {len(commits)} outgoing commits.')


if __name__ == '__main__':
    try:
        main()
    except (PrivacyError, OSError, UnicodeError, KeyError, json.JSONDecodeError) as error:
        # Unexpected file/JSON errors can contain content; keep their details private.
        message = str(error) if isinstance(error, PrivacyError) else 'Required snapshot or CI metadata unavailable'
        raise SystemExit('Privacy check failed: ' + message) from None
