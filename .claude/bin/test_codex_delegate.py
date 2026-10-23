"""Legacy CLI compatibility against a local fake Codex; never a paid model."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('codex_delegate.py')
SHELL = SCRIPT.with_name('codex-delegate.sh')


class LegacyCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.checkout = self.root / 'assigned checkout'
        self.checkout.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.checkout)], check=True)
        self.brief = self.root / 'brief.md'
        self.brief.write_text('Analyze only. Owned paths: []. No external writes.\nLiteral `value` and $(not-a-command).\n')
        cli = self.root / 'fake-codex'
        cli.write_text('#!' + sys.executable + '\n' + '''import json, os, sys
from pathlib import Path
args = sys.argv[1:]
if args in (['--version'], ['login', 'status']):
    sys.exit(0)
Path(os.environ['FIXTURE_RECORD']).write_text(json.dumps({
    'args': args, 'cwd': os.getcwd(), 'prompt': sys.stdin.read()}))
Path(args[args.index('--output-last-message') + 1]).write_text(json.dumps({
    'summary': 'Verified fake report.', 'complete': True, 'changes': [],
    'verification': ['Fixture'], 'gaps': []}))
print(json.dumps({'type': 'turn.completed'}))
''')
        cli.chmod(0o700)
        self.record = self.root / 'record.json'
        self.output = self.root / 'private output'
        self.env = {**os.environ, 'CODEX_BIN': str(cli), 'FIXTURE_RECORD': str(self.record),
                    'PYTHONDONTWRITEBYTECODE': '1'}
        self.env.pop('_SHARED_AGENT_EXECUTOR_ACTIVE', None)

    def launch(self, role='delegate-low', entry=SCRIPT, source=None, extra=()):
        command = [str(entry)] if entry == SHELL else [sys.executable, str(entry)]
        if role is not None:
            command += ['--role', role]
        deadline = (datetime.now(timezone.utc) + timedelta(seconds=60)).isoformat()
        return subprocess.run([*command, '--checkout', str(self.checkout),
                               *(source or ['--brief-file', str(self.brief)]),
                               '--output', str(self.output), '--finish-by', deadline, *extra],
                              env=self.env, capture_output=True, text=True, timeout=30)

    def test_shell_command_preserves_exact_legacy_brief_and_read_only_default(self):
        result = self.launch(entry=SHELL)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Verified fake report.', result.stdout)
        record = json.loads(self.record.read_text())
        self.assertEqual(record['cwd'], str(self.checkout.resolve()))
        self.assertTrue(record['prompt'].endswith(self.brief.read_text()))
        self.assertEqual(record['args'][record['args'].index('--model') + 1], 'gpt-6-luna')
        self.assertIn('model_reasoning_effort="high"', record['args'])
        self.assertEqual(record['args'][record['args'].index('--sandbox') + 1], 'read-only')
        manifest = json.loads((self.output / 'manifest.json').read_text())
        self.assertEqual(manifest['reviewer_attribution'], 'Reviewed by GPT-6 Luna high.')
        self.assertFalse(manifest['process']['running'])
        self.assertEqual((self.output / 'brief.md').read_text(), self.brief.read_text())
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        self.assertEqual(manifest['initial_state'], manifest['final_state'])

    def test_legacy_brief_remains_read_only_for_a_write_capable_role(self):
        result = self.launch(role='pr-resolve')
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.output / 'manifest.json').read_text())
        self.assertEqual(manifest['sandbox'], 'read-only')
        self.assertEqual(json.loads((self.output / 'assignment.json').read_text())['owned_paths'], [])

    def test_legacy_brief_cannot_request_writes(self):
        result = self.launch(role='pr-resolve', extra=('--sandbox', 'workspace-write'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Legacy briefs support read-only', result.stderr)
        self.assertFalse(self.record.exists())
        self.assertFalse(self.output.exists())

    def test_structured_assignment_preserves_role_default_sandbox(self):
        task = self.root / 'assignment.json'
        task.write_text(json.dumps({'objective': 'Edit the assigned source', 'scope': 'source.txt',
                                    'expected_result': 'Verified source', 'owned_paths': ['source.txt'],
                                    'constraints': [], 'approvals': [], 'sources': [], 'verification': []}))
        result = self.launch(role='pr-resolve', source=['--assignment', str(task)])
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.output / 'manifest.json').read_text())
        self.assertEqual(manifest['sandbox'], 'workspace-write')
        self.assertEqual(json.loads((self.output / 'assignment.json').read_text()), json.loads(task.read_text()))

    def test_explicit_role_is_still_required(self):
        result = self.launch(role=None)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--role', result.stderr)
        self.assertFalse(self.record.exists())
        self.assertFalse(self.output.exists())

    def test_empty_legacy_brief_is_rejected_before_launch(self):
        self.brief.write_text('  \n')
        result = self.launch()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('brief must not be empty', result.stderr)
        self.assertFalse(self.record.exists())
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
