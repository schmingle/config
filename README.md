# Development configuration

Reusable development settings, agent definitions, and skills. This repository is
public; follow [AGENTS.md](AGENTS.md) before adding or publishing content.

- [Global instructions](.codex/AGENTS.md): reusable working agreements for every Codex task.
- [Agents](.codex/agents/): role definitions, shared instructions, and Claude execution helpers.
- [Skills](.codex/skills/): custom skills and supporting files.

The `.codex/` directory mirrors the corresponding directories in `~/.codex/`.
Instruction references use that default installation path; adapt them if your Codex
home differs. Symlink the installed `AGENTS.md` file and the `agents` and `skills`
folders to these tracked paths to edit the same files from either location. Back up
existing files and folders before linking.
Other local Codex settings are not included.

Keep reusable defaults in the tracked instructions. Customize them through the
local `.codex/AGENTS-PRIVATE.md`, the canonical home for private preferences,
identifying details, and the work/personal account map. This file is gitignored and
must never be committed. To customize a local installation, create it, restrict its
permissions to the owner (`chmod 600 .codex/AGENTS-PRIVATE.md`), and symlink
`~/.codex/AGENTS-PRIVATE.md` to it alongside the tracked global instructions.
The global instructions explicitly direct agents to load this file if present at
the start of each task and apply its relevant preferences and account context.
The tracked defaults remain usable without private settings.

Codex-managed `.system` skills are excluded by `skills/.gitignore`; runtime state is
also excluded. The writer references
a private `~/.codex/writing/style-guide.md`; supply your own guide outside this repo.
This repository does not include writing samples, credentials, or session history.

## Validate changes

Use Python 3.12 or newer. Activate the versioned local hooks for this checkout:

```sh
git config --local core.hooksPath .githooks
```

The pre-commit hook scans the exact staged index, the commit-msg hook checks the
commit message, and the pre-push hook scans outgoing commits and tag messages.
These privacy checks use only the Python standard library and apply to
all changes, including Markdown. They must succeed before publication; CI cannot
replace them. Do not bypass or disable them without explicit user authorization
for the specific bypass and reason.

Run the full local validation:

```sh
python3 -m venv ~/.cache/codex-config-validation
. ~/.cache/codex-config-validation/bin/activate
python -m pip install -r requirements-dev.txt
python -S scripts/check_privacy.py --staged
python scripts/check_config.py
PYTHONDONTWRITEBYTECODE=1 python -S -m unittest discover -s scripts -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s .codex/agents/scripts -p 'test_*.py'
```

The full configuration validator uses the dependencies in `requirements-dev.txt`;
the isolated environment keeps them outside the repository and system Python.
The privacy gate does not need these dependencies. A missing dependency or failed
check blocks publication.
GitHub Actions runs validation on pushes and pull requests as an additional check.
Tests use local fixtures and a fake CLI; they do not invoke a paid model or
connected service. The checks flag common configuration mistakes and credential
formats; review the full diff for privacy and correctness before committing or
pushing.
