#!/usr/bin/env python3
"""Prepare full review evidence and run one owned Claude session. Never publishes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
import tomllib
import uuid

AGENTS = Path(__file__).resolve().parents[1]
PROFILE = Path(__file__).with_name('claude-review.toml')
REPORT_FIELDS = {'correctness', 'approach', 'risk', 'summary', 'findings', 'coverage',
                 'gaps', 'validation', 'reviewer_attribution'}


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reviewer_profile():
    profile = tomllib.loads(PROFILE.read_text())
    profile['attribution'] = f"Reviewed by {profile['label']} {profile['effort']}."
    return profile


def validate_evidence(value):
    """Check visible errors/truncation without transforming any source content."""
    pages = {}

    def walk(item, route=()):
        if isinstance(item, list):
            for child in item:
                walk(child, route)
        elif isinstance(item, dict):
            if item.get('errors') or ('documentation_url' in item and 'message' in item):
                raise ValueError('API error in evidence; retrieve a successful response')
            if item.get('id') is not None:
                route += (str(item['id']),)
            if 'pageInfo' in item:
                info = item['pageInfo']
                if not isinstance(info, dict) or not isinstance(info.get('hasNextPage'), bool):
                    raise ValueError('Invalid pagination metadata')
                pages.setdefault(route, []).append(info)
            for key, child in item.items():
                if key != 'pageInfo' and isinstance(child, (dict, list)):
                    walk(child, route + (key,))

    walk(value)
    if any(sequence[-1]['hasNextPage'] for sequence in pages.values()):
        raise ValueError('Evidence connection not fully paginated')


def git(checkout, *args):
    return subprocess.check_output(['git', '-C', str(checkout), *args], text=True).strip()


def verify_checkout(checkout, head):
    if git(checkout, 'rev-parse', 'HEAD') != head or git(checkout, 'status', '--porcelain'):
        raise ValueError('Review checkout is not clean at the pinned head')


def instruction_file(directory):
    for name in ('AGENTS.override.md', 'AGENTS.md'):
        path = directory / name
        if path.is_file() and path.read_text().strip():
            return path
    return None


def collect_guides(checkout, changed_paths, additional=(), codex_home=None):
    home = Path(codex_home or os.environ.get('CODEX_HOME') or Path.home() / '.codex')
    guides = [instruction_file(home)]
    directories = {checkout}
    for name in changed_paths:
        parent = (checkout / name).parent
        while parent == checkout or checkout in parent.parents:
            directories.add(parent)
            if parent == checkout:
                break
            parent = parent.parent
    guides.extend(instruction_file(path) for path in sorted(directories, key=lambda path: (len(path.parts), str(path))))
    testing = checkout / 'AGENTS-TESTING.md'
    if testing.is_file():
        guides.append(testing)
    for name in additional:
        path = Path(name).expanduser().resolve()
        if not path.is_file():
            raise ValueError('Additional guidance file is unavailable: ' + str(path))
        if path.name in ('AGENTS.md', 'AGENTS.override.md'):
            path = instruction_file(path.parent)
        guides.append(path)
    return list(dict.fromkeys(path.resolve() for path in guides if path is not None))


def prepare(args):
    spec = load(args.spec)
    for field in ('repo', 'number', 'head', 'base', 'merge_base', 'base_ref'):
        if not spec.get(field):
            raise ValueError('Missing review specification field: ' + field)
    if not spec.get('evidence'):
        raise ValueError('Full saved GitHub evidence is required')
    checkout = Path(args.checkout).resolve()
    output = Path(args.output).resolve()
    if output == checkout or checkout in output.parents:
        raise ValueError('Evidence bundle must be outside the review checkout')
    verify_checkout(checkout, spec['head'])
    if git(checkout, 'merge-base', spec['base'], spec['head']) != spec['merge_base']:
        raise ValueError('Pinned merge-base does not match repository ancestry')
    # Validate every input before creating output. Filenames cannot collide or escape raw/.
    evidence = []
    for name, source in spec['evidence'].items():
        if Path(name).name != name or name in ('', '.', '..'):
            raise ValueError('Evidence names must be unique plain filenames')
        source = Path(source).expanduser().resolve()
        if source.suffix == '.json':
            validate_evidence(load(source))
        evidence.append((name, source))
    paths = subprocess.check_output(['git', '-C', str(checkout), 'diff', '--name-only', '-z',
                                     spec['merge_base'], spec['head'], '--']).decode().split('\0')
    paths = [path for path in paths if path]
    guides = collect_guides(checkout, paths, spec.get('guidance', []))
    output.mkdir(parents=True, exist_ok=False)
    rawdir = output / 'raw'
    rawdir.mkdir()
    inventory = []
    for name, source in evidence:
        target = rawdir / name
        shutil.copyfile(source, target)
        inventory.append({'file': str(target.relative_to(output)), 'sha256': digest(target)})
    (output / 'diff.patch').write_bytes(subprocess.check_output(
        ['git', '-C', str(checkout), 'diff', spec['merge_base'], spec['head'], '--']))
    (output / 'guidance.md').write_text('\n\n'.join('## ' + str(path) + '\n\n' + path.read_text() for path in guides))
    spec.pop('evidence')
    spec.update({'bundle_format': 2, 'checkout': str(checkout), 'changed_paths': paths,
                 'guidance': [str(path) for path in guides], 'raw_evidence': inventory,
                 'guidance_sha256': digest(output / 'guidance.md'), 'reviewer': reviewer_profile()})
    dump(output / 'manifest.json', spec)
    print(output)


def launch_args(bundle, session, max_turns, profile):
    settings = {'allowedMcpServers': [{'serverUrl': 'https://mcp.linear.app/mcp'}]}
    return [shutil.which('claude') or str(Path.home() / '.local/bin/claude'), '--print',
            '--model', profile['model'], '--effort', profile['effort'], '--session-id', session,
            '--output-format', 'stream-json', '--verbose', '--permission-mode', 'dontAsk',
            '--setting-sources', '', '--settings', json.dumps(settings), '--disable-slash-commands',
            '--tools', 'default', '--add-dir', str(bundle), '--append-system-prompt-file',
            str(bundle / 'review-system.md'), '--max-turns', str(max_turns),
            '--allowedTools', *profile['allowed_tools'], '--disallowedTools', 'Agent']


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
        raise ValueError('Absolute review finish-by has passed')
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


def run_process(argv, checkout, prompt, timeout, artifact, session):
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
                    stop_process(proc)
            finally:
                if proc is not None:
                    state.update(running=proc.poll() is None, exit_code=proc.poll())
                dump(artifact('process.json'), state)
    return state


def run(args):
    bundle = Path(args.bundle).resolve()
    manifest = load(bundle / 'manifest.json')
    if manifest.get('bundle_format') != 2:
        raise ValueError('Reprepare this bundle with the current helper before running it')
    finish_by = args.finish_by or manifest.get('finish_by')
    bounded_timeout(args.timeout, finish_by)
    if args.max_turns <= 0:
        raise ValueError('max-turns must be positive')
    checkout = Path(manifest['checkout'])
    verify_checkout(checkout, manifest['head'])
    for item in manifest['raw_evidence']:
        if digest(bundle / item['file']) != item['sha256']:
            raise ValueError('Saved review evidence changed after preparation')
    if digest(bundle / 'guidance.md') != manifest['guidance_sha256']:
        raise ValueError('Saved guidance changed after preparation')
    profile = manifest['reviewer']
    suffix = ''
    if args.resume:
        argv = load(bundle / 'launch.json')
        selector = argv.index('--session-id')
        session = argv[selector + 1]
        argv[selector] = '--resume'
        suffix = '-continuation-' + str(len(list(bundle.glob('process-continuation-*.json'))) + 1)
        if not args.prompt_file:
            raise ValueError('Continuation requires a focused --prompt-file')
    else:
        (bundle / 'review-system.md').write_text(
            (AGENTS / 'context.md').read_text() + '\n\n' + (AGENTS / 'pr-review.md').read_text())
        session = str(uuid.uuid4())
        argv = launch_args(bundle, session, args.max_turns, profile)

    def artifact(name):
        path = Path(name)
        return bundle / (path.stem + suffix + path.suffix)

    timeout = bounded_timeout(args.timeout, finish_by)
    prompt = ('Review this pinned snapshot independently. Start with manifest.json and diff.patch. '
              'Select applicable instructions and source context from guidance.md and the saved evidence; '
              'follow references and gather more context when needed. The bundle is a starting point, '
              'not an investigation boundary. Complete the coverage required by the shared review contract. Bundle: ' + str(bundle)
              + '. Reviewer attribution: ' + profile['attribution'] + '\n'
              + 'The assignment is analysis-only: no publication, source edits, dependency installs, '
              'test runs, delegation, or external mutations. Tool access is trusted; it does not expand this task.\n'
              + 'First verify live Linear access with ToolSearch: read linked issues and relevant comment pages, '
              + 'or verify get_user(me) when unlinked without reading unrelated tickets. '
              + 'Missing required access remains Incomplete.\n'
              + 'Use the shared review standards. Return one JSON object with these fields: '
              + ', '.join(sorted(REPORT_FIELDS)) + ', prior_findings, open_questions. '
              + 'Findings include priority, path, line, side, scenario, consequence, evidence, and correction. '
              + 'Coverage identifies inspected source/guidance, discussion, and actual Linear reads.\n')
    if manifest.get('benchmark'):
        prompt += ('Blind historical benchmark: use the saved GitHub evidence; do not fetch current '
                   'GitHub discussion or previous review reports. Disclose live Linear temporal differences.\n')
    if args.resume:
        prompt += '\nFocused continuation:\n' + Path(args.prompt_file).read_text()
    prompt += f'\nTime budget: {timeout:.0f} seconds.'
    if finish_by:
        prompt += '\nAbsolute finish-by: ' + finish_by
    dump(artifact('launch.json'), argv)
    artifact('prompt.txt').write_text(prompt)
    started = time.monotonic()
    state = run_process(argv, checkout, prompt, bounded_timeout(timeout, finish_by), artifact, session)
    events = []
    for line in artifact('events.jsonl').read_text().splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue  # Partial final output on cancellation is diagnostic, never sign-off.
    result = next((item for item in reversed(events) if item.get('type') == 'result'), {})
    complete = (state.get('exit_code') == 0 and not state['timed_out']
                and not result.get('is_error', True) and profile['model'] in result.get('modelUsage', {}))
    text = result.get('result', '')
    report = None
    try:
        report = json.loads(re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip()))
    except ValueError:
        pass
    report_valid = (isinstance(report, dict) and REPORT_FIELDS <= report.keys()
                    and isinstance(report.get('findings'), list)
                    and report.get('reviewer_attribution') == profile['attribution'])
    checkout_matches = (git(checkout, 'rev-parse', 'HEAD') == manifest['head']
                        and not git(checkout, 'status', '--porcelain'))
    metrics = {'session': session, 'model': profile['model'], 'effort': profile['effort'],
               'execution_complete': complete, 'report_valid': report_valid,
               'coverage_verification': 'Publisher must verify actual source coverage before sign-off',
               'elapsed_seconds': round(time.monotonic() - started, 2), 'turns': result.get('num_turns'),
               'usage': result.get('usage', {}), 'model_usage': result.get('modelUsage', {}),
               'permission_denials': result.get('permission_denials', []), 'checkout_matches': checkout_matches}
    dump(artifact('result.json'), result)
    dump(artifact('metrics.json'), metrics)
    artifact('report.txt').write_text(text)
    if report is not None:
        dump(artifact('report.json'), report)
    print(json.dumps(metrics))
    if not complete or not report_valid or not checkout_matches:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('--spec', required=True)
    prep.add_argument('--checkout', required=True)
    prep.add_argument('--output', required=True)
    launch = sub.add_parser('run')
    launch.add_argument('--bundle', required=True)
    launch.add_argument('--timeout', type=int, default=900)
    launch.add_argument('--max-turns', type=int, default=80)
    launch.add_argument('--resume', action='store_true')
    launch.add_argument('--prompt-file')
    launch.add_argument('--finish-by', help='ISO 8601 deadline with timezone; overrides manifest finish-by')
    args = parser.parse_args()

    def cancel(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, cancel)
    try:
        (prepare if args.command == 'prepare' else run)(args)
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == '__main__':
    main()
