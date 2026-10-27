#!/usr/bin/env python3
"""Prepare full review evidence and run one owned Claude session. Never publishes."""
if __name__ == '__main__':
    from claude_runtime import ensure_runtime
    ensure_runtime()

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
import uuid

import claude_runner
from claude_runner import (assignment_deadline, bounded_timeout, digest, dump,
                           ensure_settled, git, load, persistence_preflight,
                           saved_transcript, stop_process)

AGENTS = Path(__file__).resolve().parents[1]
COMMON_GUIDE = (Path(os.environ.get('AGENT_LAUNCH_ROOT', AGENTS.parents[1])).expanduser().resolve()
                / 'scripts/agent-launch.md')
REPORT_FIELDS = {'correctness', 'approach', 'risk', 'summary', 'findings', 'coverage',
                 'gaps', 'validation', 'reviewer_attribution', 'risk_discrepancies', 'prior_findings', 'open_questions'}


def reviewer_profile():
    profile = claude_runner.execution_profile("pr-review-high")
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


def validate_risk_report(report):
    """Require a complete assessment without demanding publication or rerating it."""
    fields = ('body', 'head', 'base', 'merge_base')
    if (not isinstance(report, dict)
            or report.get('rating') not in ('Low', 'Medium low', 'Medium', 'Medium high', 'High')
            or any(not isinstance(report.get(field), str) or not report[field].strip() for field in fields)
            or ('url' in report and (not isinstance(report['url'], str) or not report['url'].strip()))):
        raise ValueError('A complete risk_report with rating, body, and assessed commits is required')


def prepare(args):
    spec = load(args.spec)
    for field in ('repo', 'number', 'head', 'base', 'merge_base', 'base_ref'):
        if not spec.get(field):
            raise ValueError('Missing review specification field: ' + field)
    validate_risk_report(spec.get('risk_report'))
    if not spec.get('evidence'):
        raise ValueError('Full saved GitHub evidence is required')
    checkout = Path(args.checkout).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    config_repo = Path(__file__).resolve().parents[3]
    if any(output == root or root in output.parents for root in (checkout, config_repo)):
        raise ValueError('Evidence bundle must be outside the review checkout and public configuration repository')
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
    # The embedded Claude guide delegates common rules here; preserve their body
    # in the hashed snapshot even when the caller supplies additional guidance.
    guides = collect_guides(checkout, paths, [COMMON_GUIDE, *spec.get('guidance', [])])
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
    spec.update({'bundle_format': 3, 'checkout': str(checkout), 'changed_paths': paths,
                 'guidance': [str(path) for path in guides], 'raw_evidence': inventory,
                 'guidance_sha256': digest(output / 'guidance.md'), 'reviewer': reviewer_profile()})
    dump(output / 'manifest.json', spec)
    print(output)


def report_schema():
    """Constrain transport shape; the publisher still verifies review coverage."""
    text = {'type': 'string'}
    strings = {'type': 'array', 'items': text}
    finding = {'type': 'object', 'properties': {
        'priority': {'type': 'string', 'enum': ['P0', 'P1', 'P2', 'P3']},
        'path': text, 'line': {'type': 'integer', 'minimum': 1},
        'side': {'type': 'string', 'enum': ['LEFT', 'RIGHT']},
        **{key: text for key in ('scenario', 'consequence', 'evidence', 'correction')}},
        'required': ['priority', 'path', 'line', 'side', 'scenario', 'consequence', 'evidence', 'correction']}
    coverage = {'scope_complete': {'type': 'boolean'}, 'inspected_sources': strings,
                'interfaces': strings, 'deployment': strings, 'discussion': text, 'linear': text}
    properties = {key: text for key in ('correctness', 'approach', 'risk', 'summary',
                                       'validation', 'reviewer_attribution')}
    properties.update(findings={'type': 'array', 'items': finding},
                      coverage={'type': 'object', 'properties': coverage, 'required': list(coverage)},
                      gaps=strings, risk_discrepancies=strings, prior_findings=strings, open_questions=strings)
    return {'type': 'object', 'properties': properties, 'required': sorted(REPORT_FIELDS)}


def launch_args(bundle, session, max_turns, profile):
    settings = {'allowedMcpServers': [{'serverUrl': 'https://mcp.linear.app/mcp'}]}
    cli = shutil.which('claude') or str(Path.home() / '.local/bin/claude')
    return claude_runner.launch_args(cli, bundle, session, max_turns, profile,
                                     report_schema(), 'review-system.md', settings)


def run_process(argv, checkout, prompt, timeout, artifact, session):
    return claude_runner.run_process(argv, checkout, prompt, timeout, artifact, session,
                                     cleanup=stop_process)


def run(args):
    if os.environ.get('_SHARED_AGENT_EXECUTOR_ACTIVE'):
        raise ValueError('Nested agent launch refused: execute the assigned review directly')
    bundle = Path(args.bundle).resolve()
    manifest = load(bundle / 'manifest.json')
    if manifest.get('bundle_format') != 3:
        raise ValueError('Reprepare this bundle with the current helper before running it')
    if not (bundle / 'launch.json').exists() and str(COMMON_GUIDE) not in manifest.get('guidance', []):
        raise ValueError('Unstarted review bundle lacks the shared execution contract; reprepare it '
                         'before launch without extending the original assignment deadline')
    validate_risk_report(manifest.get('risk_report'))
    requested_deadline = args.finish_by or (manifest.get('finish_by')
                                            if not (bundle / 'assignment.json').exists() else None)
    finish_by = assignment_deadline(bundle, requested_deadline, args.timeout)
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
    ensure_settled(bundle)
    replace = getattr(args, 'replace_failed', False)
    reason = getattr(args, 'recovery_reason', None)
    if args.resume and replace:
        raise ValueError('Choose continuation or replacement, not both')
    if bool(reason) != bool(replace):
        raise ValueError('Replacement requires --replace-failed and --recovery-reason')
    initial = bundle / 'launch.json'
    replacement = bundle / 'launch-replacement.json'
    if initial.exists() and not args.resume and not replace:
        raise ValueError('Initial session already launched; resume it or use the single bounded replacement')
    if (args.resume or replace) and not initial.exists():
        raise ValueError('No original review session exists')
    if replace and replacement.exists():
        raise ValueError('The single replacement session has already been used')
    if args.resume and not args.prompt_file:
        raise ValueError('Continuation requires a focused --prompt-file')
    original_argv = load(replacement if replacement.exists() else initial) if initial.exists() else None
    if original_argv and any(original_argv[original_argv.index(flag) + 1] != profile[field]
                             for flag, field in (('--model', 'model'), ('--effort', 'effort'))):
        raise ValueError('Review execution profile changed after initial launch')
    cli = original_argv[0] if original_argv else shutil.which('claude') or str(Path.home() / '.local/bin/claude')
    storage = persistence_preflight(cli, checkout)
    previous_storage = bundle / 'persistence.json'
    if previous_storage.exists() and load(previous_storage)['config_directory'] != storage['config_directory']:
        raise ValueError('Claude config directory changed; preserve the original login and session storage')
    suffix = ''
    if args.resume:
        argv = list(original_argv)
        selector = argv.index('--session-id')
        session = argv[selector + 1]
        transcript = saved_transcript(storage, session)
        if not transcript:
            raise ValueError('Persisted Claude session is missing; do not spend tokens on a blind resume')
        argv[selector:selector + 2] = ['--resume', transcript]
        suffix = '-continuation-' + str(len(list(bundle.glob('process-continuation-*.json'))) + 1)
    else:
        if replace:
            prior_session = original_argv[original_argv.index('--session-id') + 1]
            metrics_paths = sorted(bundle.glob('metrics*.json'), key=lambda path: path.stat().st_mtime_ns)
            prior = load(metrics_paths[-1]) if metrics_paths else {}
            justified = ((reason == 'missing-session' and not saved_transcript(storage, prior_session))
                         or (reason in ('invalid-output', 'cli-error') and prior.get('failure_kind') == reason))
            if not (bundle / 'process.json').exists() or not justified:
                raise ValueError('Replacement requires evidence of the specified infrastructure failure')
            suffix = '-replacement'
        session = str(uuid.uuid4())
        if replace:
            argv = list(original_argv)
            argv[argv.index('--session-id') + 1] = session
        else:
            (bundle / 'review-system.md').write_text(
                (AGENTS / 'context.md').read_text() + '\n\n'
                + (AGENTS / 'claude.md').read_text() + '\n\n' + (AGENTS / 'pr-review.md').read_text())
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
              + 'Continue accessible required review work until coverage is complete, a concrete blocker '
              + 'prevents further progress, or the measured deadline is reached. Diff size, anticipated time '
              + 'pressure, finding a defect, or a valid partial report are not reasons to stop early. '
              + 'Check the actual clock; reserve needed reporting/cleanup time. Continue independent areas '
              + 'when another area is blocked. For Incomplete, include the stop reason, checked time and '
              + 'deadline, completed coverage, exact remaining areas, and blocker or next action in validation/gaps.\n'
              + 'Use manifest.risk_report unchanged: it is the coordinator-supplied risk assessment, '
              + 'not a request to reassess or publish it separately. '
              + 'Return risk as its exact rating. Cite a source URL only when one already exists. '
              + 'Reuse it even when its assessed commits differ from this review. '
              + 'Return concrete contradictions as a risk_discrepancies list (empty if none); '
              + 'a material unresolved contradiction prevents whole-PR sign-off. Do not silently rerate.\n'
              + 'Use the shared review standards. Return one JSON object with these fields: '
              + ', '.join(sorted(REPORT_FIELDS)) + ', prior_findings, open_questions. '
              + 'Findings include priority, path, line, side, scenario, consequence, evidence, and correction. '
              + 'Coverage must identify actual inspected sources, interfaces/retained implementations, deployment '
              + 'boundaries, discussion, and actual Linear reads. Set scope_complete false for material missing '
              + 'coverage and explain the gaps; searches for removed names alone do not prove surviving behavior. '
              + 'Use string verdict/summaries for correctness and approach, string arrays for gaps, '
              + 'prior_findings, open_questions, and risk_discrepancies, and the supplied structured-output schema.\n')
    if manifest.get('benchmark'):
        prompt += ('Blind historical benchmark: use the saved GitHub evidence; do not fetch current '
                   'GitHub discussion or previous review reports. Disclose live Linear temporal differences.\n')
    if replace:
        prompt += '\nThis is the single replacement for a settled infrastructure failure: ' + reason + '. Establish full coverage independently; a partial prior report is not sign-off.\n'
    if args.resume:
        prompt += '\nFocused continuation:\n' + Path(args.prompt_file).read_text()
    prompt += f'\nTime budget: {timeout:.0f} seconds.'
    if finish_by:
        prompt += '\nAbsolute finish-by: ' + finish_by
    dump(artifact('preflight.json'), storage)
    # Exclusive attempt creation also prevents two racing callers from launching it.
    with artifact('launch.json').open('x') as launch_file:
        json.dump(argv, launch_file, indent=2)
        launch_file.write('\n')
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
    report = result.get('structured_output')
    schema = report_schema()
    report_valid = (isinstance(report, dict) and REPORT_FIELDS <= report.keys()
                    and all(isinstance(report.get(key), str) for key, spec in schema['properties'].items()
                            if spec['type'] == 'string')
                    and all(isinstance(report.get(key), list) for key, spec in schema['properties'].items()
                            if spec['type'] == 'array')
                    and isinstance(report.get('coverage'), dict)
                    and isinstance(report['coverage'].get('scope_complete'), bool)
                    and all(key in report['coverage'] for key in schema['properties']['coverage']['required'])
                    and report.get('risk') == manifest['risk_report']['rating']
                    and report.get('reviewer_attribution') == profile['attribution'])
    transcript = saved_transcript(storage, session)
    storage.update(session=session, transcript=transcript, transcript_persisted=bool(transcript))
    dump(artifact('persistence.json'), storage)
    failure_kind = ('timeout' if state['timed_out'] else
                    'cli-error' if not complete else 'invalid-output' if not report_valid else None)
    checkout_matches = (git(checkout, 'rev-parse', 'HEAD') == manifest['head']
                        and not git(checkout, 'status', '--porcelain'))
    metrics = {'session': session, 'model': profile['model'], 'effort': profile['effort'],
               'execution_complete': complete, 'report_valid': report_valid,
               'failure_kind': failure_kind, 'transcript_persisted': bool(transcript),
               'coverage_complete_claimed': report.get('coverage', {}).get('scope_complete') if report_valid else False,
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
    launch.add_argument('--replace-failed', action='store_true', help='Use the single replacement for a verified infrastructure failure')
    launch.add_argument('--recovery-reason', choices=['missing-session', 'invalid-output', 'cli-error'])
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
