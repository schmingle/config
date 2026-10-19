import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import claude_runner as runner


SURVIVOR = '''import os, signal, sys, time
from pathlib import Path
ready_read, ready_write = os.pipe()
child = os.fork()
if child == 0:
    os.close(ready_read)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    Path(sys.argv[1], 'child.pid').write_text(str(os.getpid()))
    os.write(ready_write, b'ready')
    os.close(ready_write)
    time.sleep(30)
    os._exit(0)
os.close(ready_write)
os.read(ready_read, 5)
os.close(ready_read)
if sys.argv[2] == 'timeout':
    time.sleep(30)
'''


@unittest.skipUnless(hasattr(os, 'waitid') and hasattr(os, 'WNOWAIT') and hasattr(os, 'fork'), 'requires POSIX waitid/fork')
class ProcessSettlementTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.addCleanup(self.clean_fixture)

    def clean_fixture(self):
        # An assertion failure must not leave either sleeping fixture alive.
        pids = []
        path = self.root / 'child.pid'
        if path.exists():
            pids.append(int(path.read_text()))
        path = self.root / 'process.json'
        if path.exists() and runner.load(path).get('pid'):
            pids.append(runner.load(path)['pid'])
        for pid in pids:
            result = subprocess.run(['ps', '-p', str(pid), '-o', 'command='],
                                    capture_output=True, text=True, timeout=3)
            if str(self.root) in result.stdout:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            self.assert_terminated(pid)
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass

    def assert_terminated(self, pid):
        deadline = time.monotonic() + 3
        while True:
            result = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='],
                                    capture_output=True, text=True, timeout=3)
            if result.returncode == 1 or result.stdout.strip().startswith('Z'):
                return
            if time.monotonic() >= deadline:
                self.fail('fixture process is still alive: ' + str(pid))
            time.sleep(0.01)

    def run_survivor(self, mode):
        state = runner.run_process([sys.executable, '-c', SURVIVOR, str(self.root), mode],
                                   self.root, 'fixture input', 0.5,
                                   lambda name: self.root / name, 'fixture-session')
        self.assertEqual(state['timed_out'], mode == 'timeout')
        self.assertFalse(state['running'])
        self.assertIsNotNone(state['exit_code'])
        self.assertEqual(runner.load(self.root / 'process.json'), state)
        self.assert_terminated(int((self.root / 'child.pid').read_text()))
        self.assert_terminated(state['pid'])
        with self.assertRaises(ChildProcessError):
            os.waitpid(state['pid'], os.WNOHANG)
        runner.ensure_settled(self.root)
        return state

    def test_timeout_kills_sigterm_ignoring_child_after_leader_exits(self):
        state = self.run_survivor('timeout')
        self.assertEqual(state['exit_code'], -signal.SIGTERM)

    def test_normal_exit_kills_sigterm_ignoring_child_and_preserves_exit_code(self):
        state = self.run_survivor('normal')
        self.assertEqual(state['exit_code'], 0)

    def test_large_input_cannot_block_timeout_or_cleanup(self):
        state = runner.run_process([sys.executable, '-c', 'import time; time.sleep(30)', str(self.root)],
                                   self.root, 'fixture input' * 100000, 0.1,
                                   lambda name: self.root / name, 'fixture-session')
        self.assertTrue(state['timed_out'])
        self.assertFalse(state['running'])
        self.assert_terminated(state['pid'])

    def test_unverifiable_group_remains_unsettled_and_blocks_reuse(self):
        def refuse_settlement(proc):
            # Let the real implementation clean the fixture before simulating
            # the inability to certify settlement to the caller.
            runner.stop_process(proc)
            raise RuntimeError('fixture inspection unavailable')

        with self.assertRaisesRegex(RuntimeError, 'inspection unavailable'):
            runner.run_process([sys.executable, '-c', 'pass'], self.root, '', 3,
                               lambda name: self.root / name, 'fixture-session',
                               cleanup=refuse_settlement)
        state = runner.load(self.root / 'process.json')
        self.assertTrue(state['running'])
        self.assertEqual(state['exit_code'], 0)
        with self.assertRaisesRegex(ValueError, 'not settled'):
            runner.ensure_settled(self.root)

    def test_inspection_failure_never_signals_group_and_reaps_exited_leader(self):
        proc = subprocess.Popen([sys.executable, '-c', 'pass'], start_new_session=True)
        self.addCleanup(proc.wait)
        runner.wait_for_exit(proc, 3)
        with patch.object(runner.subprocess, 'check_output', side_effect=OSError('fixture ps failure')), \
                patch.object(runner.os, 'killpg') as kill_group:
            with self.assertRaisesRegex(OSError, 'ps failure'):
                runner.stop_process(proc)
        kill_group.assert_not_called()
        self.assertEqual(proc.returncode, 0)

    def test_reaped_identity_never_signals_a_possibly_reused_group(self):
        proc = subprocess.Popen([sys.executable, '-c', 'pass'], start_new_session=True)
        proc.wait(timeout=3)
        with patch.object(runner.os, 'killpg') as kill_group:
            with self.assertRaises(ChildProcessError):
                runner.stop_process(proc)
        kill_group.assert_not_called()


if __name__ == '__main__':
    unittest.main()
