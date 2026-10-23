"""Compatibility CLI forwarding and bootstrap; no provider or model calls."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
ENTRIES = ((ROOT / '.codex/agents/scripts/claude_delegate.py', {'default_role': 'delegate-xhigh'}),
           (ROOT / '.claude/bin/codex_delegate.py', {'legacy_brief': True}))


class CompatibilityEntrypointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.runtime = self.root / '.codex/agents/scripts/claude_runtime.py'
        self.runtime.parent.mkdir(parents=True)
        self.runtime.write_text("import os\ndef ensure_runtime():\n    os.environ['FIXTURE_BOOTSTRAPPED'] = '1'\n")
        scripts = self.root / 'scripts'
        scripts.mkdir()
        (scripts / 'agent_launcher.py').write_text('''import json, os, sys
from pathlib import Path

def main(**options):
    Path(os.environ['FIXTURE_RECORD']).write_text(json.dumps({
        'options': options, 'argv': sys.argv[1:],
        'bootstrapped': os.environ.get('FIXTURE_BOOTSTRAPPED')}))
    return int(os.environ.get('FIXTURE_EXIT', '0'))
''')
        self.record = self.root / 'record.json'
        self.env = {**os.environ, 'AGENT_LAUNCH_ROOT': str(self.root),
                    'FIXTURE_RECORD': str(self.record), 'PYTHONDONTWRITEBYTECODE': '1'}
        self.env.pop('FIXTURE_BOOTSTRAPPED', None)

    def launch(self, entry, arguments=()):
        return subprocess.run([sys.executable, str(entry), *arguments], env=self.env,
                              capture_output=True, text=True, timeout=10)

    def test_commands_bootstrap_and_forward_unchanged_arguments_with_legacy_defaults(self):
        arguments = ['--role', 'delegate-medium', '--assignment', '/private/task with spaces.json',
                     '--checkout', '/assigned/checkout', '--output', '/private/new bundle',
                     '--finish-by', '2030-01-01T12:00:00Z', '--max-turns', '7']
        for entry, options in ENTRIES:
            with self.subTest(entry=entry):
                result = self.launch(entry, arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                record = json.loads(self.record.read_text())
                self.assertEqual(record['argv'], arguments)
                self.assertEqual(record['options'], options)
                self.assertEqual(record['bootstrapped'], '1')

    def test_launcher_failure_exit_status_is_preserved(self):
        self.env['FIXTURE_EXIT'] = '37'
        for entry, _ in ENTRIES:
            with self.subTest(entry=entry):
                self.assertEqual(self.launch(entry).returncode, 37)

    def test_bootstrap_failure_prevents_launcher_dispatch(self):
        self.runtime.write_text("def ensure_runtime():\n    raise SystemExit('Fixture runtime unavailable')\n")
        for entry, _ in ENTRIES:
            with self.subTest(entry=entry):
                result = self.launch(entry)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Fixture runtime unavailable', result.stderr)
                self.assertFalse(self.record.exists())


if __name__ == '__main__':
    unittest.main()
