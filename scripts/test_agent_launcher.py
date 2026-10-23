"""Both provider adapters against local CLIs; no models or connected services."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import agent_launcher as launcher
import agent_claude
import agent_codex

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'scripts/agent-launch'
FAKE = '''#!/usr/bin/env python3
import json, os, re, subprocess, sys, time
from pathlib import Path
root = Path(os.environ['FIXTURE_ROOT'])
args = sys.argv[1:]
provider = Path(sys.argv[0]).name
with (root / 'calls.jsonl').open('a') as stream:
    stream.write(json.dumps({'args': args, 'provider': provider, 'cwd': os.getcwd(),
                             'active': os.environ.get('_SHARED_AGENT_EXECUTOR_ACTIVE')}) + '\\n')
if args == ['--version']:
    print('fixture version')
    sys.exit(0)
if args in (['auth', 'status'], ['login', 'status']):
    print(json.dumps({'loggedIn': True, 'configDirectory': str(root / 'config')}))
    sys.exit(int(os.environ.get('AUTH_FAILURE', '0')))
prompt = sys.stdin.read()
(root / 'prompt.txt').write_text(prompt)
mode = os.environ.get('MODE', '')
def value(flag):
    return args[args.index(flag) + 1]
if mode == 'timeout':
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
    (root / 'child.pid').write_text(str(child.pid))
    time.sleep(60)
if mode == 'nested':
    nested = subprocess.run([str(root / 'entry'), *json.loads(os.environ['NESTED_ARGS'])], capture_output=True, text=True)
    (root / 'nested.json').write_text(json.dumps({'code': nested.returncode, 'stderr': nested.stderr}))
if mode == 'error':
    sys.exit(7)
report = {'summary': 'Fixture report', 'complete': mode != 'incomplete', 'changes': [],
          'verification': ['Fixture evidence'], 'gaps': ['Pending decision'] if mode == 'incomplete' else []}
if mode == 'invalid':
    report = {'summary': 'Missing required fields'}
if provider == 'codex':
    if mode != 'missing-report':
        Path(value('--output-last-message')).write_text(json.dumps(report))
    print(json.dumps({'type': 'turn.completed'}))
else:
    session = value('--session-id')
    project = root / 'config' / 'projects' / re.sub(r'[^a-zA-Z0-9]', '-', os.getcwd())
    project.mkdir(parents=True, exist_ok=True)
    if mode != 'no-transcript':
        (project / (session + '.jsonl')).write_text('{}\\n')
    result = {'type': 'result', 'is_error': False,
              'modelUsage': {'wrong-model' if mode == 'wrong-model' else value('--model'): {}}}
    if mode != 'missing-report':
        result['structured_output'] = report
    print(json.dumps(result))
'''


class SharedLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.checkout = self.root / 'assigned checkout'
        self.checkout.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.checkout)], check=True)
        (self.checkout / 'existing.txt').write_text('Preserved local work\n')
        self.task = self.root / 'assignment.json'
        self.data = {'objective': 'Inspect assigned source', 'scope': 'Analysis only',
                     'expected_result': 'Evidence and gaps', 'constraints': ['Preserve existing work'],
                     'approvals': [], 'sources': [], 'verification': ['Read source'], 'owned_paths': []}
        self.write_task()
        self.output = self.root / 'private bundle'
        for provider in ('codex', 'claude'):
            path = self.root / provider
            path.write_text(FAKE)
            path.chmod(0o700)
        (self.root / 'entry').symlink_to(ENTRY)
        self.env = {**os.environ, 'CODEX_BIN': str(self.root / 'codex'),
                    'CLAUDE_BIN': str(self.root / 'claude'), 'FIXTURE_ROOT': str(self.root),
                    'PYTHONDONTWRITEBYTECODE': '1'}
        self.env.pop(launcher.ACTIVE, None)

    def write_task(self):
        self.task.write_text(json.dumps(self.data))

    def args(self, role, seconds=60, extra=()):
        return ['--role', role, '--assignment', str(self.task), '--checkout', str(self.checkout),
                '--output', str(self.output), '--finish-by',
                (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat(), *extra]

    def run_role(self, role='delegate-low', seconds=60, extra=()):
        return subprocess.run([str(ENTRY), *self.args(role, seconds, extra)], env=self.env,
                              capture_output=True, text=True, timeout=30)

    def calls(self):
        path = self.root / 'calls.jsonl'
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_all_roles_select_canonical_executor_without_caller_provider(self):
        for role in launcher.NATIVE_ROLES + launcher.CLAUDE_ROLES:
            with self.subTest(role=role):
                self.output = self.root / role
                limits = launcher.capabilities(role)
                self.data['owned_paths'] = (['existing.txt']
                                            if limits['default_sandbox'] == 'workspace-write' else [])
                self.write_task()
                result = self.run_role(role)
                self.assertEqual(result.returncode, 0, result.stderr)
                manifest = launcher.shared.load(self.output / 'manifest.json')
                metrics = launcher.shared.load(self.output / 'metrics.json')
                self.assertEqual(metrics['status'], 'complete')
                self.assertEqual(manifest['capabilities'], limits)
                self.assertEqual(manifest['sandbox'], limits['default_sandbox'])
                settings = launcher.role_settings(launcher.AGENTS, role)
                if role in launcher.NATIVE_ROLES:
                    self.assertEqual(manifest['provider'], 'codex')
                    self.assertEqual(manifest['model'], settings['model'])
                    self.assertEqual(manifest['effort'], settings['model_reasoning_effort'])
                    command = launcher.shared.load(self.output / 'launch.json')
                    self.assertIn('features.multi_agent=false', command)
                    self.assertIn('--strict-config', command)
                    self.assertEqual(command[command.index('--sandbox') + 1], manifest['sandbox'])
                    self.assertIn('approval_policy=' + json.dumps(limits['approval_policy']), command)
                    self.assertIn('approvals_reviewer=' + json.dumps(limits['approvals_reviewer']), command)
                    self.assertNotIn('--approve-for-me', command)
                    self.assertFalse(any('dangerously-bypass' in part for part in command))
                else:
                    self.assertEqual(manifest['provider'], 'claude')
                    self.assertEqual(manifest['execution'], agent_claude.execution(settings))
                    self.assertTrue(metrics['transcript_persisted'])
                    instructions = (self.output / 'task-system.md').read_text()
                    self.assertIn('~/.claude/agent-guides/context.md', instructions)
                    self.assertNotIn('Use ~/.codex/agents/scripts/claude_delegate.py', instructions)
                self.assertIn('existing.txt', manifest['initial_state']['status'])
                self.assertEqual(manifest['initial_state'], manifest['final_state'])
                self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
                self.assertEqual(launcher.shared.load(self.output / 'assignment.json'), self.data)
                self.assertFalse(manifest['process']['running'])
        launches = [call for call in self.calls() if call['args'] not in
                    (['--version'], ['auth', 'status'], ['login', 'status'])]
        self.assertEqual(len(launches), 12)
        self.assertTrue(all(call['active'] == '1' for call in launches))
        self.assertTrue(all(call['cwd'] == str(self.checkout) for call in launches))
        self.assertEqual((self.checkout / 'existing.txt').read_text(), 'Preserved local work\n')

    def test_both_providers_preserve_incomplete_report_as_incomplete(self):
        self.env['MODE'] = 'incomplete'
        for role in ('delegate-low', 'delegate-xhigh'):
            self.output = self.root / role
            result = self.run_role(role)
            self.assertEqual(result.returncode, 0, result.stderr)
            metrics = launcher.shared.load(self.output / 'metrics.json')
            self.assertTrue(metrics['execution_complete'])
            self.assertEqual(metrics['status'], 'incomplete')
            self.assertFalse(metrics['task_complete_claimed'])
            self.assertFalse(launcher.shared.load(self.output / 'report.json')['complete'])

    def test_provider_failures_and_missing_or_invalid_reports_fail_closed(self):
        for role in ('delegate-low', 'delegate-xhigh'):
            modes = ['error', 'missing-report', 'invalid']
            if role == 'delegate-xhigh':
                modes += ['wrong-model', 'no-transcript']
            for mode in modes:
                with self.subTest(role=role, mode=mode):
                    self.env['MODE'] = mode
                    self.output = self.root / (role + mode)
                    result = self.run_role(role)
                    self.assertNotEqual(result.returncode, 0)
                    metrics = launcher.shared.load(self.output / 'metrics.json')
                    self.assertEqual(metrics['status'], 'failed')
                    self.assertFalse(launcher.shared.load(self.output / 'process.json')['running'])

    def test_both_provider_auth_failures_prevent_executor_launch_and_save_final_state(self):
        self.env['AUTH_FAILURE'] = '1'
        for role in ('delegate-low', 'delegate-xhigh'):
            self.output = self.root / role
            result = self.run_role(role)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((self.output / 'process.json').exists())
            self.assertIn('final_state', launcher.shared.load(self.output / 'manifest.json'))
        self.assertTrue(all(call['args'] in (['--version'], ['auth', 'status'], ['login', 'status'])
                            for call in self.calls()))

    def test_invalid_installation_root_fails_cleanly_before_cli(self):
        self.env['AGENT_LAUNCH_ROOT'] = str(self.root / 'absent')
        for entry in (ENTRY, ROOT / '.claude/bin/codex_delegate.py',
                      ROOT / '.codex/agents/scripts/claude_delegate.py'):
            result = subprocess.run([sys.executable, str(entry), *self.args('delegate-low')],
                                    env=self.env, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('set AGENT_LAUNCH_ROOT', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(self.calls(), [])

    def test_inherited_recursion_guard_blocks_both_providers_before_artifacts(self):
        self.env[launcher.ACTIVE] = '1'
        for role in ('delegate-low', 'delegate-xhigh'):
            result = self.run_role(role)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Nested agent launch refused', result.stderr)
            self.assertFalse(self.output.exists())
        self.assertEqual(self.calls(), [])

    def test_child_cannot_reenter_shared_launcher(self):
        self.env['MODE'] = 'nested'
        self.env['NESTED_ARGS'] = json.dumps(self.args('delegate-xhigh'))
        result = self.run_role()
        self.assertEqual(result.returncode, 0, result.stderr)
        nested = launcher.shared.load(self.root / 'nested.json')
        self.assertNotEqual(nested['code'], 0)
        self.assertIn('Nested agent launch refused', nested['stderr'])

    def test_deadline_extension_and_missing_timezone_are_rejected_before_auth(self):
        self.data['finish_by'] = (datetime.now(timezone.utc) + timedelta(seconds=40)).isoformat()
        self.write_task()
        result = self.run_role(seconds=60)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('extend', result.stderr)
        self.assertFalse(self.output.exists())
        self.data['finish_by'] = '2100-01-01T00:00:00'
        self.write_task()
        result = self.run_role()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('timezone', result.stderr)
        self.assertEqual(self.calls(), [])

    def test_private_sources_bundles_and_assignment_shape_are_validated(self):
        self.output = self.checkout / 'bundle'
        self.assertNotEqual(self.run_role().returncode, 0)
        self.output = self.root / 'bundle'
        self.task = self.checkout / 'assignment.json'
        self.write_task()
        self.assertNotEqual(self.run_role().returncode, 0)
        self.task = self.root / 'invalid.json'
        del self.data['owned_paths']
        self.write_task()
        self.assertNotEqual(self.run_role().returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_no_write_sandbox_without_owned_paths_and_review_roles_remain_read_only(self):
        self.assertNotEqual(self.run_role(extra=('--sandbox', 'workspace-write')).returncode, 0)
        self.data['owned_paths'] = ['source.txt']
        self.write_task()
        for role in launcher.READ_ONLY_ROLES:
            self.assertNotEqual(self.run_role(role, extra=('--sandbox', 'workspace-write')).returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_role_defaults_and_action_ceilings_are_explicit(self):
        for role in ('delegate-low', 'delegate-medium', 'delegate-high', 'writer', 'delegate-xhigh'):
            with self.subTest(role=role):
                limits = launcher.capabilities(role)
                self.assertEqual(limits['default_sandbox'], 'read-only')
                self.assertTrue(limits['source_writes'])
                self.assertFalse(limits['requires_network_reads'])
                self.assertEqual(limits['external_actions'], 'task-authorized')
                self.assertIn('Optional network reads remain allowed', launcher.executor_rules(role))
                if limits['provider'] == 'codex':
                    self.assertEqual(limits['approval_policy'], 'on-request')
                    self.assertEqual(limits['approvals_reviewer'], 'auto_review')
        for role in ('pr-resolve', 'pr-update'):
            self.assertEqual(launcher.capabilities(role)['default_sandbox'], 'workspace-write')
            result = self.run_role(role)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('owned_paths', result.stderr)
            self.assertFalse(self.output.exists())
        for role in ('pr-risk', 'pr-review-high', 'port-to-claude'):
            limits = launcher.capabilities(role)
            self.assertFalse(limits['source_writes'])
            self.assertEqual(limits['external_actions'], 'none')
            self.assertIn('do not commit, push, publish, rerun CI', launcher.executor_rules(role))
        self.assertEqual(self.calls(), [])

    def test_review_and_ci_have_approval_paths_without_source_write_permission(self):
        for role, action in (('pr-review', 'COMMENT review'), ('pr-green', 'CI rerun')):
            with self.subTest(role=role):
                self.output = self.root / role
                self.data['approvals'] = ['Explicit authorization for one assigned ' + action]
                self.write_task()
                result = self.run_role(role)
                self.assertEqual(result.returncode, 0, result.stderr)
                command = launcher.shared.load(self.output / 'launch.json')
                self.assertEqual(command[command.index('--sandbox') + 1], 'read-only')
                self.assertIn('approval_policy="on-request"', command)
                self.assertIn('approvals_reviewer="auto_review"', command)
                self.assertEqual(launcher.shared.load(self.output / 'assignment.json'), self.data)
                instructions = (self.output / 'task-system.md').read_text()
                self.assertIn('The only permitted external write', instructions)
                self.assertIn('explicitly authorized', instructions)
                self.assertIn('Do not edit source files', instructions)

    def test_risk_analysis_has_read_network_approval_path_without_write_authority(self):
        self.data['approvals'] = ['Read the assigned live GitHub and Linear evidence']
        self.data['constraints'] = ['No source edits or external writes']
        self.write_task()
        result = self.run_role('pr-risk')
        self.assertEqual(result.returncode, 0, result.stderr)
        command = launcher.shared.load(self.output / 'launch.json')
        self.assertEqual(command[command.index('--sandbox') + 1], 'read-only')
        self.assertIn('approval_policy="on-request"', command)
        self.assertIn('approvals_reviewer="auto_review"', command)
        limits = launcher.shared.load(self.output / 'manifest.json')['capabilities']
        self.assertTrue(limits['requires_network_reads'])
        self.assertFalse(limits['source_writes'])
        self.assertEqual(limits['external_actions'], 'none')
        self.assertEqual(launcher.shared.load(self.output / 'assignment.json'), self.data)
        instructions = (self.output / 'task-system.md').read_text()
        self.assertIn('scoped read-only network access', instructions)
        self.assertIn('a read approval does not authorize an external write', instructions)
        self.assertIn('require_escalated command runs outside the default sandbox', instructions)
        self.assertIn('Do not edit source files', instructions)
        self.assertIn('do not commit, push, publish, rerun CI', instructions)

    def test_offline_native_analysis_can_keep_never_approval_policy(self):
        limits = {**launcher.ROLE_CAPABILITIES['pr-risk'],
                  'requires_network_reads': False, 'approval_policy': 'never'}
        with patch.dict(launcher.ROLE_CAPABILITIES, {'offline-analysis': limits}):
            profile = agent_codex.execution({'name': 'offline-analysis', 'model': 'fixture-model',
                                             'model_reasoning_effort': 'low'})
            command = agent_codex.launch_args('codex', self.checkout, self.output, '', 120, profile,
                                             'read-only', {}, '', {})
        self.assertIn('approval_policy="never"', command)
        self.assertIn('approvals_reviewer="user"', command)

    def test_owned_edits_keep_task_approvals_and_have_approval_path_for_authorized_pushes(self):
        self.data['owned_paths'] = ['existing.txt']
        self.data['scope'] = 'Only the assigned source change'
        self.data['approvals'] = ['Commit and push the verified assigned change']
        self.data['constraints'] = ['No merge or deploy']
        self.write_task()
        for role in ('delegate-low', 'delegate-medium', 'delegate-high', 'pr-resolve', 'pr-update', 'writer'):
            with self.subTest(role=role):
                self.output = self.root / role
                result = self.run_role(role, extra=('--sandbox', 'workspace-write'))
                self.assertEqual(result.returncode, 0, result.stderr)
                command = launcher.shared.load(self.output / 'launch.json')
                self.assertEqual(command[command.index('--sandbox') + 1], 'workspace-write')
                self.assertIn('approval_policy="on-request"', command)
                self.assertIn('approvals_reviewer="auto_review"', command)
                self.assertEqual(launcher.shared.load(self.output / 'assignment.json'), self.data)
                self.assertIn('Commits, pushes, publication, and other external writes require explicit task authorization',
                              (self.output / 'task-system.md').read_text())

    def test_adapter_rejects_writable_review_even_when_called_without_launcher(self):
        profile = agent_codex.execution(launcher.role_settings(launcher.AGENTS, 'pr-review'))
        with self.assertRaisesRegex(ValueError, 'read-only'):
            agent_codex.launch_args('codex', self.checkout, self.output, '', 120, profile,
                                    'workspace-write', {}, '', {})

    def test_both_provider_timeouts_settle_descendants(self):
        self.env['MODE'] = 'timeout'
        for role in ('delegate-low', 'delegate-xhigh'):
            self.output = self.root / role
            result = self.run_role(role, seconds=11)
            self.assertNotEqual(result.returncode, 0)
            state = launcher.shared.load(self.output / 'process.json')
            self.assertTrue(state['timed_out'])
            self.assertFalse(state['running'])
            pid = int((self.root / 'child.pid').read_text())
            process = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True)
            self.assertTrue(process.returncode != 0 or process.stdout.strip().startswith('Z'))


if __name__ == '__main__':
    unittest.main()
