"""Exercise both real entrypoints with a local fake CLI, never a paid model."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import claude_runner as runner

SCRIPTS = Path(__file__).resolve().parent
INCOMPATIBLE = '''import os, runpy, sys
if hasattr(os, 'waitid'):
    del os.waitid
sys.executable = sys.argv[1]
sys.argv = sys.argv[2:]
sys.path.insert(0, os.path.dirname(sys.argv[0]))
runpy.run_path(sys.argv[0], run_name='__main__')
'''
FAKE_CLAUDE = '''import json, os, re, sys
from pathlib import Path
root = Path(os.environ['FIXTURE_ROOT'])
with (root / 'calls.jsonl').open('a') as calls:
    calls.write(json.dumps({'args': sys.argv[1:], 'cwd': os.getcwd(),
                            'sentinel': os.environ.get('FIXTURE_SENTINEL'),
                            'runtime_marker': os.environ.get('_CODEX_CLAUDE_RUNTIME_ATTEMPTED')}) + '\\n')
if sys.argv[1:] == ['auth', 'status']:
    print(json.dumps({'loggedIn': True, 'configDirectory': str(root / 'config')}))
    sys.exit(0)
def value(flag):
    return sys.argv[sys.argv.index(flag) + 1]
session = value('--session-id')
project = root / 'config' / 'projects' / re.sub(r'[^a-zA-Z0-9]', '-', os.getcwd())
project.mkdir(parents=True, exist_ok=True)
(project / (session + '.jsonl')).write_text('{}\\n')
report = json.loads((root / 'report.json').read_text())
print(json.dumps({'type': 'result', 'is_error': False, 'modelUsage': {value('--model'): {}},
                  'structured_output': report, 'result': 'Fixture complete'}))
'''


class EntrypointRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.checkout = self.root / 'checkout'
        self.checkout.mkdir()
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        cli = self.bin / 'claude'
        cli.write_text('#!' + sys.executable + '\n' + FAKE_CLAUDE)
        cli.chmod(0o755)
        self.env = os.environ.copy()
        self.env.update(PATH=str(self.bin) + os.pathsep + self.env['PATH'],
                        FIXTURE_ROOT=str(self.root), FIXTURE_SENTINEL='unchanged',
                        PYTHONDONTWRITEBYTECODE='1', CODEX_HOME=str(self.root / 'empty-guides'))
        self.deadline = (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat()

    def args(self, role):
        self.output = self.root / ('bundle-' + role)
        if role == 'delegate':
            task = self.root / 'task.json'
            runner.dump(task, {'objective': 'Fixture task', 'scope': 'Read checkout',
                               'expected_result': 'Fixture report', 'constraints': [],
                               'approvals': [], 'sources': [], 'verification': [], 'owned_paths': []})
            runner.dump(self.root / 'report.json', {'summary': 'Complete', 'complete': True,
                                                   'changes': [], 'verification': [], 'gaps': []})
            return ['--assignment', str(task), '--checkout', str(self.checkout),
                    '--output', str(self.output), '--finish-by', self.deadline, '--max-turns', '7']
        self.git('init', '-q', '-b', 'main')
        self.git('-c', 'user.name=Developer', '-c', 'user.email=developer@example.invalid',
                 'commit', '-q', '--allow-empty', '-m', 'Fixture')
        head = self.git('rev-parse', 'HEAD')
        self.output.mkdir()
        common = (Path(self.env.get('AGENT_LAUNCH_ROOT', SCRIPTS.parents[2])).expanduser().resolve()
                  / 'scripts/agent-launch.md')
        (self.output / 'guidance.md').write_text('Fixture guidance\n\n## ' + str(common) + '\n\n'
                                                + common.read_text())
        profile = runner.execution_profile()
        profile['attribution'] = 'Reviewed by ' + profile['label'] + ' ' + profile['effort'] + '.'
        runner.dump(self.output / 'manifest.json', {
            'bundle_format': 3, 'checkout': str(self.checkout), 'head': head,
            'risk_report': {'rating': 'Low', 'body': 'Fixture', 'head': head, 'base': head, 'merge_base': head},
            'raw_evidence': [], 'guidance': [str(common)],
            'guidance_sha256': runner.digest(self.output / 'guidance.md'),
            'reviewer': profile})
        report = {key: 'Fixture' for key in ('correctness', 'approach', 'summary', 'validation')}
        report.update(risk='Low', reviewer_attribution=profile['attribution'], findings=[], gaps=[],
                      risk_discrepancies=[], prior_findings=[], open_questions=[],
                      coverage={'scope_complete': True, 'inspected_sources': [], 'interfaces': [],
                                'deployment': [], 'discussion': 'Fixture', 'linear': 'Fixture'})
        runner.dump(self.root / 'report.json', report)
        return ['run', '--bundle', str(self.output), '--finish-by', self.deadline, '--max-turns', '7']

    def git(self, *args):
        return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null',
                                        '-c', 'commit.gpgsign=false', '-C', str(self.checkout),
                                        *args], text=True, stderr=subprocess.DEVNULL).strip()

    def launch(self, role, missing=False, incompatible=True):
        entry = SCRIPTS / ('claude_' + role + '.py')
        args = [str(entry), *self.args(role)]
        if missing:
            # Every installed Python sees the same absent capability, including probes.
            (self.root / 'sitecustomize.py').write_text(
                "import os\nif hasattr(os, 'waitid'):\n    del os.waitid\n")
            self.env['PYTHONPATH'] = str(self.root)
        if incompatible and not missing:
            # Simulate macOS Python 3.12: WNOWAIT exists, but waitid does not.
            command = [sys.executable, '-c', INCOMPATIBLE, str(self.bin / 'incompatible-python'), *args]
        else:
            command = [sys.executable, *args]
        return subprocess.run(command, env=self.env, cwd=self.checkout, capture_output=True,
                              text=True, timeout=45)

    def assert_complete(self, result, role):
        self.assertEqual(result.returncode, 0, result.stderr)
        metrics = runner.load(self.output / 'metrics.json')
        self.assertTrue(metrics['execution_complete'])
        self.assertTrue(metrics['report_valid'])
        self.assertTrue(metrics['transcript_persisted'])
        self.assertFalse(runner.load(self.output / 'process.json')['running'])
        deadline_file = 'manifest.json' if role == 'delegate' else 'assignment.json'
        self.assertEqual(runner.load(self.output / deadline_file)['finish_by'], self.deadline)
        calls = [json.loads(line) for line in (self.root / 'calls.jsonl').read_text().splitlines()]
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]['args'], ['auth', 'status'])
        self.assertEqual(calls[1]['args'][calls[1]['args'].index('--max-turns') + 1], '7')
        for call in calls:
            self.assertEqual(call['cwd'], str(self.checkout))
            self.assertEqual(call['sentinel'], 'unchanged')
            self.assertIsNone(call['runtime_marker'])

    def test_both_entrypoints_handoff_from_missing_waitid_and_finish(self):
        for role in ('delegate', 'review'):
            with self.subTest(role=role):
                # Each role needs its own clean fixture and unique output bundle.
                case = EntrypointRuntimeTests()
                case.setUp()
                try:
                    result = case.launch(role)
                    case.assert_complete(result, role)
                    self.assertIn('using compatible Python', result.stderr)
                finally:
                    case.doCleanups()

    def test_both_entrypoints_run_from_the_actual_entry_interpreter(self):
        for role in ('delegate', 'review'):
            with self.subTest(role=role):
                case = EntrypointRuntimeTests()
                case.setUp()
                try:
                    result = case.launch(role, incompatible=False)
                    case.assert_complete(result, role)
                    if not hasattr(os, 'waitid'):
                        self.assertIn('using compatible Python', result.stderr)
                    else:
                        self.assertNotIn('using compatible Python', result.stderr)
                finally:
                    case.doCleanups()

    def test_both_entrypoints_fail_before_auth_when_no_runtime_is_compatible(self):
        for role in ('delegate', 'review'):
            with self.subTest(role=role):
                result = self.launch(role, missing=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('No compatible installed runtime', result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse((self.root / 'calls.jsonl').exists())
                self.assertFalse((self.output / 'launch.json').exists())

    def test_runtime_recheck_failure_cannot_loop(self):
        self.env['_CODEX_CLAUDE_RUNTIME_ATTEMPTED'] = '1'
        result = self.launch('delegate', missing=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('using compatible Python', result.stderr)
        self.assertFalse((self.root / 'calls.jsonl').exists())


if __name__ == '__main__':
    unittest.main()
