import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('review', Path(__file__).with_name('claude_review.py'))
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)

class EvidenceTests(unittest.TestCase):
    def test_checks_keep_outcome_and_commit_without_transport_noise(self):
        result = review.project_checks({'check_runs': [{'name': 'Test', 'head_sha': 'abc',
            'conclusion': 'failure', 'details_url': 'https://example/check', 'app': {'irrelevant': 'large'},
            'output': {'text': 'raw details retained separately'}}]})
        self.assertEqual(result, [{'name': 'Test', 'head_sha': 'abc', 'conclusion': 'failure',
                                   'details_url': 'https://example/check'}])

    def test_duplicate_bodies_preserve_thread_and_evidence(self):
        comment = {'id': 12, 'node_id': 'C12', 'body': 'Full finding body', 'html_url': 'https://x#12',
                   'path': 'source.ts', 'line': 4, 'user': {'login': 'engineer'}}
        thread = {'id': 'T1', 'isResolved': False, 'isOutdated': True,
                  'comments': {'nodes': [{'id': 'C12', 'body': comment['body'], 'url': comment['html_url']}],
                               'pageInfo': {'hasNextPage': False}}}
        value = review.project_discussion({'inline.json': [comment], 'threads.json': [thread]})
        self.assertEqual(len(value['comments']), 1)
        self.assertEqual(value['comments']['https://x#12']['body'], comment['body'])
        self.assertEqual(value['comments']['https://x#12']['path'], 'source.ts')
        self.assertEqual(value['threads'][0]['comments'], ['https://x#12'])
        self.assertTrue(value['threads'][0]['isOutdated'])
        self.assertEqual(len(value['comments']['https://x#12']['sources']), 2)
        self.assertEqual(value['comments']['https://x#12']['author'], 'engineer')

    def test_truncated_connection_is_rejected(self):
        with self.assertRaises(ValueError):
            review.project_discussion({'threads.json': {'nodes': [], 'pageInfo': {'hasNextPage': True}}})

    def test_complete_paginated_connection_is_accepted(self):
        self.assertEqual(review.project_discussion({'threads.json': [
            {'nodes': [], 'pageInfo': {'hasNextPage': True}},
            {'nodes': [], 'pageInfo': {'hasNextPage': False}}]})['threads'], [])

    def test_expired_or_ambiguous_deadline_cannot_launch(self):
        with self.assertRaises(ValueError):
            review.bounded_timeout(60, '2000-01-01T00:00:00Z')
        with self.assertRaises(ValueError):
            review.bounded_timeout(60, '2100-01-01T00:00:00')
        self.assertEqual(review.bounded_timeout(60, '2100-01-01T00:00:00Z'), 60)

    def test_fixed_launch_retains_linear_and_excludes_machine_prefix(self):
        args = review.launch_args(Path('/tmp/bundle'), 'session', 80)
        self.assertIn('--exclude-dynamic-system-prompt-sections', args)
        self.assertNotIn('--strict-mcp-config', args)
        self.assertEqual(args[args.index('--effort') + 1], 'medium')
        settings = json.loads(args[args.index('--settings') + 1])
        self.assertEqual(settings['allowedMcpServers'], [{'serverUrl': 'https://mcp.linear.app/mcp'}])
        self.assertIn('mcp__claude_ai_Linear__list_comments', args)
        self.assertNotIn('Bash(*)', args)

if __name__ == '__main__':
    unittest.main()
