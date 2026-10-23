# Development configuration

Reusable development settings, agent definitions, and skills. This repository is
public; follow [AGENTS.md](AGENTS.md) before adding or publishing content.

- [Global instructions](.codex/AGENTS.md): reusable working agreements for every Codex task.
- [Agents](.codex/agents/): role definitions, shared instructions, and Claude execution helpers.
- [Skills](.codex/skills/): custom skills and supporting files.
- [Claude Code](.claude/): the Claude Code counterparts, mirroring `~/.claude/`: delegate and PR agents (`agents/`), their shared guides (`agent-guides/`), skills (`skills/`), and compatibility handoff entry points (`bin/`).

The `.codex/` directory mirrors the corresponding directories in `~/.codex/`.
Instruction references use that default installation path; adapt them if your Codex
home differs. Symlink the installed `AGENTS.md` file and the `agents` and `skills`
folders to these tracked paths to edit the same files from either location. Back up
existing files and folders before linking.
Other local Codex settings are not included.

The Claude Code counterpart is the gitignored `.claude/CLAUDE-PRIVATE.md`, installed
as `~/.claude/CLAUDE-PRIVATE.md` and read by `.claude/CLAUDE.md`. Create it the same
way (`chmod 600`, symlink); never commit it.

`.claude/` follows the same rules for `~/.claude/`: symlink or copy the `agents`,
`agent-guides`, `skills`, and `bin` folders from the tracked paths after backing up
existing files. Its definitions reference `~/.claude/` paths. Claude Code settings,
credentials, history, and runtime state are not included.

Keep reusable defaults in the tracked instructions. Customize them through the
local `.codex/AGENTS-PRIVATE.md`, the canonical home for private preferences,
identifying details, and the work/personal account map. This file is gitignored and
must never be committed. To customize a local installation, create it, restrict its
permissions to the owner (`chmod 600 .codex/AGENTS-PRIVATE.md`), and symlink
`~/.codex/AGENTS-PRIVATE.md` to it alongside the tracked global instructions.
The global instructions explicitly direct agents to load this file if present at
the start of each task and apply its relevant preferences and account context.
The general defaults work without private settings. Operational workflows may
require additional private configuration: [Linear ticket triage](.codex/skills/linear-ticket/references/triage.md#private-workflow-settings)
requires the documented team, repository, creator allowlist, and estimate settings
in `~/.codex/private/linear-ticket-workflows.json`; it stops if they are missing or
cannot be verified. An account map alone does not configure that workflow.

Codex-managed `.system` skills are excluded by `skills/.gitignore`; runtime state is
also excluded. Supply your own private writing guide outside this repo; the
[guide-location rules](.codex/agents/writer.md#guide-location) support an explicit
path or `<codex-home>/writing/style-guide.md`.
This repository does not include writing samples, credentials, or session history.

## Agent execution

Both providers can call the same [role launcher](scripts/agent-launch.md):

```sh
./scripts/agent-launch --role delegate-low --assignment /private/task.json --checkout /absolute/checkout --output /new/private/bundle --finish-by 2030-01-01T12:00:00Z
```

Use real paths and a current deadline. Roles select the canonical executor settings;
there is no direction or caller-specific model override. The launcher shares task
validation, deadlines, checkout records, logging, and process settlement, with small
Codex and Claude adapters. Existing provider entry points remain compatibility
wrappers. Follow the linked contract for assignment fields and verification.

Resolve installed symlinks back to this checkout. For copied provider folders,
set `AGENT_LAUNCH_ROOT` to this configuration checkout so both providers can find
the shared launcher and helpers. Recursive handoffs are rejected. Configuration
porting remains Codex to Claude.

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
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s .claude/bin -p 'test_*.py'
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
