"""Exercise role settings and the foreground handoff without paid model calls."""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest

SCRIPT = Path(__file__).with_name('codex_delegate.py')
ROOT = SCRIPT.resolve().parents[2]
AGENTS = ROOT / '.codex/agents'
spec = importlib.util.spec_from_file_location('codex_delegate', SCRIPT)
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


class RoleSettingsTests(unittest.TestCase):
    def test_every_public_role_has_the_correct_executor(self):
        roles = {path.stem for path in AGENTS.glob('*.toml')}
        counterparts = {path.stem for path in (ROOT / '.claude/agents').glob('*.md')}
        self.assertEqual(roles, counterparts)
        profile = tomllib.loads((AGENTS / 'scripts/claude-review.toml').read_text())
        for role in roles:
            text = (ROOT / '.claude/agents' / (role + '.md')).read_text()
            fields = dict(re.findall(r'^(model|effort): (.+)$', text, re.MULTILINE))
            if role in handoff.NATIVE_ROLES:
                self.assertEqual(fields, {'model': 'haiku', 'effort': 'low'})
                self.assertIn('--role ' + role, text)
                settings = handoff.role_settings(AGENTS, role)
                command = handoff.launch_args('codex', Path('/checkout'), Path('/private-output'), settings, 'read-only')
                self.assertEqual(command[command.index('--model') + 1], settings['model'])
                self.assertIn('model_reasoning_effort=' + json.dumps(settings['model_reasoning_effort']), command)
                instructions = handoff.role_instructions(settings)
                self.assertNotIn('claude_delegate.py', instructions)
                self.assertNotIn('claude_review.py', instructions)
                self.assertIn('Never spawn agents', instructions)
            else:
                self.assertEqual(fields, {'model': profile['model'], 'effort': profile['effort']})

    def test_claude_roles_remain_available_to_the_shared_dispatcher(self):
        for role in ('delegate-xhigh', 'pr-review-high', 'port-to-claude'):
            self.assertEqual(handoff.role_settings(AGENTS, role)['name'], role)

    def test_native_executor_preserves_canonical_guide_paths_and_role(self):
        settings = handoff.role_settings(AGENTS, 'pr-update')
        text = handoff.role_instructions(settings)
        self.assertIn('~/.codex/skills/pr-merge-queue/SKILL.md', text)
        self.assertIn('~/.codex/agents/pr-review.md', text)
        self.assertIn('Never silently ignore P3', text)
        self.assertIn('~/.codex/agents/writer.md', handoff.role_instructions(handoff.role_settings(AGENTS, 'writer')))


class FakeCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.checkout = self.root / 'assigned checkout'
        self.checkout.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.checkout)], check=True)
        self.brief = self.root / 'brief.md'
        self.brief.write_text('Analyze only. Owned paths: []. No external writes.\nLiteral `value` and $(not-a-command).\n')
        self.cli = self.root / 'fake-codex'
        self.cli.write_text('''#!/usr/bin/env python3
import json, os
from pathlib import Path
import subprocess, sys, time
args = sys.argv[1:]
if args == ['--version']:
    print('fake-codex 1')
elif args == ['login', 'status']:
    print('fake authentication')
    sys.exit(int(os.environ.get('FAKE_AUTH_FAILURE', '0')))
else:
    Path(os.environ['FAKE_RECORD']).write_text(json.dumps({'args': args, 'cwd': os.getcwd(), 'prompt': sys.stdin.read()}))
    mode = os.environ.get('FAKE_MODE', '')
    if mode == 'error':
        sys.exit(7)
    if mode == 'timeout':
        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
        Path(os.environ['FAKE_CHILD']).write_text(str(child.pid))
        time.sleep(60)
    if mode != 'missing-report':
        Path(args[args.index('--output-last-message') + 1]).write_text(json.dumps({'summary': 'Verified fake report.', 'complete': True, 'changes': [], 'verification': ['Fixture'], 'gaps': []}))
    print(json.dumps({'type': 'turn.completed'}))
''')
        self.cli.chmod(0o700)
        self.record = self.root / 'record.json'
        self.output = self.root / 'private output'
        self.env = {**os.environ, 'CODEX_BIN': str(self.cli), 'CODEX_HOME': str(ROOT / '.codex'),
                    'PYTHONDONTWRITEBYTECODE': '1', 'FAKE_RECORD': str(self.record),
                    'FAKE_CHILD': str(self.root / 'child.pid')}

    def tearDown(self):
        self.temp.cleanup()

    def run_handoff(self, role='delegate-low', seconds=60, sandbox='read-only', extra=()):
        deadline = (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()
        source = ['--brief-file', str(self.brief)]
        if sandbox == 'workspace-write':
            task = self.root / 'task.json'
            task.write_text(json.dumps({'objective': 'Edit the assigned source', 'scope': 'source.txt',
                                       'expected_result': 'Verified source', 'owned_paths': ['source.txt'],
                                       'constraints': [], 'approvals': [], 'sources': [], 'verification': []}))
            source = ['--assignment', str(task)]
        return subprocess.run([sys.executable, str(SCRIPT), '--role', role,
                               '--checkout', str(self.checkout), *source,
                               '--output', str(self.output), '--finish-by', deadline,
                               '--sandbox', sandbox, *extra], env=self.env, capture_output=True, text=True, timeout=30)

    def test_foreground_report_uses_assigned_checkout_and_exact_brief(self):
        result = self.run_handoff()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Verified fake report.', result.stdout)
        record = json.loads(self.record.read_text())
        self.assertEqual(record['cwd'], str(self.checkout.resolve()))
        self.assertTrue(record['prompt'].endswith(self.brief.read_text()))
        self.assertEqual(record['args'][record['args'].index('--model') + 1], 'gpt-6-luna')
        self.assertIn('model_reasoning_effort="high"', record['args'])
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', record['args'])
        manifest = json.loads((self.output / 'manifest.json').read_text())
        self.assertEqual(manifest['reviewer_attribution'], 'Reviewed by GPT-6 Luna high.')
        self.assertFalse(manifest['process']['running'])
        self.assertFalse(manifest['process']['timed_out'])
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        self.assertEqual(subprocess.check_output(['git', '-C', str(self.checkout), 'status', '--porcelain'], text=True), '')

    def test_writable_role_requires_an_explicit_sandbox_selection(self):
        result = self.run_handoff(role='pr-resolve', sandbox='workspace-write')
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(self.record.read_text())
        self.assertEqual(record['args'][record['args'].index('--sandbox') + 1], 'workspace-write')

    def test_read_only_roles_reject_writable_sandbox_before_launch(self):
        for role in handoff.READ_ONLY_ROLES:
            result = self.run_handoff(role=role, sandbox='workspace-write')
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.record.exists())
            self.assertFalse(self.output.exists())

    def test_expired_deadline_prevents_launch(self):
        result = self.run_handoff(seconds=-1)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.record.exists())
        self.assertFalse(self.output.exists())

    def test_existing_bundle_cannot_be_reused(self):
        self.output.mkdir()
        result = self.run_handoff()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.record.exists())

    def test_artifacts_and_brief_cannot_enter_checkout(self):
        self.output = self.checkout / 'forbidden-bundle'
        result = self.run_handoff()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.record.exists())
        self.output = self.root / 'new-private-output'
        self.brief = self.checkout / 'forbidden-brief.md'
        self.brief.write_text('private task')
        result = self.run_handoff()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.record.exists())

    def test_authentication_failure_prevents_model_launch(self):
        self.env['FAKE_AUTH_FAILURE'] = '1'
        result = self.run_handoff()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.record.exists())

    def test_dry_run_prepares_settings_without_cli_launch(self):
        result = self.run_handoff(extra=('--dry-run',))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['dry_run'])
        self.assertFalse(self.record.exists())

    def test_failed_or_missing_report_is_never_completion(self):
        for mode in ('error', 'missing-report'):
            self.env['FAKE_MODE'] = mode
            self.output = self.root / mode
            result = self.run_handoff()
            self.assertNotEqual(result.returncode, 0)
            process = json.loads((self.output / 'process.json').read_text())
            self.assertFalse(process['running'])

    def test_timeout_settles_descendants_before_return(self):
        self.env['FAKE_MODE'] = 'timeout'
        result = self.run_handoff(seconds=11)
        self.assertNotEqual(result.returncode, 0)
        process = json.loads((self.output / 'process.json').read_text())
        self.assertTrue(process['timed_out'])
        self.assertFalse(process['running'])
        pid = int((self.root / 'child.pid').read_text())
        state = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True)
        self.assertTrue(state.returncode != 0 or state.stdout.strip().startswith('Z'))


if __name__ == '__main__':
    unittest.main()
