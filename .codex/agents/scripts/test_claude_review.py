import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, call, patch

MODULE = Path(__file__).with_name('claude_review.py')
spec = importlib.util.spec_from_file_location('review', MODULE)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class EvidenceTests(unittest.TestCase):
    def test_api_errors_are_not_empty_discussion(self):
        for value in ({'errors': [{'message': 'Unavailable'}], 'data': None},
                      {'data': {'errors': [{'message': 'Partial failure'}]}},
                      {'message': 'Not Found', 'documentation_url': 'https://example.invalid'}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                review.validate_evidence(value)

    def test_partial_connections_are_rejected_for_both_graphql_shapes(self):
        for key in ('nodes', 'edges'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                review.validate_evidence({key: [], 'pageInfo': {'hasNextPage': True}})

    def test_full_pages_and_nested_thread_pages_are_accepted(self):
        review.validate_evidence([
            {'nodes': [{'id': 'T1', 'comments': {'edges': [], 'pageInfo': {'hasNextPage': True}}}],
             'pageInfo': {'hasNextPage': True}},
            {'nodes': [], 'pageInfo': {'hasNextPage': False}},
            {'nodes': [{'id': 'T1', 'comments': {'edges': [], 'pageInfo': {'hasNextPage': False}}}],
             'pageInfo': {'hasNextPage': False}},
        ])

    def test_one_complete_thread_cannot_hide_another_incomplete_thread(self):
        with self.assertRaises(ValueError):
            review.validate_evidence({'nodes': [
                {'id': 'T1', 'comments': {'nodes': [], 'pageInfo': {'hasNextPage': True}}},
                {'id': 'T2', 'comments': {'nodes': [], 'pageInfo': {'hasNextPage': False}}},
            ], 'pageInfo': {'hasNextPage': False}})

    def test_invalid_deadlines_cannot_launch(self):
        for timeout, deadline in ((0, None), (-1, None), (60, '2000-01-01T00:00:00Z'),
                                  (60, '2100-01-01T00:00:00')):
            with self.subTest(timeout=timeout, deadline=deadline), self.assertRaises(ValueError):
                review.bounded_timeout(timeout, deadline)
        self.assertEqual(review.bounded_timeout(60, '2100-01-01T00:00:00Z'), 60)

    def test_launch_uses_profile_with_trusted_shell_and_linear(self):
        profile = review.reviewer_profile()
        args = review.launch_args(Path('/tmp/review-bundle'), 'session', 80, profile)
        self.assertEqual(args[args.index('--model') + 1], profile['model'])
        self.assertEqual(args[args.index('--effort') + 1], profile['effort'])
        self.assertIn('Bash', args)
        self.assertNotIn('Bash(git diff *)', args)
        self.assertNotIn('--strict-mcp-config', args)
        self.assertNotIn('--exclude-dynamic-system-prompt-sections', args)
        self.assertIn('mcp__claude_ai_Linear__list_comments', args)
        self.assertIn('Agent', args[args.index('--disallowedTools') + 1:])


    def test_unresponsive_process_is_killed_and_reaped(self):
        proc = MagicMock()
        proc.pid = 12345
        proc.poll.return_value = None
        proc.wait.side_effect = [subprocess.TimeoutExpired('fake-cli', 3), -9]
        with patch.object(review.os, 'killpg') as kill:
            review.stop_process(proc)
        self.assertEqual(kill.call_args_list, [call(proc.pid, signal.SIGTERM),
                                               call(proc.pid, signal.SIGKILL)])
        self.assertEqual(proc.wait.call_count, 2)


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.checkout = self.root / 'checkout'
        self.checkout.mkdir()
        self.codex_home = self.root / 'codex-home'
        self.codex_home.mkdir()
        self.environment = patch.dict(os.environ, {'CODEX_HOME': str(self.codex_home)})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.git('init', '-q', '-b', 'main')
        (self.checkout / 'source.txt').write_text('before\n')
        self.commit('Base')
        self.base = self.git('rev-parse', 'HEAD')
        (self.checkout / 'source.txt').write_text('after\n')
        self.commit('Change')
        self.head = self.git('rev-parse', 'HEAD')
        self.evidence = self.root / 'threads.json'
        self.evidence.write_text(json.dumps([
            {'nodes': [{'id': 'T1', 'path': 'source.txt', 'line': 1, 'isResolved': False,
                        'comments': {'edges': [{'node': {'id': 'C1', 'body': 'Original objection'}}],
                                     'pageInfo': {'hasNextPage': True}}}],
             'pageInfo': {'hasNextPage': False}},
            {'nodes': [{'id': 'T1', 'path': 'source.txt', 'line': 1, 'isResolved': False,
                        'comments': {'edges': [{'node': {'id': 'C2', 'body': 'Later reply'}}],
                                     'pageInfo': {'hasNextPage': False}}}],
             'pageInfo': {'hasNextPage': False}},
        ], indent=2) + '\n')
        self.bundle = self.root / 'bundle'
        self.spec = self.root / 'spec.json'
        review.dump(self.spec, {'repo': 'example/config', 'number': 1, 'head': self.head,
                               'base': self.base, 'base_ref': 'main', 'merge_base': self.base,
                               'evidence': {'threads.json': str(self.evidence)}})

    def git(self, *args):
        return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', '-c',
                                        'commit.gpgsign=false', '-C', str(self.checkout), *args],
                                       stderr=subprocess.DEVNULL, text=True).strip()

    def commit(self, message):
        self.git('add', '--all')
        self.git('-c', 'user.name=Developer', '-c', 'user.email=developer@example.invalid',
                 'commit', '-q', '-m', message)

    def prepare(self):
        with contextlib.redirect_stdout(io.StringIO()):
            review.prepare(SimpleNamespace(spec=str(self.spec), checkout=str(self.checkout),
                                           output=str(self.bundle)))

    def test_saved_evidence_keeps_all_pages_edges_anchors_and_exact_bytes(self):
        self.prepare()
        self.assertEqual((self.bundle / 'raw/threads.json').read_bytes(), self.evidence.read_bytes())
        saved = review.load(self.bundle / 'manifest.json')
        self.assertEqual(saved['raw_evidence'][0]['sha256'], review.digest(self.evidence))

    def test_error_response_is_rejected_before_bundle_creation(self):
        review.dump(self.evidence, {'data': None, 'errors': [{'message': 'Failure'}]})
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.bundle.exists())

    def test_guide_override_precedence_and_empty_override_fallback(self):
        (self.codex_home / 'AGENTS.md').write_text('Global default')
        (self.codex_home / 'AGENTS.override.md').write_text('Global override')
        (self.checkout / 'AGENTS.md').write_text('Repo default')
        (self.checkout / 'AGENTS.override.md').write_text('Repo override')
        child = self.checkout / 'nested'
        child.mkdir()
        (child / 'AGENTS.md').write_text('Child default')
        (child / 'AGENTS.override.md').write_text(' \n')
        guides = review.collect_guides(self.checkout, ['nested/file.txt'])
        self.assertEqual(guides, [self.codex_home / 'AGENTS.override.md',
                                  self.checkout / 'AGENTS.override.md', child / 'AGENTS.md'])

    def test_missing_explicit_guide_is_a_blocker(self):
        with self.assertRaises(ValueError):
            review.collect_guides(self.checkout, [], [self.root / 'missing.md'])

    def test_interruption_and_stdin_errors_always_settle_owned_process(self):
        self.bundle.mkdir()
        for error in (KeyboardInterrupt(), BrokenPipeError()):
            proc = MagicMock()
            proc.pid = 12345
            proc.poll.return_value = -15
            proc.communicate.side_effect = error
            with self.subTest(error=type(error).__name__), \
                    patch.object(review.subprocess, 'Popen', return_value=proc), \
                    patch.object(review, 'stop_process') as stop:
                with self.assertRaises(type(error)):
                    review.run_process(['fake-cli'], self.checkout, 'prompt', 1,
                                       lambda name: self.bundle / name, 'session')
                stop.assert_called_once_with(proc)
                state = review.load(self.bundle / 'process.json')
                self.assertFalse(state['running'])
                self.assertTrue(state['interrupted'])

    def test_real_timeout_terminates_and_reaps_process(self):
        self.bundle.mkdir()
        state = review.run_process([sys.executable, '-c', 'import time; time.sleep(60)'],
                                   self.checkout, '', 0.1, lambda name: self.bundle / name, 'session')
        self.assertTrue(state['timed_out'])
        self.assertFalse(state['running'])
        self.assertIsNotNone(state['exit_code'])

    def test_sigterm_to_runner_settles_fake_cli_without_model_usage(self):
        self.prepare()
        binary = self.root / 'bin'
        binary.mkdir()
        fake = binary / 'claude'
        fake.write_text('#!' + sys.executable + '\nimport time\ntime.sleep(60)\n')
        fake.chmod(0o755)
        environment = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH'])
        proc = subprocess.Popen([sys.executable, str(MODULE), 'run', '--bundle', str(self.bundle),
                                 '--timeout', '30'], env=environment, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        try:
            cutoff = time.monotonic() + 5
            while not (self.bundle / 'process.json').exists() and time.monotonic() < cutoff:
                if proc.poll() is not None:
                    self.fail('Runner exited before the fake CLI started: ' + proc.stderr.read().decode())
                time.sleep(0.02)
            self.assertTrue((self.bundle / 'process.json').is_file())
            proc.send_signal(signal.SIGTERM)
            proc.communicate(timeout=10)
            self.assertEqual(proc.returncode, 130)
            state = review.load(self.bundle / 'process.json')
            self.assertFalse(state['running'])
            self.assertTrue(state['interrupted'])
            with self.assertRaises(ProcessLookupError):
                os.kill(state['pid'], 0)
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.communicate(timeout=10)
            proc.stdout.close()
            proc.stderr.close()

    def run_with_result(self, text, mutate=None):
        self.prepare()
        args = SimpleNamespace(bundle=str(self.bundle), finish_by=None, timeout=60,
                               resume=False, max_turns=80, prompt_file=None)

        def finish(argv, checkout, prompt, timeout, artifact, session):
            if mutate:
                mutate()
            artifact('events.jsonl').write_text(json.dumps({'type': 'result', 'is_error': False,
                'modelUsage': {review.reviewer_profile()['model']: {}}, 'result': text}) + '\n')
            return {'exit_code': 0, 'timed_out': False}

        with patch.object(review, 'run_process', side_effect=finish), contextlib.redirect_stdout(io.StringIO()):
            review.run(args)

    def valid_report(self):
        report = dict.fromkeys(review.REPORT_FIELDS, '')
        report.update(findings=[], coverage={}, gaps=[],
                      reviewer_attribution=review.reviewer_profile()['attribution'])
        return json.dumps(report)

    def test_valid_review_of_unchanged_checkout_is_accepted(self):
        self.run_with_result(self.valid_report())
        metrics = review.load(self.bundle / 'metrics.json')
        self.assertTrue(metrics['execution_complete'])
        self.assertTrue(metrics['report_valid'])
        self.assertTrue(metrics['checkout_matches'])

    def test_invalid_report_cannot_be_accepted(self):
        with self.assertRaises(SystemExit):
            self.run_with_result('No JSON report')
        self.assertFalse(review.load(self.bundle / 'metrics.json')['report_valid'])

    def test_different_clean_final_head_is_rejected(self):
        def move_head():
            self.git('checkout', '--detach', self.base)
        with self.assertRaises(SystemExit):
            self.run_with_result(self.valid_report(), move_head)
        self.assertFalse(review.load(self.bundle / 'metrics.json')['checkout_matches'])

    def test_changed_saved_evidence_blocks_before_launch(self):
        self.prepare()
        (self.bundle / 'raw/threads.json').write_text('[]\n')
        args = SimpleNamespace(bundle=str(self.bundle), finish_by=None, timeout=60,
                               resume=False, max_turns=80, prompt_file=None)
        with patch.object(review, 'run_process') as launch, self.assertRaises(ValueError):
            review.run(args)
        launch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
