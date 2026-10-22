"""Publication regressions use disposable repositories and synthetic credentials."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
SPEC = importlib.util.spec_from_file_location('check_privacy', SCRIPTS / 'check_privacy.py')
privacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(privacy)
ZERO = '0' * 40


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
                    'GIT_AUTHOR_NAME': 'Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.com',
                    'GIT_COMMITTER_NAME': 'Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.com',
                    'PYTHONDONTWRITEBYTECODE': '1'}
        for key in list(self.env):
            if key.startswith(('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_CONFIG_COUNT', 'GIT_CONFIG_KEY_', 'GIT_CONFIG_VALUE_')):
                self.env.pop(key)
        self.git('init', '-q')
        self.git('config', 'commit.gpgsign', 'false')
        self.write('README.md', 'Public development configuration.\n')
        self.commit()
        self.base = self.git('rev-parse', 'HEAD').strip()

    def run_command(self, command, input=None, env=None):
        return subprocess.run(command, cwd=self.root, env=env or self.env, input=input,
                              text=True, capture_output=True)

    def git(self, *args):
        result = self.run_command(['git', *args])
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def commit(self):
        self.git('add', '-A')
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Fixture snapshot')

    def check(self, *args, input=None, env=None):
        # -S disables site-packages, proving the gate does not require PyYAML.
        return self.run_command([sys.executable, '-S', str(SCRIPTS / 'check_privacy.py'), *args], input, env)

    def assert_blocked(self, result, reason):
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(reason, result.stderr)

    def test_clean_index_without_site_packages(self):
        self.assertEqual(self.check('--staged').returncode, 0)

    def test_staged_secret_cannot_be_hidden_by_clean_worktree(self):
        credential = 'gh' + 'p_' + 'A' * 36
        self.write('settings.txt', credential)
        self.git('add', 'settings.txt')
        self.write('settings.txt', 'sanitized\n')
        result = self.check('--staged')
        self.assert_blocked(result, 'possible credential')
        self.assertNotIn(credential, result.stderr + result.stdout)

    def test_unstaged_secret_is_not_scanned_as_staged_content(self):
        self.write('README.md', 'Public and safe.\n')
        self.git('add', 'README.md')
        self.write('README.md', 'gh' + 'p_' + 'B' * 36)
        self.assertEqual(self.check('--staged').returncode, 0)

    def test_earlier_deleted_secret_still_blocks_push(self):
        self.write('settings.txt', 'gh' + 'p_' + 'C' * 36)
        self.commit()
        (self.root / 'settings.txt').unlink()
        self.commit()
        head = self.git('rev-parse', 'HEAD').strip()
        update = f'refs/heads/main {head} refs/heads/main {self.base}\n'
        self.assert_blocked(self.check('--pre-push', input=update), 'possible credential')

    def test_new_remote_branch_scans_entire_ancestry(self):
        self.write('nested/AGENTS-PRIVATE.md', 'Local settings\n')
        self.commit()
        (self.root / 'nested/AGENTS-PRIVATE.md').unlink()
        self.commit()
        head = self.git('rev-parse', 'HEAD').strip()
        update = f'refs/heads/main {head} refs/heads/new {ZERO}\n'
        self.assert_blocked(self.check('--pre-push', input=update), 'private/local-only filename')

    def test_forced_private_file_and_nested_runtime_paths(self):
        self.write('.gitignore', 'AGENTS-PRIVATE.md\nCLAUDE-PRIVATE.md\n')
        for name in ('AGENTS-PRIVATE.md', 'CLAUDE-PRIVATE.md', 'nested/AGENTS-PRIVATE.md', 'nested/.codex/sessions/run.json',
                     'nested/memories/private.md', 'nested/auth.json', '.codex/config.toml',
                     '.codex/private/account-context.md', 'nested/private/local.md'):
            with self.subTest(name=name):
                self.git('reset', '--hard', self.base)
                self.write(name, 'Private fixture\n')
                self.git('add', '-f', name)
                self.assert_blocked(self.check('--staged'), 'private/local-only filename')

    def test_symlink_payload_is_rejected_without_following_target(self):
        (self.root / 'link').symlink_to('/nonexistent-private-fixture')
        self.git('add', 'link')
        self.assert_blocked(self.check('--staged'), 'symlink or unsupported')

    def test_binary_content_fails_closed(self):
        (self.root / 'image.bin').write_bytes(b'\0fixture')
        self.git('add', 'image.bin')
        self.assert_blocked(self.check('--staged'), 'binary content')

    def test_clean_force_push_and_deletion(self):
        self.write('old.txt', 'Old public branch\n')
        self.commit()
        remote = self.git('rev-parse', 'HEAD').strip()
        self.git('reset', '--hard', self.base)
        self.write('new.txt', 'Replacement public branch\n')
        self.commit()
        head = self.git('rev-parse', 'HEAD').strip()
        updates = (f'refs/heads/main {head} refs/heads/main {remote}\n'
                   f'(delete) {ZERO} refs/heads/old {remote}\n')
        self.assertEqual(self.check('--pre-push', input=updates).returncode, 0)

    def test_unknown_remote_and_malformed_input_fail_closed(self):
        update = f'refs/heads/main {self.base} refs/heads/main {"f" * 40}\n'
        self.assert_blocked(self.check('--pre-push', input=update), 'Git snapshot unavailable')
        self.assert_blocked(self.check('--pre-push', input='unexpected\n'), 'Unsupported pre-push input')

    def test_ci_event_scans_history_without_site_packages(self):
        self.write('private.txt', 'gh' + 'p_' + 'D' * 36)
        self.commit()
        head = self.git('rev-parse', 'HEAD').strip()
        event_path = self.root / 'event.json'
        for event in ('push', 'pull_request'):
            with self.subTest(event=event):
                event_path.write_text(json.dumps({'before': self.base, 'after': head,
                    'pull_request': {'base': {'sha': self.base}, 'head': {'sha': head}}}))
                env = {**self.env, 'GITHUB_EVENT_NAME': event, 'GITHUB_EVENT_PATH': str(event_path)}
                self.assert_blocked(self.check('--ci', env=env), 'possible credential')

    def test_hooks_fail_closed_and_propagate_rejection(self):
        shutil.copytree(REPO / '.githooks', self.root / '.githooks')
        self.write('scripts/check_privacy.py', (SCRIPTS / 'check_privacy.py').read_text())
        self.git('config', 'core.hooksPath', '.githooks')
        self.write('secret.txt', 'gh' + 'p_' + 'E' * 36)
        self.git('add', 'secret.txt')
        self.assert_blocked(self.run_command(['git', 'commit', '-qm', 'Blocked fixture']), 'possible credential')
        self.git('reset', '--hard', self.base)
        self.assertEqual(self.run_command(['sh', '.githooks/pre-commit']).returncode, 0)
        (self.root / 'scripts/check_privacy.py').unlink()
        self.assertNotEqual(self.run_command(['sh', '.githooks/pre-commit']).returncode, 0)
        update = f'refs/heads/main {self.base} refs/heads/main {ZERO}\n'
        self.assertNotEqual(self.run_command(['sh', '.githooks/pre-push'], input=update).returncode, 0)

    def test_credential_shaped_filename_is_redacted(self):
        filename = 'gh' + 'p_' + 'F' * 36 + '.txt'
        self.write(filename, 'Public fixture contents\n')
        self.git('add', filename)
        result = self.check('--staged')
        self.assert_blocked(result, 'Git filename (value omitted)')
        self.assertNotIn(filename, result.stderr + result.stdout)

    def test_outgoing_commit_message_is_scanned_and_redacted(self):
        credential = 'gh' + 'p_' + 'G' * 36
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '--allow-empty', '-qm', credential)
        head = self.git('rev-parse', 'HEAD').strip()
        update = f'refs/heads/main {head} refs/heads/main {self.base}\n'
        result = self.check('--pre-push', input=update)
        self.assert_blocked(result, 'message:1: possible credential')
        self.assertNotIn(credential, result.stderr + result.stdout)

    def test_tag_message_is_scanned_when_commit_already_remote(self):
        credential = 'gh' + 'p_' + 'H' * 36
        self.git('tag', '-a', 'fixture-tag', '-m', credential)
        tag = self.git('rev-parse', 'refs/tags/fixture-tag').strip()
        update = f'refs/tags/fixture-tag {tag} refs/tags/fixture-tag {self.base}\n'
        result = self.check('--pre-push', input=update)
        self.assert_blocked(result, 'outgoing tag')
        self.assertNotIn(credential, result.stderr + result.stdout)

    def test_commit_msg_hook_rejects_secret_before_creating_commit(self):
        shutil.copytree(REPO / '.githooks', self.root / '.githooks')
        self.write('scripts/check_privacy.py', (SCRIPTS / 'check_privacy.py').read_text())
        self.git('config', 'core.hooksPath', '.githooks')
        credential = 'gh' + 'p_' + 'I' * 36
        result = self.run_command(['git', 'commit', '--allow-empty', '-qm', credential])
        self.assert_blocked(result, 'commit message:1: possible credential')
        self.assertNotIn(credential, result.stderr + result.stdout)
        self.assertEqual(self.git('rev-parse', 'HEAD').strip(), self.base)

    def test_push_hook_propagates_history_rejection(self):
        self.write('public.txt', 'gh' + 'p_' + 'J' * 36)
        self.commit()
        head = self.git('rev-parse', 'HEAD').strip()
        shutil.copytree(REPO / '.githooks', self.root / '.githooks')
        self.write('scripts/check_privacy.py', (SCRIPTS / 'check_privacy.py').read_text())
        update = f'refs/heads/main {head} refs/heads/main {self.base}\n'
        result = self.run_command(['sh', '.githooks/pre-push'], input=update)
        self.assert_blocked(result, 'possible credential')

    def test_hooks_fail_closed_without_python(self):
        shutil.copytree(REPO / '.githooks', self.root / '.githooks')
        executable_dir = self.root / 'fixture-bin'
        executable_dir.mkdir()
        (executable_dir / 'git').symlink_to(shutil.which('git'))
        env = {**self.env, 'PATH': str(executable_dir)}
        shell = shutil.which('sh')
        for hook in ('pre-commit', 'pre-push', 'commit-msg'):
            with self.subTest(hook=hook):
                result = self.run_command([shell, '.githooks/' + hook, '.git/COMMIT_EDITMSG'], env=env)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('python3', result.stderr)

    def test_literal_assignments_in_supported_formats_are_blocked_and_redacted(self):
        credential = 'synthetic-' + 'value-123'
        uppercase = 'SYNTHETIC' + 'VALUE123'
        triple_single = "'" * 3
        triple_double = '"' * 3
        cases = [
            ('settings.json', json.dumps({'password': credential})),
            ('settings.json', json.dumps({'password': credential}, indent=2).replace(': ', ':\n')),
            ('settings.py', 'password' + ' = ' + triple_single + '\n' + credential + '\n' + triple_single),
            ('settings.py', 'password' + ' = ' + triple_double + '\n' + credential + '\n' + triple_double),
            ('settings.py', 'password' + ' = (\n    # comment\n    "' + credential + '"\n)'),
            ('settings.json', json.dumps({'name': 'public', 'password': credential})),
            ('settings.json', json.dumps({'password': '<PASSWORD>', 'token': credential})),
            ('settings.js', 'const password' + ' = `' + credential + '`;'),
            ('settings.js', 'const cfg = {' + 'password: `' + credential + '`};'),
            ('settings.py', 'cfg = {' + '"password": "' + credential + '"}'),
            ('settings.js', 'const password' + ' = `\n' + credential + '\n`;'),
            ('settings.py', 'password' + '=(\n    \' ' + credential + ' \'\n)\n'),
            ('settings.ts', 'const api_key' + ' = "' + credential + '"; // comment'),
            ('settings.py', 'password' + '=(\n    "' + credential + '"\n)\n'),
            ('settings.py', 'password' + ' = ("' + credential + '")\n'),
            ('.env.example', 'PASSWORD' + '=' + uppercase + ' # comment'),
        ]
        for name, content in cases:
            with self.subTest(name=name, case=cases.index((name, content))):
                self.write(name, content)
                self.git('add', name)
                result = self.check('--staged')
                self.assert_blocked(result, 'possible literal credential assignment')
                self.assertNotIn(credential, result.stderr + result.stdout)
                self.assertNotIn(uppercase, result.stderr + result.stdout)
                self.git('reset', '--hard', self.base)

    def test_source_references_fixtures_and_unrelated_config_are_allowed(self):
        cases = [
            ('settings.py', 'password' + ' = PASSWORD_VALUE'),
            ('settings.py', 'password' + ' = settings.password'),
            ('settings.py', 'password' + ' = os.getenv("PASSWORD")'),
            ('settings.py', 'password' + ' = (\n    os.environ["PASSWORD"]\n)'),
            ('settings.py', 'password' + ' = (\n    # comment\n    os.getenv("PASSWORD")\n)'),
            ('fixture.py', 'password' + ' = (\n    # fixture\n    "synthetic-" + "value-123"\n)'),
            ('settings.json', json.dumps({'password': '${PASSWORD}'}, indent=2).replace(': ', ':\n')),
            ('settings.js', 'const password' + ' = process.env.PASSWORD;'),
            ('settings.ts', 'const api_key' + ' = env.API_KEY;'),
            ('settings.js', 'const password' + ' = `${process.env.PASSWORD}`;'),
            ('fixture.py', 'password' + ' = "synthetic-" + "value-123"'),
            ('fixture.js', 'const token' + ' = "prefix".repeat(32);'),
            ('fixture.py', 'token' + ' = build_fixture("synthetic")'),
            ('.env.example', 'PASSWORD' + '=${PASSWORD}'),
            ('settings.yaml', 'secret' + ': os.getenv("SECRET")'),
            ('settings.json', '{"password":"<PASSWORD>","token":"example-token"}'),
            ('settings.txt', 'PASSWORDLESS=true\nmax_tokens=1024\ndescription: password requirements'),
            ('settings.py', '# password' + ' = "descriptive comment"'),
        ]
        for name, content in cases:
            with self.subTest(name=name, case=cases.index((name, content))):
                privacy.inspect_blob(name, '100644', content.encode())

    def test_content_patterns_and_safe_placeholders(self):
        unsafe = [
            'password' + ' = "synthetic-value-123"',
            'password' + ' = "synthetic-value-123" # comment',
            'api_key' + ': synthetic-value-123',
            'https://user:' + 'synthetic-value-123@private.example.com/repo',
            'https://hooks.slack.com/' + 'services/T123/B123/synthetic-value-123',
            'https://hooks.slack.com/' + 'triggers/T123/456/synthetic-value-123',
            'https://discord.com/api/' + 'webhooks/123/synthetic-value-123',
            'https://service.example.com/?' + 'access_token=synthetic-value-123',
            '-----BEGIN ' + 'ENCRYPTED PRIVATE KEY-----',
        ]
        for content in unsafe:
            with self.subTest(content_kind=unsafe.index(content)):
                with self.assertRaises(privacy.PrivacyError):
                    privacy.inspect_blob('example.txt', '100644', content.encode())
        safe = [
            'password' + ': ${PASSWORD}', 'token' + ': "<TOKEN>"',
            'api_key' + ': "example-api-key"', 'secret' + ' = os.getenv("SECRET")',
            'https://user:${PASSWORD}@service.example.com',
            'https://hooks.slack.com/' + 'services/EXAMPLE/PLACEHOLDER/EXAMPLE',
        ]
        for content in safe:
            privacy.inspect_blob('example.txt', '100644', content.encode())


if __name__ == '__main__':
    unittest.main()
