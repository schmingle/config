import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import claude_delegate as delegate
import agent_claude
import claude_runner as runner


class DelegateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.checkout = self.root / 'checkout'
        self.checkout.mkdir()
        self.git('init', '-q', '-b', 'main')
        self.git('-c', 'user.name=Developer', '-c', 'user.email=developer@example.invalid',
                 'commit', '-q', '--allow-empty', '-m', 'Initial')
        (self.checkout / 'existing.txt').write_text('Unrelated local work\n')
        self.task = self.root / 'task.json'
        runner.dump(self.task, {'objective': 'Complete a scoped task', 'scope': 'source.txt',
                               'owned_paths': ['source.txt'], 'constraints': ['Preserve existing.txt'],
                               'approvals': [], 'sources': [], 'verification': ['Inspect output'],
                               'expected_result': 'A verified implementation'})
        self.output = self.root / 'bundle'
        self.args = SimpleNamespace(assignment=str(self.task), checkout=str(self.checkout),
                                    output=str(self.output), timeout=60, max_turns=10,
                                    finish_by=None)
        self.projects = self.root / 'projects'
        (self.projects / 'checkout').mkdir(parents=True)

    def git(self, *args):
        return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null',
                                        '-c', 'commit.gpgsign=false', '-C', str(self.checkout),
                                        *args], text=True, stderr=subprocess.DEVNULL).strip()

    def run_fake(self, model=None, report=None, persisted=True, edit=False, timed_out=False):
        profile = runner.execution_profile()

        def finish(argv, checkout, prompt, timeout, artifact, session):
            if edit:
                (checkout / 'source.txt').write_text('Scoped change\n')
            if persisted:
                (self.projects / 'checkout' / (session + '.jsonl')).write_text('{}\n')
            result = {'type': 'result', 'is_error': False,
                      'modelUsage': {model or profile['model']: {}},
                      'structured_output': report if report is not None else {
                          'summary': 'Implemented', 'complete': True, 'changes': ['source.txt'],
                          'verification': ['Inspected output'], 'gaps': []}}
            artifact('events.jsonl').write_text(json.dumps(result) + '\n')
            return {'exit_code': 0, 'timed_out': timed_out, 'running': False}

        with patch.object(agent_claude.shutil, 'which', return_value='fake-claude'), \
                patch.object(runner, 'persistence_preflight', return_value={
                    'config_directory': str(self.root), 'projects_directory': str(self.projects)}), \
                patch.object(runner, 'run_process', side_effect=finish), \
                contextlib.redirect_stdout(io.StringIO()):
            delegate.run(self.args)

    def test_scoped_edits_allow_dirty_checkout_and_preserve_existing_work(self):
        self.run_fake(edit=True)
        manifest = runner.load(self.output / 'manifest.json')
        metrics = runner.load(self.output / 'metrics.json')
        self.assertIn('existing.txt', manifest['before']['status'])
        self.assertIn('source.txt', metrics['after']['status'])
        self.assertEqual((self.checkout / 'existing.txt').read_text(), 'Unrelated local work\n')
        self.assertEqual(manifest['execution'], agent_claude.execution({}))
        self.assertEqual(runner.load(self.output / 'assignment.json'), runner.load(self.task))
        self.assertTrue(metrics['transcript_persisted'])

    def test_general_task_can_use_a_directory_without_a_git_repository(self):
        self.checkout = self.root / 'research'
        self.checkout.mkdir()
        self.args.checkout = str(self.checkout)
        self.run_fake()
        self.assertEqual(runner.load(self.output / 'manifest.json')['before'], {'git': False})
        self.assertEqual(runner.load(self.output / 'metrics.json')['after'], {'git': False})

    def test_shared_launcher_preserves_profile_and_blocks_nested_agents(self):
        profile = runner.execution_profile()
        argv = delegate.launch_args('fake-claude', self.output, 'session', 12, profile)
        self.assertEqual(argv[argv.index('--model') + 1], profile['model'])
        self.assertEqual(argv[argv.index('--effort') + 1], profile['effort'])
        self.assertEqual(argv[argv.index('--allowedTools') + 1:argv.index('--disallowedTools')],
                         profile['allowed_tools'])
        self.assertEqual(argv[argv.index('--disallowedTools') + 1:], ['Agent'])
        self.assertNotIn('--strict-mcp-config', argv)
        self.assertNotIn('--settings', argv)
        self.assertIn('task-system.md', argv[argv.index('--append-system-prompt-file') + 1])

    def test_wrong_model_invalid_report_missing_transcript_and_timeout_are_failures(self):
        cases = [{'model': 'wrong-model'}, {'report': {'summary': 'Incomplete envelope'}},
                 {'persisted': False}, {'timed_out': True}]
        for index, options in enumerate(cases):
            self.args.output = str(self.root / ('failure-' + str(index)))
            with self.subTest(options=options), self.assertRaises(SystemExit):
                self.run_fake(**options)

    def test_reported_incomplete_work_is_not_rewritten_as_complete(self):
        self.run_fake(report={'summary': 'Blocked', 'complete': False, 'changes': [],
                              'verification': [], 'gaps': ['Missing decision']})
        metrics = runner.load(self.output / 'metrics.json')
        self.assertTrue(metrics['execution_complete'])
        self.assertFalse(metrics['task_complete_claimed'])

    def test_output_inside_checkout_or_public_repo_is_rejected_before_launch(self):
        for root in (self.checkout, Path(delegate.__file__).resolve().parents[3]):
            self.args.output = str(root / 'private-bundle')
            with self.subTest(root=root), patch.object(runner, 'run_process') as launch, \
                    self.assertRaisesRegex(ValueError, 'outside'):
                delegate.run(self.args)
            launch.assert_not_called()

    def test_missing_ownership_and_duplicate_bundle_are_rejected(self):
        task = runner.load(self.task)
        del task['owned_paths']
        runner.dump(self.task, task)
        with self.assertRaisesRegex(ValueError, 'owned_paths'):
            delegate.assignment(self.task)
        task['owned_paths'] = []
        runner.dump(self.task, task)
        self.run_fake()
        with self.assertRaises(FileExistsError):
            self.run_fake()

    def test_deadline_cannot_be_extended(self):
        task = runner.load(self.task)
        task['finish_by'] = '2100-01-01T00:00:00Z'
        runner.dump(self.task, task)
        self.args.finish_by = '2100-01-02T00:00:00Z'
        with self.assertRaisesRegex(ValueError, 'extend'):
            self.run_fake()


if __name__ == '__main__':
    unittest.main()
