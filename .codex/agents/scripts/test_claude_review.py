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

import claude_runner as runner

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


class PersistenceTests(unittest.TestCase):
    def test_actual_config_directory_is_probed_without_changing_login_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary) / 'actual-cli-config'
            checkout = Path(temporary) / 'checkout'
            checkout.mkdir()
            status = SimpleNamespace(returncode=0, stdout=json.dumps(
                {'loggedIn': True, 'configDirectory': str(config)}))
            with patch.object(review.subprocess, 'run', return_value=status) as authenticate:
                storage = review.persistence_preflight('fake-cli', checkout)
            self.assertEqual(storage['config_directory'], str(config.resolve()))
            self.assertTrue((config / 'projects').is_dir())
            self.assertEqual(authenticate.call_args.args[0], ['fake-cli', 'auth', 'status'])
            self.assertNotIn('env', authenticate.call_args.kwargs)

    def test_disabled_history_missing_login_and_unwritable_storage_fail_fast(self):
        with tempfile.TemporaryDirectory() as temporary:
            checkout = Path(temporary)
            status = SimpleNamespace(returncode=0, stdout=json.dumps(
                {'loggedIn': True, 'configDirectory': temporary}))
            with patch.dict(os.environ, {'CLAUDE_CODE_SKIP_PROMPT_HISTORY': '1'}), \
                    self.assertRaisesRegex(ValueError, 'persistence is disabled'):
                review.persistence_preflight('fake-cli', checkout)
            with patch.object(review.subprocess, 'run', return_value=SimpleNamespace(
                    returncode=1, stdout='{"loggedIn": false}')), self.assertRaisesRegex(ValueError, 'login/config'):
                review.persistence_preflight('fake-cli', checkout)
            with patch.object(review.subprocess, 'run', return_value=status), \
                    patch.object(runner.tempfile, 'TemporaryFile', side_effect=PermissionError()), \
                    self.assertRaisesRegex(ValueError, 'not writable'):
                review.persistence_preflight('fake-cli', checkout)


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
        self.storage = {'config_directory': str(self.root / 'claude'),
                        'projects_directory': str(self.root / 'claude/projects')}
        Path(self.storage['projects_directory']).mkdir(parents=True)
        preflight = patch.object(review, 'persistence_preflight', return_value=self.storage.copy())
        preflight.start()
        self.addCleanup(preflight.stop)
        self.bundle = self.root / 'bundle'
        self.spec = self.root / 'spec.json'
        self.risk_report = {'rating': 'Medium high',
                            'body': '## PR risk assessment\n**Medium high** — Shared behavior with coordinated rollout.\n',
                            'head': self.head, 'base': self.base, 'merge_base': self.base}
        review.dump(self.spec, {'repo': 'example/config', 'number': 1, 'head': self.head,
                               'base': self.base, 'base_ref': 'main', 'merge_base': self.base,
                               'evidence': {'threads.json': str(self.evidence)},
                               'risk_report': self.risk_report})

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
        fake.write_text('#!' + sys.executable + '\nimport json,sys,time\n'
                        + 'if sys.argv[1:] == ["auth", "status"]:\n'
                        + ' print(json.dumps(' + repr({'loggedIn': True,
                            'configDirectory': self.storage['config_directory']}) + ')); sys.exit(0)\n'
                        + 'time.sleep(60)\n')
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

    def run_with_result(self, text, mutate=None, persist=True, **options):
        if not self.bundle.exists():
            self.prepare()
        args = SimpleNamespace(bundle=str(self.bundle), finish_by=None, timeout=60,
                               resume=False, max_turns=80, prompt_file=None,
                               replace_failed=False, recovery_reason=None)
        vars(args).update(options)

        def finish(argv, checkout, prompt, timeout, artifact, session):
            if mutate:
                mutate()
            result = {'type': 'result', 'is_error': False,
                      'modelUsage': {review.reviewer_profile()['model']: {}}, 'result': 'Human prose around the report.'}
            try:
                result['structured_output'] = json.loads(text)
            except ValueError:
                result['result'] = text
            artifact('events.jsonl').write_text(json.dumps(result) + '\n')
            review.dump(artifact('process.json'), {'session': session, 'running': False, 'exit_code': 0})
            if persist:
                transcript = Path(self.storage['projects_directory']) / 'fixture' / (session + '.jsonl')
                transcript.parent.mkdir(exist_ok=True)
                transcript.write_text('{"type":"user","message":"fixture"}\n')
            return {'exit_code': 0, 'timed_out': False}

        with patch.object(review, 'run_process', side_effect=finish), contextlib.redirect_stdout(io.StringIO()):
            review.run(args)

    def valid_report(self):
        report = dict.fromkeys(review.REPORT_FIELDS, '')
        report.update(findings=[], coverage={'scope_complete': True,
                      'inspected_sources': ['source.txt'], 'interfaces': ['caller inspected'],
                      'deployment': ['runtime boundary inspected'], 'discussion': 'All pages read',
                      'linear': 'Live issue/comments read'}, gaps=[], prior_findings=[], open_questions=[],
                      risk=self.risk_report['rating'],
                      risk_discrepancies=[],
                      reviewer_attribution=review.reviewer_profile()['attribution'])
        return json.dumps(report)

    def test_valid_review_of_unchanged_checkout_is_accepted(self):
        self.run_with_result(self.valid_report())
        metrics = review.load(self.bundle / 'metrics.json')
        self.assertTrue(metrics['execution_complete'])
        self.assertTrue(metrics['report_valid'])
        self.assertTrue(metrics['checkout_matches'])

    def test_missing_risk_report_blocks_preparation(self):
        spec = review.load(self.spec)
        del spec['risk_report']
        review.dump(self.spec, spec)
        with self.assertRaisesRegex(ValueError, 'complete risk_report'):
            self.prepare()
        self.assertFalse(self.bundle.exists())

    def test_existing_risk_report_survives_new_head_and_base_unchanged(self):
        (self.checkout / 'source.txt').write_text('later revision\n')
        self.commit('Later revision')
        spec = review.load(self.spec)
        spec.update(head=self.git('rev-parse', 'HEAD'), base=self.head, merge_base=self.head)
        review.dump(self.spec, spec)
        self.run_with_result(self.valid_report())
        saved = review.load(self.bundle / 'manifest.json')
        self.assertEqual(saved['risk_report'], self.risk_report)
        self.assertNotEqual(saved['head'], saved['risk_report']['head'])
        self.assertNotEqual(saved['base'], saved['risk_report']['base'])
        self.assertTrue(review.load(self.bundle / 'metrics.json')['report_valid'])

    def test_silent_risk_rerating_is_rejected(self):
        report = json.loads(self.valid_report())
        report['risk'] = 'Low'
        with self.assertRaises(SystemExit):
            self.run_with_result(json.dumps(report))
        self.assertFalse(review.load(self.bundle / 'metrics.json')['report_valid'])

    def test_legacy_published_risk_report_remains_accepted(self):
        spec = review.load(self.spec)
        spec['risk_report']['url'] = 'https://example.invalid/pull/1#pullrequestreview-1'
        review.dump(self.spec, spec)
        self.run_with_result(self.valid_report())
        self.assertEqual(review.load(self.bundle / 'manifest.json')['risk_report']['url'],
                         spec['risk_report']['url'])
        self.assertTrue(review.load(self.bundle / 'metrics.json')['report_valid'])

    def test_contradiction_is_preserved_without_changing_rating(self):
        report = json.loads(self.valid_report())
        report['correctness'] = 'Incomplete'
        report['risk_discrepancies'] = ['New persistent write conflicts with claimed easy reversal.']
        self.run_with_result(json.dumps(report))
        saved = review.load(self.bundle / 'report.json')
        self.assertEqual(saved['risk'], self.risk_report['rating'])
        self.assertEqual(saved['risk_discrepancies'], report['risk_discrepancies'])

    def test_structured_report_is_used_despite_human_prose(self):
        self.run_with_result(self.valid_report())
        self.assertEqual(review.load(self.bundle / 'report.json')['correctness'], '')
        self.assertEqual((self.bundle / 'report.txt').read_text(), 'Human prose around the report.')
        self.assertTrue(review.load(self.bundle / 'metrics.json')['transcript_persisted'])

    def test_persistence_failure_blocks_before_model_launch(self):
        self.prepare()
        args = SimpleNamespace(bundle=str(self.bundle), finish_by=None, timeout=60,
                               resume=False, max_turns=80, prompt_file=None)
        with patch.object(review, 'persistence_preflight', side_effect=ValueError('Not writable')), \
                patch.object(review, 'run_process') as launch, self.assertRaises(ValueError):
            review.run(args)
        launch.assert_not_called()

    def test_missing_transcript_is_recorded_and_blind_resume_is_blocked(self):
        self.run_with_result(self.valid_report(), persist=False)
        self.assertFalse(review.load(self.bundle / 'metrics.json')['transcript_persisted'])
        focused = self.root / 'focused.txt'
        focused.write_text('Inspect the remaining interface.')
        with self.assertRaisesRegex(ValueError, 'Persisted Claude session is missing'):
            self.run_with_result(self.valid_report(), resume=True, prompt_file=str(focused))
        self.assertFalse((self.bundle / 'launch-continuation-1.json').exists())

    def test_resume_uses_verified_transcript_without_new_session(self):
        self.run_with_result(self.valid_report())
        session = review.load(self.bundle / 'process.json')['session']
        focused = self.root / 'focused.txt'
        focused.write_text('Inspect the remaining interface.')
        self.run_with_result(self.valid_report(), resume=True, prompt_file=str(focused))
        argv = review.load(self.bundle / 'launch-continuation-1.json')
        self.assertNotIn('--session-id', argv)
        self.assertTrue(argv[argv.index('--resume') + 1].endswith(session + '.jsonl'))
        self.assertEqual(review.load(self.bundle / 'process-continuation-1.json')['session'], session)

    def test_invalid_output_allows_only_one_replacement_with_original_deadline(self):
        with self.assertRaises(SystemExit):
            self.run_with_result('Broken output')
        deadline = review.load(self.bundle / 'assignment.json')['finish_by']
        initial = review.load(self.bundle / 'launch.json')
        self.run_with_result(self.valid_report(), replace_failed=True, recovery_reason='invalid-output')
        replacement = review.load(self.bundle / 'launch-replacement.json')
        self.assertNotEqual(initial[initial.index('--session-id') + 1],
                            replacement[replacement.index('--session-id') + 1])
        for flag in ('--model', '--effort'):
            self.assertEqual(initial[initial.index(flag) + 1], replacement[replacement.index(flag) + 1])
        self.assertEqual(review.load(self.bundle / 'assignment.json')['finish_by'], deadline)
        with self.assertRaisesRegex(ValueError, 'already been used'):
            self.run_with_result(self.valid_report(), replace_failed=True, recovery_reason='invalid-output')

    def test_missing_session_allows_replacement_even_when_initial_report_was_valid(self):
        self.run_with_result(self.valid_report(), persist=False)
        self.run_with_result(self.valid_report(), replace_failed=True, recovery_reason='missing-session')
        self.assertTrue(review.load(self.bundle / 'metrics-replacement.json')['transcript_persisted'])

    def test_replacement_rejects_unproven_failure_or_unsettled_process(self):
        self.run_with_result(self.valid_report())
        with self.assertRaisesRegex(ValueError, 'requires evidence'):
            self.run_with_result(self.valid_report(), replace_failed=True, recovery_reason='missing-session')
        state = review.load(self.bundle / 'process.json')
        state['running'] = True
        review.dump(self.bundle / 'process.json', state)
        with self.assertRaisesRegex(ValueError, 'not settled'):
            self.run_with_result(self.valid_report(), replace_failed=True, recovery_reason='invalid-output')

    def test_relaunch_without_recovery_and_deadline_extension_are_rejected(self):
        self.run_with_result(self.valid_report())
        with self.assertRaisesRegex(ValueError, 'already launched'):
            self.run_with_result(self.valid_report())
        with self.assertRaisesRegex(ValueError, 'cannot extend'):
            self.run_with_result(self.valid_report(), finish_by='2100-01-01T00:00:00Z')

    def test_shortened_deadline_is_retained_when_resume_omits_override(self):
        self.run_with_result(self.valid_report())
        original = review.load(self.bundle / 'assignment.json')['finish_by']
        manifest = review.load(self.bundle / 'manifest.json')
        manifest['finish_by'] = original
        review.dump(self.bundle / 'manifest.json', manifest)
        from datetime import datetime, timedelta
        shortened = (datetime.fromisoformat(original) - timedelta(seconds=10)).isoformat()
        focused = self.root / 'focused.txt'
        focused.write_text('Inspect remaining coverage.')
        self.run_with_result(self.valid_report(), resume=True, prompt_file=str(focused), finish_by=shortened)
        self.run_with_result(self.valid_report(), resume=True, prompt_file=str(focused))
        self.assertEqual(review.load(self.bundle / 'assignment.json')['finish_by'], shortened)

    def test_recovery_cannot_change_recorded_execution_profile(self):
        with self.assertRaises(SystemExit):
            self.run_with_result('Broken output')
        manifest = review.load(self.bundle / 'manifest.json')
        manifest['reviewer']['effort'] = 'high'
        review.dump(self.bundle / 'manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'execution profile changed'):
            self.run_with_result(self.valid_report(), replace_failed=True, recovery_reason='invalid-output')

    def test_structured_incomplete_coverage_is_not_execution_signoff(self):
        report = json.loads(self.valid_report())
        report['correctness'] = 'Incomplete'
        report['coverage']['scope_complete'] = False
        report['gaps'] = ['Retained runtime implementation remains uninspected.']
        self.run_with_result(json.dumps(report))
        metrics = review.load(self.bundle / 'metrics.json')
        self.assertTrue(metrics['report_valid'])
        self.assertFalse(metrics['coverage_complete_claimed'])
        self.assertIn('Publisher must verify', metrics['coverage_verification'])

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
