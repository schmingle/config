"""Select an installed Python before importing either Claude runner."""
import os
from pathlib import Path
import re
import subprocess
import sys

REQUIRED_OS = ('waitid', 'P_PID', 'WNOWAIT', 'WEXITED', 'WNOHANG')
ATTEMPTED = '_CODEX_CLAUDE_RUNTIME_ATTEMPTED'
PROBE = ('import os, sys, tomllib; sys.exit(0 if all(hasattr(os, name) for name in '
         + repr(REQUIRED_OS) + ') else 1)')


def supported():
    try:
        import tomllib
    except ImportError:
        return False
    return all(hasattr(os, name) for name in REQUIRED_OS)


def candidates():
    """Search explicit executables, including runtimes hidden behind PATH shims."""
    directories = [str(Path(sys.executable).parent), *os.get_exec_path(),
                   '/opt/homebrew/bin', '/usr/local/bin', '/usr/bin']
    seen = {str(Path(sys.executable).resolve())}
    for directory in dict.fromkeys(directories):
        root = Path(directory)
        try:
            paths = [path for path in root.iterdir()
                     if re.fullmatch(r'python3(?:\.[0-9]+)?', path.name)]
        except OSError:
            continue
        for path in sorted(paths, key=lambda item: (int(item.name.split('.')[-1])
                                                   if '.' in item.name else 0), reverse=True):
            identity = str(path.resolve())
            if identity not in seen and path.is_file() and os.access(path, os.X_OK):
                seen.add(identity)
                yield str(path.absolute())


def ensure_runtime():
    """Replace this process once; keep assignment arguments, environment, and cwd."""
    attempted = os.environ.pop(ATTEMPTED, None)
    if supported():
        return
    if not attempted:
        for executable in candidates():
            try:
                result = subprocess.run([executable, '-c', PROBE], capture_output=True, timeout=3)
            except (OSError, subprocess.TimeoutExpired):
                continue
            if result.returncode == 0:
                print('Claude runner: using compatible Python ' + executable, file=sys.stderr)
                os.environ[ATTEMPTED] = '1'
                try:
                    os.execv(executable, [executable, *sys.argv])
                except OSError:
                    os.environ.pop(ATTEMPTED, None)
                    continue
    raise SystemExit('Claude runner needs Python 3.11+ with POSIX waitid/WNOWAIT support. '
                     'No compatible installed runtime could be started. Install a Python build '
                     'with these capabilities (Python 3.14+ on macOS), or add it to PATH; '
                     'Claude was not launched.')
